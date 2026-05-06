"""xtb GFN2 single-point + HOMO-LUMO gap on full NPAtlas 9997 mol (paper #B coverage).

CPU-only, multiprocessing.Pool.
Reuses xtb python interface (no subprocess / temp file overhead).
Output: pilot/cpu_meaningful/xtb_npass_9997_singlept.csv
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
ROOT = Path("/home/crazat/genesis_medicine")
MASTER = ROOT / "pilot/cpu_meaningful/xtb_npass_10k_master.csv"
OUT = ROOT / "pilot/cpu_meaningful/xtb_npass_9997_singlept.csv"


def xtb_single(args):
    rank, np_id, smi = args
    try:
        from xtb.libxtb import VERBOSITY_MUTED
        from xtb.interface import Calculator, Param

        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return {"rank": rank, "np_id": np_id, "status": "no_mol"}
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True) != 0:
            return {"rank": rank, "np_id": np_id, "status": "no_embed"}
        AllChem.UFFOptimizeMolecule(m, maxIters=500)

        atoms = np.array([a.GetAtomicNum() for a in m.GetAtoms()], dtype=np.int32)
        conf = m.GetConformer()
        xyz = np.array([list(conf.GetAtomPosition(i)) for i in range(m.GetNumAtoms())], dtype=np.float64)
        xyz_bohr = xyz * 1.8897259886

        calc = Calculator(Param.GFN2xTB, atoms, xyz_bohr)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        energy = float(res.get_energy())
        orbital_e = res.get_orbital_eigenvalues()
        n_occ = int(sum(1 for x in res.get_orbital_occupations() if x > 0.5))
        if n_occ < 1 or n_occ >= len(orbital_e):
            gap_eV = None; homo = None; lumo = None
        else:
            homo = float(orbital_e[n_occ - 1]) * 27.2114
            lumo = float(orbital_e[n_occ]) * 27.2114
            gap_eV = lumo - homo
        return {"rank": rank, "np_id": np_id, "status": "ok",
                "xtb_energy_au": energy, "homo_eV": homo, "lumo_eV": lumo, "gap_eV": gap_eV,
                "n_atoms": int(m.GetNumAtoms())}
    except Exception as e:
        return {"rank": rank, "np_id": np_id, "status": f"err:{str(e)[:80]}"}


def main():
    df = pd.read_csv(MASTER)
    df = df[df["smiles"].notna()].copy()
    print(f"loaded {len(df)} mols from master")

    # Skip if already done
    if OUT.exists():
        done = pd.read_csv(OUT)
        done_ids = set(done["np_id"])
        df = df[~df["np_id"].isin(done_ids)]
        print(f"resuming: {len(done)} done, {len(df)} remaining")
    else:
        done = pd.DataFrame()

    tasks = [(int(r["rank"]), str(r["np_id"]), str(r["smiles"])) for _, r in df.iterrows()]
    print(f"tasks: {len(tasks)}")

    if not tasks:
        print("nothing to do")
        return

    t0 = time.time()
    with Pool(processes=22) as pool:
        results = []
        for i, r in enumerate(pool.imap_unordered(xtb_single, tasks, chunksize=8), 1):
            results.append(r)
            if i % 500 == 0:
                elapsed = (time.time() - t0) / 60
                eta = elapsed * (len(tasks) - i) / i
                print(f"  {i}/{len(tasks)} ({elapsed:.1f} min, ETA {eta:.1f} min)")
                # incremental save
                merged = pd.concat([done, pd.DataFrame(results)], ignore_index=True)
                merged.to_csv(OUT, index=False)
    new_df = pd.DataFrame(results)
    merged = pd.concat([done, new_df], ignore_index=True)
    merged.to_csv(OUT, index=False)
    n_ok = (merged["status"] == "ok").sum()
    print(f"done {len(results)} new in {(time.time()-t0)/60:.1f} min")
    print(f"total: {n_ok}/{len(merged)} ok, saved {OUT}")


if __name__ == "__main__":
    main()
