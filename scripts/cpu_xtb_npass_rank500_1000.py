"""xTB GFN2 scan for a NPASS permeability rank slice.

This is a CPU-only background filler. It complements the protected conformer
queues without touching them:
  - PID 15578: conformer ensemble for rank 500-1000
  - this script: electronic stability for rank 500-1000

No TensorFlow, no ADMET-AI. Safe to run with multiprocessing.Pool.

Output:
  pilot/cpu_meaningful/xtb_npass_rank<start>_<end>.csv
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
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
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
XTB_BIN = Path("/home/crazat/miniforge3/envs/genesis-md/bin/xtb")
POOL_SIZE = 10


def parse_xtb(stdout: str) -> tuple[float | None, float | None, float | None, float | None]:
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


def run_one(args: tuple[int, str, str, float, float, float]) -> dict[str, object]:
    rank, np_id, smi, logkp, logp, mw = args
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "invalid_smiles"}
        mol = Chem.AddHs(mol)
        cids = AllChem.EmbedMultipleConfs(
            mol, numConfs=3, randomSeed=20260430 + rank, pruneRmsThresh=0.5, numThreads=1
        )
        if not cids:
            return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "no_conformer"}

        records = []
        with tempfile.TemporaryDirectory(prefix=f"xtb_npass_{rank}_") as tmp:
            tmp_path = Path(tmp)
            for cid in cids:
                try:
                    AllChem.MMFFOptimizeMolecule(mol, confId=cid, maxIters=250)
                except Exception:
                    pass
                wd = tmp_path / f"conf_{cid}"
                wd.mkdir()
                xyz = wd / "input.xyz"
                xyz.write_text(Chem.MolToXYZBlock(mol, confId=cid))
                try:
                    proc = subprocess.run(
                        [str(XTB_BIN), str(xyz), "--gfn", "2", "--alpb", "water"],
                        cwd=wd,
                        capture_output=True,
                        text=True,
                        timeout=180,
                        env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
                    )
                    if proc.returncode != 0:
                        continue
                    energy, homo, lumo, gap = parse_xtb(proc.stdout)
                    if energy is not None:
                        records.append({"energy_au": energy, "HOMO_eV": homo, "LUMO_eV": lumo, "gap_eV": gap})
                finally:
                    shutil.rmtree(wd, ignore_errors=True)

        if not records:
            return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "all_failed"}
        best = min(records, key=lambda row: row["energy_au"])
        gaps = [row["gap_eV"] for row in records if row["gap_eV"] is not None]
        return {
            "rank": rank,
            "np_id": np_id,
            "smiles": smi,
            "log_kp_pottsguy": logkp,
            "logp": logp,
            "mw": mw,
            "status": "ok",
            "n_xtb_confs": len(records),
            "energy_au_min": best["energy_au"],
            "energy_kcal_min": best["energy_au"] * 627.5095,
            "HOMO_eV": best["HOMO_eV"],
            "LUMO_eV": best["LUMO_eV"],
            "gap_eV_mean": float(np.mean(gaps)) if gaps else None,
        }
    except subprocess.TimeoutExpired:
        return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "timeout"}
    except Exception as exc:
        return {"rank": rank, "np_id": np_id, "smiles": smi, "status": f"error:{str(exc)[:80]}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=500)
    parser.add_argument("--end", type=int, default=1000)
    parser.add_argument("--out", default=None)
    parser.add_argument("--workers", type=int, default=POOL_SIZE)
    args_ns = parser.parse_args()
    start = args_ns.start
    end = args_ns.end
    out_name = args_ns.out or f"xtb_npass_rank{start}_{end}.csv"
    workers = max(1, int(args_ns.workers))

    print(f"NPASS xTB rank {start}-{end} CPU filler")
    print(f"POOL_SIZE={workers}")
    if not XTB_BIN.exists():
        print(f"xTB missing: {XTB_BIN}")
        return 1

    npass = pd.read_csv(OUT / "npass_2026_pottsguy_logkp_10k.csv")
    ranked = npass.sort_values("log_kp_pottsguy", ascending=False).reset_index(drop=True)
    target = ranked.iloc[start:end].copy()
    print(
        f"Slice: {len(target)} mol, "
        f"logKp {target['log_kp_pottsguy'].min():.2f} to {target['log_kp_pottsguy'].max():.2f}"
    )

    args = [
        (
            start + i,
            str(row["np_id"]),
            str(row["smiles"]),
            float(row["log_kp_pottsguy"]),
            float(row["logp"]),
            float(row["mw"]),
        )
        for i, row in target.reset_index(drop=True).iterrows()
    ]

    t0 = time.time()
    with Pool(workers) as pool:
        rows = pool.map(run_one, args)

    df = pd.DataFrame(rows)
    out = OUT / out_name
    df.to_csv(out, index=False)
    ok = int(df["status"].eq("ok").sum()) if "status" in df else 0
    print(f"Saved {out} ({ok}/{len(df)} ok)")
    print(f"Wall: {(time.time() - t0) / 60:.1f} min")
    if ok:
        print("\nTop electronic-stable NPASS slice compounds:")
        cols = ["rank", "np_id", "log_kp_pottsguy", "logp", "mw", "gap_eV_mean", "energy_kcal_min"]
        print(df[df["status"].eq("ok")].sort_values("gap_eV_mean", ascending=False)[cols].head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
