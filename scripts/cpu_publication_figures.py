"""Generate publication-quality figures from R12+R13 outputs.

Figures:
  1. ChEMBL Boltz-2 calibration scatter (already exists, regenerate)
  2. Pareto front 1 vs front 2-10 distribution
  3. Bayesian active learning EI heatmap (top 50)
  4. Selectivity matrix heatmap (50 × 14 targets)
  5. Multi-ranker overlap Venn-style table
  6. Round 4 candidate diversity scatter (logKp vs QED)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG_DIR = OUT / "figures_r13"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def fig_pareto_distribution():
    try:
        df = pd.read_csv(OUT / "pareto_ranking.csv")
    except Exception:
        return False

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ranks = df["pareto_rank"].clip(1, 10)
    counts = ranks.value_counts().sort_index()

    bars = ax.bar(counts.index, counts.values,
                    color=["#06d6a0" if i == 1 else "#3a86ff" if i <= 3
                            else "#8338ec" for i in counts.index],
                    edgecolor="white", linewidth=1.5)
    ax.set_xlabel("Pareto Front Rank", fontsize=12)
    ax.set_ylabel("# molecules", fontsize=12)
    ax.set_title("Pareto Multi-Objective Distribution (9 objectives, "
                  f"n={len(df)} mol)", fontsize=13, weight="bold")
    ax.grid(True, alpha=0.3)
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                 str(val), ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "pareto_distribution.png", dpi=300, bbox_inches="tight")
    plt.close()
    return True


def fig_bayesian_ei():
    try:
        df = pd.read_csv(OUT / "bayesian_round4_candidates.csv")
    except Exception:
        return False
    df = df.head(50)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    ax = axes[0]
    ax.scatter(df["gp_pred"], df["expected_improvement"],
                c=df["gp_uncertainty"], cmap="viridis", s=80,
                edgecolors="white", linewidths=1, alpha=0.8)
    ax.set_xlabel("GP predicted affinity_prob_binary", fontsize=12)
    ax.set_ylabel("Expected Improvement", fontsize=12)
    ax.set_title("Bayesian Active Learning — Top 50 Round 4 Candidates",
                  fontsize=12, weight="bold")
    cbar = plt.colorbar(ax.collections[0], ax=ax)
    cbar.set_label("GP uncertainty (σ)", fontsize=10)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.errorbar(range(len(df)), df["gp_pred"], yerr=df["gp_uncertainty"],
                 fmt="o", color="#3a86ff", ecolor="lightgray",
                 capsize=3, markersize=6, alpha=0.8)
    ax.axhline(y=df["gp_pred"].iloc[0] - df["gp_uncertainty"].iloc[0] * 2,
                color="red", linestyle="--", alpha=0.5,
                label="2σ below top candidate")
    ax.set_xlabel("Rank by Expected Improvement", fontsize=12)
    ax.set_ylabel("GP predicted affinity ± σ", fontsize=12)
    ax.set_title("Predicted affinity with uncertainty", fontsize=12, weight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "bayesian_ei_top50.png", dpi=300, bbox_inches="tight")
    plt.close()
    return True


def fig_selectivity_heatmap():
    try:
        df = pd.read_csv(OUT / "selectivity_matrix.csv")
    except Exception:
        return False

    target_cols = [c for c in df.columns if c not in
                    ("compound", "smiles", "best_target", "best_affinity",
                      "mean_off_target", "selectivity_index", "n_off_target_hits")]

    if not target_cols:
        return False

    sel = df.head(30).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    matrix = sel[target_cols].values

    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn_r",
                    vmin=0, vmax=1)
    ax.set_xticks(range(len(target_cols)))
    ax.set_xticklabels(target_cols, rotation=45, ha="right", fontsize=10)
    ax.set_yticks(range(len(sel)))
    ax.set_yticklabels([f"#{i+1}" for i in range(len(sel))], fontsize=8)
    ax.set_title("Cross-target selectivity matrix (top 30 candidates × all targets)",
                  fontsize=12, weight="bold")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("predicted affinity_prob_binary", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "selectivity_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    return True


def fig_multi_ranker_overlap():
    try:
        df = pd.read_csv(OUT / "paper_tier_lead_panel.csv")
    except Exception:
        return False

    fig, ax = plt.subplots(figsize=(10, 5.5))
    counts = df["n_rankers_in_top"].value_counts().sort_index()
    bars = ax.bar(counts.index, counts.values,
                    color=["#ef476f" if i >= 4 else "#3a86ff" if i >= 2
                            else "#a8dadc" for i in counts.index],
                    edgecolor="white", linewidth=1.5)
    ax.set_xlabel("# of rankers where mol is in top", fontsize=12)
    ax.set_ylabel("# molecules", fontsize=12)
    ax.set_title("Multi-Ranker Lead Panel Overlap (7 rankers, "
                  f"{len(df)} unique mol)", fontsize=13, weight="bold")
    ax.grid(True, alpha=0.3)
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 str(val), ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "multi_ranker_overlap.png", dpi=300, bbox_inches="tight")
    plt.close()
    return True


def fig_round4_diversity():
    try:
        df = pd.read_csv(OUT / "round4_top100.csv")
    except Exception:
        return False

    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(df["logKp"], df["QED"], c=df["MW"], cmap="viridis",
                      s=80, alpha=0.7, edgecolors="white", linewidths=1)
    ax.set_xlabel("logKp (Potts-Guy skin permeation)", fontsize=12)
    ax.set_ylabel("QED (Quantitative Drug-Likeness)", fontsize=12)
    ax.set_title("Round 4 candidates diversity — REINVENT-style fragment design",
                  fontsize=12, weight="bold")
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("MW (Da)", fontsize=10)
    ax.axvline(-3.0, color="gray", linestyle="--", alpha=0.5,
                label="logKp = -3 (skin-permeable threshold)")
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5,
                label="QED = 0.5 (drug-like threshold)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "round4_diversity.png", dpi=300, bbox_inches="tight")
    plt.close()
    return True


def main():
    print("=" * 72)
    print("Publication-quality R13 figures")
    print("=" * 72)

    figs = [
        ("Pareto distribution", fig_pareto_distribution),
        ("Bayesian EI top 50", fig_bayesian_ei),
        ("Selectivity heatmap", fig_selectivity_heatmap),
        ("Multi-ranker overlap", fig_multi_ranker_overlap),
        ("Round 4 diversity", fig_round4_diversity),
    ]

    results = []
    for name, func in figs:
        try:
            ok = func()
            results.append((name, ok))
            print(f"  {'✅' if ok else '⏭️'} {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            results.append((name, False))

    success = sum(1 for _, ok in results if ok)
    print(f"\n{success}/{len(figs)} figures generated → {FIG_DIR}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
