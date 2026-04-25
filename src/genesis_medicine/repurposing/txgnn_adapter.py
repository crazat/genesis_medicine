"""TxGNN — Zitnik lab (Harvard) 약물 재창출 GNN 어댑터.

https://github.com/mims-harvard/TxGNN (MIT)
Nature Medicine 2024 — clinician-centered drug repurposing.

성능
----
- 17,080 질병 × 7,957 후보 (PrimeKG 기반)
- zero-shot indication +49.2% vs 8 baseline
- zero-shot contraindication +35.1%
- multi-hop 경로 설명 (Explainer 모듈)

용도 (Stage 1.5 — Genesis_Medicine v2.1)
----------------------------------------
질병 EFO → zero-shot 후보 약물 → 이후 우리 6단계 스크리닝의 ligand library에 합류.
**타겟 발굴 보다 더 빠른 임상 진입 경로** (이미 승인된 약물).

라이선스
-------
MIT. PrimeKG 기반 (PrimeKG도 MIT). commercial-safe.

설치
----
pip install -e git+https://github.com/mims-harvard/TxGNN.git
또는 docker/Dockerfile.repurposing
"""

from __future__ import annotations

import time
from pathlib import Path

from loguru import logger

from .base import RepurposingHit, RepurposingRequest, RepurposingResult


class TxGNNAdapter:
    engine_name = "txgnn"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/txgnn"),
        model_path: Path | None = None,
        kg_version: str = "primekg_2023_12",
        device: str = "cuda:0",
        explain: bool = True,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = model_path
        self.kg_version = kg_version
        self.device = device
        self.explain = explain
        self._model = None

    def supports_explanation(self) -> bool:
        return self.explain

    def repurpose(self, req: RepurposingRequest) -> RepurposingResult:
        t0 = time.time()
        try:
            hits = self._run_python_api(req)
        except ImportError:
            logger.warning(
                "TxGNN 미설치. pip install -e git+https://github.com/mims-harvard/TxGNN"
            )
            return RepurposingResult(
                engine=self.engine_name, disease_id=req.disease_id, hits=[],
                wall_seconds=time.time() - t0,
                metadata={"error": "txgnn not installed"},
            )

        hits.sort(key=lambda h: h.score, reverse=True)
        hits = hits[: req.top_k]

        logger.info(
            "TxGNN [{}]: {} 후보 약물 ({}). 상위: {}",
            req.disease_id,
            len(hits),
            req.relation,
            [(h.drug_name or h.drug_id, round(h.score, 3)) for h in hits[:5]],
        )
        return RepurposingResult(
            engine=self.engine_name,
            disease_id=req.disease_id,
            hits=hits,
            wall_seconds=time.time() - t0,
            metadata={"kg_version": self.kg_version, "explain": self.explain},
        )

    def _run_python_api(self, req: RepurposingRequest) -> list[RepurposingHit]:
        """TxGNN Python API 호출.

        패키지 import는 lazy — 미설치 시 ImportError가 상위에서 처리됨.
        """
        from txgnn import TxData, TxGNN, TxEval  # type: ignore[import-untyped]

        if self._model is None:
            data = TxData(data_folder_path=str(self.cache_dir / self.kg_version))
            data.prepare_split(split="complex_disease", seed=req.seed)
            tx = TxGNN(data=data, weight_bias_track=False, proj_name="genesis", exp_name="repurpose")
            if self.model_path and self.model_path.exists():
                tx.load_pretrained(str(self.model_path))
            else:
                logger.warning("TxGNN 사전훈련 가중치 없음 — 랜덤 초기화 (실 사용 시 다운로드 필요)")
            self._model = tx

        eval_module = TxEval(model=self._model)
        result = eval_module.eval_disease_centric(
            disease_idxs=[req.disease_id],
            relation=req.relation,
            return_raw=True,
        )

        hits: list[RepurposingHit] = []
        for entry in result.get("predictions", []):
            hits.append(
                RepurposingHit(
                    drug_id=str(entry["drug_id"]),
                    drug_name=entry.get("drug_name"),
                    smiles=entry.get("smiles"),
                    score=float(entry["score"]),
                    explanation=self._extract_explanation(entry) if self.explain else None,
                    targets=list(entry.get("targets", [])),
                )
            )
        return hits

    def _extract_explanation(self, entry: dict) -> str | None:
        if "explanation_path" not in entry:
            return None
        path = entry["explanation_path"]
        return " → ".join(str(node) for node in path)
