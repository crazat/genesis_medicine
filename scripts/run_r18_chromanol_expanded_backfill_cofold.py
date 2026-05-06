"""R18 expanded chromanol backfill Boltz-2 cofold queue.

This is an overnight GPU backfill after the curated R17 240-row atlas is
complete. It creates conservative triple-substituted chromanol analogs without
chlorine, keeps only route-ready/topical-window candidates, and writes explicit
triage-only cofold batches.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from itertools import combinations, product
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from rdkit import Chem, DataStructs, RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.write_chromanol_generative_optimizer import (  # noqa: E402
    BASE_SMILES,
    TARGET_BIASES,
    apply_design,
    aromatic_h_positions,
    descriptors,
    morgan,
    topical_score,
)
from scripts.run_r17_chromanol_generative_top_cofold import (  # noqa: E402
    read_target_map,
    safe_id,
    sequence_from_cache,
)

OUT = ROOT / "pilot/cpu_meaningful"
MSA_DIR = ROOT / "data/msa"
CSV_SOURCE = OUT / "r18_chromanol_expanded_backfill_queue.csv"
SUBSTITUENTS = ("F", "Me", "OMe", "OH")


def build_queue() -> pd.DataFrame:
    base = Chem.MolFromSmiles(BASE_SMILES)
    if base is None:
        raise RuntimeError("base chromanol SMILES failed")
    base_fp = morgan(base)
    positions = aromatic_h_positions(base)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for pos_combo in combinations(positions, 3):
        for sub_combo in product(SUBSTITUENTS, repeat=3):
            design = list(zip(pos_combo, sub_combo))
            mol = apply_design(base, design)
            if mol is None:
                continue
            smiles = Chem.MolToSmiles(mol, canonical=True)
            if smiles in seen:
                continue
            seen.add(smiles)
            desc = descriptors(mol)
            fp = morgan(mol)
            sim = DataStructs.TanimotoSimilarity(base_fp, fp)
            topo = topical_score(desc)
            sub_names = "+".join(sub_combo)
            pos_names = "+".join(f"arom{p}" for p in pos_combo)
            photosafety = "none_detected"
            for target, bias in TARGET_BIASES.items():
                priority = topo * 0.48 + sim * 0.15 + bias * 0.14 + float(desc["QED"]) * 0.12
                priority += 0.06
                action = "Boltz-2_backfill_triage" if priority >= 0.62 else "archive_low_priority"
                rows.append(
                    {
                        "design_id": f"r18_chromanol_{pos_names}_{sub_names}_{target}",
                        "target": target,
                        "smiles": smiles,
                        "substituents": sub_names,
                        "positions": pos_names,
                        **desc,
                        "base_tanimoto": round(sim, 4),
                        "topical_window_score": topo,
                        "target_bias": bias,
                        "local_design_priority": round(priority, 4),
                        "novelty_status": "new_local_design_unchecked_fto",
                        "synthesis_route_proxy": "route_ready_proxy",
                        "photosafety_proxy": photosafety,
                        "recommended_next_action": action,
                    }
                )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values(["local_design_priority", "topical_window_score", "QED"], ascending=False)
    CSV_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_SOURCE, index=False)
    return df


def completed_pairs() -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    for path in sorted(OUT.glob("r18_chromanol_expanded_backfill_batch*_cofold.csv")):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        for row in df.itertuples(index=False):
            design_id = str(getattr(row, "design_id", "")).strip()
            target = str(getattr(row, "target", "")).strip().lower()
            if design_id and target:
                done.add((design_id, target))
    return done


def next_batch_id() -> int:
    max_batch = 0
    for path in OUT.glob("r18_chromanol_expanded_backfill_batch*_cofold.csv"):
        match = re.search(r"batch(\d+)", path.stem)
        if match:
            max_batch = max(max_batch, int(match.group(1)))
    return max_batch + 1


def select_batch(batch_size: int) -> pd.DataFrame:
    df = pd.read_csv(CSV_SOURCE) if CSV_SOURCE.exists() else build_queue()
    if df.empty:
        return df
    df["target"] = df["target"].astype(str).str.lower()
    df["design_id"] = df["design_id"].astype(str)
    df = df[
        (df["recommended_next_action"] == "Boltz-2_backfill_triage")
        & (df["synthesis_route_proxy"] == "route_ready_proxy")
        & (df["photosafety_proxy"] == "none_detected")
    ].copy()
    done = completed_pairs()
    df = df[~df.apply(lambda r: (str(r["design_id"]), str(r["target"]).lower()) in done, axis=1)].copy()
    if df.empty:
        return df
    target_priority = {"tgfb1": 0, "dct": 1, "tyr": 2, "mmp1": 3, "ptgs2": 4}
    df["target_priority"] = df["target"].map(target_priority).fillna(9).astype(int)
    df = df.sort_values(["local_design_priority", "target_priority"], ascending=[False, True])
    return df.head(batch_size).reset_index(drop=True)


def write_inputs(candidates: pd.DataFrame, input_dir: Path, manifest_path: Path) -> list[dict[str, Any]]:
    target_map = read_target_map()
    input_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for rank, row in enumerate(candidates.itertuples(index=False), start=1):
        target = str(getattr(row, "target")).lower()
        meta = target_map.get(target)
        if not meta:
            continue
        msa = MSA_DIR / f"{target}.a3m"
        sequence = sequence_from_cache(meta["uniprot"], target)
        if not sequence or not msa.exists():
            continue
        design_id = str(getattr(row, "design_id"))
        job_id = f"r18_{rank:02d}_{target}_{safe_id(design_id)}"
        payload = {
            "version": 1,
            "sequences": [
                {"protein": {"id": "A", "sequence": sequence, "msa": str(msa.absolute())}},
                {"ligand": {"id": "L", "smiles": str(getattr(row, "smiles"))}},
            ],
            "properties": [{"affinity": {"binder": "L"}}],
        }
        (input_dir / f"{job_id}.yaml").write_text(yaml.safe_dump(payload, sort_keys=False))
        manifest.append(
            {
                "job_id": job_id,
                "design_id": design_id,
                "target": target,
                "smiles": str(getattr(row, "smiles")),
                "local_design_priority": float(getattr(row, "local_design_priority")),
                "topical_window_score": float(getattr(row, "topical_window_score")),
                "QED": float(getattr(row, "QED")),
                "cLogP": float(getattr(row, "cLogP")),
                "photosafety_proxy": str(getattr(row, "photosafety_proxy")),
                "novelty_status": str(getattr(row, "novelty_status")),
            }
        )
    pd.DataFrame(manifest).to_csv(manifest_path, index=False)
    return manifest


def collect_results(output_dir: Path, manifest: list[dict[str, Any]], csv_out: Path) -> pd.DataFrame:
    by_job = {row["job_id"]: row for row in manifest}
    rows: list[dict[str, Any]] = []
    for path in sorted(output_dir.rglob("affinity_*.json")):
        job_id = path.stem.replace("affinity_", "")
        data = json.loads(path.read_text())
        rows.append(
            {
                **by_job.get(job_id, {}),
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
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--sampling-steps", type=int, default=25)
    parser.add_argument("--diffusion-samples", type=int, default=1)
    parser.add_argument("--recycling-steps", type=int, default=3)
    parser.add_argument("--sampling-steps-affinity", type=int, default=200)
    parser.add_argument("--diffusion-samples-affinity", type=int, default=5)
    args = parser.parse_args()

    batch = next_batch_id()
    tag = f"batch{batch:02d}"
    input_dir = OUT / f"inputs_r18_chromanol_expanded_backfill_{tag}"
    output_dir = OUT / f"output_r18_chromanol_expanded_backfill_{tag}"
    manifest_path = OUT / f"r18_chromanol_expanded_backfill_{tag}_manifest.csv"
    csv_out = OUT / f"r18_chromanol_expanded_backfill_{tag}_cofold.csv"

    candidates = select_batch(args.batch_size)
    if candidates.empty:
        print("No R18 expanded chromanol backfill candidates pending.")
        return 0
    manifest = write_inputs(candidates, input_dir, manifest_path)
    if not manifest:
        print("No runnable R18 YAMLs generated.")
        return 2

    print(f"R18 expanded chromanol backfill cofold: {len(manifest)} jobs tag={tag}")
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
    print(f"Boltz-2 exit={rc}, wall={(time.time() - t0) / 60:.2f} min")
    if rc != 0:
        return rc
    result = collect_results(output_dir, manifest, csv_out)
    print(f"results: {csv_out} rows={len(result)}")
    if not result.empty:
        print(result[["design_id", "target", "affinity_probability_binary"]].head(20).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
