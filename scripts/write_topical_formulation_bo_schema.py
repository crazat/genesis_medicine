"""Topical formulation Bayesian-optimization schema and initial plan."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DATA = ROOT / "data"
DOC = ROOT / "docs/TOPICAL_FORMULATION_BO.md"
PLAN_CSV = OUT / "topical_formulation_bo_plan.csv"
TEMPLATE_CSV = DATA / "topical_formulation_experiment_template.csv"

TEMPLATE_COLUMNS = [
    "experiment_id",
    "date",
    "compound_id",
    "smiles",
    "formulation_type",
    "api_percent_w_w",
    "vehicle_phase",
    "ethanol_percent",
    "propylene_glycol_percent",
    "glycerol_percent",
    "limonene_percent",
    "menthol_percent",
    "polymer_or_gel",
    "pH",
    "viscosity_cP",
    "dry_down_time_min",
    "IVRT_release_6h_percent",
    "IVPT_flux_ug_cm2_h",
    "skin_retention_ug_cm2",
    "receptor_amount_ug_cm2",
    "irritation_flag",
    "stability_flag",
    "notes",
]


def col_or_default(df: pd.DataFrame, names: list[str], default: object = "") -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


def collect_leads() -> pd.DataFrame:
    frames = []
    for path, source, id_col in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16", "analog_id"),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15", "compound"),
        (OUT / "npass_xtb_refine_best_candidates.csv", "npass", "np_id"),
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "smiles" not in df.columns:
            continue
        score_col = "affinity_probability_binary" if "affinity_probability_binary" in df.columns else "topical_xtb_priority"
        frames.append(
            pd.DataFrame(
                {
                    "compound_id": col_or_default(df, [id_col]),
                    "target": col_or_default(df, ["target"]),
                    "smiles": col_or_default(df, ["smiles"]),
                    "source": source,
                    "score": pd.to_numeric(col_or_default(df, [score_col], 0), errors="coerce").fillna(0),
                    "logP": pd.to_numeric(col_or_default(df, ["logP", "logp"], 0), errors="coerce").fillna(0),
                    "MW": pd.to_numeric(col_or_default(df, ["MW", "mw"], 0), errors="coerce").fillna(0),
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    return df.sort_values("score", ascending=False).drop_duplicates(subset=["compound_id", "target", "smiles"]).head(60)


def formulation(row: pd.Series) -> dict[str, object]:
    logp = float(row.get("logP", 0) or 0)
    mw = float(row.get("MW", 0) or 0)
    if 1.0 <= logp <= 3.2 and mw <= 350:
        archetype = "hydroalcoholic_gel"
        objective = "maximize skin retention while limiting receptor flux"
        enhancers = "ethanol 10-30%; propylene glycol 5-20%; polymer screen"
    elif logp < 1.0:
        archetype = "penetration_enhancer_gel"
        objective = "raise stratum-corneum partitioning without irritation"
        enhancers = "propylene glycol 10-30%; menthol/limonene 0-3%"
    else:
        archetype = "nanoemulsion_or_lipid_gel"
        objective = "improve release from lipophilic vehicle and avoid surface residue"
        enhancers = "lipid phase 5-20%; surfactant screen; ethanol 0-15%"
    return {
        "compound_id": row.get("compound_id", ""),
        "target": row.get("target", ""),
        "source": row.get("source", ""),
        "smiles": row.get("smiles", ""),
        "logP": round(logp, 3),
        "MW": round(mw, 3),
        "formulation_archetype": archetype,
        "BO_objective": objective,
        "initial_factor_ranges": enhancers,
        "primary_endpoint": "IVPT skin_retention_ug_cm2 / receptor_amount_ug_cm2",
        "safety_endpoint": "keratinocyte/fibroblast viability + irritation flag",
        "next_action": "CRO IVRT/IVPT design or in-house formulation screen",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    leads = collect_leads()
    rows = [formulation(row) for _, row in leads.iterrows()]
    if rows:
        with PLAN_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        PLAN_CSV.write_text("", encoding="utf-8")
    with TEMPLATE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TEMPLATE_COLUMNS)
        writer.writeheader()
    lines = [
        "# Topical Formulation BO",
        "",
        f"- timestamp: `{now}`",
        f"- lead_rows: `{len(rows)}`",
        f"- plan_csv: `{PLAN_CSV.relative_to(ROOT)}`",
        f"- experiment_template: `{TEMPLATE_CSV.relative_to(ROOT)}`",
        "- purpose: molecule discovery를 실제 외용제 IVRT/IVPT/formulation optimization loop와 연결한다.",
        "",
        "## Initial Formulation Plans",
        "",
        "| compound | target | archetype | objective | factor ranges |",
        "|---|---|---|---|---|",
    ]
    for row in rows[:25]:
        lines.append(
            f"| {row['compound_id']} | {row['target']} | {row['formulation_archetype']} | {row['BO_objective']} | {row['initial_factor_ranges']} |"
        )
    lines.extend(
        [
            "",
            "## BO Decision Rule",
            "",
            "- Low-cost formulation readouts: solubility, viscosity, dry-down, IVRT release.",
            "- Medium-cost readouts: IVPT flux, skin retention, receptor compartment exposure.",
            "- High-cost readouts: cell irritation/viability plus disease-relevant phenotype.",
            "- Acquisition objective: maximize local skin retention and phenotype signal while minimizing receptor exposure and irritation.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {PLAN_CSV.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
