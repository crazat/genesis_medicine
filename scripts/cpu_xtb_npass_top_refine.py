"""Refine top NPASS xTB candidates with a larger conformer ensemble.

This CPU-only filler consolidates the 0-10000 NPASS xTB slice outputs, ranks
skin/plausibility candidates, then reruns xTB on a larger conformer set.

No TensorFlow, no ADMET-AI. Safe to run with multiprocessing.Pool.

Outputs:
  pilot/cpu_meaningful/xtb_npass_10k_master.csv
  pilot/cpu_meaningful/xtb_npass_top_refine_input.csv
  pilot/cpu_meaningful/xtb_npass_top_refine.csv
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


def zscore(series: pd.Series) -> pd.Series:
    sd = float(series.std(ddof=0))
    if sd == 0.0 or np.isnan(sd):
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - float(series.mean())) / sd


def load_master() -> pd.DataFrame:
    paths = sorted(OUT.glob("xtb_npass_rank*_*.csv"))
    frames = []
    for path in paths:
        if path.name == "xtb_npass_top_refine.csv":
            continue
        try:
            frames.append(pd.read_csv(path))
        except Exception as exc:
            print(f"Skipping {path.name}: {exc}")
    if not frames:
        raise FileNotFoundError("No xtb_npass_rank*.csv files found")
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["rank", "np_id", "smiles"]).sort_values("rank")
    df.to_csv(OUT / "xtb_npass_10k_master.csv", index=False)
    return df


def hetero_atom_count(smiles: str) -> int:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return 0
    return sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() not in (1, 6))


def select_candidates(df: pd.DataFrame, topn: int, min_hetero_atoms: int) -> pd.DataFrame:
    ok = df[df["status"].eq("ok")].copy()
    ok = ok[np.isfinite(ok["gap_eV_mean"]) & np.isfinite(ok["log_kp_pottsguy"])]
    ok = ok[(ok["mw"] <= 650) & (ok["logp"].between(-2.5, 6.0))]
    ok["hetero_atoms"] = ok["smiles"].map(hetero_atom_count)
    if min_hetero_atoms > 0:
        ok = ok[ok["hetero_atoms"] >= min_hetero_atoms]
    ok["topical_refine_score"] = (
        0.55 * zscore(ok["log_kp_pottsguy"])
        + 0.35 * zscore(ok["gap_eV_mean"])
        + 0.10 * zscore(-abs(ok["logp"] - 2.0))
        + 0.05 * zscore(-abs(ok["mw"] - 300.0))
    )
    cols = [
        "rank",
        "np_id",
        "smiles",
        "log_kp_pottsguy",
        "logp",
        "mw",
        "hetero_atoms",
        "gap_eV_mean",
        "energy_kcal_min",
        "topical_refine_score",
    ]
    selected = ok.sort_values("topical_refine_score", ascending=False)[cols].head(topn).copy()
    selected.to_csv(OUT / "xtb_npass_top_refine_input.csv", index=False)
    return selected


def run_one(args: tuple[int, str, str, float, float, float, float, int]) -> dict[str, object]:
    rank, np_id, smi, logkp, logp, mw, base_gap, num_confs = args
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "invalid_smiles"}
        mol = Chem.AddHs(mol)
        cids = AllChem.EmbedMultipleConfs(
            mol,
            numConfs=num_confs,
            randomSeed=20260430 + rank,
            pruneRmsThresh=0.35,
            numThreads=1,
        )
        if not cids:
            return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "no_conformer"}

        records = []
        with tempfile.TemporaryDirectory(prefix=f"xtb_refine_{rank}_") as tmp:
            tmp_path = Path(tmp)
            for cid in cids:
                try:
                    AllChem.MMFFOptimizeMolecule(mol, confId=cid, maxIters=350)
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
                        timeout=240,
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
            "base_gap_eV_mean": base_gap,
            "status": "ok",
            "n_xtb_confs": len(records),
            "energy_au_min": best["energy_au"],
            "energy_kcal_min": best["energy_au"] * 627.5095,
            "HOMO_eV": best["HOMO_eV"],
            "LUMO_eV": best["LUMO_eV"],
            "gap_eV_mean": float(np.mean(gaps)) if gaps else None,
            "gap_eV_max": float(np.max(gaps)) if gaps else None,
        }
    except subprocess.TimeoutExpired:
        return {"rank": rank, "np_id": np_id, "smiles": smi, "status": "timeout"}
    except Exception as exc:
        return {"rank": rank, "np_id": np_id, "smiles": smi, "status": f"error:{str(exc)[:80]}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topn", type=int, default=80)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--num-confs", type=int, default=12)
    parser.add_argument("--min-hetero-atoms", type=int, default=0)
    parser.add_argument("--out", default="xtb_npass_top_refine.csv")
    args = parser.parse_args()

    if not XTB_BIN.exists():
        print(f"xTB missing: {XTB_BIN}")
        return 1

    print("NPASS xTB 10k consolidation + top refine")
    master = load_master()
    print(f"Master rows: {len(master)}")
    selected = select_candidates(master, args.topn, args.min_hetero_atoms)
    print(f"Selected top {len(selected)} for {args.num_confs}-conformer xTB refinement")
    print(selected.head(12).to_string(index=False))

    payload = [
        (
            int(row["rank"]),
            str(row["np_id"]),
            str(row["smiles"]),
            float(row["log_kp_pottsguy"]),
            float(row["logp"]),
            float(row["mw"]),
            float(row["gap_eV_mean"]),
            int(args.num_confs),
        )
        for _, row in selected.iterrows()
    ]

    t0 = time.time()
    with Pool(max(1, int(args.workers))) as pool:
        rows = pool.map(run_one, payload)

    result = pd.DataFrame(rows)
    out = OUT / args.out
    result.to_csv(out, index=False)
    ok = int(result["status"].eq("ok").sum()) if "status" in result else 0
    print(f"Saved {out.relative_to(ROOT)} ({ok}/{len(result)} ok)")
    print(f"Wall: {(time.time() - t0) / 60:.1f} min")
    if ok:
        cols = ["rank", "np_id", "log_kp_pottsguy", "logp", "mw", "gap_eV_mean", "gap_eV_max"]
        print(result[result["status"].eq("ok")].sort_values("gap_eV_mean", ascending=False)[cols].head(15).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
