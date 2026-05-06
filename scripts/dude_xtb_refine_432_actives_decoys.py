"""DUD-E 432-conf xtb refine on 15 actives + 314 decoys.

Subprocess-pattern (safe alongside apo MD per memory rule).
Each worker forks xtb subprocess → wait → read result. ~46 sec/mol on 22 workers → ~11 min wall for 329 mol.

Output: pilot/dude_benchmark_mmp1/scored_all_432conf.csv
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path("/home/crazat/genesis_medicine")
XTB_BIN = Path("/home/crazat/miniforge3/envs/genesis-md/bin/xtb")
OUT_DIR = ROOT / "pilot/dude_benchmark_mmp1"

ACTIVES = ROOT / "data/chembl_mmp1_calibration.csv"
DECOYS = OUT_DIR / "decoys.csv"
OUT_CSV = OUT_DIR / "scored_all_432conf.csv"

NUM_CONFS = 432


def parse_xtb(stdout: str):
    energy = homo = lumo = gap = None
    for line in stdout.splitlines():
        upper = line.upper()
        vals = [float(x) for x in re.findall(r"[-+]?\d+\.\d+(?:[Ee][-+]?\d+)?", line)]
        if "TOTAL ENERGY" in upper and vals:
            energy = vals[-1]
        elif "(HOMO)" in upper and vals:
            homo = vals[-1]
        elif "(LUMO)" in upper and vals:
            lumo = vals[-1]
        elif "HOMO-LUMO GAP" in upper and vals:
            gap = vals[-1]
    return energy, homo, lumo, gap


def process_mol(args):
    """Process one molecule with NUM_CONFS conformers via subprocess xtb GFN2."""
    idx, smi, source = args
    try:
        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return {"idx": idx, "source": source, "smiles": smi, "status": "no_mol"}
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=NUM_CONFS, randomSeed=42, useRandomCoords=True,
                                          numThreads=1)
        if not cids:
            return {"idx": idx, "source": source, "smiles": smi, "status": "no_embed"}
        AllChem.MMFFOptimizeMoleculeConfs(m, numThreads=1, maxIters=100)

        # Score each conformer with xtb subprocess; track best (most negative energy)
        records = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for cid in cids:
                xyz = Path(tmpdir) / f"c{cid}.xyz"
                Chem.MolToXYZFile(m, str(xyz), confId=cid)
                proc = subprocess.run(
                    [str(XTB_BIN), str(xyz), "--gfn", "2", "--alpb", "water"],
                    capture_output=True, text=True, timeout=30,
                    env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
                    cwd=tmpdir,
                )
                if proc.returncode != 0:
                    continue
                e, h, l, g = parse_xtb(proc.stdout)
                if e is not None:
                    records.append({"energy": e, "HOMO": h, "LUMO": l, "gap": g})

        if not records:
            return {"idx": idx, "source": source, "smiles": smi, "status": "all_fail"}
        # Best = most negative energy
        best = min(records, key=lambda r: r["energy"])
        gaps = [r["gap"] for r in records if r["gap"] is not None]
        return {
            "idx": idx, "source": source, "smiles": smi, "status": "ok",
            "n_xtb_confs": len(records),
            "energy_au_min": best["energy"],
            "energy_kcal_min": best["energy"] * 627.5095,
            "HOMO_eV": best["HOMO"], "LUMO_eV": best["LUMO"],
            "gap_eV_min": best["gap"],
            "gap_eV_mean": float(np.mean(gaps)) if gaps else None,
            "gap_eV_max": float(np.max(gaps)) if gaps else None,
        }
    except subprocess.TimeoutExpired:
        return {"idx": idx, "source": source, "smiles": smi, "status": "timeout"}
    except Exception as e:
        return {"idx": idx, "source": source, "smiles": smi, "status": f"err:{str(e)[:80]}"}


def main():
    actives = pd.read_csv(ACTIVES)
    decoys = pd.read_csv(DECOYS)
    print(f"actives n={len(actives)}, decoys n={len(decoys)}")
    tasks = []
    for i, r in actives.iterrows():
        tasks.append((f"a{i}", str(r["smiles"]), "active"))
    for i, r in decoys.iterrows():
        tasks.append((f"d{i}", str(r["smiles"]), "decoy"))
    print(f"total tasks: {len(tasks)}, num_confs={NUM_CONFS}")

    t0 = time.time()
    with Pool(processes=22) as pool:
        results = []
        for i, r in enumerate(pool.imap_unordered(process_mol, tasks, chunksize=1), 1):
            results.append(r)
            if i % 30 == 0:
                elapsed = (time.time() - t0) / 60
                eta = elapsed * (len(tasks) - i) / max(i, 1)
                print(f"  {i}/{len(tasks)} ({elapsed:.1f} min, ETA {eta:.1f} min)")
                pd.DataFrame(results).to_csv(OUT_CSV, index=False)
    df = pd.DataFrame(results)
    df.to_csv(OUT_CSV, index=False)
    n_ok = (df["status"] == "ok").sum()
    print(f"done {len(results)} in {(time.time()-t0)/60:.1f} min, {n_ok} ok")


if __name__ == "__main__":
    main()
