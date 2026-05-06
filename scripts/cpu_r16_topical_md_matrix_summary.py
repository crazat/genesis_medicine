"""Consolidate R16 topical chromanol 30 ns MD summaries.

This is a lightweight CPU-side manuscript support artifact. It combines the
completed R16 30 ns topical chromanol runs into one matrix table without
touching any running MD jobs.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

SOURCES = [
    (
        "priority_target_diverse",
        ROOT / "pilot/md_r16_chromanol_topical_priority_30ns/summary.json",
    ),
    (
        "tgfb1_extra",
        ROOT / "pilot/md_r16_chromanol_topical_tgfb1_extra_30ns/summary.json",
    ),
    (
        "chloro_tgfb1_positional",
        ROOT / "pilot/md_r16_chromanol_topical_chloro_tgfb1_30ns/summary.json",
    ),
    (
        "chloro_pigment_positional",
        ROOT / "pilot/md_r16_chromanol_topical_chloro_pigment_30ns/summary.json",
    ),
    (
        "dimethyl_pigment_completion",
        ROOT / "pilot/md_r16_chromanol_topical_dimethyl_pigment_30ns/summary.json",
    ),
]

CSV_OUT = OUT / "r16_topical_chromanol_30ns_matrix_summary.csv"
MD_OUT = OUT / "r16_topical_chromanol_30ns_matrix_summary.md"


def load_rows(label: str, path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = json.loads(path.read_text())
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if isinstance(row, dict):
            item = dict(row)
            item["source_set"] = label
            out.append(item)
    return out


def stable(row: dict[str, Any]) -> bool:
    if row.get("status") != "ok":
        return False
    return float(row.get("rmsd_max_A", 99.0)) <= 2.0 and float(row.get("rmsd_last_third_A", 99.0)) <= 1.5


def fmt(value: Any, digits: int = 3) -> str:
    if value is None or value == "":
        return ""
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for label, path in SOURCES:
        rows.extend(load_rows(label, path))

    rows.sort(
        key=lambda r: (
            str(r.get("target", "")),
            str(r.get("analog_id", "")),
            str(r.get("source_set", "")),
        )
    )

    fields = [
        "source_set",
        "job_id",
        "analog_id",
        "target",
        "smiles",
        "logP",
        "QED",
        "gap_eV",
        "affinity_probability_binary",
        "rmsd_mean_A",
        "rmsd_last_third_A",
        "rmsd_max_A",
        "ns_simulated",
        "stable_30ns",
    ]

    with CSV_OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields[:-1]} | {"stable_30ns": stable(row)})

    ok = [row for row in rows if row.get("status") == "ok"]
    stable_rows = [row for row in ok if stable(row)]
    max_rmsd = max((float(row.get("rmsd_max_A", 0.0)) for row in ok), default=0.0)
    max_last = max((float(row.get("rmsd_last_third_A", 0.0)) for row in ok), default=0.0)

    lines = [
        "# R16 Topical Chromanol 30 ns Matrix Summary",
        "",
        f"- rows: {len(rows)}",
        f"- ok: {len(ok)}",
        f"- stable_30ns: {len(stable_rows)}/{len(ok)}",
        f"- max_rmsd_A: {max_rmsd:.2f}",
        f"- max_last_third_A: {max_last:.2f}",
        "- stability_rule: status ok, rmsd_max_A <= 2.0, rmsd_last_third_A <= 1.5",
        "- caveat: in silico OpenMM pose-stability evidence only; no wet-lab potency, permeability, or toxicology claim.",
        "",
        "| analog_id | target | affinity_probability_binary | logP | QED | mean_A | last_third_A | max_A | source_set |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("analog_id", "")),
                    str(row.get("target", "")),
                    fmt(row.get("affinity_probability_binary")),
                    fmt(row.get("logP"), 3),
                    fmt(row.get("QED"), 3),
                    fmt(row.get("rmsd_mean_A"), 2),
                    fmt(row.get("rmsd_last_third_A"), 2),
                    fmt(row.get("rmsd_max_A"), 2),
                    str(row.get("source_set", "")),
                ]
            )
            + " |"
        )
    MD_OUT.write_text("\n".join(lines) + "\n")

    print(f"wrote {CSV_OUT}")
    print(f"wrote {MD_OUT}")
    print(f"stable_30ns {len(stable_rows)}/{len(ok)}; max_rmsd_A {max_rmsd:.2f}; max_last_third_A {max_last:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
