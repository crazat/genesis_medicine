"""xtb GFN2 on full Round 4 expanded 194 mol."""
import sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def xtb_quantum(args):
    idx, smi = args
    try:
        from xtb.libxtb import VERBOSITY_MUTED
        from xtb.interface import Calculator, Param

        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True) != 0:
            return None
        AllChem.UFFOptimizeMolecule(m, maxIters=500)

        atoms = np.array([a.GetAtomicNum() for a in m.GetAtoms()],
                          dtype=np.int32)
        conf = m.GetConformer()
        xyz = np.array(
            [[conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y,
                conf.GetAtomPosition(i).z]
              for i in range(m.GetNumAtoms())],
            dtype=np.float64) * 1.8897259886

        calc = Calculator(Param.GFN2xTB, atoms, xyz)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        e_au = res.get_energy()
        try:
            dipole = res.get_dipole()
            dipole_norm = float(np.linalg.norm(dipole))
        except Exception:
            dipole_norm = float("nan")

        return {
            "idx": idx, "smi": smi,
            "energy_au": float(e_au),
            "energy_kcal_mol": float(e_au * 627.509),
            "dipole_debye": dipole_norm,
            "n_atoms": m.GetNumAtoms(),
        }
    except Exception as e:
        return {"idx": idx, "smi": smi, "error": str(e)[:100]}


def main():
    df = pd.read_csv(OUT / "round4_expanded.csv")
    print(f"xtb GFN2 on full R4 expanded {len(df)} mol")
    args = [(i, df.iloc[i]["smiles"]) for i in range(len(df))]
    t0 = time.time()
    with Pool(12) as p:
        results = p.map_async(xtb_quantum, args).get(timeout=2400)
    valid = [r for r in results if r and "energy_au" in r]
    pd.DataFrame(valid).to_csv(OUT / "xtb_r4_full194.csv", index=False)
    print(f"Wall: {(time.time()-t0)/60:.1f} min")
    print(f"✅ xtb_r4_full194.csv ({len(valid)})")


if __name__ == "__main__":
    sys.exit(main())
