"""Genetic causality and direction-of-effect gate for target claims."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "genetic_causality_direction_gate.csv"
DOC = ROOT / "docs/GENETIC_CAUSALITY_DIRECTION_GATE.md"

DESIRED_DIRECTION = {
    "tgfb1": "inhibit_or_reduce_pathway",
    "ctgf": "inhibit_or_reduce_pathway",
    "lox": "inhibit_or_reduce_pathway",
    "mmp1": "context_dependent_modulate",
    "tyr": "inhibit_for_depigmentation_or_preserve_for_hair_pigment",
    "dct": "context_dependent_pigment_modulate",
    "tyrp1": "context_dependent_pigment_modulate",
    "mc1r": "context_dependent_pigment_modulate",
    "ar": "antagonize_in_acne_or_alopecia_context",
    "ptgs2": "inhibit_in_inflammatory_context",
    "nr3c1": "agonize_or_modulate_with_barrier_safety_caveat",
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
    target_gate = read_csv(OUT / "target_evidence_gate.csv")
    spatial = read_csv(OUT / "skin_spatial_atlas_gate.csv")
    perturb = read_csv(OUT / "perturbation_biology_gate.csv")
    rows: list[dict[str, object]] = []
    if not target_gate.empty:
        for _, row in target_gate.iterrows():
            target = clean(row.get("target")).lower()
            if not target:
                continue
            gate = clean(row.get("gate"))
            modes = clean(row.get("modes"))
            ot_skin = float(row.get("ot_max_skin_score", 0) or 0)
            ot_trans = float(row.get("ot_max_translational_score", 0) or 0)
            ot_count = int(row.get("ot_total_disease_count", 0) or 0)
            sp = spatial[spatial["target"].astype(str).str.lower().eq(target)] if not spatial.empty and "target" in spatial.columns else pd.DataFrame()
            spatial_gate = clean(sp.iloc[0].get("skin_spatial_gate")) if not sp.empty else "missing"
            pt = perturb[perturb["target"].astype(str).str.lower().eq(target)] if not perturb.empty and "target" in perturb.columns else pd.DataFrame()
            perturb_priority = clean(pt.iloc[0].get("perturbation_priority")) if not pt.empty else "missing"
            if target in DESIRED_DIRECTION and gate == "green" and (ot_skin > 0 or ot_trans > 0 or perturb_priority == "high"):
                causality_gate = "direction_plausible"
                action = "use target claim with explicit direction-of-effect caveat"
            elif target in DESIRED_DIRECTION and gate in {"green", "yellow"}:
                causality_gate = "direction_needs_genetic_or_phenotype_support"
                action = "add Open Targets direction/MR/pQTL/eQTL limitation before strong biology claim"
            else:
                causality_gate = "causality_weak_or_unknown"
                action = "keep as exploratory target or negative-control until causal evidence improves"
            rows.append(
                {
                    "target": target,
                    "target_gate": gate,
                    "open_targets_total_disease_count": ot_count,
                    "open_targets_skin_score": ot_skin,
                    "open_targets_translational_score": ot_trans,
                    "observed_or_intended_modes": modes,
                    "desired_direction_of_effect": DESIRED_DIRECTION.get(target, "unknown"),
                    "skin_spatial_gate": spatial_gate,
                    "perturbation_priority": perturb_priority,
                    "genetic_causality_gate": causality_gate,
                    "evidence_to_add": "Open Targets Genetics;fine-mapping;colocalization;pQTL/eQTL;drug-target MR;PheWAS safety traits",
                    "next_action": action,
                }
            )
    rows.sort(key=lambda r: {"direction_plausible": 0, "direction_needs_genetic_or_phenotype_support": 1, "causality_weak_or_unknown": 2}.get(str(r["genetic_causality_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["genetic_causality_gate"] == g) for g in ["direction_plausible", "direction_needs_genetic_or_phenotype_support", "causality_weak_or_unknown"]}
    lines = [
        "# Genetic Causality Direction Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: target evidence를 disease association뿐 아니라 desired direction-of-effect, genetic/MR caveat와 연결한다.",
        "",
        "## Direction Rows",
        "",
        "| target | gate | desired direction | OT skin | OT translational | next |",
        "|---|---|---|---:|---:|---|",
    ]
    for item in rows[:40]:
        lines.append(
            f"| {item['target']} | {item['genetic_causality_gate']} | {item['desired_direction_of_effect']} | {item['open_targets_skin_score']} | {item['open_targets_translational_score']} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `direction_plausible`: target-focused narrative 가능하지만 causal proof가 아니라는 caveat를 유지한다.",
            "- `direction_needs_genetic_or_phenotype_support`: phenotype or genetic direction evidence를 먼저 보강한다.",
            "- `causality_weak_or_unknown`: biology claim을 exploratory로 낮춘다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
