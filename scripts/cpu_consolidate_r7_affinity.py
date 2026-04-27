"""Consolidate R7 affinity results across 14 targets — feed Bayesian v4."""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
TARGETS = ["tgfb1","mmp1","ctgf","ar","mitf","lox","sirt1","tyr","tyrp1","dct",
           "srd5a1","srd5a2","srebp1","ptgs2"]

def main():
    candidates = pd.read_csv(OUT / "bayesian_v3_round7_candidates.csv").head(30)
    rows = []
    for tgt in TARGETS:
        pred_dir = OUT / f"output_r7_{tgt}/boltz_results_inputs_r7_{tgt}/predictions"
        if not pred_dir.exists():
            print(f"  ⏭️  {tgt} predictions missing")
            continue
        for d in sorted(pred_dir.iterdir()):
            if not d.is_dir(): continue
            aff = list(d.glob("affinity_*.json"))
            if not aff: continue
            try:
                data = json.loads(aff[0].read_text())
                idx = int(d.name.split("_")[-1])
                rows.append({
                    "compound": d.name,
                    "target": tgt.upper(),
                    "candidate_idx": idx,
                    "smiles": candidates.iloc[idx]["smiles"] if idx < len(candidates) else None,
                    "affinity_prob_binary": float(data.get("affinity_probability_binary", 0.5)),
                    "affinity_pred_value": float(data.get("affinity_pred_value", 0.0)),
                })
            except Exception as e:
                continue
    df = pd.DataFrame(rows)
    out_csv = OUT / "r7_affinity_consolidated.csv"
    df.to_csv(out_csv, index=False)
    print(f"✅ {out_csv} ({len(df)} rows × {df['target'].nunique()} targets × {df['compound'].nunique()} compounds)")

    # Top 10 by affinity_prob across all targets
    top = df.sort_values("affinity_prob_binary", ascending=False).head(20)
    print(f"\n[Top 20 R7 cofold hits]")
    print(top[["target","candidate_idx","affinity_prob_binary","smiles"]].to_string(index=False))

    # Per-target top-3
    print(f"\n[Per-target top-3]")
    for tgt in df["target"].unique():
        sub = df[df["target"] == tgt].sort_values("affinity_prob_binary", ascending=False).head(3)
        for _, r in sub.iterrows():
            print(f"  {tgt}: cand_{r['candidate_idx']} aff={r['affinity_prob_binary']:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
