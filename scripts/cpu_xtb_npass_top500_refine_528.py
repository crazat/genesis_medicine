"""xtb GFN2 432-conf refine on NPAtlas top500 — subprocess pattern (safe alongside OpenMM CUDA).

Extends the existing top500 refine ladder (12, 24, 36, 48, 72, 96, 120, 144, 168, 192,
240, 288, 336, 384) to the converged 432-conf threshold from paper #B finding.

Output: pilot/cpu_meaningful/xtb_npass_top500_refine_528conf.csv (resumable)
"""
from __future__ import annotations

import os
import re
import subprocess
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
TOP500 = ROOT / "pilot/cpu_meaningful/xtb_npass_top500.csv"
OUT = ROOT / "pilot/cpu_meaningful/xtb_npass_top500_refine_528conf.csv"
NUM_CONFS = 528


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
    idx, smi = args
    try:
        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return {"idx": idx, "smiles": smi, "status": "no_mol"}
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=NUM_CONFS, randomSeed=42,
                                           useRandomCoords=True, numThreads=1)
        if not cids:
            return {"idx": idx, "smiles": smi, "status": "no_embed"}
        AllChem.MMFFOptimizeMoleculeConfs(m, numThreads=1, maxIters=100)
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
            return {"idx": idx, "smiles": smi, "status": "all_fail"}
        best = min(records, key=lambda r: r["energy"])
        gaps = [r["gap"] for r in records if r["gap"] is not None]
        return {
            "idx": idx, "smiles": smi, "status": "ok",
            "n_xtb_confs": len(records),
            "energy_au_min": best["energy"],
            "energy_kcal_min": best["energy"] * 627.5095,
            "HOMO_eV": best["HOMO"], "LUMO_eV": best["LUMO"],
            "gap_eV_min": best["gap"],
            "gap_eV_mean": float(np.mean(gaps)) if gaps else None,
            "gap_eV_max": float(np.max(gaps)) if gaps else None,
        }
    except subprocess.TimeoutExpired:
        return {"idx": idx, "smiles": smi, "status": "timeout"}
    except Exception as e:
        return {"idx": idx, "smiles": smi, "status": f"err:{str(e)[:80]}"}


def main():
    df = pd.read_csv(TOP500)
    print(f"top500: {len(df)} mol")
    smi_col = "smi" if "smi" in df.columns else "smiles"
    idx_col = "idx" if "idx" in df.columns else "rank"
    done = set()
    if OUT.exists():
        prev = pd.read_csv(OUT)
        done = set(prev["idx"].astype(str).tolist())
        print(f"resume: {len(done)} already done")
    todo = [(str(r[idx_col]), str(r[smi_col])) for _, r in df.iterrows() if str(r[idx_col]) not in done]
    if not todo:
        print("nothing to do")
        return
    print(f"launching {len(todo)} mol on 22 subprocess workers, num_confs={NUM_CONFS}")

    cols = ["idx","smiles","status","n_xtb_confs","energy_au_min","energy_kcal_min",
            "HOMO_eV","LUMO_eV","gap_eV_min","gap_eV_mean","gap_eV_max"]
    write_header = not OUT.exists()
    t0 = time.time()
    with Pool(processes=22) as pool, OUT.open("a") as f:
        if write_header:
            f.write(",".join(cols) + "\n")
        for i, r in enumerate(pool.imap_unordered(process_mol, todo, chunksize=1), 1):
            f.write(",".join(str(r.get(c, "")) for c in cols) + "\n")
            if i % 30 == 0:
                f.flush()
                elapsed = (time.time()-t0)/60
                eta = elapsed * (len(todo)-i) / max(i, 1)
                print(f"  {i}/{len(todo)} ({elapsed:.1f} min, ETA {eta:.1f} min)")
    print(f"done {len(todo)} in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
