"""Target engagement and target-deconvolution assay readiness gate."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "target_engagement_assay_gate.csv"
DOC = ROOT / "docs/TARGET_ENGAGEMENT_ASSAY_GATE.md"

ASSAY_MAP = {
    "tyr": ("enzyme_activity", "biochemical tyrosinase activity;cellular melanin content", "recombinant TYR or melanocyte lysate"),
    "dct": ("cellular_target_context", "melanocyte DCT/TYR/TYRP1 expression;melanin phenotype;CETSA if antibody works", "melanocyte model and DCT antibody"),
    "tyrp1": ("cellular_target_context", "melanosome maturation and TYRP1 expression;CETSA if antibody works", "melanocyte model and TYRP1 antibody"),
    "tgfb1": ("pathway_ligand_context", "TGF-beta pathway reporter;pSMAD2/3;SPR/BLI only if direct ligand binding is plausible", "TGF-beta responsive fibroblast assay"),
    "mmp1": ("enzyme_activity", "MMP1 enzymatic assay;collagen degradation;CETSA/MS", "recombinant MMP1 and fibroblast model"),
    "ctgf": ("secreted_matrix_context", "CTGF ELISA;fibroblast activation panel;target deconvolution if phenotype-first", "scar fibroblast model"),
    "lox": ("enzyme_activity", "LOX activity assay;collagen crosslinking readout", "LOX enzyme assay and matrix model"),
    "ar": ("nuclear_receptor", "androgen receptor reporter;DHT competition;CETSA/nanoBRET if available", "AR reporter cell line"),
    "ptgs2": ("enzyme_activity", "COX-2 enzyme assay;PGE2 release;NSAID positive control", "COX-2 assay and inflammatory keratinocyte/sebocyte model"),
    "nr3c1": ("nuclear_receptor", "glucocorticoid reporter;GRE luciferase;barrier/inflammation phenotype", "NR3C1 reporter and keratinocyte model"),
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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    consensus = read_csv(OUT / "structure_consensus_v2.csv")
    pocket = read_csv(OUT / "pocket_evidence_gate.csv")
    spatial = read_csv(OUT / "skin_spatial_atlas_gate.csv")
    rows: list[dict[str, object]] = []

    if consensus.empty:
        CSV_OUT.write_text("", encoding="utf-8")
    else:
        for _, row in consensus.iterrows():
            target = clean(row.get("target")).lower()
            modality, assays, materials = ASSAY_MAP.get(
                target,
                ("phenotype_deconvolution", "CETSA/TPP-MS or phenotype-first target deconvolution", "disease-relevant skin cell model"),
            )
            pocket_gate = clean(row.get("pocket_gate"))
            if not pocket_gate and not pocket.empty and "target" in pocket.columns:
                sub = pocket[pocket["target"].astype(str).str.lower().eq(target)]
                pocket_gate = clean(sub.iloc[0].get("pocket_class")) if not sub.empty else "missing"
            sp = spatial[spatial["target"].astype(str).str.lower().eq(target)] if not spatial.empty and "target" in spatial.columns else pd.DataFrame()
            spatial_gate = clean(sp.iloc[0].get("skin_spatial_gate")) if not sp.empty else "missing"
            readiness = clean(row.get("claim_readiness"))
            if modality in {"enzyme_activity", "nuclear_receptor"} and readiness in {"claim_ready_in_silico", "claim_with_caveat"}:
                gate = "engagement_assay_ready"
                next_action = "make wet-lab card with biochemical/cellular target engagement endpoint"
            elif spatial_gate == "spatially_anchorable" and readiness in {"claim_with_caveat", "needs_cross_model"}:
                gate = "cellular_engagement_preferred"
                next_action = "prioritize cellular CETSA/reporter/phenotype endpoint over more docking"
            elif pocket_gate in {"hard_or_indirect", "interface_or_biologic"} or modality == "phenotype_deconvolution":
                gate = "deconvolution_first"
                next_action = "treat docking as hypothesis and plan TPP/CETSA-MS or phenotype deconvolution"
            else:
                gate = "assay_materials_review"
                next_action = "check recombinant protein, antibody, reporter, and disease-cell material availability"
            rows.append(
                {
                    "job_id": clean(row.get("job_id")),
                    "target": target,
                    "compound": clean(row.get("compound")),
                    "smiles": clean(row.get("smiles")),
                    "claim_readiness": readiness,
                    "target_engagement_modality": modality,
                    "recommended_assays": assays,
                    "materials_needed": materials,
                    "pocket_gate": pocket_gate or "missing",
                    "skin_spatial_gate": spatial_gate,
                    "target_engagement_gate": gate,
                    "next_action": next_action,
                }
            )

    rows.sort(key=lambda r: {"engagement_assay_ready": 0, "cellular_engagement_preferred": 1, "deconvolution_first": 2, "assay_materials_review": 3}.get(str(r["target_engagement_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    counts = {g: sum(1 for r in rows if r["target_engagement_gate"] == g) for g in ["engagement_assay_ready", "cellular_engagement_preferred", "deconvolution_first", "assay_materials_review"]}
    lines = [
        "# Target Engagement Assay Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: in-silico binding hypothesis를 CETSA/TPP/SPR/reporter/phenotype assay로 넘길 수 있는지 평가한다.",
        "",
        "## Engagement Rows",
        "",
        "| job | target | compound | gate | modality | assays | next |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in rows[:40]:
        lines.append(
            f"| {item['job_id']} | {item['target']} | {item['compound']} | {item['target_engagement_gate']} | {item['target_engagement_modality']} | {item['recommended_assays']} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `engagement_assay_ready`: DMTL/wet-lab card로 승격한다.",
            "- `cellular_engagement_preferred`: 추가 docking보다 reporter/CETSA/phenotype assay 설계를 우선한다.",
            "- `deconvolution_first`: direct binding claim을 피하고 TPP/CETSA-MS 계획을 붙인다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
