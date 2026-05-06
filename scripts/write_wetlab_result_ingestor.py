"""Normalize wet-lab/CRO feedback rows into queue decisions."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/WETLAB_RESULT_INGESTOR.md"
SOURCE = DATA / "wetlab_feedback_results.csv"
TEMPLATE = DATA / "wetlab_feedback_results_template.csv"
INGESTED_CSV = OUT / "wetlab_feedback_ingested.csv"
DECISION_CSV = OUT / "wetlab_queue_decisions.csv"
SUMMARY_JSON = OUT / "wetlab_result_ingestor_summary.json"

REQUIRED_COLUMNS = [
    "experiment_id",
    "date",
    "compound_id",
    "smiles",
    "target_or_pathway",
    "disease_context",
    "assay_type",
    "cell_type_or_model",
    "endpoint",
    "value",
    "unit",
    "dose",
    "dose_unit",
    "timepoint",
    "replicates",
    "control",
    "quality_flag",
    "interpretation",
    "raw_file",
    "raw_file_sha256",
    "notes",
]


def ensure_template() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if TEMPLATE.exists():
        return
    with TEMPLATE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()


def read_source() -> pd.DataFrame:
    if not SOURCE.exists() or SOURCE.stat().st_size == 0:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    try:
        df = pd.read_csv(SOURCE)
    except Exception:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[REQUIRED_COLUMNS].copy()


def decision(row: pd.Series) -> dict[str, object]:
    quality = str(row.get("quality_flag", "")).lower().strip()
    interpretation = str(row.get("interpretation", "")).lower().strip()
    endpoint = str(row.get("endpoint", "")).lower()
    assay = str(row.get("assay_type", "")).lower()
    if quality == "pass" and interpretation == "promote":
        queue_action = "promote_to_next_fidelity"
        next_compute = "update BO/active-learning and consider orthogonal MD/cofold only if not already done"
    elif quality == "fail" or interpretation == "deprioritize":
        queue_action = "deprioritize"
        next_compute = "block duplicate compute and preserve as negative evidence"
    else:
        queue_action = "hold_for_repeat_or_qc"
        next_compute = "repeat assay or request missing metadata before compute escalation"
    if "ivpt" in assay or "retention" in endpoint:
        paper_link = "P29/P32 topical formulation and dermal regulatory"
    elif "cell painting" in assay or "morphology" in endpoint:
        paper_link = "P37 phenomics signature gate"
    elif any(key in endpoint for key in ["col1a1", "acta2", "melanin", "tyrosinase"]):
        paper_link = "P23/P24 disease-focused lead papers"
    else:
        paper_link = "P26 reproducible autonomous workflow"
    return {
        "experiment_id": row.get("experiment_id", ""),
        "compound_id": row.get("compound_id", ""),
        "target_or_pathway": row.get("target_or_pathway", ""),
        "disease_context": row.get("disease_context", ""),
        "assay_type": row.get("assay_type", ""),
        "endpoint": row.get("endpoint", ""),
        "value": row.get("value", ""),
        "unit": row.get("unit", ""),
        "quality_flag": quality,
        "interpretation": interpretation,
        "queue_action": queue_action,
        "next_compute_or_assay": next_compute,
        "paper_link": paper_link,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ensure_template()
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    df = read_source()
    if df.empty:
        INGESTED_CSV.write_text(",".join(REQUIRED_COLUMNS) + "\n", encoding="utf-8")
        DECISION_CSV.write_text("", encoding="utf-8")
        summary = {"timestamp": now, "status": "no_wetlab_results_yet", "source": str(SOURCE.relative_to(ROOT)), "rows": 0}
    else:
        df.to_csv(INGESTED_CSV, index=False)
        decisions = [decision(row) for _, row in df.iterrows()]
        with DECISION_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(decisions[0].keys()))
            writer.writeheader()
            writer.writerows(decisions)
        summary = {
            "timestamp": now,
            "status": "ingested",
            "source": str(SOURCE.relative_to(ROOT)),
            "rows": len(df),
            "promote": sum(1 for row in decisions if row["queue_action"] == "promote_to_next_fidelity"),
            "hold": sum(1 for row in decisions if row["queue_action"] == "hold_for_repeat_or_qc"),
            "deprioritize": sum(1 for row in decisions if row["queue_action"] == "deprioritize"),
        }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Wet-lab Result Ingestor",
        "",
        f"- timestamp: `{now}`",
        f"- status: `{summary['status']}`",
        f"- source_file: `{SOURCE.relative_to(ROOT)}`",
        f"- result_template: `{TEMPLATE.relative_to(ROOT)}`",
        f"- ingested_csv: `{INGESTED_CSV.relative_to(ROOT)}`",
        f"- decision_csv: `{DECISION_CSV.relative_to(ROOT)}`",
        "- purpose: CRO/in-house assay 결과가 들어오면 quality/interpretation 기반으로 다음 compute 또는 논문 근거를 자동 분기한다.",
        "",
        "## Decision Rules",
        "",
        "| input | queue action |",
        "|---|---|",
        "| `quality_flag=pass` and `interpretation=promote` | BO/active-learning update and next fidelity promotion |",
        "| `quality_flag=fail` or `interpretation=deprioritize` | duplicate compute block and negative evidence preservation |",
        "| otherwise | repeat/QC hold before escalation |",
        "",
    ]
    if not df.empty and DECISION_CSV.exists() and DECISION_CSV.stat().st_size > 0:
        decisions_df = pd.read_csv(DECISION_CSV)
        lines.extend(["## Current Decisions", "", "| compound | pathway | action | next |", "|---|---|---|---|"])
        for _, row in decisions_df.head(30).iterrows():
            lines.append(f"| {row['compound_id']} | {row['target_or_pathway']} | {row['queue_action']} | {row['next_compute_or_assay']} |")
    lines.extend(
        [
            "## Curator Rule",
            "",
            "- `data/wetlab_feedback_results.csv`가 생기면 이 ingestor를 먼저 실행하고, promote row만 후속 GPU/CPU 큐로 승격한다.",
            "- template 파일은 예시용이다. 실제 결과는 `data/wetlab_feedback_results.csv`에 별도 저장한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
