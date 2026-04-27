"""xtb GFN2 single-point on remaining BRICS pool (2000-2240, 240 mol).

Continues from xtb_progressive_slice_1500 (which got stuck on 1-2 mol).
Skips slice 1500-2000 (problematic), processes 2000-2240 only.
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def xtb_energy(args):
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
            dtype=np.float64) * 1.8897259886  # Angstrom → Bohr

        calc = Calculator(Param.GFN2xTB, atoms, xyz)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        e_au = res.get_energy()

        return {
            "idx": idx,
            "smi": smi,
            "energy_au": float(e_au),
            "energy_kcal_mol": float(e_au * 627.509),
            "n_atoms": m.GetNumAtoms(),
        }
    except Exception as e:
        return {"idx": idx, "smi": smi, "error": str(e)[:100]}


def main():
    print("=" * 72)
    print("xtb GFN2 progressive — slice 2000-2240 (final 240 mol)")
    print("=" * 72)

    df = pd.read_csv(ROOT / "pilot/cpu_queue_v5/brics_with_novelty.csv")
    df = df.sort_values("combined", ascending=False).reset_index(drop=True)
    print(f"BRICS pool: {len(df)}")

    slice_df = df.iloc[2000:].reset_index(drop=True)
    print(f"Slice 2000+: {len(slice_df)}")

    args = [(2000 + i, slice_df.iloc[i]["smiles"]) for i in range(len(slice_df))]

    t0 = time.time()
    with Pool(processes=12) as p:
        results = p.map_async(xtb_energy, args).get(timeout=1800)
    valid = [r for r in results if r and "energy_au" in r]
    failed = [r for r in results if r and "error" in r]

    out = pd.DataFrame(valid)
    out.to_csv(OUT / "xtb_progressive_slice_2000.csv", index=False)
    print(f"\n✅ xtb_progressive_slice_2000.csv ({len(out)} success / {len(failed)} fail)")
    print(f"  Wall: {(time.time()-t0)/60:.1f} min")

    # Aggregate ALL slices
    slices = sorted(OUT.glob("xtb_progressive_slice_*.csv"))
    all_df = pd.concat([pd.read_csv(f) for f in slices], ignore_index=True)
    all_df = all_df.drop_duplicates("smi")
    all_df.to_csv(OUT / "xtb_progressive_all.csv", index=False)
    print(f"\n✅ xtb_progressive_all.csv ({len(all_df)} unique mol total)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
