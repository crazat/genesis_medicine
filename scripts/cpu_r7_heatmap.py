"""R7 affinity heatmap — 14 targets × 30 candidates."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path(__file__).resolve().parents[1]
mpl.rcParams["figure.dpi"] = 300
mpl.rcParams["savefig.bbox"] = "tight"


def main():
    df = pd.read_csv(ROOT / "pilot/cpu_meaningful/r7_affinity_consolidated.csv")
    print(f"R7 rows: {len(df)}")

    # Pivot: rows=candidate_idx, cols=target
    pivot = df.pivot_table(values="affinity_prob_binary",
                            index="candidate_idx",
                            columns="target",
                            aggfunc="max")
    pivot = pivot.fillna(0).sort_index()
    print(f"Pivot shape: {pivot.shape}")

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(pivot.values, cmap="RdYlBu_r", aspect="auto",
                    vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"R7_{i}" for i in pivot.index], fontsize=7)
    ax.set_xlabel("Target", fontsize=12)
    ax.set_ylabel("R7 candidate", fontsize=12)
    ax.set_title("R7 cofold affinity heatmap (Boltz-2 probability_binary)\n"
                  "14 cached-MSA targets × 30 R7 candidates",
                  fontsize=12)
    cbar = plt.colorbar(im, ax=ax, fraction=0.04)
    cbar.set_label("Affinity probability (binary)")

    # Annotate cells with high affinity (>= 0.6)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if v >= 0.6:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                          fontsize=6, color="black" if v < 0.75 else "white")

    fig_dir = ROOT / "preprints/03_emb3_scar_case_study/figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out = fig_dir / "r7_affinity_heatmap.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"✅ {out}")

    # Per-target leader
    print("\n[Per-target R7 leader]")
    for tgt in pivot.columns:
        col = pivot[tgt].sort_values(ascending=False)
        if len(col) > 0:
            print(f"  {tgt}: cand_{col.index[0]} aff={col.iloc[0]:.3f}")

    # Multi-target leaders (≥3 targets in top-5 each)
    print("\n[Multi-target leaders — # targets where ranked top-5]")
    leader_count = {}
    for tgt in pivot.columns:
        col = pivot[tgt].sort_values(ascending=False).head(5)
        for cand_idx in col.index:
            leader_count[cand_idx] = leader_count.get(cand_idx, 0) + 1
    multi_leaders = sorted(leader_count.items(), key=lambda x: -x[1])[:10]
    for cand_idx, n in multi_leaders:
        if n >= 2:
            print(f"  R7_{cand_idx}: top-5 in {n} targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
