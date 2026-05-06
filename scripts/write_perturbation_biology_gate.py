"""Target/candidate perturbation-biology gate for virtual-cell style evidence."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/PERTURBATION_BIOLOGY_GATE.md"
CSV_OUT = OUT / "perturbation_biology_gate.csv"

CELL_MAP = {
    "pigment": "melanocyte",
    "scar": "dermal_fibroblast",
    "photoaging": "dermal_fibroblast;keratinocyte",
    "alopecia": "dermal_papilla_cell;hair_follicle_keratinocyte",
    "acne": "sebocyte;keratinocyte;immune_cell",
}


def target_categories() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for path in (ROOT / "conf/skin_targets").glob("*.yaml"):
        category = path.stem
        try:
            data = yaml.safe_load(path.read_text()) or {}
        except Exception:
            continue
        targets = data.get("targets") or data.get("target_genes") or []
        if isinstance(targets, dict):
            targets = targets.keys()
        for item in targets:
            if isinstance(item, dict):
                name = item.get("key") or item.get("symbol") or item.get("target") or item.get("gene")
            else:
                name = item
            if not name:
                continue
            out.setdefault(str(name).lower(), set()).add(category)
    return out


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    cats = target_categories()
    target_gate = read_csv(OUT / "target_evidence_gate.csv")
    consensus = read_csv(OUT / "structure_consensus_calibration.csv")
    wetlab = read_csv(OUT / "wetlab_endpoint_priority.csv")
    endpoint_by_target = {}
    if not wetlab.empty and ("target" in wetlab.columns or "target_or_pathway" in wetlab.columns):
        target_col = "target" if "target" in wetlab.columns else "target_or_pathway"
        for _, row in wetlab.iterrows():
            raw_targets = str(row.get(target_col, "")).replace("/", ";").replace(",", ";").split(";")
            endpoint = str(row.get("primary_endpoint", row.get("recommended_assay", row.get("endpoint", ""))))
            for raw in raw_targets:
                target = raw.strip().lower()
                if target:
                    endpoint_by_target.setdefault(target, []).append(endpoint)
    target_gate_map = {}
    if not target_gate.empty:
        for _, row in target_gate.iterrows():
            target_gate_map[str(row.get("target", "")).lower()] = str(row.get("gate", ""))

    rows = []
    targets = sorted(set(cats) | set(target_gate_map) | set(consensus.get("target", pd.Series(dtype=str)).astype(str).str.lower()))
    for target in targets:
        if not target or target == "nan":
            continue
        categories = sorted(cats.get(target, set()))
        cells = sorted({cell for cat in categories for cell in CELL_MAP.get(cat, "").split(";") if cell})
        gate = target_gate_map.get(target, "missing")
        pair_count = 0
        high_conf = 0
        if not consensus.empty:
            subset = consensus[consensus["target"].astype(str).str.lower().eq(target)]
            pair_count = len(subset)
            high_conf = int(subset["consensus_class"].astype(str).eq("high_confidence").sum()) if "consensus_class" in subset.columns else 0
        endpoints = [e for e in endpoint_by_target.get(target, []) if e and e != "nan"]
        score = 0
        score += 2 if gate == "green" else 1 if gate == "yellow" else 0
        score += 1 if cells else 0
        score += 1 if endpoints else 0
        score += 1 if high_conf else 0
        if score >= 5:
            priority = "high"
            next_action = "connect candidate to LINCS/Geneformer/scGPT or wet-lab phenotype endpoint"
        elif score >= 3:
            priority = "review"
            next_action = "collect cell-type perturbation evidence before strong target claim"
        else:
            priority = "low"
            next_action = "do not prioritize virtual-cell follow-up yet"
        rows.append(
            {
                "target": target,
                "target_gate": gate,
                "skin_categories": ";".join(categories) if categories else "missing",
                "recommended_cell_contexts": ";".join(cells) if cells else "missing",
                "wetlab_endpoints_available": ";".join(endpoints[:4]) if endpoints else "missing",
                "consensus_pair_count": pair_count,
                "high_confidence_pair_count": high_conf,
                "perturbation_priority": priority,
                "external_data_needed": "LINCS L1000;Geneformer;scGPT;Virtual Cell Challenge style perturbation benchmark",
                "next_action": next_action,
            }
        )
    rows.sort(key=lambda r: {"high": 0, "review": 1, "low": 2}.get(str(r["perturbation_priority"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {p: sum(1 for r in rows if r["perturbation_priority"] == p) for p in ["high", "review", "low"]}
    lines = [
        "# Perturbation Biology Gate",
        "",
        f"- timestamp: `{now}`",
        f"- target_rows: `{len(rows)}`",
        f"- priority_counts: `{counts}`",
        "- purpose: direct binding 후보를 실제 피부 cell phenotype/perturbation evidence와 연결할 수 있는지 평가한다.",
        "",
        "## Priority Targets",
        "",
        "| target | priority | cells | target gate | high-confidence pairs | next |",
        "|---|---|---|---|---:|---|",
    ]
    for row in rows[:25]:
        lines.append(
            f"| {row['target']} | {row['perturbation_priority']} | {row['recommended_cell_contexts']} | {row['target_gate']} | {row['high_confidence_pair_count']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `high` target은 cofold/MD 결과를 wet-lab phenotype 또는 perturbation signature plan과 연결한다.",
            "- `review` target은 direct binding claim보다 hypothesis 수준으로 낮춘다.",
            "- `low` target은 heavy compute보다 target evidence 보강이 먼저다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
