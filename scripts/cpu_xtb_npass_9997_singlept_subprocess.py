"""xtb GFN2 single-point on 9997 mol — SUBPROCESS pattern (validated safe alongside OpenMM CUDA).

Each worker forks xtb subprocess for a 1-conf single-point. Subprocess-blocking pool ≪ in-process pool
in deadlock risk. Validated by 432-conf refine running safely alongside apo MD.

Resumable: skips ranks already in OUT csv.

Output: pilot/cpu_meaningful/xtb_npass_9997_singlept.csv
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
MASTER = ROOT / "pilot/cpu_meaningful/xtb_npass_10k_master.csv"
OUT = ROOT / "pilot/cpu_meaningful/xtb_npass_9997_singlept.csv"


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
    rank, np_id, smi = args
    try:
        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return {"rank": rank, "np_id": np_id, "status": "no_mol"}
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True) != 0:
            return {"rank": rank, "np_id": np_id, "status": "no_embed"}
        AllChem.UFFOptimizeMolecule(m, maxIters=500)
        n_atoms = m.GetNumAtoms()
        with tempfile.TemporaryDirectory() as tmpdir:
            xyz = Path(tmpdir) / "in.xyz"
            Chem.MolToXYZFile(m, str(xyz))
            proc = subprocess.run(
                [str(XTB_BIN), str(xyz), "--gfn", "2"],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
                cwd=tmpdir,
            )
            if proc.returncode != 0:
                return {"rank": rank, "np_id": np_id, "status": "xtb_fail"}
            e, h, l, g = parse_xtb(proc.stdout)
            if e is None:
                return {"rank": rank, "np_id": np_id, "status": "no_energy"}
            return {
                "rank": rank, "np_id": np_id, "status": "ok",
                "xtb_energy_au": e, "homo_eV": h, "lumo_eV": l,
                "gap_eV": g, "n_atoms": n_atoms,
            }
    except subprocess.TimeoutExpired:
        return {"rank": rank, "np_id": np_id, "status": "timeout"}
    except Exception as e:
        return {"rank": rank, "np_id": np_id, "status": f"err:{str(e)[:80]}"}


def main():
    df = pd.read_csv(MASTER)
    print(f"master: {len(df)} mol")
    done = set()
    if OUT.exists():
        prev = pd.read_csv(OUT)
        done = set(prev["rank"].astype(int).tolist())
        print(f"resume: {len(done)} already scored, {len(df)-len(done)} remaining")
    todo = []
    for _, r in df.iterrows():
        rk = int(r["rank"])
        if rk in done:
            continue
        todo.append((rk, str(r["np_id"]), str(r["smiles"])))
    if not todo:
        print("nothing to do")
        return
    print(f"launching {len(todo)} tasks on 22 subprocess workers")

    # Append mode: keep existing rows
    write_header = not OUT.exists()
    t0 = time.time()
    batch = []
    with Pool(processes=22) as pool, OUT.open("a") as f:
        if write_header:
            f.write("rank,np_id,status,xtb_energy_au,homo_eV,lumo_eV,gap_eV,n_atoms\n")
        for i, r in enumerate(pool.imap_unordered(process_mol, todo, chunksize=1), 1):
            cols = ["rank","np_id","status","xtb_energy_au","homo_eV","lumo_eV","gap_eV","n_atoms"]
            f.write(",".join(str(r.get(c, "")) for c in cols) + "\n")
            if i % 200 == 0:
                f.flush()
                elapsed = (time.time()-t0)/60
                eta = elapsed * (len(todo)-i) / max(i, 1)
                print(f"  {i}/{len(todo)} ({elapsed:.1f} min, ETA {eta:.1f} min)")
    print(f"done {len(todo)} in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
