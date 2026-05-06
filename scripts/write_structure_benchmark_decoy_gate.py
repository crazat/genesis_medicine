"""Benchmark-style decoy and negative-control gate for structure claims."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
CSV_OUT = OUT / "structure_benchmark_decoy_gate.csv"
DOC = ROOT / "docs/STRUCTURE_BENCHMARK_DECOY_GATE.md"

KNOWN_CONTROLS = {
    "tyr": "kojic_acid_or_arbutin_positive_control",
    "dct": "melanogenesis_reference_compound_and_inactive_decoys",
    "tgfb1": "TGF-beta pathway positive/negative phenotype controls",
    "mmp1": "MMP inhibitor or UV-photoaging control",
    "ptgs2": "celecoxib_or_indomethacin_class_control",
    "ar": "DHT/antiandrogen reporter controls",
    "nr3c1": "dexamethasone reporter control",
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
    route = read_csv(OUT / "route_enumeration_gate.csv")
    safety = read_csv(OUT / "photosafety_sensitization_v2.csv")
    rows: list[dict[str, object]] = []
    if not consensus.empty:
        for _, row in consensus.iterrows():
            target = clean(row.get("target")).lower()
            compound = clean(row.get("compound"))
            readiness = clean(row.get("claim_readiness"))
            score = float(row.get("consensus_v2_score", 0) or 0)
            rsub = route[route["candidate_id"].astype(str).eq(compound)] if not route.empty and "candidate_id" in route.columns else pd.DataFrame()
            route_gate = clean(rsub.iloc[0].get("route_gate")) if not rsub.empty else "missing"
            ssub = safety[safety["candidate_id"].astype(str).eq(compound)] if not safety.empty and "candidate_id" in safety.columns else pd.DataFrame()
            safety_gate = clean(ssub.iloc[0].get("safety_gate_v2")) if not ssub.empty else "missing"
            if readiness == "claim_ready_in_silico":
                gate = "benchmark_decoys_required_before_strong_claim"
                action = "run target-specific decoys, cross-model pose, PLIF, and negative control before stronger wording"
            elif readiness == "claim_with_caveat":
                gate = "benchmark_ready_as_caveat"
                action = "add matched decoy/enrichment plan to methods; keep caveat wording"
            elif readiness == "needs_cross_model":
                gate = "cross_model_first"
                action = "run Chai-1/DiffDock/Vina/PLIF or target-shuffle before lead table"
            else:
                gate = "benchmark_low_priority"
                action = "use as exploratory or negative-control row"
            rows.append(
                {
                    "job_id": clean(row.get("job_id")),
                    "target": target,
                    "compound": compound,
                    "smiles": clean(row.get("smiles")),
                    "claim_readiness": readiness,
                    "consensus_v2_score": round(score, 4),
                    "route_gate": route_gate,
                    "safety_gate_v2": safety_gate,
                    "positive_control_hint": KNOWN_CONTROLS.get(target, "literature ligand or pathway positive control required"),
                    "decoy_strategy": "matched_property_decoys;inactive_same_scaffold;target_shuffle;irrelevant_target;PLIF_Wasserstein_or_ProLIF_overlap",
                    "minimum_benchmark_package": ">=20 decoys or available local analogs;candidate beats decoy median;no severe PoseBusters fail;MD stable or cross-model concordant",
                    "structure_benchmark_gate": gate,
                    "next_action": action,
                }
            )
    rows.sort(key=lambda r: {"benchmark_decoys_required_before_strong_claim": 0, "benchmark_ready_as_caveat": 1, "cross_model_first": 2, "benchmark_low_priority": 3}.get(str(r["structure_benchmark_gate"]), 9))
    if rows:
        with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        CSV_OUT.write_text("", encoding="utf-8")
    counts = {g: sum(1 for r in rows if r["structure_benchmark_gate"] == g) for g in ["benchmark_decoys_required_before_strong_claim", "benchmark_ready_as_caveat", "cross_model_first", "benchmark_low_priority"]}
    lines = [
        "# Structure Benchmark Decoy Gate",
        "",
        f"- timestamp: `{now}`",
        f"- rows: `{len(rows)}`",
        f"- gate_counts: `{counts}`",
        "- purpose: PoseBench-style claim discipline을 local candidate에 적용해 decoy, negative-control, PLIF, cross-model requirement를 명시한다.",
        "",
        "## Benchmark Rows",
        "",
        "| job | target | compound | gate | control | benchmark package | next |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in rows[:45]:
        lines.append(
            f"| {item['job_id']} | {item['target']} | {item['compound']} | {item['structure_benchmark_gate']} | {item['positive_control_hint']} | {item['minimum_benchmark_package']} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Curator Rule",
            "",
            "- `benchmark_decoys_required_before_strong_claim`: strong binding language 전 decoy/cross-model package 필수.",
            "- `benchmark_ready_as_caveat`: caveat 유지 시 논문 methods에 benchmark plan을 포함한다.",
            "- `cross_model_first`: 다음 GPU-free window에서 cross-model/decoy 중 하나를 우선 큐잉한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
