"""Consolidate R15 chromanol Boltz-2 affinity outputs.

Input:
    pilot/cpu_meaningful/output_r15_chromanol/boltz_results_inputs_r15_chromanol/

Output:
    pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
RESULT_DIR = OUT / "output_r15_chromanol" / "boltz_results_inputs_r15_chromanol"
CSV_PATH = OUT / "r15_chromanol_cofold_14targets.csv"
SMILES = "OCC1COc2cc(O)ccc2C1"
COMPOUND = "R15_chromanol"

TARGET_ORDER = [
    "tgfb1",
    "mmp1",
    "ctgf",
    "ar",
    "mitf",
    "lox",
    "sirt1",
    "tyr",
    "tyrp1",
    "dct",
    "srd5a1",
    "srd5a2",
    "srebp1",
    "ptgs2",
]


def target_from_affinity_path(path: Path) -> str:
    stem = path.stem
    prefix = "affinity_r15_chrom_"
    if stem.startswith(prefix):
        return stem[len(prefix):].lower()
    return path.parent.name.replace("r15_chrom_", "").lower()


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
    rows_by_target: dict[str, dict[str, object]] = {}
    pred_root = RESULT_DIR / "predictions"

    for affinity_path in sorted(pred_root.glob("*/affinity_*.json")):
        target = target_from_affinity_path(affinity_path)
        try:
            affinity = json.loads(affinity_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Skipping unreadable affinity file: {affinity_path} ({exc})")
            continue

        row: dict[str, object] = {
            "target": target,
            "compound": COMPOUND,
            "smiles": SMILES,
            "affinity_pred_value": affinity.get("affinity_pred_value"),
            "affinity_probability_binary": affinity.get("affinity_probability_binary"),
            "affinity_pred_value1": affinity.get("affinity_pred_value1"),
            "affinity_probability_binary1": affinity.get("affinity_probability_binary1"),
            "affinity_pred_value2": affinity.get("affinity_pred_value2"),
            "affinity_probability_binary2": affinity.get("affinity_probability_binary2"),
            "affinity_json": str(affinity_path.relative_to(ROOT)),
            "prediction_dir": str(affinity_path.parent.relative_to(ROOT)),
        }
        row.update(load_confidence(affinity_path.parent))
        rows_by_target[target] = row

    rows = [rows_by_target[target] for target in TARGET_ORDER if target in rows_by_target]
    extra_targets = sorted(set(rows_by_target) - set(TARGET_ORDER))
    rows.extend(rows_by_target[target] for target in extra_targets)

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
        "target",
        "compound",
        "smiles",
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

    missing = [target for target in TARGET_ORDER if target not in rows_by_target]
    print(f"Saved {CSV_PATH.relative_to(ROOT)} ({len(rows)} rows)")
    if missing:
        print(f"Missing targets: {', '.join(missing)}")
    if rows:
        print("Top 3 by affinity_probability_binary:")
        for row in rows[:3]:
            print(
                f"  {row['target']}: "
                f"{row.get('affinity_probability_binary')} "
                f"(pred={row.get('affinity_pred_value')})"
            )
    return 0 if len(rows) == len(TARGET_ORDER) else 1


if __name__ == "__main__":
    raise SystemExit(main())
