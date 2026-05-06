"""Run Boltz-2 cofold for top R17 generative chromanol designs.

This is a lightweight GPU side-queue for moments when long OpenMM jobs are in
CPU-only preparation. It uses only precomputed generator CSVs and cached MSAs.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
MSA_DIR = ROOT / "data/msa"
SOURCE_CSV = OUT / "chromanol_generative_optimizer.csv"


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


def safe_id(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return cleaned[:80] or "design"


def select_designs(topn: int, offset: int = 0, balanced: bool = True) -> pd.DataFrame:
    df = pd.read_csv(SOURCE_CSV)
    selected = df[
        (df["recommended_next_action"] == "Boltz-2_next_when_GPU_free")
        & (df["synthesis_route_proxy"] == "route_ready")
        & (df["novelty_status"] == "new_local_design")
    ].copy()
    selected = selected.sort_values(
        ["local_design_priority", "topical_window_score", "QED"],
        ascending=[False, False, False],
    )
    if not balanced:
        return selected.iloc[offset : offset + topn].reset_index(drop=True)

    target_order = ["tgfb1", "dct", "tyr", "mmp1", "ptgs2"]
    groups = {
        target: group.reset_index(drop=True)
        for target, group in selected.groupby("target", sort=False)
    }
    ordered_rows: list[pd.Series] = []
    idx = 0
    while True:
        added = False
        for target in target_order:
            group = groups.get(target)
            if group is not None and idx < len(group):
                ordered_rows.append(group.iloc[idx])
                added = True
        if not added:
            break
        idx += 1
    if not ordered_rows:
        return selected.head(0).copy()
    balanced_df = pd.DataFrame(ordered_rows)
    return balanced_df.iloc[offset : offset + topn].reset_index(drop=True)


def write_inputs(designs: pd.DataFrame, input_dir: Path, manifest_path: Path) -> list[dict[str, Any]]:
    target_map = read_target_map()
    input_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []

    for rank, row in enumerate(designs.itertuples(index=False), start=1):
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

        design_id = str(getattr(row, "design_id"))
        job_id = f"r17_{rank:02d}_{target}_{safe_id(design_id)}"
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
                "rank": rank,
                "design_id": design_id,
                "target": target,
                "smiles": str(getattr(row, "smiles")),
                "local_design_priority": float(getattr(row, "local_design_priority")),
                "topical_window_score": float(getattr(row, "topical_window_score")),
                "QED": float(getattr(row, "QED")),
                "cLogP": float(getattr(row, "cLogP")),
                "photosafety_proxy": str(getattr(row, "photosafety_proxy")),
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
    parser.add_argument("--topn", type=int, default=32)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--tag", default="")
    parser.add_argument("--global-only", action="store_true")
    parser.add_argument("--sampling-steps", type=int, default=25)
    parser.add_argument("--diffusion-samples", type=int, default=1)
    parser.add_argument("--recycling-steps", type=int, default=3)
    parser.add_argument("--sampling-steps-affinity", type=int, default=200)
    parser.add_argument("--diffusion-samples-affinity", type=int, default=5)
    args = parser.parse_args()

    end_rank = args.offset + args.topn
    tag = args.tag or (f"rank{args.offset + 1:03d}_{end_rank:03d}" if args.offset else f"top{args.topn}")
    input_dir = OUT / f"inputs_r17_chromanol_generative_{tag}"
    output_dir = OUT / f"output_r17_chromanol_generative_{tag}"
    manifest_path = OUT / f"r17_chromanol_generative_{tag}_manifest.csv"
    csv_out = OUT / f"r17_chromanol_generative_{tag}_cofold.csv"

    designs = select_designs(args.topn, offset=args.offset, balanced=not args.global_only)
    if designs.empty:
        print("No R17 generative designs selected.")
        return 1

    manifest = write_inputs(designs, input_dir, manifest_path)
    if not manifest:
        print("No runnable YAMLs generated.")
        return 2

    print(f"R17 generative chromanol cofold: {len(manifest)} jobs")
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
        print(result[["job_id", "target", "affinity_probability_binary"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
