"""AIMNet2 adapter (Zubatyuk lab, JACS Au 2024 + ACS 2025 plenary).

Foundation neural network potential covering 14 elements (incl. Cl, Br, I,
S, P, B, As) with explicit Coulomb long-range term. Critical advantage over
MACE-OFF24 for charged drug-like ligands and ionizable side chains.

License : open (MIT precursor; verify zubatyuk/aimnet2 repo LICENSE for v2)
GitHub  : https://github.com/zubatyuk/aimnet2
Issue   : openmm-ml integration #63 not yet merged

Why this matters for skin natural products:
    Berberine (cation, AR target), shikonin (anionic naphthoquinone),
    licochalcone A (deprotonated phenol at physiological pH), ginsenoside
    Rg1 (glycoside): all our top-hit compounds are charged at physiological
    pH where MACE-OFF24 silently underperforms (no explicit Coulomb).
    AIMNet2 handles them natively.

Pipeline integration:
    - As MLPotential('aimnet2') wrapper analogous to existing MACE one
      (`src/genesis_medicine/md/openmm_ml_refine.py`)
    - For charged-compound ABFE refinement / energy correction
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import numpy as np
from loguru import logger


@dataclass
class AIMNet2Result:
    compound: str
    smiles: str
    n_atoms: int
    energy_hartree: Optional[float]
    energy_kcal_mol: Optional[float]
    forces_max_kcal_mol_A: Optional[float]
    method: str = "aimnet2_singlepoint"
    available: bool = False
    note: str = ""


class AIMNet2Adapter:
    engine_name = "aimnet2"

    def __init__(self, *, cache_dir: Path = Path(".cache/aimnet2"),
                 model_name: str = "aimnet2"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self._calculator = None
        self._available = self._lazy_load()

    def _lazy_load(self) -> bool:
        try:
            from aimnet import AIMNetCalculator  # type: ignore
            self._calculator = AIMNetCalculator(self.model_name)
            return True
        except Exception as e:
            logger.debug(f"AIMNet2 unavailable: {e}")
            return False

    def singlepoint(self, *, compound: str, smiles: str,
                    optimize_3d: bool = True) -> AIMNet2Result:
        if not self._available:
            return AIMNet2Result(
                compound=compound, smiles=smiles, n_atoms=0,
                energy_hartree=None, energy_kcal_mol=None,
                forces_max_kcal_mol_A=None, available=False,
                note="aimnet not installed; run `uv pip install aimnet` "
                     "and verify model checkpoints download.",
            )
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
            if optimize_3d:
                AllChem.EmbedMolecule(mol, randomSeed=42)
                AllChem.MMFFOptimizeMolecule(mol)
            conf = mol.GetConformer()
            coords = np.array([list(conf.GetAtomPosition(i))
                                for i in range(mol.GetNumAtoms())])
            numbers = np.array([a.GetAtomicNum() for a in mol.GetAtoms()])

            self._calculator.set_coordinates(coords, numbers)
            energy = float(self._calculator.energy())
            forces = self._calculator.forces()
            f_max = float(np.linalg.norm(forces, axis=1).max())

            return AIMNet2Result(
                compound=compound, smiles=smiles,
                n_atoms=int(mol.GetNumAtoms()),
                energy_hartree=energy,
                energy_kcal_mol=energy * 627.509,
                forces_max_kcal_mol_A=f_max * 627.509,
                available=True,
            )
        except Exception as e:
            return AIMNet2Result(
                compound=compound, smiles=smiles, n_atoms=0,
                energy_hartree=None, energy_kcal_mol=None,
                forces_max_kcal_mol_A=None, available=False,
                note=f"runtime error: {str(e)[:200]}",
            )
