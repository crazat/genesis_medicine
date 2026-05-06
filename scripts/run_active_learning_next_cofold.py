"""Run a short Boltz-2 cofold batch for active-learning next candidates.

This is a GPU fallback queue: after the long R16/R17 validation panels finish,
keep the GPU useful without launching new long-MD or free-energy work. The
inputs come from the CPU active-learning surrogate and are treated as triage
only until prior-art, synthesis, and biology gates promote them.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
MSA_DIR = ROOT / "data/msa"
SOURCE_CSV = OUT / "active_learning_next_candidates.csv"


def safe_id(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_").lower()
    return cleaned[:90] or "candidate"


def read_target_map() -> dict[str, dict[str, str]]:
    targets: dict[str, dict[str, str]] = {}
    for path in sorted((ROOT / "conf/skin_targets").glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        for row in data.get("targets", []):
            key = str(row.get("key", "")).strip().lower()
            uniprot = str(row.get("uniprot", "")).strip()
            if key and uniprot:
                targets[key] = {
                    "key": key,
                    "uniprot": uniprot,
                    "display": str(row.get("display", key)),
                }
    return targets


def sequence_from_cache(uniprot: str, target: str) -> str | None:
    msa = MSA_DIR / f"{target}.a3m"
    if msa.exists():
        lines = msa.read_text().splitlines()
        for idx, line in enumerate(lines):
            if line.startswith(">") and idx + 1 < len(lines):
                return lines[idx + 1].strip().replace("-", "")
    fasta = MSA_DIR / f"{uniprot}.fasta"
    if fasta.exists():
        return "".join(line.strip() for line in fasta.read_text().splitlines() if not line.startswith(">"))
    return None


def runnable_targets() -> set[str]:
    runnable: set[str] = set()
    for target, meta in read_target_map().items():
        msa = MSA_DIR / f"{target}.a3m"
        if msa.exists() and sequence_from_cache(meta["uniprot"], target):
            runnable.add(target)
    return runnable


def completed_pairs() -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    for path in sorted(OUT.glob("active_learning_next_cofold_batch*.csv")):
        if path.stem.endswith("_manifest"):
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        for row in df.itertuples(index=False):
            candidate_id = str(getattr(row, "candidate_id", "")).strip()
            target = str(getattr(row, "target", "")).strip().lower()
            if candidate_id and target:
                done.add((candidate_id, target))
    return done


def next_batch_id() -> int:
    existing = sorted(OUT.glob("active_learning_next_cofold_batch*.csv"))
    max_batch = 0
    for path in existing:
        match = re.search(r"batch(\d+)", path.stem)
        if match:
            max_batch = max(max_batch, int(match.group(1)))
    return max_batch + 1


def select_candidates(batch_size: int, include_mmp1: bool) -> pd.DataFrame:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(SOURCE_CSV)
    df = pd.read_csv(SOURCE_CSV)
    if df.empty:
        return df

    already = completed_pairs()
    df["target"] = df["target"].astype(str).str.lower()
    df["candidate_id"] = df["candidate_id"].astype(str)
    already_labeled = (
        df["already_labeled_pair"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes", "y"})
    )
    mask = (
        (df["recommended_next_fidelity"].astype(str) == "Boltz-2 cofold")
        & (~already_labeled)
        & (df["synthesis_gate"].astype(str) != "red")
    )
    if not include_mmp1:
        mask &= df["target"] != "mmp1"
    selected = df.loc[mask].copy()
    if selected.empty:
        return selected
    runnable = runnable_targets()
    selected = selected[selected["target"].isin(runnable)].copy()
    if selected.empty:
        return selected
    selected = selected[
        ~selected.apply(lambda row: (str(row["candidate_id"]), str(row["target"]).lower()) in already, axis=1)
    ].copy()
    if selected.empty:
        return selected

    target_priority = {"dct": 0, "ctgf": 1, "lox": 2, "mc1r": 3, "nr3c1": 4, "tyrp1": 5}
    selected["target_priority"] = selected["target"].map(target_priority).fillna(9).astype(int)
    selected = selected.sort_values(
        ["acquisition_score", "uncertainty", "target_priority"],
        ascending=[False, False, True],
    )
    return selected.head(batch_size).reset_index(drop=True)


def write_inputs(candidates: pd.DataFrame, input_dir: Path, manifest_path: Path) -> list[dict[str, Any]]:
    target_map = read_target_map()
    input_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []

    for rank, row in enumerate(candidates.itertuples(index=False), start=1):
        target = str(getattr(row, "target")).lower()
        meta = target_map.get(target)
        if not meta:
            print(f"skip {target}: no target metadata")
            continue
        msa = MSA_DIR / f"{target}.a3m"
        sequence = sequence_from_cache(meta["uniprot"], target)
        if not sequence or not msa.exists():
            print(f"skip {target}: missing sequence/MSA")
            continue

        candidate_id = str(getattr(row, "candidate_id"))
        job_id = f"al_{rank:02d}_{target}_{safe_id(candidate_id)}"
        cfg = {
            "version": 1,
            "sequences": [
                {"protein": {"id": "A", "sequence": sequence, "msa": str(msa.absolute())}},
                {"ligand": {"id": "L", "smiles": str(getattr(row, "smiles"))}},
            ],
            "properties": [{"affinity": {"binder": "L"}}],
        }
        (input_dir / f"{job_id}.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        manifest.append(
            {
                "job_id": job_id,
                "candidate_id": candidate_id,
                "target": target,
                "smiles": str(getattr(row, "smiles")),
                "source": str(getattr(row, "source")),
                "synthesis_score": float(getattr(row, "synthesis_score")),
                "synthesis_gate": str(getattr(row, "synthesis_gate")),
                "predicted_score": float(getattr(row, "predicted_score")),
                "uncertainty": float(getattr(row, "uncertainty")),
                "acquisition_score": float(getattr(row, "acquisition_score")),
            }
        )

    pd.DataFrame(manifest).to_csv(manifest_path, index=False)
    return manifest


def collect_results(output_dir: Path, manifest: list[dict[str, Any]], csv_out: Path) -> pd.DataFrame:
    by_job = {row["job_id"]: row for row in manifest}
    rows: list[dict[str, Any]] = []
    for path in sorted(output_dir.rglob("affinity_*.json")):
        job_id = path.stem.replace("affinity_", "")
        meta = by_job.get(job_id, {})
        data = json.loads(path.read_text())
        rows.append(
            {
                **meta,
                "affinity_pred_value": data.get("affinity_pred_value"),
                "affinity_probability_binary": data.get("affinity_probability_binary"),
                "affinity_probability": data.get("affinity_probability"),
                "affinity_pred_value1": data.get("affinity_pred_value1"),
                "affinity_probability_binary1": data.get("affinity_probability_binary1"),
            }
        )
    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values("affinity_probability_binary", ascending=False)
    result.to_csv(csv_out, index=False)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--include-mmp1", action="store_true")
    parser.add_argument("--sampling-steps", type=int, default=25)
    parser.add_argument("--diffusion-samples", type=int, default=1)
    parser.add_argument("--recycling-steps", type=int, default=3)
    parser.add_argument("--sampling-steps-affinity", type=int, default=200)
    parser.add_argument("--diffusion-samples-affinity", type=int, default=5)
    args = parser.parse_args()

    batch = next_batch_id()
    tag = f"batch{batch:02d}"
    input_dir = OUT / f"inputs_active_learning_next_{tag}"
    output_dir = OUT / f"output_active_learning_next_{tag}"
    manifest_path = OUT / f"active_learning_next_cofold_{tag}_manifest.csv"
    csv_out = OUT / f"active_learning_next_cofold_{tag}.csv"

    candidates = select_candidates(args.batch_size, include_mmp1=args.include_mmp1)
    if candidates.empty:
        print("No active-learning candidates pending Boltz-2 cofold.")
        return 0

    manifest = write_inputs(candidates, input_dir, manifest_path)
    if not manifest:
        print("No runnable active-learning YAMLs generated.")
        return 2

    print(f"active-learning Boltz-2 cofold: {len(manifest)} jobs tag={tag}")
    print(f"inputs: {input_dir}")
    print(f"output: {output_dir}")
    print(f"manifest: {manifest_path}")

    boltz = ROOT / ".venv/bin/boltz"
    cmd = [
        str(boltz),
        "predict",
        str(input_dir),
        "--out_dir",
        str(output_dir),
        "--sampling_steps",
        str(args.sampling_steps),
        "--diffusion_samples",
        str(args.diffusion_samples),
        "--recycling_steps",
        str(args.recycling_steps),
        "--sampling_steps_affinity",
        str(args.sampling_steps_affinity),
        "--diffusion_samples_affinity",
        str(args.diffusion_samples_affinity),
        "--affinity_mw_correction",
        "--devices",
        "1",
    ]
    t0 = time.time()
    print("$ " + " ".join(cmd))
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    wall = (time.time() - t0) / 60.0
    print(f"Boltz-2 exit={rc}, wall={wall:.2f} min")
    if rc != 0:
        return rc

    result = collect_results(output_dir, manifest, csv_out)
    print(f"results: {csv_out} rows={len(result)}")
    if not result.empty:
        print(result[["candidate_id", "target", "affinity_probability_binary"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
