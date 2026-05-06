"""Skin cell-state evidence gate for target and candidate claims."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "skin_cell_state_evidence_gate.csv"
DOC = ROOT / "docs/SKIN_CELL_STATE_EVIDENCE_GATE.md"

CELL_STATE_MAP = {
    "tgfb1": ("scar", "activated_dermal_fibroblast;myofibroblast", "collagen I/III, alpha-SMA, CTGF, wound contraction"),
    "mmp1": ("scar;photoaging", "dermal_fibroblast;photoaged_fibroblast", "MMP1, COL1A1 rescue, ECM remodeling"),
    "ctgf": ("scar", "activated_dermal_fibroblast", "CTGF, collagen deposition, fibroblast activation"),
    "lox": ("scar;photoaging", "dermal_fibroblast", "collagen crosslinking, matrix stiffness"),
    "dct": ("pigment", "melanocyte;melanosome_state", "melanin content, DCT/TYR/TYRP1 expression"),
    "tyr": ("pigment", "melanocyte;melanosome_state", "tyrosinase activity, melanin content"),
    "tyrp1": ("pigment", "melanocyte;melanosome_state", "melanosome maturation, melanin content"),
    "mc1r": ("pigment", "melanocyte", "cAMP response, pigmentation phenotype"),
    "ar": ("alopecia;acne", "dermal_papilla_cell;sebocyte", "androgen response, hair-cycle marker, sebum marker"),
    "ptgs2": ("acne;photoaging", "keratinocyte;immune_cell;sebocyte", "PGE2, inflammatory cytokine panel"),
    "nr3c1": ("acne;photoaging", "keratinocyte;immune_cell", "glucocorticoid-response and barrier markers"),
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def collect_targets() -> set[str]:
    targets: set[str] = set()
    for path in [
        OUT / "target_evidence_gate.csv",
        OUT / "perturbation_biology_gate.csv",
        OUT / "structure_consensus_v2.csv",
        OUT / "chromanol_generative_optimizer.csv",
    ]:
        df = read_csv(path)
        if not df.empty and "target" in df.columns:
            targets.update(str(x).lower() for x in df["target"].dropna().tolist())
    return {t for t in targets if t and t != "nan"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    target_gate = read_csv(OUT / "target_evidence_gate.csv")
    perturb = read_csv(OUT / "perturbation_biology_gate.csv")
    consensus = read_csv(OUT / "structure_consensus_v2.csv")
    targets = collect_targets()
    rows: list[dict[str, object]] = []

    for target in sorted(targets):
        disease, cells, endpoints = CELL_STATE_MAP.get(target, ("unknown", "skin_context_missing", "define disease-cell phenotype endpoint"))
        tg = target_gate[target_gate["target"].astype(str).str.lower().eq(target)] if not target_gate.empty and "target" in target_gate.columns else pd.DataFrame()
        target_evidence = str(tg.iloc[0].get("gate", "missing")) if not tg.empty else "missing"
        pt = perturb[perturb["target"].astype(str).str.lower().eq(target)] if not perturb.empty and "target" in perturb.columns else pd.DataFrame()
        perturb_priority = str(pt.iloc[0].get("perturbation_priority", "missing")) if not pt.empty else "missing"
        cs = consensus[consensus["target"].astype(str).str.lower().eq(target)] if not consensus.empty and "target" in consensus.columns else pd.DataFrame()
        n_claim_ready = int((cs["claim_readiness"].astype(str) == "claim_ready_in_silico").sum()) if not cs.empty and "claim_readiness" in cs.columns else 0
        n_caveat = int((cs["claim_readiness"].astype(str) == "claim_with_caveat").sum()) if not cs.empty and "claim_readiness" in cs.columns else 0
        has_cell_anchor = target in CELL_STATE_MAP
        if has_cell_anchor and target_evidence == "green" and (n_claim_ready + n_caveat) > 0:
            gate = "cell_state_anchored"
            action = "write disease-cell endpoint table and CRO assay card"
        elif has_cell_anchor and target_evidence in {"green", "yellow"}:
            gate = "phenotype_first"
            action = "prioritize single-cell/spatial/literature anchor before stronger binding claim"
        else:
            gate = "target_claim_limited"
            action = "keep as exploratory or negative-control target until cell-state evidence exists"
        rows.append(
            {
                "target": target,
                "disease_axis": disease,
                "recommended_skin_cell_states": cells,
                "phenotype_endpoints": endpoints,
                "target_evidence_gate": target_evidence,
                "perturbation_priority": perturb_priority,
                "claim_ready_pairs": n_claim_ready,
                "caveat_pairs": n_caveat,
                "skin_cell_state_gate": gate,
                "external_data_to_add": "skin single-cell atlas;spatial transcriptomics;cell painting;disease organoid or skin-on-chip",
                "next_action": action,
            }
        )

    rows.sort(key=lambda r: {"cell_state_anchored": 0, "phenotype_first": 1, "target_claim_limited": 2}.get(str(r["skin_cell_state_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {k: sum(1 for r in rows if r["skin_cell_state_gate"] == k) for k in ["cell_state_anchored", "phenotype_first", "target_claim_limited"]}
    lines = [
        "# Skin Cell-State Evidence Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: target/cofold evidence를 실제 피부 세포 상태와 disease phenotype endpoint에 연결한다.",
        "",
        "## Target Cell-State Map",
        "",
        "| target | gate | disease | cell states | endpoints | next |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['target']} | {row['skin_cell_state_gate']} | {row['disease_axis']} | {row['recommended_skin_cell_states']} | {row['phenotype_endpoints']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `cell_state_anchored`: target-focused 논문과 CRO endpoint table에 바로 반영한다.",
            "- `phenotype_first`: 추가 GPU보다 cell phenotype evidence/assay design을 우선한다.",
            "- `target_claim_limited`: direct target efficacy claim을 피하고 exploratory로 둔다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
