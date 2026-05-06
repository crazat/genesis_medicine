"""xtb GFN2 576-conf refine on hetero10 top9997 cohort.

Fills mid-ladder gap of paper #A §3.6 (432/480/528/576/624/720/816).
Source: 432-conf csv (986 mol). Resumable on np_id.
22 subprocess workers (safe alongside OpenMM CUDA — long task pattern).
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
INPUT = ROOT / "pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_432conf.csv"
OUT = ROOT / "pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_576conf.csv"
NUM_CONFS = 576

PARENT_COLS = ["rank", "np_id", "smiles", "log_kp_pottsguy", "logp", "mw", "base_gap_eV_mean"]
XTB_COLS = ["status", "n_xtb_confs", "energy_au_min", "energy_kcal_min",
            "HOMO_eV", "LUMO_eV", "gap_eV_mean", "gap_eV_max"]
ALL_COLS = PARENT_COLS + XTB_COLS


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


def process_mol(parent):
    smi = parent["smiles"]
    np_id = parent["np_id"]
    try:
        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return {**parent, "status": "no_mol"}
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=NUM_CONFS, randomSeed=42,
                                           useRandomCoords=True, numThreads=1)
        if not cids:
            return {**parent, "status": "no_embed"}
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
            return {**parent, "status": "all_fail"}
        best = min(records, key=lambda r: r["energy"])
        gaps = [r["gap"] for r in records if r["gap"] is not None]
        return {
            **parent,
            "status": "ok",
            "n_xtb_confs": len(records),
            "energy_au_min": best["energy"],
            "energy_kcal_min": best["energy"] * 627.5095,
            "HOMO_eV": best["HOMO"], "LUMO_eV": best["LUMO"],
            "gap_eV_min": best["gap"],
            "gap_eV_mean": float(np.mean(gaps)) if gaps else None,
            "gap_eV_max": float(np.max(gaps)) if gaps else None,
        }
    except subprocess.TimeoutExpired:
        return {**parent, "status": "timeout"}
    except Exception as e:
        return {**parent, "status": f"err:{str(e)[:80]}"}


def main():
    df = pd.read_csv(INPUT)
    df_ok = df[df["status"] == "ok"].copy() if "status" in df.columns else df
    print(f"hetero10 input (ok): {len(df_ok)} mol")
    done = set()
    if OUT.exists():
        prev = pd.read_csv(OUT)
        done = set(prev["np_id"].astype(str).tolist())
        print(f"resume: {len(done)} already done")
    todo = []
    for _, r in df_ok.iterrows():
        if str(r["np_id"]) in done:
            continue
        parent = {c: r[c] for c in PARENT_COLS if c in df_ok.columns}
        todo.append(parent)
    if not todo:
        print("nothing to do")
        return
    print(f"launching {len(todo)} mol on 22 subprocess workers, num_confs={NUM_CONFS}")

    write_header = not OUT.exists()
    t0 = time.time()
    with Pool(processes=22) as pool, OUT.open("a") as f:
        if write_header:
            f.write(",".join(ALL_COLS) + "\n")
        for i, r in enumerate(pool.imap_unordered(process_mol, todo, chunksize=1), 1):
            row = ",".join(str(r.get(c, "")).replace(",", ";") for c in ALL_COLS)
            f.write(row + "\n")
            if i % 30 == 0:
                f.flush()
                elapsed = (time.time()-t0)/60
                eta = elapsed * (len(todo)-i) / max(i, 1)
                print(f"  {i}/{len(todo)} ({elapsed:.1f} min, ETA {eta:.1f} min)")
    print(f"done {len(todo)} in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
