"""CarsiDock-Cov adapter (CarbonSilicon AI, 2025; Apache-2.0).

The first deep-learning covalent docking model. Critical for our entire
chemotype family: shikonin (자근) quinone, EGCG (녹차) catechin polyphenols,
embelin / EMB-3 (자단) p-quinones — all Michael acceptors that can form
covalent adducts with cysteine residues in MMP-1, TYR, MITF, and other
catalytic-Cys targets.

License : Apache-2.0 (code); model weights have separate commercial-OK license.
GitHub  : https://github.com/sc8668/CarsiDock-Cov
Paper   : PMC12647997.

Pipeline integration:
    Augments our standard non-covalent cofold (Boltz-2 + Chai-1) with
    explicit covalent-adduct scoring for compounds whose pharmacophore
    contains Michael-acceptor or epoxide-like warheads.

Use case:
    For TYR target — the catalytic dicopper site sits at the bottom of a
    pocket lined by Cys residues (Cys81, Cys83). Polyphenol oxidative
    quinones can covalently modify these — a mechanism completely missed
    by Boltz-2 / Chai-1 affinity heads.
    For MMP-1 — Cys278 in the catalytic cleft is targetable by sulfhydryl
    inhibitors (compare to the discontinued thiol-based MMP inhibitors).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger


COVALENT_WARHEAD_SMARTS = {
    "michael_acceptor_acrylate": "C=CC(=O)O",
    "michael_acceptor_acrylamide": "C=CC(=O)N",
    "p_quinone": "O=C1C=CC(=O)C=C1",
    "ortho_quinone": "O=C1C=CC=C(O)1",
    "epoxide": "C1OC1",
    "isothiocyanate": "N=C=S",
    "michael_acceptor_alpha_beta_unsaturated_carbonyl": "C=CC=O",
    "vinyl_sulfone": "C=CS(=O)=O",
    "alkynone": "C#CC=O",
}


@dataclass
class CovalentDockingResult:
    compound: str
    smiles: str
    target: str
    has_covalent_warhead: bool
    detected_warheads: List[str]
    proposed_residue_cys: Optional[str]    # e.g. "Cys278" if known
    covalent_score: Optional[float]
    non_covalent_score: Optional[float]
    consensus_call: str = "covalent_capable"
    method: str = "carsidock_cov"
    available: bool = False
    note: str = ""


class CarsiDockCovAdapter:
    engine_name = "carsidock_cov"

    # Catalytic Cys residues for our skin targets (literature)
    TARGET_CYS = {
        "MMP1": "Cys278",     # catalytic; pro-domain "cysteine switch"
        "MMP3": "Cys100",
        "MMP9": "Cys99",
        "TYR": "Cys81",        # near dicopper site
        "MITF": None,          # transcription factor, less Cys-druggable
        "TGFB1": "Cys223",     # disulfide-bridged; covalent disrupts dimer
        "SIRT1": "Cys371",     # NAD+-binding regulatory cysteine
        "AR": None,
    }

    def __init__(self, *, cache_dir: Path = Path(".cache/carsidock_cov")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._available = self._check_install()

    def _check_install(self) -> bool:
        try:
            import torch  # noqa: F401
            carsidock_root = Path.home() / "CarsiDock-Cov"
            return carsidock_root.exists()
        except ImportError:
            return False

    def detect_warhead(self, smiles: str) -> List[str]:
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return []
            found = []
            for name, smarts in COVALENT_WARHEAD_SMARTS.items():
                pat = Chem.MolFromSmarts(smarts)
                if pat and mol.HasSubstructMatch(pat):
                    found.append(name)
            return found
        except ImportError:
            return []

    def score(self, *, compound: str, smiles: str, target: str,
              receptor_pdb: Optional[Path] = None) -> CovalentDockingResult:
        warheads = self.detect_warhead(smiles)
        cys = self.TARGET_CYS.get(target.upper())
        has_warhead = len(warheads) > 0

        if not self._available:
            return CovalentDockingResult(
                compound=compound, smiles=smiles, target=target,
                has_covalent_warhead=has_warhead,
                detected_warheads=warheads,
                proposed_residue_cys=cys,
                covalent_score=None, non_covalent_score=None,
                consensus_call=("covalent_capable" if has_warhead
                                  else "non_covalent_only"),
                available=False,
                note=("CarsiDock-Cov not installed; warhead detection only. "
                       "Clone https://github.com/sc8668/CarsiDock-Cov into "
                       "$HOME/CarsiDock-Cov + download model weights."),
            )
        # Production scoring would call CarsiDock-Cov inference
        return CovalentDockingResult(
            compound=compound, smiles=smiles, target=target,
            has_covalent_warhead=has_warhead, detected_warheads=warheads,
            proposed_residue_cys=cys,
            covalent_score=None, non_covalent_score=None,
            consensus_call="covalent_capable" if has_warhead else "non_covalent_only",
            available=True, note="model present; inference pipeline pending.",
        )
