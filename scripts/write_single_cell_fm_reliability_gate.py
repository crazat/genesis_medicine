"""Reliability gate for single-cell foundation-model and virtual-cell claims."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "single_cell_fm_reliability_gate.csv"
DOC = ROOT / "docs/SINGLE_CELL_FM_RELIABILITY_GATE.md"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def clean(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    perturb = read_csv(OUT / "perturbation_biology_gate.csv")
    spatial = read_csv(OUT / "skin_spatial_atlas_gate.csv")
    phenomics = read_csv(OUT / "phenomics_signature_gate.csv")
    rows: list[dict[str, object]] = []
    targets = sorted(set(perturb.get("target", pd.Series(dtype=str)).astype(str).str.lower()) | set(spatial.get("target", pd.Series(dtype=str)).astype(str).str.lower()))
    for target in targets:
        if not target or target == "nan":
            continue
        pt = perturb[perturb["target"].astype(str).str.lower().eq(target)] if not perturb.empty and "target" in perturb.columns else pd.DataFrame()
        sp = spatial[spatial["target"].astype(str).str.lower().eq(target)] if not spatial.empty and "target" in spatial.columns else pd.DataFrame()
        fm_priority = clean(pt.iloc[0].get("perturbation_priority")) if not pt.empty else "missing"
        cell_context = clean(pt.iloc[0].get("recommended_cell_contexts")) if not pt.empty else clean(sp.iloc[0].get("cell_context")) if not sp.empty else "missing"
        spatial_gate = clean(sp.iloc[0].get("skin_spatial_gate")) if not sp.empty else "missing"
        phenomics_rows = 0
        if not phenomics.empty and "target" in phenomics.columns:
            phenomics_rows = len(phenomics[phenomics["target"].astype(str).str.lower().eq(target)])
        if fm_priority == "high" and spatial_gate == "spatially_anchorable" and phenomics_rows > 0:
            gate = "fm_supported_with_controls"
            action = "allow virtual-cell/phenomics hypothesis with simple-baseline and wet-lab caveat"
        elif fm_priority in {"high", "review"}:
            gate = "zero_shot_reliability_review"
            action = "require cell-type match, fine-tuning/proximity check, and simpler-baseline comparison"
        else:
            gate = "fm_not_actionable"
            action = "do not use single-cell FM for target claim yet"
        rows.append(
            {
                "target": target,
                "recommended_models": "Geneformer;scGPT;scFoundation;UCE;Cell Painting/JUMP baselines",
                "cell_context": cell_context,
                "perturbation_priority": fm_priority,
                "skin_spatial_gate": spatial_gate,
                "phenomics_rows": phenomics_rows,
                "required_controls": "zero-shot baseline;cell-type proximity;batch/domain check;simpler model comparison;wet-lab endpoint caveat",
                "single_cell_fm_gate": gate,
                "next_action": action,
            }
        )
    rows.sort(key=lambda r: {"fm_supported_with_controls": 0, "zero_shot_reliability_review": 1, "fm_not_actionable": 2}.get(str(r["single_cell_fm_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["single_cell_fm_gate"] == g) for g in ["fm_supported_with_controls", "zero_shot_reliability_review", "fm_not_actionable"]}
    lines = [
        "# Single-Cell FM Reliability Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: scGPT/Geneformer/virtual-cell style evidence를 zero-shot limitation과 baseline-control 요구사항으로 제한한다.",
        "",
        "## FM Reliability Rows",
        "",
        "| target | gate | cells | perturbation | spatial | controls | next |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['target']} | {row['single_cell_fm_gate']} | {row['cell_context']} | {row['perturbation_priority']} | {row['skin_spatial_gate']} | {row['required_controls']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `fm_supported_with_controls`: virtual-cell claim은 hypothesis로만 쓰고 baseline-control을 명시한다.",
            "- `zero_shot_reliability_review`: fine-tuning/proximity/simple baseline 없이는 manuscript main claim 금지.",
            "- `fm_not_actionable`: 추가 docking보다 target/cell evidence 보강이 먼저다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
