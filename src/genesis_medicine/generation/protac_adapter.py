"""PROTAC 생성 어댑터 — 그래프 기반 generative model + RL.

근거: Nori et al. arxiv 2211.02660 — De novo PROTAC design with graph-based deep
generative models. POI 친화도 + 분해 활성 둘 다 RL 보상.

용도 (Stage 5.5 — B2)
---------------------
타겟이 분해 가능 (E3 ligase 협력), 단순 inhibitor가 막힌 경우.
AD 멀티타겟 시나리오에서 tau, APP의 protein degradation에 적합.

라이선스
--------
이 어댑터 자체는 MIT, 상업 OK으로 등록되어 있음. 단 학습 데이터셋 출처가
모호한 가중치를 사용하면 라이선스 검증 필요. 안전 기본은 research 빌드.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger
from pydantic import BaseModel, Field


class PROTACRequest(BaseModel):
    poi_smiles: str = Field(description="POI warhead SMILES")
    e3_ligase: str = Field(default="CRBN", description="CRBN | VHL | MDM2 | IAP")
    e3_ligand_smiles: str | None = None
    linker_length_range: tuple[int, int] = (3, 12)
    n_molecules: int = 200
    seed: int = 42


class PROTACMolecule(BaseModel):
    smiles: str
    n_heavy_atoms: int
    predicted_dc50_nm: float | None = None
    sa_score: float | None = None


class PROTACResult(BaseModel):
    engine: str
    molecules: list[PROTACMolecule]
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


class PROTACAdapter:
    engine_name = "protac_jt_vae"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/protac"),
        weights_path: Path | None = None,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.weights_path = weights_path
        self.device = device

    def generate(self, req: PROTACRequest) -> PROTACResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="protac_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            cfg = tmp_dir / "req.json"
            cfg.write_text(json.dumps(req.model_dump()))
            out = tmp_dir / "out.json"

            cmd = [
                "python", "-m", "protac_design.generate",
                "--config", str(cfg),
                "--output", str(out),
                "--device", self.device,
            ]
            if self.weights_path:
                cmd += ["--weights", str(self.weights_path)]

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
            except FileNotFoundError:
                logger.warning("PROTAC 생성 모듈 미설치 — research/Dockerfile.protac")
                return PROTACResult(
                    engine=self.engine_name, molecules=[],
                    wall_seconds=time.time() - t0,
                    metadata={"error": "module not installed"},
                )
            data = json.loads(out.read_text()) if out.exists() else {"molecules": []}
            mols = [
                PROTACMolecule(
                    smiles=m["smiles"],
                    n_heavy_atoms=int(m.get("n_heavy", 0)),
                    predicted_dc50_nm=m.get("dc50_nm"),
                    sa_score=m.get("sa"),
                )
                for m in data.get("molecules", [])
            ]
            logger.info("PROTAC 생성: {} 분자 (E3={})", len(mols), req.e3_ligase)
            return PROTACResult(
                engine=self.engine_name,
                molecules=mols,
                wall_seconds=time.time() - t0,
                metadata={"e3_ligase": req.e3_ligase},
            )
