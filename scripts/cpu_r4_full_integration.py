"""R4 full integration — refresh all rankers with 1877 cofold rows."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def main():
    print("=" * 72)
    print("R4 full integration — 1877 cofold rows")
    print("=" * 72)

    cofold = pd.read_csv(OUT / "all_boltz2_affinity_consolidated_r4.csv")
    print(f"Cofold rows: {len(cofold)}")
    print(f"Targets: {cofold['target'].nunique()}")

    # Per target top 5
    print("\n[Per-target top 5 by affinity_prob_binary]")
    rows_top = []
    for tgt, sub in cofold.groupby("target"):
        if len(sub) < 5 or tgt in ("unknown", "tgfb1_pocket2", "tgfb1full"):
            continue
        top = sub.nlargest(5, "affinity_prob_binary")
        for _, r in top.iterrows():
            rows_top.append({
                "target": tgt,
                "compound": r["compound"],
                "affinity_pred": r["affinity_pred"],
                "affinity_prob_binary": r["affinity_prob_binary"],
                "source": r["source"],
            })
        print(f"\n  [{tgt}] (n={len(sub)})")
        for _, r in top.iterrows():
            print(f"    {r['compound']:15s} prob={r['affinity_prob_binary']:.3f}")

    pd.DataFrame(rows_top).to_csv(
        OUT / "r4_per_target_top5.csv", index=False)
    print(f"\n✅ r4_per_target_top5.csv ({len(rows_top)} rows)")

    # Cross-target binders (compound binding ≥ 3 targets > 0.5)
    cross = (cofold[cofold["affinity_prob_binary"] > 0.5]
              .groupby("compound").size().reset_index(name="n_targets_active"))
    cross_active = cross[cross["n_targets_active"] >= 3].sort_values(
        "n_targets_active", ascending=False)
    cross_active.to_csv(OUT / "r4_promiscuous_compounds.csv", index=False)

    print(f"\n[Promiscuous (active ≥3 targets, prob > 0.5): {len(cross_active)}]")
    for _, r in cross_active.head(15).iterrows():
        print(f"  {r['compound']:18s} active in {r['n_targets_active']} targets")

    # Selective (high single, low rest)
    sel_rows = []
    for cmpd, grp in cofold.groupby("compound"):
        if len(grp) < 4:
            continue
        max_p = grp["affinity_prob_binary"].max()
        mean_other = (grp["affinity_prob_binary"].sum()
                       - max_p) / (len(grp) - 1)
        sel_idx = max_p - mean_other
        if max_p > 0.55 and sel_idx > 0.15:
            best = grp.nlargest(1, "affinity_prob_binary").iloc[0]
            sel_rows.append({
                "compound": cmpd,
                "best_target": best["target"],
                "best_prob": float(max_p),
                "mean_other_prob": float(mean_other),
                "selectivity_index": float(sel_idx),
                "n_targets_tested": len(grp),
            })

    sel_df = pd.DataFrame(sel_rows).sort_values(
        "selectivity_index", ascending=False)
    sel_df.to_csv(OUT / "r4_selective_compounds.csv", index=False)

    print(f"\n[Selective (best > 0.55, gap > 0.15): {len(sel_df)}]")
    for _, r in sel_df.head(15).iterrows():
        print(f"  {r['compound']:15s} → {r['best_target']:8s} "
              f"prob={r['best_prob']:.3f} sel_idx={r['selectivity_index']:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
