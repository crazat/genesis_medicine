"""GFN2-xTB single-point + opt on universal scaffold 5 leaders.

Quantum-grade energies for paper-tier reviewer rigor.
Output: pilot/universal_scaffold_admet/xtb_energies.csv
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/universal_scaffold_admet"
OUT.mkdir(parents=True, exist_ok=True)

LEADERS = [
    ("R12_4",  "OCC1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R12_11", "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"),
    ("R12_23", "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R14_5",  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"),
    ("R13_13", "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1"),
]


def xtb_one(args):
    name, smi = args
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import AllChem
        from xtb.interface import Calculator, Param
        from xtb.libxtb import VERBOSITY_MUTED
        RDLogger.DisableLog("rdApp.*")

        m = Chem.MolFromSmiles(smi)
        m = Chem.AddHs(m)
        cid = AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True)
        if cid < 0:
            return {"leader": name, "smiles": smi, "error": "embed"}
        AllChem.MMFFOptimizeMolecule(m, maxIters=500)

        conf = m.GetConformer()
        natoms = m.GetNumAtoms()
        nums = [a.GetAtomicNum() for a in m.GetAtoms()]
        positions = [(conf.GetAtomPosition(i).x,
                       conf.GetAtomPosition(i).y,
                       conf.GetAtomPosition(i).z) for i in range(natoms)]
        import numpy as np
        positions_np = np.array(positions) / 0.5291772083  # Å → Bohr
        nums_np = np.array(nums)

        calc = Calculator(Param.GFN2xTB, nums_np, positions_np)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        e_au = res.get_energy()
        e_kcal = e_au * 627.509474

        # Try HOMO-LUMO from orbital energies
        try:
            orbs = res.get_orbital_eigenvalues()
            occ = res.get_orbital_occupations()
            homo_idx = max(i for i, o in enumerate(occ) if o > 0.5)
            lumo_idx = homo_idx + 1
            homo = orbs[homo_idx] * 27.211386  # Hartree → eV
            lumo = orbs[lumo_idx] * 27.211386
            gap = lumo - homo
        except Exception:
            homo = lumo = gap = float("nan")

        return {"leader": name, "smiles": smi, "natoms": natoms,
                "energy_au": round(e_au, 6),
                "energy_kcal": round(e_kcal, 2),
                "HOMO_eV": round(homo, 3) if homo == homo else None,
                "LUMO_eV": round(lumo, 3) if lumo == lumo else None,
                "gap_eV": round(gap, 3) if gap == gap else None}
    except Exception as e:
        return {"leader": name, "smiles": smi, "error": str(e)[:200]}


def main():
    print(f"GFN2-xTB on {len(LEADERS)} universal scaffold leaders")
    with Pool(min(5, len(LEADERS))) as p:
        results = p.map(xtb_one, LEADERS)
    df = pd.DataFrame(results)
    df.to_csv(OUT / "xtb_energies.csv", index=False)
    print(df.to_string(index=False))
    print(f"\nSaved {OUT/'xtb_energies.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
