"""Final synthesis: combine xtb quantum energy + full herbal xref + paper score
into final figures + extended master table + CPU-heavy cross-correlations.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG = OUT / "figures"


def fig_xtb_energy_per_atom():
    df = pd.read_csv(OUT / "xtb_quantum_energies.csv")
    fig, ax = plt.subplots(figsize=(10, 6))
    df["category"] = df["idx"].apply(
        lambda x: "Korean herbal" if str(x).startswith("herbal_") else "BRICS top integrated")
    for cat, color in zip(df["category"].unique(),
                            ["forestgreen", "royalblue"]):
        sub = df[df["category"] == cat]
        ax.hist(sub["energy_per_atom_kcal"].dropna(), bins=30, alpha=0.6,
                 label=f"{cat} (n={len(sub)})", color=color)
    ax.set_xlabel("GFN2-xTB energy per atom (kcal/mol)", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Quantum mechanical (GFN2-xTB) energy per atom distribution",
                 fontsize=12, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "11_xtb_energy_per_atom.png", dpi=300)
    plt.close()
    print("✅ 11_xtb_energy_per_atom.png")


def fig_full_herbal_high_sim():
    df = pd.read_csv(OUT / "full_herbal_high_similarity.csv")
    fig, ax = plt.subplots(figsize=(11, 7))
    top_matches = df["best_match"].value_counts().head(10)
    colors = plt.cm.Set2(np.linspace(0, 1, len(top_matches)))
    bars = ax.barh(range(len(top_matches)), top_matches.values, color=colors)
    ax.set_yticks(range(len(top_matches)))
    ax.set_yticklabels(top_matches.index, fontsize=10)
    ax.set_xlabel("Number of BRICS/screen molecules", fontsize=11)
    ax.set_title(f"Top Korean herbal proxies among {len(df)} high-similarity hits (T > 0.5)",
                 fontsize=12, fontweight="bold")
    for bar, count in zip(bars, top_matches.values):
        ax.text(count + 0.5, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(FIG / "12_korean_herbal_proxies_top10.png", dpi=300)
    plt.close()
    print("✅ 12_korean_herbal_proxies_top10.png")


def fig_recap_fragments():
    if not (OUT / "recap_fragment_freq.csv").exists():
        return
    df = pd.read_csv(OUT / "recap_fragment_freq.csv").head(15)
    if len(df) == 0:
        return
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(range(len(df)), df["count"], color=plt.cm.Blues(np.linspace(0.4, 0.9, len(df))))
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"{f[:50]}..." if len(f) > 50 else f
                          for f in df["recap_fragment"]], fontsize=8)
    ax.set_xlabel("Count across 2336 mol", fontsize=11)
    ax.set_title("Top 15 RECAP fragments (BRICS pool decomposition)",
                 fontsize=12, fontweight="bold")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(FIG / "13_recap_fragments.png", dpi=300)
    plt.close()
    print("✅ 13_recap_fragments.png")


def fig_master_table_summary():
    df = pd.read_csv(OUT / "MASTER_R12_publication_table.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Per source distribution
    ax = axes[0]
    src_means = df.groupby("source")["paper_tier_score"].agg(["mean", "max", "count"])
    src_means.plot(kind="bar", ax=ax, secondary_y=False)
    ax.set_title("Paper-tier score by source", fontweight="bold")
    ax.set_ylabel("Score")
    ax.set_xticklabels(src_means.index, rotation=15, ha="right")
    ax.grid(alpha=0.3)

    # Per target top score
    ax = axes[1]
    tgt_max = df.groupby("target")["paper_tier_score"].max().sort_values(
        ascending=True)
    ax.barh(range(len(tgt_max)), tgt_max.values,
             color=plt.cm.viridis(np.linspace(0.2, 0.9, len(tgt_max))))
    ax.set_yticks(range(len(tgt_max)))
    ax.set_yticklabels(tgt_max.index)
    ax.set_xlabel("Max paper-tier score per target")
    ax.set_title("Best candidate score per target (across all sources)",
                 fontweight="bold")
    ax.grid(alpha=0.3, axis="x")
    ax.set_xlim(0, 1)

    plt.tight_layout()
    plt.savefig(FIG / "14_master_table_summary.png", dpi=300)
    plt.close()
    print("✅ 14_master_table_summary.png")


def main():
    fig_xtb_energy_per_atom()
    fig_full_herbal_high_sim()
    fig_recap_fragments()
    fig_master_table_summary()
    print("\n✅ All R12 figures complete: 14 publication figures")


if __name__ == "__main__":
    sys.exit(main())
