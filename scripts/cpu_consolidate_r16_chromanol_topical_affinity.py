"""Consolidate R16 chromanol topical analog Boltz-2 affinity outputs.

Input:
    pilot/cpu_meaningful/r16_chromanol_topical_manifest.csv
    pilot/cpu_meaningful/output_r16_chromanol_topical/

Output:
    pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
MANIFEST = OUT / "r16_chromanol_topical_manifest.csv"
RESULT_DIR = OUT / "output_r16_chromanol_topical" / "boltz_results_inputs_r16_chromanol_topical"
CSV_PATH = OUT / "r16_chromanol_topical_cofold.csv"


def load_confidence(pred_dir: Path) -> dict[str, float | None]:
    confidence_files = sorted(pred_dir.glob("confidence_*.json"))
    if not confidence_files:
        return {}
    try:
        data = json.loads(confidence_files[0].read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        "confidence_score": data.get("confidence_score"),
        "ptm": data.get("ptm"),
        "iptm": data.get("iptm"),
        "ligand_iptm": data.get("ligand_iptm"),
        "complex_plddt": data.get("complex_plddt"),
    }


def main() -> int:
    manifest = pd.read_csv(MANIFEST)
    meta_by_job = {str(row["job_id"]): row.to_dict() for _, row in manifest.iterrows()}
    pred_root = RESULT_DIR / "predictions"

    rows: list[dict[str, object]] = []
    for affinity_path in sorted(pred_root.glob("*/affinity_*.json")):
        job_id = affinity_path.parent.name
        try:
            affinity = json.loads(affinity_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Skipping unreadable affinity file: {affinity_path} ({exc})")
            continue

        row: dict[str, object] = dict(meta_by_job.get(job_id, {"job_id": job_id}))
        row.update(
            {
                "affinity_pred_value": affinity.get("affinity_pred_value"),
                "affinity_probability_binary": affinity.get("affinity_probability_binary"),
                "affinity_pred_value1": affinity.get("affinity_pred_value1"),
                "affinity_probability_binary1": affinity.get("affinity_probability_binary1"),
                "affinity_pred_value2": affinity.get("affinity_pred_value2"),
                "affinity_probability_binary2": affinity.get("affinity_probability_binary2"),
                "affinity_json": str(affinity_path.relative_to(ROOT)),
                "prediction_dir": str(affinity_path.parent.relative_to(ROOT)),
            }
        )
        row.update(load_confidence(affinity_path.parent))
        rows.append(row)

    rows.sort(
        key=lambda row: (
            row.get("affinity_probability_binary") is not None,
            float(row.get("affinity_probability_binary") or -1.0),
        ),
        reverse=True,
    )
    for rank, row in enumerate(rows, start=1):
        row["rank_by_affinity_probability"] = rank

    fieldnames = [
        "rank_by_affinity_probability",
        "job_id",
        "analog_rank",
        "analog_id",
        "target",
        "smiles",
        "topical_followup_score",
        "logP",
        "QED",
        "gap_eV",
        "affinity_probability_binary",
        "affinity_pred_value",
        "affinity_probability_binary1",
        "affinity_pred_value1",
        "affinity_probability_binary2",
        "affinity_pred_value2",
        "confidence_score",
        "ptm",
        "iptm",
        "ligand_iptm",
        "complex_plddt",
        "affinity_json",
        "prediction_dir",
    ]

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})

    expected = set(meta_by_job)
    observed = {str(row["job_id"]) for row in rows}
    missing = sorted(expected - observed)
    print(f"Saved {CSV_PATH.relative_to(ROOT)} ({len(rows)}/{len(expected)} rows)")
    if missing:
        print(f"Missing jobs: {', '.join(missing)}")
    if rows:
        print("Top 5 by affinity_probability_binary:")
        for row in rows[:5]:
            print(
                f"  {row.get('job_id')}: {row.get('analog_id')} x {row.get('target')} "
                f"{row.get('affinity_probability_binary')} "
                f"(pred={row.get('affinity_pred_value')})"
            )
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
