"""R15 BRICS xtb-only HOMO-LUMO scan (round1 + round2 = 104 candidates).

ADMET-AI는 별도로 실행해야 함 (TF + multiprocessing fork 데드락 회피).

Output: pilot/cpu_meaningful/r15_xtb_only.csv
"""
from __future__ import annotations
import sys
from pathlib import Path
from multiprocessing import Pool
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def xtb_one(args):
    idx, smi = args
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
            return {"idx": idx, "smi": smi, "error": "embed"}
        AllChem.MMFFOptimizeMolecule(m, maxIters=500)
        conf = m.GetConformer()
        natoms = m.GetNumAtoms()
        nums = np.array([a.GetAtomicNum() for a in m.GetAtoms()])
        positions = np.array([(conf.GetAtomPosition(i).x,
                                conf.GetAtomPosition(i).y,
                                conf.GetAtomPosition(i).z)
                               for i in range(natoms)]) / 0.5291772083
        calc = Calculator(Param.GFN2xTB, nums, positions)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        e_au = res.get_energy()
        try:
            orbs = res.get_orbital_eigenvalues()
            occ = res.get_orbital_occupations()
            homo_idx = max(i for i, o in enumerate(occ) if o > 0.5)
            homo = orbs[homo_idx] * 27.211386
            lumo = orbs[homo_idx + 1] * 27.211386
            gap = lumo - homo
        except Exception:
            homo = lumo = gap = float("nan")
        return {"idx": idx, "derivative_smiles": smi,
                "energy_au": round(e_au, 6),
                "HOMO_eV": round(homo, 3) if homo == homo else None,
                "LUMO_eV": round(lumo, 3) if lumo == lumo else None,
                "gap_eV": round(gap, 3) if gap == gap else None}
    except Exception as e:
        return {"idx": idx, "derivative_smiles": smi, "error": str(e)[:200]}


def main():
    r1 = pd.read_csv(OUT / "r15_brics_candidates.csv")
    r2_path = OUT / "r15_brics_round2.csv"
    if r2_path.exists():
        r2 = pd.read_csv(r2_path)
        df = pd.concat([r1, r2], ignore_index=True).drop_duplicates("derivative_smiles").reset_index(drop=True)
    else:
        df = r1
    print(f"Total R15 BRICS pool: {len(df)} unique candidates")

    args = [(i, s) for i, s in enumerate(df["derivative_smiles"].tolist())]
    nproc = min(8, len(args))
    print(f"Launching {nproc} xtb workers...")
    with Pool(nproc) as p:
        xtb_results = p.map(xtb_one, args)
    xtb_df = pd.DataFrame(xtb_results)
    merged = df.merge(xtb_df.drop(columns=["idx"], errors="ignore"),
                      on="derivative_smiles", how="left")
    out_path = OUT / "r15_xtb_only.csv"
    merged.to_csv(out_path, index=False)
    n_ok = merged["gap_eV"].notna().sum()
    print(f"\nSaved {out_path} ({len(merged)} rows, {n_ok} with gap_eV)")
    if n_ok:
        print("\nGap statistics (eV):")
        print(merged["gap_eV"].describe().to_string())
        print("\nTop 10 by gap (electronic stability):")
        cols = ["leader_seed", "derivative_smiles", "MW", "logP", "QED", "HOMO_eV", "LUMO_eV", "gap_eV"]
        cols = [c for c in cols if c in merged.columns]
        print(merged.sort_values("gap_eV", ascending=False).head(10)[cols].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
