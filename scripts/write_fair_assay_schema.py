"""Write FAIR assay metadata templates for wet-lab and CRO feedback."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/FAIR_ASSAY_SCHEMA.md"
DICT_CSV = OUT / "fair_assay_dictionary.csv"
TEMPLATE_CSV = DATA / "fair_assay_metadata_template.csv"
SCHEMA_JSON = DATA / "fair_assay_schema.json"

FIELDS = [
    ("investigation_id", "required", "ISA investigation identifier", "string", ""),
    ("study_id", "required", "ISA study identifier or project arm", "string", ""),
    ("assay_id", "required", "assay run identifier", "string", ""),
    ("experiment_date", "required", "ISO date for experiment start", "date", ""),
    ("compound_id", "required", "Genesis candidate identifier", "string", ""),
    ("smiles", "required", "canonical or submitted SMILES", "string", ""),
    ("batch_id", "required", "compound batch or vendor lot", "string", ""),
    ("target_or_pathway", "required", "target, pathway, or phenotype axis", "string", ""),
    ("disease_context", "required", "scar, pigment, acne, alopecia, photoaging, or control", "controlled_string", ""),
    ("assay_type", "required", "qPCR, enzyme, Cell Painting, viability, IVRT, IVPT, etc.", "controlled_string", ""),
    ("bao_assay_format", "recommended", "BAO-style assay format class", "string", ""),
    ("cell_type_or_model", "required", "cell line, primary cell, organoid, skin model, or biochemical assay", "string", ""),
    ("plate_id", "recommended", "plate or run identifier", "string", ""),
    ("well_id", "recommended", "well position if plate-based", "string", ""),
    ("dose", "required", "dose value", "number", ""),
    ("dose_unit", "required", "dose unit", "controlled_string", "uM;ug/mL;percent_w_w"),
    ("timepoint", "required", "duration or sampling time", "string", ""),
    ("endpoint", "required", "measured endpoint", "string", ""),
    ("value", "required", "numeric readout", "number", ""),
    ("unit", "required", "endpoint unit", "controlled_string", ""),
    ("replicate_id", "required", "biological/technical replicate identifier", "string", ""),
    ("control_type", "required", "vehicle, positive, negative, untreated, reference drug", "controlled_string", ""),
    ("control_id", "recommended", "control compound or condition", "string", ""),
    ("protocol_version", "required", "protocol or SOP version", "string", ""),
    ("instrument_id", "recommended", "instrument and acquisition setting", "string", ""),
    ("reagent_lot", "recommended", "critical reagent lot", "string", ""),
    ("raw_file", "required", "path or URI for raw data", "string", ""),
    ("raw_file_sha256", "required", "hash for raw file integrity", "sha256", ""),
    ("analysis_script", "recommended", "script/notebook used for processing", "string", ""),
    ("analysis_version", "recommended", "git commit or version", "string", ""),
    ("quality_flag", "required", "pass, review, fail", "controlled_string", "pass;review;fail"),
    ("interpretation", "required", "promote, hold, deprioritize", "controlled_string", "promote;hold;deprioritize"),
    ("notes", "optional", "free-text caveats", "string", ""),
]


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    rows = [
        {
            "field": name,
            "requirement": req,
            "description": desc,
            "type": typ,
            "allowed_values_or_example": allowed,
        }
        for name, req, desc, typ, allowed in FIELDS
    ]
    with DICT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    if not TEMPLATE_CSV.exists():
        with TEMPLATE_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[row["field"] for row in rows])
            writer.writeheader()

    schema = {
        "timestamp": now,
        "schema_name": "Genesis_Medicine FAIR assay metadata v1",
        "principles": ["ISA-style investigation/study/assay identifiers", "BAO-style assay format", "RO-Crate-ready raw file provenance"],
        "required_fields": [row["field"] for row in rows if row["requirement"] == "required"],
        "fields": rows,
    }
    SCHEMA_JSON.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# FAIR Assay Schema",
        "",
        f"- timestamp: `{now}`",
        f"- dictionary_csv: `{DICT_CSV.relative_to(ROOT)}`",
        f"- template_csv: `{TEMPLATE_CSV.relative_to(ROOT)}`",
        f"- schema_json: `{SCHEMA_JSON.relative_to(ROOT)}`",
        "- purpose: wet-lab/CRO 결과를 ISA/BAO/RO-Crate-ready metadata로 받아 compute loop와 논문 provenance에 재사용한다.",
        "",
        "## Required Fields",
        "",
        "| field | type | description |",
        "|---|---|---|",
    ]
    for row in rows:
        if row["requirement"] == "required":
            lines.append(f"| {row['field']} | {row['type']} | {row['description']} |")
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- raw assay value만 있는 CSV는 논문 근거로 쓰지 않는다. `dose`, `unit`, `replicate_id`, `control_type`, `quality_flag`, `raw_file_sha256`가 필요하다.",
            "- `quality_flag=review/fail`은 음성 결과로 보존하되 lead promotion에는 쓰지 않는다.",
            "- `interpretation=promote` row가 들어오면 active-learning/BO planner가 다음 compute 또는 assay를 승격해야 한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {DICT_CSV.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
