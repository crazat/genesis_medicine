"""xtb GFN2 single-point on 9997 mol — LONG-TASK batched (100 mol/batch = ~50s/task).

Designed to be safe alongside OpenMM CUDA jobs (apo MD).
Each Pool worker processes 100 mol per call → no rapid task churn → no GPU dispatch starvation.

Output: pilot/cpu_meaningful/xtb_npass_9997_singlept.csv (resumable)
"""
from __future__ import annotations

import os
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


def xtb_one(args):
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


def process_batch(batch):
    """Each worker processes a batch of ~100 mol — long-task pattern."""
    return [xtb_one(t) for t in batch]


def main():
    df = pd.read_csv(MASTER)
    df = df[df["smiles"].notna()].copy()

    if OUT.exists():
        done = pd.read_csv(OUT)
        done_ids = set(done["np_id"].astype(str))
        df = df[~df["np_id"].astype(str).isin(done_ids)]
        print(f"resume: {len(done)} done, {len(df)} remaining")
    else:
        done = pd.DataFrame()

    if len(df) == 0:
        print("nothing to do")
        return

    tasks = [(int(r["rank"]), str(r["np_id"]), str(r["smiles"])) for _, r in df.iterrows()]
    BATCH_SIZE = 100
    batches = [tasks[i:i+BATCH_SIZE] for i in range(0, len(tasks), BATCH_SIZE)]
    print(f"tasks: {len(tasks)} → {len(batches)} batches of ≤{BATCH_SIZE}")

    t0 = time.time()
    # 22 workers — sole CPU tenant (no concurrent refine cohort), safe alongside apo MD
    with Pool(processes=22) as pool:
        results = []
        for i, batch_results in enumerate(pool.imap_unordered(process_batch, batches), 1):
            results.extend(batch_results)
            elapsed = (time.time() - t0) / 60
            n_done = len(results)
            eta = elapsed * (len(tasks) - n_done) / max(n_done, 1)
            print(f"  batch {i}/{len(batches)} ({n_done}/{len(tasks)}, {elapsed:.1f} min, ETA {eta:.1f} min)")
            # incremental save
            merged = pd.concat([done, pd.DataFrame(results)], ignore_index=True)
            merged.to_csv(OUT, index=False)

    print(f"done {len(results)} in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
