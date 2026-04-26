"""Boltz-ABFE adapter (Recursion + MIT, arXiv 2508.19385, 2025-10).

Eliminates the crystal-structure prerequisite for ABFE: a Boltz-2 cofold pose
feeds an automated Sage/OpenMM ABFE pipeline that achieves Pearson R = 0.95
and centered MAE 0.42 kcal/mol on a benchmark protein-ligand set.

Status: Recursion fork is the canonical implementation (not yet merged into
mainstream `jwohlwend/boltz` 2.2.1). This adapter follows our standard
license-gated import pattern: it returns a stub with installation guidance
when the optional `boltz_abfe` package is not present.

License: MIT (Recursion + MIT 2025).
GitHub : pending Recursion public release; Bio-IT World coverage Oct 2025.
Paper  : arXiv 2508.19385 / JCTC 2025 10.1021/acs.jctc.5c01451.

Use case for skin-fibrosis pipeline:
    Currently 12 of our 13 disease targets (TYR, TYRP1, DCT, SRD5A1/2, AR,
    Wnt10b, β-catenin, CTGF, LOX, FBN1, mTOR, PIEZO1) lack a co-crystal
    structure of any natural-product analog. Boltz-ABFE unblocks these
    targets at quantitative ΔG resolution.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class BoltzABFEResult:
    compound: str
    target: str
    smiles: str
    delta_g_kcal_mol: Optional[float]
    uncertainty_kcal_mol: Optional[float]
    pearson_r_calibration: float = 0.95   # benchmark, not per-run
    mae_calibration_kcal_mol: float = 0.42
    method: str = "boltz_abfe"
    available: bool = False
    note: str = ""


class BoltzABFEAdapter:
    """Boltz-ABFE wrapper — license-gated.

    Two integration paths:
        1) Recursion fork CLI (`boltz-abfe predict ...`) once public.
        2) DIY: Boltz-2 cofold → openmmtools alchemical RE on the predicted pose.
           Path 2 is what our `scripts/run_abfe_corrected.py` already does;
           this adapter provides a uniform call site.
    """

    engine_name = "boltz_abfe"

    def __init__(self, *, cache_dir: Path = Path(".cache/boltz_abfe")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._available = self._check_install()

    def _check_install(self) -> bool:
        """Check whether a boltz-abfe CLI is on PATH."""
        return shutil.which("boltz-abfe") is not None

    def predict(self, *, compound: str, target: str, smiles: str,
                receptor_pdb: Path, **kwargs) -> BoltzABFEResult:
        if not self._available:
            return BoltzABFEResult(
                compound=compound, target=target, smiles=smiles,
                delta_g_kcal_mol=None, uncertainty_kcal_mol=None,
                available=False,
                note=("boltz-abfe CLI not on PATH. Install from Recursion fork "
                       "when public release lands; until then use "
                       "scripts/run_abfe_corrected.py for the same cycle."),
            )

        out = self.cache_dir / f"{target}__{compound}"
        cmd = [
            "boltz-abfe", "predict",
            "--smiles", smiles,
            "--receptor", str(receptor_pdb),
            "--out", str(out),
        ]
        try:
            subprocess.run(cmd, check=True, timeout=14400)
            result_json = out / "abfe_result.json"
            data = json.loads(result_json.read_text())
            return BoltzABFEResult(
                compound=compound, target=target, smiles=smiles,
                delta_g_kcal_mol=data["delta_g_kcal_mol"],
                uncertainty_kcal_mol=data["uncertainty_kcal_mol"],
                available=True,
            )
        except Exception as e:
            logger.error(f"Boltz-ABFE failed for {target}×{compound}: {e}")
            return BoltzABFEResult(
                compound=compound, target=target, smiles=smiles,
                delta_g_kcal_mol=None, uncertainty_kcal_mol=None,
                available=False, note=f"runtime error: {e}",
            )
