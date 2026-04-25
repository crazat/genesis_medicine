"""분자글루 생성 — Conditioned JT-VAE + 단백질 임베딩.

근거: MDPI Biomolecules 2025 (15:849) — VHL/CRBN/MDM2 조건부 분자 생성.

라이선스 — 안전 기본 research-only.
학습 데이터에 NC 출처가 포함될 수 있어 commercial 사용 시 별도 검증 필요.
LicenseGate가 'molglue_jtvae' 키로 commercial 빌드에서 자동 차단.

용도
----
- 단일 protein-protein interaction에서 neosubstrate 도출
- AD에서 tau filament 분해 등
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger
from pydantic import BaseModel, Field

from ..licensing import LicenseGate
from ..licensing.gate import BuildProfile


class MolecularGlueRequest(BaseModel):
    target_sequence: str = Field(description="neosubstrate 후보 단백질 시퀀스")
    e3_ligase: str = Field(default="CRBN")
    n_molecules: int = 100
    rotational_features: bool = True   # 3D 회전 각 통합 (정확도 ↑)
    seed: int = 42


class MolecularGlueResult(BaseModel):
    engine: str
    molecules: list[dict]
    wall_seconds: float = 0.0


class MolecularGlueAdapter:
    engine_name = "molglue_jtvae"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/glue"),
        weights_path: Path | None = None,
        device: str = "cuda:0",
        build_profile: str = "research",  # ⚠️ commercial은 LicenseGate가 차단
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.weights_path = weights_path
        self.device = device
        # 라이선스 게이트 — commercial에서 호출 시 LicenseViolation
        gate = LicenseGate(BuildProfile.from_name(build_profile))
        gate.require(self.engine_name)

    def generate(self, req: MolecularGlueRequest) -> MolecularGlueResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="glue_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            cfg = tmp_dir / "req.json"
            cfg.write_text(json.dumps(req.model_dump()))
            out = tmp_dir / "out.json"

            cmd = [
                "python", "-m", "molglue_jtvae.sample",
                "--config", str(cfg),
                "--output", str(out),
                "--device", self.device,
            ]
            if self.weights_path:
                cmd += ["--weights", str(self.weights_path)]
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
            except FileNotFoundError:
                logger.warning("분자글루 모듈 미설치 — research only.")
                return MolecularGlueResult(
                    engine=self.engine_name, molecules=[],
                    wall_seconds=time.time() - t0,
                )
            data = json.loads(out.read_text()) if out.exists() else {"molecules": []}
            return MolecularGlueResult(
                engine=self.engine_name,
                molecules=data.get("molecules", []),
                wall_seconds=time.time() - t0,
            )
