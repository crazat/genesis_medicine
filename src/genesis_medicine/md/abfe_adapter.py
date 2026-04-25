"""Stage 8.5 — Absolute Binding Free Energy (ABFE).

도구
----
- FEP-SPell-ABFE (MIT, JCIM 2025) — OpenMM 기반 자동화
- pmx (GPL-3) — GROMACS 기반, 서브프로세스 격리 + research 빌드 한정
- BindFlow — pipeline (외부 호출)

근거: Bossche et al. JCIM 2024 — pmx-Sage 2.0이 FEP+와 통계적 동급
     (482 perturbations에서 AUE 3.64 vs 3.66 kJ/mol).

용도
----
6단계 스크리닝의 상위 10~50개 후보를 ABFE로 검증.
임상 후보 결정 직전 마지막 정량 게이트.

라이선스 노트
------------
- FEP-SPell-ABFE: MIT → commercial OK
- pmx: GPL-3 → 코드 결합 불가, 서브프로세스 호출만 + research 한정
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field


class ABFERequest(BaseModel):
    receptor_pdb: Path
    ligand_sdf: Path
    output_dir: Path
    n_replicas: int = 3                # 통계 신뢰
    n_lambda_windows: int = 16
    timestep_fs: float = 2.0
    eq_ns: float = 5.0                 # equilibration
    prod_ns: float = 10.0              # production per window
    seed: int = 42


class ABFEResult(BaseModel):
    engine: str
    delta_g: float = Field(description="결합자유에너지 (kcal/mol)")
    delta_g_uncertainty: float = 0.0
    pkd_predicted: float | None = None
    n_failed_windows: int = 0
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


class ABFEAdapter:
    """FEP-SPell-ABFE / pmx 통합 ABFE 워크플로."""

    engine_name = "fep_spell_abfe"

    def __init__(
        self,
        *,
        backend: str = "fep_spell",       # fep_spell | pmx
        cache_dir: Path = Path(".cache/abfe"),
        device: str = "cuda:0",
        threads: int = 8,
    ) -> None:
        self.backend = backend
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.threads = threads

    def compute(self, req: ABFERequest) -> ABFEResult:
        t0 = time.time()
        if self.backend == "fep_spell":
            return self._run_fep_spell(req, t0)
        if self.backend == "pmx":
            return self._run_pmx(req, t0)
        raise ValueError(f"Unknown ABFE backend: {self.backend}")

    def _run_fep_spell(self, req: ABFERequest, t0: float) -> ABFEResult:
        out = req.output_dir
        out.mkdir(parents=True, exist_ok=True)
        config = {
            "receptor": str(req.receptor_pdb),
            "ligand": str(req.ligand_sdf),
            "n_replicas": req.n_replicas,
            "n_lambda_windows": req.n_lambda_windows,
            "timestep_fs": req.timestep_fs,
            "eq_ns": req.eq_ns,
            "prod_ns": req.prod_ns,
            "seed": req.seed,
            "device": self.device,
        }
        config_path = out / "abfe_config.json"
        config_path.write_text(json.dumps(config, indent=2))

        cmd = ["fep-spell-abfe", "run", "--config", str(config_path), "--out", str(out)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=86400)
        except FileNotFoundError:
            logger.warning(
                "FEP-SPell-ABFE 미설치. pip install fep-spell-abfe 또는 git clone."
            )
            return ABFEResult(
                engine=self.engine_name, delta_g=0.0,
                wall_seconds=time.time() - t0,
                metadata={"error": "fep-spell-abfe not installed"},
            )

        result_path = out / "abfe_result.json"
        if not result_path.exists():
            logger.error("ABFE 결과 파일 없음: {}", result_path)
            return ABFEResult(engine=self.engine_name, delta_g=0.0,
                              wall_seconds=time.time() - t0)
        data = json.loads(result_path.read_text())
        dg = float(data["delta_g_kcal"])
        return ABFEResult(
            engine=self.engine_name,
            delta_g=dg,
            delta_g_uncertainty=float(data.get("uncertainty", 0.0)),
            pkd_predicted=-dg / 1.364,    # ΔG = -RT ln(Kd), 310K
            n_failed_windows=int(data.get("n_failed", 0)),
            wall_seconds=time.time() - t0,
            metadata=data.get("metadata", {}),
        )

    def _run_pmx(self, req: ABFERequest, t0: float) -> ABFEResult:
        """pmx 호출 — research 빌드 한정.

        GPL-3이므로 반드시 서브프로세스로 격리. 우리 코드와 import 결합 금지.
        commercial 빌드에서 호출하면 LicenseGate가 위에서 차단.
        """
        out = req.output_dir
        out.mkdir(parents=True, exist_ok=True)
        cmd = [
            "pmx", "abfe",
            "--receptor", str(req.receptor_pdb),
            "--ligand", str(req.ligand_sdf),
            "--output", str(out),
            "--lambdas", str(req.n_lambda_windows),
            "--replicas", str(req.n_replicas),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=86400)
        except FileNotFoundError:
            logger.warning("pmx 미설치 (research only).")
            return ABFEResult(engine="pmx", delta_g=0.0,
                              wall_seconds=time.time() - t0,
                              metadata={"error": "pmx not installed"})
        result_path = out / "result.json"
        data = json.loads(result_path.read_text()) if result_path.exists() else {}
        dg = float(data.get("delta_g", 0.0))
        return ABFEResult(
            engine="pmx",
            delta_g=dg,
            pkd_predicted=-dg / 1.364,
            wall_seconds=time.time() - t0,
            metadata=data,
        )
