"""Write wet-lab feedback schema and endpoint priority table."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/WETLAB_FEEDBACK_SCHEMA.md"
TEMPLATE = DATA_DIR / "wetlab_feedback_template.csv"
ENDPOINTS = OUT / "wetlab_endpoint_priority.csv"

FEEDBACK_COLUMNS = [
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
    "vendor_or_lab",
    "raw_file",
    "quality_flag",
    "interpretation",
    "notes",
]

ENDPOINT_ROWS = [
    {
        "priority": 1,
        "paper_link": "P16/P24",
        "context": "scar/fibrosis topical lead",
        "target_or_pathway": "TGFB1/SMAD",
        "recommended_assay": "fibroblast TGF-beta induced COL1A1/ACTA2 qPCR + viability",
        "decision_rule": "lead only if anti-fibrotic signal appears below cytotoxic concentration",
    },
    {
        "priority": 2,
        "paper_link": "P16/P23",
        "context": "pigmentation topical lead",
        "target_or_pathway": "TYR/DCT/melanin synthesis",
        "recommended_assay": "B16F10 or human melanocyte melanin content + tyrosinase activity",
        "decision_rule": "lead only if pigment endpoint changes without broad toxicity",
    },
    {
        "priority": 3,
        "paper_link": "P17",
        "context": "systemic-safety chromanol fragment",
        "target_or_pathway": "hERG/AMES/DILI counterscreen",
        "recommended_assay": "commercial safety panel or orthogonal ADMET counterscreen",
        "decision_rule": "systemic path only if wet-lab safety remains clean",
    },
    {
        "priority": 4,
        "paper_link": "P18/P19",
        "context": "NPASS atlas candidates",
        "target_or_pathway": "top-ranked target-specific candidates",
        "recommended_assay": "single-concentration cellular phenotypic triage before more GPU",
        "decision_rule": "promote only candidates with phenotype signal and acceptable solubility",
    },
]


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    with TEMPLATE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FEEDBACK_COLUMNS)
        writer.writeheader()

    with ENDPOINTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ENDPOINT_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(ENDPOINT_ROWS)

    lines = [
        "# Wet-lab Feedback Schema",
        "",
        f"- timestamp: `{now}`",
        f"- feedback_template: `{TEMPLATE.relative_to(ROOT)}`",
        f"- endpoint_priority: `{ENDPOINTS.relative_to(ROOT)}`",
        "- purpose: 계산 루프가 wet-lab 결과를 구조적으로 다시 받아 다음 큐잉을 판단하게 만든다.",
        "",
        "## Required Columns",
        "",
        "| column | purpose |",
        "|---|---|",
    ]
    descriptions = {
        "compound_id": "R15/R16/NPASS 등 계산 ID와 연결한다.",
        "smiles": "동일성, salt/tautomer 확인, novelty 재계산에 쓴다.",
        "target_or_pathway": "TGFB1, TYR, DCT처럼 계산 target 또는 phenotype pathway.",
        "assay_type": "qPCR, enzyme, cell viability, melanin content 등.",
        "endpoint": "COL1A1, ACTA2, melanin, IC50, viability 등.",
        "quality_flag": "pass, review, fail 중 하나로 curator가 후속 큐를 결정한다.",
        "interpretation": "promote, hold, deprioritize 중 하나를 권장한다.",
    }
    for col in FEEDBACK_COLUMNS:
        lines.append(f"| {col} | {descriptions.get(col, 'raw wet-lab metadata 또는 분석값')} |")
    lines.extend(
        [
            "",
            "## Endpoint Priority",
            "",
            "| priority | context | recommended assay | decision rule |",
            "|---:|---|---|---|",
        ]
    )
    for row in ENDPOINT_ROWS:
        lines.append(
            f"| {row['priority']} | {row['context']} | {row['recommended_assay']} | {row['decision_rule']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- 새 wet-lab row가 들어오면 `quality_flag`와 `interpretation`을 기준으로 GPU/CPU 후속 큐를 승격한다.",
            "- wet-lab 음성 결과도 methodology/failure-mode paper의 근거로 보존한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
