"""Design-make-test-learn experiment cards from current queue evidence."""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CARD_DIR = ROOT / "docs/experiment_cards"
CSV_OUT = OUT / "dmtl_experiment_cards.csv"
DOC = ROOT / "docs/DMTL_EXPERIMENT_CARD_FACTORY.md"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip())
    return text.strip("_")[:90] or "card"


def disease_for_target(target: str) -> tuple[str, str, str]:
    mapping = {
        "tgfb1": ("scar/fibrosis", "human dermal fibroblast or scar fibroblast", "collagen I/III, alpha-SMA, CTGF, wound contraction"),
        "mmp1": ("photoaging/scar remodeling", "photoaged dermal fibroblast", "MMP1, COL1A1, ECM remodeling"),
        "dct": ("pigmentation", "human melanocyte or B16F10", "melanin content, tyrosinase activity, DCT/TYR/TYRP1"),
        "tyr": ("pigmentation", "human melanocyte or B16F10", "tyrosinase activity, melanin content"),
        "ptgs2": ("acne/inflammation", "keratinocyte/sebocyte inflammatory model", "PGE2, IL-1beta, IL-8"),
        "ar": ("alopecia/acne", "dermal papilla cell or sebocyte", "androgen-response marker panel"),
    }
    return mapping.get(target.lower(), ("skin biology exploratory", "disease-relevant skin cell", "define target-specific phenotype endpoint"))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    bo = read_csv(OUT / "multi_fidelity_bo_plan.csv")
    consensus = read_csv(OUT / "structure_consensus_v2.csv")
    safety = read_csv(OUT / "photosafety_sensitization_v2.csv")
    route = read_csv(OUT / "route_enumeration_gate.csv")
    cell = read_csv(OUT / "skin_cell_state_evidence_gate.csv")
    if bo.empty:
        CSV_OUT.write_text("", encoding="utf-8")
        DOC.write_text("# DMTL Experiment Card Factory\n\n- rows: `0`\n", encoding="utf-8")
        print(f"Saved {CSV_OUT.relative_to(ROOT)}")
        print(f"Saved {DOC.relative_to(ROOT)}")
        return 0

    rows: list[dict[str, object]] = []
    for _, item in bo.head(30).iterrows():
        cid = str(item.get("candidate_id", ""))
        target = str(item.get("target", "")).lower()
        disease, cell_model, endpoints = disease_for_target(target)
        cs = consensus[
            consensus["compound"].astype(str).eq(cid) & consensus["target"].astype(str).str.lower().eq(target)
        ] if not consensus.empty and {"compound", "target"}.issubset(consensus.columns) else pd.DataFrame()
        safety_sub = safety[
            safety["candidate_id"].astype(str).eq(cid) & safety["target"].astype(str).str.lower().eq(target)
        ] if not safety.empty and {"candidate_id", "target"}.issubset(safety.columns) else pd.DataFrame()
        route_sub = route[
            route["candidate_id"].astype(str).str.contains(re.escape(cid), regex=True, na=False)
        ] if not route.empty and "candidate_id" in route.columns else pd.DataFrame()
        cell_sub = cell[cell["target"].astype(str).str.lower().eq(target)] if not cell.empty and "target" in cell.columns else pd.DataFrame()

        readiness = str(cs.iloc[0].get("claim_readiness", "missing")) if not cs.empty else "missing"
        safety_gate = str(safety_sub.iloc[0].get("safety_gate_v2", "missing")) if not safety_sub.empty else "missing"
        route_gate = str(route_sub.iloc[0].get("route_gate", "missing")) if not route_sub.empty else "missing"
        cell_gate = str(cell_sub.iloc[0].get("skin_cell_state_gate", "missing")) if not cell_sub.empty else "missing"
        score = float(item.get("expected_value", 0) or 0)
        if readiness == "claim_ready_in_silico":
            score += 0.08
        if safety_gate == "green":
            score += 0.05
        if route_gate == "route_ready":
            score += 0.05
        if cell_gate == "cell_state_anchored":
            score += 0.05
        decision = (
            "single_point_wetlab_card"
            if str(item.get("recommended_next_fidelity", "")) == "single-point wet-lab" and safety_gate != "red"
            else "route_or_safety_prerequisite"
            if safety_gate in {"yellow", "red"} or route_gate in {"route_review", "route_hard"}
            else "compute_followup_card"
        )
        card_name = f"{slug(cid)}__{slug(target)}.md"
        rows.append(
            {
                "card_id": f"DMTL_{len(rows)+1:03d}",
                "candidate_id": cid,
                "target": target,
                "smiles": item.get("smiles", ""),
                "disease_axis": disease,
                "cell_model": cell_model,
                "primary_endpoints": endpoints,
                "recommended_next_fidelity": item.get("recommended_next_fidelity", ""),
                "claim_readiness": readiness,
                "safety_gate_v2": safety_gate,
                "route_gate": route_gate,
                "skin_cell_state_gate": cell_gate,
                "card_priority_score": round(score, 4),
                "go_no_go_rule": "go if >=30% phenotype improvement with <=15% cytotoxicity and assay QC passes; no-go if safety alert or no dose-response",
                "card_path": f"docs/experiment_cards/{card_name}",
                "decision_bucket": decision,
            }
        )

    rows.sort(key=lambda r: float(r["card_priority_score"]), reverse=True)
    rows = rows[:16]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["card_id"])
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        path = ROOT / str(row["card_path"])
        lines = [
            f"# {row['card_id']} {row['candidate_id']} x {row['target']}",
            "",
            f"- timestamp: `{now}`",
            f"- candidate_id: `{row['candidate_id']}`",
            f"- target: `{row['target']}`",
            f"- smiles: `{row['smiles']}`",
            f"- disease_axis: `{row['disease_axis']}`",
            f"- cell_model: `{row['cell_model']}`",
            f"- primary_endpoints: `{row['primary_endpoints']}`",
            f"- next_fidelity: `{row['recommended_next_fidelity']}`",
            f"- claim_readiness: `{row['claim_readiness']}`",
            f"- safety_gate_v2: `{row['safety_gate_v2']}`",
            f"- route_gate: `{row['route_gate']}`",
            f"- skin_cell_state_gate: `{row['skin_cell_state_gate']}`",
            f"- go_no_go_rule: `{row['go_no_go_rule']}`",
            "",
            "## Claim Discipline",
            "",
            "- This card supports an in-silico prioritized experiment only.",
            "- No clinical, efficacy, or confirmed-binding claim is made before wet-lab data.",
            "",
        ]
        path.write_text("\n".join(lines), encoding="utf-8")

    counts: dict[str, int] = {}
    for row in rows:
        key = str(row["decision_bucket"])
        counts[key] = counts.get(key, 0) + 1
    lines = [
        "# DMTL Experiment Card Factory",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- bucket_counts: `{counts}`",
        "- purpose: 계산 결과를 바로 CRO/wet-lab이 읽을 수 있는 design-make-test-learn card로 변환한다.",
        "",
        "## Cards",
        "",
        "| card | candidate | target | priority | bucket | path |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['card_id']} | {row['candidate_id']} | {row['target']} | {row['card_priority_score']} | {row['decision_bucket']} | {row['card_path']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `single_point_wetlab_card`: 추가 GPU보다 assay ordering/quote 준비가 우선이다.",
            "- `route_or_safety_prerequisite`: route/safety gate를 먼저 해결한다.",
            "- `compute_followup_card`: GPU/CPU가 비면 cofold/MD/free-energy follow-up 후보로 둔다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
