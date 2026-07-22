#!/usr/bin/env python
"""build_figures_v03.py — figures for paper_A v0.3, each regenerated from a named source file.

The v6 figure set is unusable: figure4's SHAP panel has no generating script or source data (so it can be
neither regenerated nor checked), its companion panel plots a descriptor table the 2026-07-16 audit refuted,
and figure5 illustrates a narrative withdrawn in §6.1. Rather than carry unverifiable art, v0.3 plots only
what its own audited data supports — and the two figures below are the paper's two most distinctive claims,
neither of which v6 had a figure for.

Figure 1 (§4.1) — engine redundancy. The pairwise NNP correlation matrix, showing that the "three-engine"
consensus is really two: MACE-OMol25 and Orb-v3 agree at r=0.9992 (shared OMol25 training), while the quoted
consensus figure (0.914) is the weakest pair, not the strongest.
  Source: pilot/paper_a_v3_three_nnp_unified.csv

Figure 2 (§4.7) — why rank, not product-moment. Spearman vs Pearson for every descriptor against dE_relax,
with the leverage artifact made visible: descriptors at Pearson |r|>0.99 whose rank correlation is ~0.26,
driven by three ligands at dE_relax ~495-600 kcal/mol against a median of 11.65.
  Source: pilot/round28_retroval/paper_a_sar_dataset.csv
"""
import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

GM = "/home/crazat/genesis_medicine"
OUT = f"{GM}/preprints/23_paper_A_v6_mmp1_5nnp_xtb/figures"
NNP = f"{GM}/pilot/paper_a_v3_three_nnp_unified.csv"
SAR = f"{GM}/pilot/round28_retroval/paper_a_sar_dataset.csv"


def figure1():
    df = pd.read_csv(NNP)
    cols = ["e_orb_v2_eV", "e_mace_omol_eV", "e_orb_v3_eV"]
    lab = ["Orb-v2", "MACE-OMol25", "Orb-v3"]
    M = np.ones((3, 3))
    for i, j in itertools.combinations(range(3), 2):
        r, _ = stats.pearsonr(df[cols[i]], df[cols[j]])
        M[i, j] = M[j, i] = r

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4),
                                  gridspec_kw={"width_ratios": [1, 1.25]})
    im = ax.imshow(M, vmin=0.90, vmax=1.0, cmap="RdYlBu_r")
    ax.set_xticks(range(3), lab, rotation=20, ha="right")
    ax.set_yticks(range(3), lab)
    for i in range(3):
        for j in range(3):
            weight = "bold" if (i != j and M[i, j] > 0.99) else "normal"
            ax.text(j, i, f"{M[i,j]:.4f}", ha="center", va="center",
                    fontsize=10, fontweight=weight,
                    color="white" if M[i, j] > 0.97 else "black")
    ax.set_title("A  Pairwise NNP agreement (n=15)", loc="left", fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.046, label="Pearson r")

    # bottom-to-top: weakest (quoted) first, redundant pair last
    pairs = [(0, 2), (0, 1), (1, 2)]
    names = [f"{lab[i]} ↔ {lab[j]}" for i, j in pairs]
    vals = [M[i, j] for i, j in pairs]
    colors = ["#2c7bb6", "#abd9e9", "#d7191c"]
    b = ax2.barh(names, vals, color=colors, height=0.55)
    ax2.set_xlim(0.90, 1.028)          # headroom so value labels sit outside the bars, never clipped
    ax2.set_xlabel("Pearson r")
    ax2.set_title("B  The consensus is quoted at its weakest pair", loc="left", fontsize=11)
    for rect, v in zip(b, vals):
        ax2.text(v + 0.0018, rect.get_y() + rect.get_height() / 2, f"{v:.4f}",
                 va="center", ha="left", fontweight="bold", fontsize=9.5)
    ax2.annotate("quoted as the consensus:\nthe FLOOR, not the ceiling",
                 xy=(0.9095, 0), xytext=(0.938, 0.42), fontsize=8.5, ha="left",
                 arrowprops=dict(arrowstyle="->", lw=1, shrinkA=0, shrinkB=2))
    ax2.annotate("both trained on OMol25 →\nredundancy, not cross-validation",
                 xy=(0.9700, 2), xytext=(0.9265, 1.42), fontsize=8.5, ha="left", color="#8b0000",
                 arrowprops=dict(arrowstyle="->", lw=1, color="#8b0000", shrinkA=0, shrinkB=2))
    ax2.set_axisbelow(True)
    ax2.grid(axis="x", ls=":", lw=0.6, color="grey", alpha=0.5)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/figure1_v03_nnp_redundancy.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return M


def figure2():
    df = pd.read_csv(SAR)
    y = df["dE_relax"]
    drop = {"cid", "ic50_nm", "dE_relax", "smiles"}
    rows = []
    for c in df.columns:
        if c in drop:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        m = x.notna() & y.notna()
        if m.sum() < 100 or x[m].nunique() < 3:
            continue
        rp, _ = stats.pearsonr(x[m], y[m])
        rs, _ = stats.spearmanr(x[m], y[m])
        if np.isfinite(rp) and np.isfinite(rs):
            rows.append((c, rp, rs))
    R = pd.DataFrame(rows, columns=["desc", "pearson", "spearman"])

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6),
                                  gridspec_kw={"width_ratios": [1.15, 1]})
    ax.scatter(R["pearson"], R["spearman"], s=9, alpha=0.35, color="#4575b4", edgecolors="none")
    lim = [-1.05, 1.05]
    ax.plot(lim, lim, ls="--", lw=1, color="grey")
    ax.set_xlim(lim), ax.set_ylim(lim)
    ax.set_xlabel("Pearson r  (with ΔE_relax)")
    ax.set_ylabel("Spearman ρ  (with ΔE_relax)")
    ax.set_title("A  Every descriptor: rank vs product-moment", loc="left", fontsize=11)
    trap = R[(R["pearson"].abs() > 0.98) & (R["spearman"].abs() < 0.4)]
    ax.scatter(trap["pearson"], trap["spearman"], s=42, facecolors="none",
               edgecolors="#d7191c", linewidths=1.4)
    ax.annotate(f"leverage artifact\n|r| > 0.99, ρ ≈ 0.26\n({len(trap)} descriptors:\nDiameter, Radius,\nECIndex, WPath)",
                xy=(0.985, 0.30), xytext=(0.30, -0.60), fontsize=8, color="#d7191c",
                ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color="#d7191c", lw=1.2,
                                connectionstyle="arc3,rad=-0.25", shrinkB=6))
    top = R.reindex(R["spearman"].abs().sort_values(ascending=False).index).head(1)
    tx, ty = float(top["pearson"].iloc[0]), float(top["spearman"].iloc[0])
    ax.scatter([tx], [ty], s=42, facecolors="none", edgecolors="black", linewidths=1.3)
    ax.annotate(f"strongest RANK signal\n({top['desc'].iloc[0]}, ρ=+{ty:.2f})",
                xy=(tx, ty), xytext=(-0.90, 0.80), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=1, connectionstyle="arc3,rad=0.15", shrinkB=6))
    ax.text(-1.0, -0.98, "on the diagonal ⇒ the two statistics agree;\noff it ⇒ the tail is doing the work",
            fontsize=7.5, color="grey", va="bottom")

    s = y.sort_values(ascending=False)
    ax2.scatter(range(len(s)), s.values, s=14, color="#4575b4", alpha=0.7)
    ax2.set_yscale("log")
    ax2.axhline(y.median(), ls="--", lw=1, color="grey")
    ax2.text(len(s) * 0.42, y.median() * 1.18, f"median {y.median():.2f} kcal/mol (IQR {y.quantile(.75)-y.quantile(.25):.2f})",
             fontsize=8.5, color="grey")
    ax2.scatter(range(3), s.values[:3], s=70, facecolors="none", edgecolors="#d7191c", linewidths=1.6)
    ax2.annotate(f"3 ligands at {s.values[2]:.0f}–{s.values[0]:.0f} kcal/mol\ndrive the |r|>0.99 correlations",
                 xy=(1, s.values[1]), xytext=(len(s) * 0.22, s.values[0] * 0.62),
                 fontsize=8.5, color="#d7191c",
                 arrowprops=dict(arrowstyle="->", color="#d7191c", lw=1.2))
    ax2.set_xlabel("ligand (sorted)")
    ax2.set_ylabel("ΔE_relax  (kcal/mol, log scale)")
    ax2.set_title("B  Why: the dependent variable is heavy-tailed", loc="left", fontsize=11)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/figure2_v03_rank_vs_pearson.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return R, len(trap)


if __name__ == "__main__":
    M = figure1()
    print(f"figure1_v03_nnp_redundancy  — Orb-v2↔Orb-v3 {M[0,2]:.4f} (quoted), "
          f"MACE↔Orb-v3 {M[1,2]:.4f} (redundant)")
    R, ntrap = figure2()
    print(f"figure2_v03_rank_vs_pearson — {len(R)} descriptors; {ntrap} leverage-artifact descriptors "
          f"(|Pearson|>0.98 with |Spearman|<0.4)")
