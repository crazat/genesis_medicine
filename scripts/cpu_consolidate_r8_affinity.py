"""Consolidate R8 affinity results — 14 targets × 30 candidates."""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
TARGETS = ["tgfb1","mmp1","ctgf","ar","mitf","lox","sirt1","tyr","tyrp1","dct",
           "srd5a1","srd5a2","srebp1","ptgs2"]


def main():
    candidates = pd.read_csv(OUT / "bayesian_v4_round8_candidates.csv").head(30)
    rows = []
    for tgt in TARGETS:
        pred_dir = OUT / f"output_r8_{tgt}/boltz_results_inputs_r8_{tgt}/predictions"
        if not pred_dir.exists(): continue
        for d in sorted(pred_dir.iterdir()):
            if not d.is_dir(): continue
            aff = list(d.glob("affinity_*.json"))
            if not aff: continue
            try:
                data = json.loads(aff[0].read_text())
                idx = int(d.name.split("_")[-1])
                rows.append({
                    "compound": d.name, "target": tgt.upper(),
                    "candidate_idx": idx,
                    "smiles": candidates.iloc[idx]["smiles"] if idx < len(candidates) else None,
                    "affinity_prob_binary": float(data.get("affinity_probability_binary", 0.5)),
                    "affinity_pred_value": float(data.get("affinity_pred_value", 0.0)),
                })
            except Exception: continue
    df = pd.DataFrame(rows)
    out_csv = OUT / "r8_affinity_consolidated.csv"
    df.to_csv(out_csv, index=False)
    print(f"✅ {out_csv} ({len(df)} rows)")

    # R8 multi-target leader analysis
    pivot = df.pivot_table(values="affinity_prob_binary",
                            index="candidate_idx", columns="target",
                            aggfunc="max").fillna(0)
    leader_count = {}
    for tgt in pivot.columns:
        col = pivot[tgt].sort_values(ascending=False).head(5)
        for cidx in col.index:
            leader_count[cidx] = leader_count.get(cidx, 0) + 1
    print("\n[R8 multi-target leaders]")
    for cidx, n in sorted(leader_count.items(), key=lambda x: -x[1])[:8]:
        if n >= 2:
            print(f"  R8_{cidx}: top-5 in {n}/14 targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
