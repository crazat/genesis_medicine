"""Skin spatial-atlas anchoring gate for dermatology target claims."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "skin_spatial_atlas_gate.csv"
DOC = ROOT / "docs/SKIN_SPATIAL_ATLAS_GATE.md"

SPATIAL_MAP = {
    "tgfb1": ("scar;photoaging", "reticular_dermis;perivascular_stroma", "activated_fibroblast;myofibroblast", "scar biopsy or fibroblast-rich reconstructed skin"),
    "ctgf": ("scar", "reticular_dermis;wound_edge", "activated_fibroblast", "scar fibroblast or collagen gel contraction"),
    "lox": ("scar;photoaging", "reticular_dermis;ECM_stroma", "dermal_fibroblast", "matrix stiffness/collagen crosslinking assay"),
    "mmp1": ("photoaging;scar", "papillary_dermis;photoexposed_skin", "photoaged_fibroblast", "UV-aged fibroblast or dermal equivalent"),
    "dct": ("pigment", "melanocyte_unit;hair_follicle_pigment_unit", "melanocyte;melanosome_state", "melanocyte melanin and DCT/TYR/TYRP1 panel"),
    "tyr": ("pigment", "melanocyte_unit;hair_follicle_pigment_unit", "melanocyte;melanosome_state", "tyrosinase activity and melanin content"),
    "tyrp1": ("pigment", "melanocyte_unit;hair_follicle_pigment_unit", "melanocyte;melanosome_state", "melanosome maturation panel"),
    "mc1r": ("pigment", "melanocyte_unit", "melanocyte", "cAMP/pigment response assay"),
    "ar": ("alopecia;acne", "hair_follicle;sebaceous_gland", "dermal_papilla_cell;sebocyte", "androgen reporter in DPC/sebocyte context"),
    "ptgs2": ("acne;photoaging", "epidermis;sebaceous_unit;immune_niche", "keratinocyte;sebocyte;immune_cell", "PGE2/cytokine panel"),
    "nr3c1": ("acne;photoaging", "epidermis;immune_niche", "keratinocyte;immune_cell", "glucocorticoid response and barrier marker panel"),
}


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


def collect_targets() -> set[str]:
    targets: set[str] = set()
    for path in [
        OUT / "target_evidence_gate.csv",
        OUT / "skin_cell_state_evidence_gate.csv",
        OUT / "structure_consensus_v2.csv",
        OUT / "perturbation_biology_gate.csv",
    ]:
        df = read_csv(path)
        if not df.empty and "target" in df.columns:
            targets.update(str(x).lower() for x in df["target"].dropna().tolist())
    return {t for t in targets if t and t != "nan"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    target_gate = read_csv(OUT / "target_evidence_gate.csv")
    cell_gate = read_csv(OUT / "skin_cell_state_evidence_gate.csv")
    consensus = read_csv(OUT / "structure_consensus_v2.csv")
    rows: list[dict[str, object]] = []

    for target in sorted(collect_targets()):
        disease, niche, cells, assay = SPATIAL_MAP.get(
            target,
            ("unknown", "atlas_context_missing", "skin_cell_context_missing", "define anatomic site and disease-cell model"),
        )
        tg = target_gate[target_gate["target"].astype(str).str.lower().eq(target)] if not target_gate.empty and "target" in target_gate.columns else pd.DataFrame()
        target_status = clean(tg.iloc[0].get("gate")) if not tg.empty else "missing"
        cg = cell_gate[cell_gate["target"].astype(str).str.lower().eq(target)] if not cell_gate.empty and "target" in cell_gate.columns else pd.DataFrame()
        cell_status = clean(cg.iloc[0].get("skin_cell_state_gate")) if not cg.empty else "missing"
        cs = consensus[consensus["target"].astype(str).str.lower().eq(target)] if not consensus.empty and "target" in consensus.columns else pd.DataFrame()
        caveat_pairs = int((cs["claim_readiness"].astype(str) == "claim_with_caveat").sum()) if not cs.empty and "claim_readiness" in cs.columns else 0
        ready_pairs = int((cs["claim_readiness"].astype(str) == "claim_ready_in_silico").sum()) if not cs.empty and "claim_readiness" in cs.columns else 0
        if target in SPATIAL_MAP and target_status == "green" and cell_status == "cell_state_anchored":
            gate = "spatially_anchorable"
            action = "use site/cell/niche table in target-focused manuscript and CRO card"
        elif target in SPATIAL_MAP:
            gate = "atlas_review"
            action = "add human skin atlas or disease-site literature before strong target claim"
        else:
            gate = "spatial_context_missing"
            action = "keep exploratory until target is mapped to skin anatomic niche"
        rows.append(
            {
                "target": target,
                "disease_axis": disease,
                "spatial_niche": niche,
                "cell_context": cells,
                "assay_model_hint": assay,
                "target_evidence_gate": target_status,
                "skin_cell_state_gate": cell_status,
                "claim_ready_pairs": ready_pairs,
                "caveat_pairs": caveat_pairs,
                "skin_spatial_gate": gate,
                "atlas_source_to_check": "Human skin spatial atlas;prenatal skin atlas;disease spatial transcriptomics;skin organoid/skin-on-chip literature",
                "next_action": action,
            }
        )

    rows.sort(key=lambda r: {"spatially_anchorable": 0, "atlas_review": 1, "spatial_context_missing": 2}.get(str(r["skin_spatial_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["skin_spatial_gate"] == g) for g in ["spatially_anchorable", "atlas_review", "spatial_context_missing"]}
    lines = [
        "# Skin Spatial Atlas Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: 피부 target claim을 세포 상태뿐 아니라 anatomic site, niche, reconstructed model로 연결한다.",
        "",
        "## Spatial Anchors",
        "",
        "| target | gate | disease | niche | cells | assay model | next |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['target']} | {row['skin_spatial_gate']} | {row['disease_axis']} | {row['spatial_niche']} | {row['cell_context']} | {row['assay_model_hint']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `spatially_anchorable`: target-focused paper에 skin site/cell/niche figure 또는 table을 넣는다.",
            "- `atlas_review`: 추가 docking보다 atlas/literature anchor 보강이 우선이다.",
            "- `spatial_context_missing`: direct dermatology target claim을 제한한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
