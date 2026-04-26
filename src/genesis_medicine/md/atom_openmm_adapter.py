"""AToM-OpenMM adapter (Gallicchio Lab, MIT-style, 2026-04-23 active).

Alchemical Transfer Method — moves the ligand wholesale between bound and
bulk states without ever de-charging in the metal coordination shell.
This sidesteps the polarization artefact that ZAFF and other non-polarizable
zinc models cannot cure in MMP-1 / MMP-3 / MMP-9 ABFE.

License : MIT-style (NOASSERTION but explicit)
GitHub  : https://github.com/Gallicchio-Lab/AToM-OpenMM (161★, active)
Paper   : Gallicchio et al., reference impl for ATM in OpenMM 8.

Cleanest formulation for our top zinc target MMP-1: ATM uses a single-
topology dual-region scheme that physically transfers the ligand between
two solvent boxes (bound complex + apo solvent) via a mid-state with
soft-core potentials. No need to "decharge around Zn²⁺" at all.

Use case:
    Replace our 16-window flat-bottom-restrained alchemical RE for the
    three matrix metalloprotease targets (MMP-1, MMP-3, MMP-9) with ATM,
    eliminating the "MMP-1 minus zinc" caveat documented in preprint #8 §4.1.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class ATMResult:
    compound: str
    target: str
    delta_g_kcal_mol: Optional[float]
    uncertainty_kcal_mol: Optional[float]
    n_replicas: int
    n_iterations: int
    method: str = "atom_openmm"
    available: bool = False
    note: str = ""


class ATOMOpenMMAdapter:
    engine_name = "atom_openmm"

    def __init__(self, *, cache_dir: Path = Path(".cache/atom_openmm")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._available = self._check_install()

    def _check_install(self) -> bool:
        try:
            import openmm  # noqa: F401
            # AToM-OpenMM is a script-driven framework; check for its repo.
            atom_root = Path.home() / "AToM-OpenMM"
            if atom_root.exists():
                return True
            return shutil.which("atom-openmm") is not None
        except ImportError:
            return False

    def predict(self, *, compound: str, target: str,
                receptor_pdb: Path, ligand_smiles: str,
                n_replicas: int = 22, n_iterations: int = 500,
                **kwargs) -> ATMResult:
        if not self._available:
            return ATMResult(
                compound=compound, target=target,
                delta_g_kcal_mol=None, uncertainty_kcal_mol=None,
                n_replicas=n_replicas, n_iterations=n_iterations,
                available=False,
                note=("AToM-OpenMM not installed. Clone "
                       "https://github.com/Gallicchio-Lab/AToM-OpenMM into "
                       "$HOME/AToM-OpenMM and ensure openmm 8 + numpy 2 env."),
            )
        # In a real run this would build the ATM input deck (`mintherm.py`,
        # `mdlambda.py`) and submit replica exchange. For now flag as scaffold.
        return ATMResult(
            compound=compound, target=target,
            delta_g_kcal_mol=None, uncertainty_kcal_mol=None,
            n_replicas=n_replicas, n_iterations=n_iterations,
            available=True,
            note=("ATM scaffold ready; production input-deck generation pending. "
                  "See AToM-OpenMM/examples for reference templates."),
        )
