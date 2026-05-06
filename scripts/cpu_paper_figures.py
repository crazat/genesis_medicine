"""Publication figures from the new integrated paper-tier data."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful/figures"
OUT.mkdir(parents=True, exist_ok=True)


def fig_paper_score_landscape():
    df = pd.read_csv(ROOT / "pilot/cpu_meaningful/integrated_top_candidates_per_target.csv")
    fig, ax = plt.subplots(figsize=(10, 6))
    targets = df["target"].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(targets)))
    for color, tgt in zip(colors, targets):
        sub = df[df["target"] == tgt].sort_values("paper_tier_score", ascending=False)
        ax.plot(range(len(sub)), sub["paper_tier_score"].values,
                "o-", label=tgt.upper(), color=color, lw=2, ms=7)
    ax.set_xlabel("Rank within target", fontsize=11)
    ax.set_ylabel("Paper-tier score (0.5 affinity + 0.3 safety + 0.2 novelty)", fontsize=11)
    ax.set_title("Integrated paper-tier ranking — top 15 BRICS candidates per target",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "01_paper_score_landscape.png", dpi=300)
    plt.close()
    print(f"  ✅ 01_paper_score_landscape.png")


def fig_pharmacophore_heatmap():
    df = pd.read_csv(ROOT / "pilot/cpu_meaningful/pharmacophore_features_top45.csv")
    feat_cols = [c for c in df.columns if c.startswith("feat_")]
    if not feat_cols:
        print("  no pharmacophore features → skip")
        return
    g = df.groupby("target")[feat_cols].mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(g.values, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(feat_cols)))
    ax.set_xticklabels([c.replace("feat_", "") for c in feat_cols],
                        rotation=45, ha="right")
    ax.set_yticks(range(len(g.index)))
    ax.set_yticklabels([t.upper() for t in g.index])
    ax.set_title("Pharmacophore feature density — mean per target",
                 fontsize=12, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Mean count")
    for i in range(g.shape[0]):
        for j in range(g.shape[1]):
            ax.text(j, i, f"{g.values[i, j]:.1f}",
                    ha="center", va="center",
                    color="white" if g.values[i, j] < g.values.max() / 2 else "black",
                    fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT / "02_pharmacophore_heatmap.png", dpi=300)
    plt.close()
    print(f"  ✅ 02_pharmacophore_heatmap.png")


def fig_safety_vs_affinity():
    df = pd.read_csv(ROOT / "pilot/cpu_meaningful/integrated_top_candidates_per_target.csv")
    fig, ax = plt.subplots(figsize=(8, 6))
    for tgt, color in zip(df["target"].unique(),
                            plt.cm.tab10(np.linspace(0, 1, df["target"].nunique()))):
        sub = df[df["target"] == tgt]
        ax.scatter(sub["affinity_score"], sub["safety_score"],
                    s=80, c=[color], label=tgt.upper(), edgecolors="k", lw=0.5)
    ax.set_xlabel("Boltz-2 affinity probability (binder)", fontsize=11)
    ax.set_ylabel("ADMET-AI safety composite (1 - hERG/AMES/Skin)", fontsize=11)
    ax.set_title("Safety × Affinity Pareto — top 15 per target", fontsize=12, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(OUT / "03_safety_affinity_pareto.png", dpi=300)
    plt.close()
    print(f"  ✅ 03_safety_affinity_pareto.png")


def fig_scaffold_clusters():
    df = pd.read_csv(ROOT / "pilot/cpu_meaningful/scaffold_clusters.csv")
    fig, ax = plt.subplots(figsize=(10, 5))
    sizes = df.groupby("cluster_id").size().sort_values(ascending=False)
    ax.bar(range(len(sizes)), sizes.values,
           color=plt.cm.viridis(np.linspace(0, 1, len(sizes))))
    ax.set_xlabel("Cluster ID (sorted by size)", fontsize=11)
    ax.set_ylabel("Number of molecules", fontsize=11)
    ax.set_title(f"Scaffold clustering — Butina d=0.6, {len(sizes)} clusters from 2000 BRICS variants",
                 fontsize=12, fontweight="bold")
    ax.set_yscale("log")
    ax.grid(alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(OUT / "04_scaffold_clusters.png", dpi=300)
    plt.close()
    print(f"  ✅ 04_scaffold_clusters.png")


def fig_admet_distribution():
    df = pd.read_csv(ROOT / "pilot/cpu_meaningful/admet_topical_focus.csv")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    cols = ["logP", "hERG", "AMES", "Skin_Reaction"]
    for ax, col in zip(axes.flat, cols):
        if col not in df.columns:
            continue
        for src in df["source"].unique():
            sub = df[df["source"] == src]
            ax.hist(sub[col].dropna(), bins=40, alpha=0.5, label=src, density=True)
        ax.set_title(col, fontweight="bold")
        ax.set_xlabel(col)
        ax.set_ylabel("Density")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    plt.suptitle("ADMET-AI v2 distributions — 2336 molecules across 3 sources",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(OUT / "05_admet_distributions.png", dpi=300)
    plt.close()
    print(f"  ✅ 05_admet_distributions.png")


def main():
    print("Generating publication figures from integrated paper-tier data")
    fig_paper_score_landscape()
    fig_pharmacophore_heatmap()
    fig_safety_vs_affinity()
    fig_scaffold_clusters()
    fig_admet_distribution()
    print(f"\nAll figures saved to {OUT}/")


if __name__ == "__main__":
    sys.exit(main())
