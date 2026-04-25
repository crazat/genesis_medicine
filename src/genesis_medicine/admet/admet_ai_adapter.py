"""ADMET-AI v2 어댑터 (Stanford, MIT).

https://github.com/swansonk14/admet_ai

41 ADMET endpoints (Therapeutics Data Commons 데이터셋 기반).
v2는 Chemprop 2.0 사용 (더 빠름, RDKit fingerprint 미사용).

핵심 endpoints
--------------
- Lipinski (룰5)
- QED (drug-likeness)
- BBB_Martins (혈뇌장벽)
- hERG (심독성)
- DILI (간독성)
- AMES (변이원성)
- SkinReaction
- LD50_Zhu
- Solubility (logS)
- Permeability_Caco2
- F20 (구강 생체이용률 20%)
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from loguru import logger

from .base import ADMETPrediction, ADMETRequest, ADMETResult


class ADMETAIAdapter:
    engine_name = "admet_ai_v2"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/admet_ai"),
        models_dir: Path | None = None,
        num_workers: int = 4,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir = models_dir
        self.num_workers = num_workers
        self.device = device
        self._predictor = None

    def predict(self, req: ADMETRequest) -> ADMETResult:
        t0 = time.time()
        try:
            df = self._run(req)
        except ImportError:
            logger.warning(
                "admet_ai 미설치. pip install -e '.[admet]'"
            )
            return ADMETResult(
                engine=self.engine_name, predictions=[],
                wall_seconds=time.time() - t0,
                metadata={"error": "admet_ai not installed"},
            )

        predictions: list[ADMETPrediction] = []
        for _, row in df.iterrows():
            smi = row.get("smiles", row.name)
            props = {k: float(v) for k, v in row.items() if k != "smiles" and pd.notna(v)}
            predictions.append(ADMETPrediction(smiles=smi, properties=props))

        logger.info(
            "ADMET-AI v2: {} 화합물 × {} endpoints",
            len(predictions),
            len(predictions[0].properties) if predictions else 0,
        )
        return ADMETResult(
            engine=self.engine_name,
            predictions=predictions,
            wall_seconds=time.time() - t0,
            metadata={"n_endpoints": len(predictions[0].properties) if predictions else 0},
        )

    def _run(self, req: ADMETRequest) -> pd.DataFrame:
        from admet_ai import ADMETModel

        if self._predictor is None:
            self._predictor = ADMETModel(
                models_dir=str(self.models_dir) if self.models_dir else None,
                num_workers=self.num_workers,
            )
        return self._predictor.predict(smiles=req.smiles_list)


def filter_by_admet(
    smiles_scores: dict[str, float],
    admet: ADMETResult,
    *,
    require_bbb: bool = False,
    require_herg_safe: bool = True,
    require_dili_safe: bool = True,
    min_qed: float = 0.4,
) -> dict[str, float]:
    """ADMET 게이트 — 안전 임계 통과 화합물만 통과.

    AD 시나리오에서는 require_bbb=True (혈뇌장벽 통과 필요).
    """
    by_smi = {p.smiles: p for p in admet.predictions}
    out: dict[str, float] = {}
    for smi, score in smiles_scores.items():
        if smi not in by_smi:
            continue
        pred = by_smi[smi]
        if require_bbb and not pred.bbb_permeable:
            continue
        if require_herg_safe and not pred.herg_safe:
            continue
        if require_dili_safe and not pred.dili_safe:
            continue
        if pred.properties.get("QED", 0.0) < min_qed:
            continue
        out[smi] = score
    return out
