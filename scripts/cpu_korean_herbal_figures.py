"""Korean herbal xref figures + final R12 integration figures."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG = OUT / "figures"


def fig_korean_herbal_scatter():
    df = pd.read_csv(OUT / "korean_herbal_xref.csv")
    fig, ax = plt.subplots(figsize=(10, 7))
    targets = df["target"].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(targets)))
    for tgt, color in zip(targets, colors):
        sub = df[df["target"] == tgt]
        ax.scatter(sub["tanimoto_best"], sub["paper_tier_score"],
                    s=100, c=[color], label=tgt.upper(),
                    edgecolors="k", lw=0.5, alpha=0.8)
        # Annotate top
        for _, r in sub.nlargest(3, "paper_tier_score").iterrows():
            ax.annotate(f"{r['compound']}→{r['best_herbal_match'][:8]}",
                         (r["tanimoto_best"], r["paper_tier_score"]),
                         fontsize=7, ha="left", va="bottom", alpha=0.7)
    ax.axvline(0.4, ls="--", c="gray", alpha=0.5, label="T=0.4 herbal-like")
    ax.set_xlabel("Best Korean herbal Tanimoto similarity", fontsize=11)
    ax.set_ylabel("Paper-tier score", fontsize=11)
    ax.set_title("Top integrated candidates × Korean herbal cross-reference",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "07_korean_herbal_xref.png", dpi=300)
    plt.close()
    print("✅ 07_korean_herbal_xref.png")


def fig_full_ranking_distribution():
    df = pd.read_csv(OUT / "full_cofold_ranking.csv")
    # Distinguish source
    def src(c):
        c = str(c)
        if c.startswith("top"):
            return "BRICS top100"
        elif c.startswith("CHEMBL"):
            return "ChEMBL extended"
        elif "bace1" in c.lower() or "egfr" in c.lower():
            return "infrastructure (BACE1/EGFR)"
        else:
            return "Korean herbal / curated"

    df["source_class"] = df["compound"].astype(str).apply(src)
    fig, ax = plt.subplots(figsize=(10, 6))
    classes = df["source_class"].unique()
    for cls, color in zip(classes, plt.cm.tab10(np.linspace(0, 1, len(classes)))):
        sub = df[df["source_class"] == cls]
        ax.hist(sub["paper_tier_score"].dropna(), bins=40, alpha=0.5,
                 label=f"{cls} (n={len(sub)})", color=color)
    ax.set_xlabel("Paper-tier score", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title(f"Paper-tier score distribution across {len(df)} cofolds (4 source classes)",
                 fontsize=12, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "08_full_ranking_distribution.png", dpi=300)
    plt.close()
    print("✅ 08_full_ranking_distribution.png")


def fig_per_target_top_korean_herbals():
    df = pd.read_csv(OUT / "full_cofold_ranking.csv")
    # Filter Korean herbal direct cofolds (compound is name, not topNNN/CHEMBLXXX)
    df["compound"] = df["compound"].astype(str)
    herbal = df[~df["compound"].str.startswith(("top", "CHEMBL", "bace1", "egfr"))]
    herbal = herbal[herbal["target"] != "unknown"]

    if len(herbal) == 0:
        print("(no herbal direct cofold rows for figure)")
        return

    # Top 15 per target, then plot bar chart by score
    fig, ax = plt.subplots(figsize=(11, 8))
    targets_with_herbal = herbal.groupby("target").size().sort_values(ascending=False)
    targets_with_herbal = targets_with_herbal[targets_with_herbal >= 3].index.tolist()[:6]

    for i, tgt in enumerate(targets_with_herbal):
        sub = herbal[herbal["target"] == tgt].sort_values(
            "paper_tier_score", ascending=False).head(8)
        sub = sub.iloc[::-1]    # for hbarh
        y_pos = np.arange(len(sub)) + i * 10
        bars = ax.barh(y_pos, sub["paper_tier_score"], height=0.8,
                        color=plt.cm.tab10(i), label=tgt.upper())
        for bar, name, score in zip(bars, sub["compound"], sub["paper_tier_score"]):
            ax.text(score + 0.005, bar.get_y() + bar.get_height() / 2,
                    f"{name[:25]} ({score:.3f})",
                    va="center", fontsize=8)
    ax.set_yticks([])
    ax.set_xlabel("Paper-tier score", fontsize=11)
    ax.set_xlim(0, 1)
    ax.set_title("Top Korean herbal compounds per target (direct Boltz-2 cofold)",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(FIG / "09_top_korean_herbals_per_target.png", dpi=300)
    plt.close()
    print("✅ 09_top_korean_herbals_per_target.png")


def main():
    fig_korean_herbal_scatter()
    fig_full_ranking_distribution()
    fig_per_target_top_korean_herbals()


if __name__ == "__main__":
    sys.exit(main())
