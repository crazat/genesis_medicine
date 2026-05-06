"""Scaffold × Target affinity heatmap on all 1109 Boltz-2 cofolds.
Paper-tier output: which scaffold classes are best per target.
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
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG = OUT / "figures"


def murcko_one(smi):
    try:
        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return None
        sc = MurckoScaffold.GetScaffoldForMol(m)
        return Chem.MolToSmiles(sc)
    except Exception:
        return None


def main():
    df = pd.read_csv(OUT / "full_cofold_ranking.csv")
    df = df.dropna(subset=["smiles", "affinity_prob_binary"]).copy()
    print(f"Cofold rows with SMILES + affinity: {len(df)}")

    print("[1] Murcko scaffolds (Pool 24)")
    with Pool(24) as p:
        df["murcko"] = p.map(murcko_one, df["smiles"].tolist())
    df = df.dropna(subset=["murcko"])
    print(f"  with Murcko: {len(df)}")

    # Top scaffolds (most molecules)
    top_scs = df["murcko"].value_counts().head(20).index.tolist()
    targets_ordered = sorted(df["target"].unique())

    # Affinity matrix
    M = pd.pivot_table(df[df["murcko"].isin(top_scs)],
                        values="affinity_prob_binary",
                        index="murcko", columns="target",
                        aggfunc="mean")
    M = M.reindex(top_scs)

    # Plot
    fig, ax = plt.subplots(figsize=(min(12, 1 + len(targets_ordered) * 0.7), 8))
    im = ax.imshow(M.values, aspect="auto", cmap="RdYlGn",
                    vmin=0.3, vmax=0.9)
    ax.set_xticks(range(M.shape[1]))
    ax.set_xticklabels(M.columns, rotation=45, ha="right")
    ax.set_yticks(range(M.shape[0]))
    ax.set_yticklabels([s[:50] + "..." if len(s) > 50 else s
                          for s in M.index], fontsize=8)
    plt.colorbar(im, ax=ax, label="Mean Boltz-2 affinity probability")
    ax.set_title("Top 20 Murcko scaffolds × Target (mean affinity probability)",
                 fontsize=12, fontweight="bold")

    # Annotate cells
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=7,
                        color="black" if 0.4 < v < 0.7 else "white")

    plt.tight_layout()
    plt.savefig(FIG / "10_scaffold_target_affinity_heatmap.png", dpi=300)
    plt.close()
    print("  ✅ 10_scaffold_target_affinity_heatmap.png")
    M.to_csv(OUT / "scaffold_target_affinity_matrix.csv")
    print(f"  ✅ scaffold_target_affinity_matrix.csv")

    # Best scaffold per target
    print("\n[Best Murcko scaffold per target]")
    for tgt in targets_ordered:
        col = M[tgt].dropna().sort_values(ascending=False)
        if len(col) > 0:
            best_sc = col.index[0]
            score = col.iloc[0]
            sub = df[(df["murcko"] == best_sc) & (df["target"] == tgt)]
            n = len(sub)
            print(f"  {tgt:12s} → {best_sc[:60]} (score={score:.3f}, n={n})")


if __name__ == "__main__":
    sys.exit(main())
