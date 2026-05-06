"""Phenomic signature gate for Cell Painting / high-content follow-up."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/PHENOMICS_SIGNATURE_GATE.md"
CSV_OUT = OUT / "phenomics_signature_gate.csv"

TARGET_CONTEXT = {
    "tgfb1": ("scar_fibrosis", "primary dermal fibroblast", "COL1A1/ACTA2 morphology + Cell Painting"),
    "ctgf": ("scar_fibrosis", "primary dermal fibroblast", "ECM-remodeling morphology + Cell Painting"),
    "mmp1": ("photoaging_scar", "UV-stressed dermal fibroblast", "MMP1 secretion + Cell Painting"),
    "lox": ("scar_matrix", "primary dermal fibroblast", "collagen cross-linking proxy + Cell Painting"),
    "tyr": ("pigmentation", "human melanocyte or B16F10", "melanin content + tyrosinase + Cell Painting"),
    "dct": ("pigmentation", "human melanocyte or B16F10", "melanin content + DCT/TYR pathway imaging"),
    "tyrp1": ("pigmentation", "human melanocyte or B16F10", "melanin content + organelle morphology"),
    "mitf": ("pigmentation", "human melanocyte", "MITF pathway reporter + Cell Painting"),
    "ptgs2": ("acne_inflammation", "keratinocyte or sebocyte", "PGE2/inflammatory morphology + Cell Painting"),
    "srebp1": ("acne_sebum", "sebocyte", "lipid droplet imaging + Cell Painting"),
    "srd5a1": ("alopecia_androgen", "dermal papilla cell", "androgen-response morphology + viability"),
    "srd5a2": ("alopecia_androgen", "dermal papilla cell", "androgen-response morphology + viability"),
    "ar": ("alopecia_androgen", "dermal papilla cell", "AR reporter + Cell Painting"),
    "sirt1": ("photoaging", "UV-stressed keratinocyte/fibroblast", "senescence morphology + Cell Painting"),
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def col(df: pd.DataFrame, names: list[str], default: object = "") -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


def collect_candidates() -> pd.DataFrame:
    frames = []
    for path, source, id_cols in [
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_chromanol", ["analog_id"]),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_chromanol", ["compound"]),
        (OUT / "active_learning_next_candidates.csv", "active_learning", ["candidate_id"]),
        (OUT / "dermal_regulatory_safety_gate.csv", "dermal_gate", ["candidate_id"]),
    ]:
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "candidate_id": col(df, id_cols),
                    "target": col(df, ["target"]),
                    "smiles": col(df, ["smiles"]),
                    "source": source,
                    "score": pd.to_numeric(
                        col(df, ["affinity_probability_binary", "acquisition_score", "topical_followup_score"], 0),
                        errors="coerce",
                    ).fillna(0),
                    "dermal_gate": col(df, ["dermal_gate"], ""),
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["target"] = out["target"].fillna("").astype(str).str.lower()
    out["smiles"] = out["smiles"].fillna("").astype(str)
    out["candidate_id"] = out["candidate_id"].fillna("").astype(str)
    out = out[out["smiles"].ne("")]
    return out.drop_duplicates(subset=["candidate_id", "target", "smiles"])


def classify(row: pd.Series) -> dict[str, object]:
    target = str(row.get("target", "")).lower()
    context, model, assay = TARGET_CONTEXT.get(
        target,
        ("general_skin_toxicology", "HaCaT keratinocyte + fibroblast counterscreen", "baseline Cell Painting + viability"),
    )
    score = float(row.get("score", 0) or 0)
    dermal_gate = str(row.get("dermal_gate", "") or "")
    priority = "medium"
    if context in {"scar_fibrosis", "pigmentation"} and score >= 0.45:
        priority = "high"
    if dermal_gate == "red":
        gate = "hold_safety_first"
        next_action = "resolve dermal safety alert before Cell Painting spend"
    elif priority == "high":
        gate = "priority_cell_painting"
        next_action = "queue CRO/in-house Cell Painting with disease-specific endpoint counter-readout"
    elif dermal_gate == "yellow":
        gate = "phenomics_with_safety_counterscreen"
        next_action = "run Cell Painting only with viability, irritation, and photosafety counterscreen"
    else:
        gate = "reference_signature_lookup"
        next_action = "map to JUMP/CPJUMP-style public morphology signatures before wet-lab spend"
    public_query = f"{row.get('candidate_id','')} {target} Cell Painting JUMP CPJUMP morphology"
    return {
        "candidate_id": row.get("candidate_id", ""),
        "target": target,
        "source": row.get("source", ""),
        "smiles": row.get("smiles", ""),
        "score": round(score, 4),
        "disease_context": context,
        "cell_model": model,
        "phenotype_anchor": assay,
        "phenomics_gate": gate,
        "public_signature_task": public_query,
        "evidence_gap": "no local Cell Painting or disease-cell morphology signature yet",
        "next_action": next_action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    candidates = collect_candidates()
    rows = [classify(row) for _, row in candidates.iterrows()]
    order = {
        "priority_cell_painting": 0,
        "phenomics_with_safety_counterscreen": 1,
        "reference_signature_lookup": 2,
        "hold_safety_first": 3,
    }
    rows.sort(key=lambda r: (order.get(str(r["phenomics_gate"]), 9), -float(r["score"])))

    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")

    counts = {gate: sum(1 for row in rows if row["phenomics_gate"] == gate) for gate in order}
    lines = [
        "# Phenomics Signature Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: docking/MD 후보를 Cell Painting, high-content imaging, disease-cell phenotype 후속으로 연결한다.",
        "",
        "## Priority Rows",
        "",
        "| candidate | target | gate | disease context | cell model | phenotype anchor | next |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows[:35]:
        lines.append(
            f"| {row['candidate_id']} | {row['target']} | {row['phenomics_gate']} | {row['disease_context']} | {row['cell_model']} | {row['phenotype_anchor']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `priority_cell_painting`: 더 큰 GPU 반복보다 CRO/in-house phenotype assay 설계를 우선 고려한다.",
            "- `phenomics_with_safety_counterscreen`: viability, irritation, photosafety counterscreen 없이는 lead claim을 피한다.",
            "- `reference_signature_lookup`: JUMP/CPJUMP/Cell Painting Gallery 유사 signature 확인 전에는 MOA claim을 하지 않는다.",
            "- `hold_safety_first`: 안전성 alert 해결 전에는 phenomics spend를 보류한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
