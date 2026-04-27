"""Multi-descriptor PCA + DBSCAN clustering on top 200 candidates.

8 descriptors: MW, logP, TPSA, RotB, HBD, HBA, QED, SA.
Output:
  - PCA 2D scatter colored by cluster
  - cluster representatives (medoid per cluster)
  - chemical space coverage analysis
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG_DIR = OUT / "figures_r13"


def main():
    print("=" * 72)
    print("Multi-descriptor PCA + DBSCAN clustering")
    print("=" * 72)

    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    print(f"Druglikeness pool: {len(drug)}")

    feats = ["mw", "logp", "tpsa", "rotbonds", "hbd", "hba", "qed", "sa_score"]
    feats_present = [f for f in feats if f in drug.columns]
    df = drug.dropna(subset=feats_present).reset_index(drop=True)
    print(f"Valid: {len(df)}")

    X = df[feats_present].values
    Xs = StandardScaler().fit_transform(X)

    pca = PCA(n_components=2)
    Xp = pca.fit_transform(Xs)
    print(f"PCA explained var: {pca.explained_variance_ratio_}")

    db = DBSCAN(eps=0.5, min_samples=8).fit(Xp)
    labels = db.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"DBSCAN clusters: {n_clusters} (noise: {(labels == -1).sum()})")

    df["pca1"] = Xp[:, 0]
    df["pca2"] = Xp[:, 1]
    df["cluster"] = labels

    # Cluster medoid (closest to centroid)
    medoids = []
    for cid in range(n_clusters):
        sub = df[df["cluster"] == cid]
        if len(sub) == 0:
            continue
        center = sub[["pca1", "pca2"]].mean()
        sub = sub.copy()
        sub["dist"] = ((sub["pca1"] - center["pca1"]) ** 2
                          + (sub["pca2"] - center["pca2"]) ** 2) ** 0.5
        medoid = sub.sort_values("dist").iloc[0]
        medoids.append({
            "cluster": cid,
            "size": len(sub),
            "medoid_smiles": medoid["smiles"],
            "medoid_qed": medoid["qed"],
            "medoid_sa": medoid["sa_score"],
            "medoid_mw": medoid["mw"],
        })

    medoids_df = pd.DataFrame(medoids).sort_values("size", ascending=False)
    medoids_df.to_csv(OUT / "descriptor_cluster_medoids.csv", index=False)
    print(f"\n✅ descriptor_cluster_medoids.csv ({len(medoids_df)})")

    df.to_csv(OUT / "descriptor_pca_clusters.csv", index=False)
    print(f"✅ descriptor_pca_clusters.csv ({len(df)})")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 7))
    cmap = plt.cm.tab20
    for cid in range(n_clusters):
        sub = df[df["cluster"] == cid]
        ax.scatter(sub["pca1"], sub["pca2"], c=[cmap(cid % 20)],
                    s=30, alpha=0.6, edgecolors="white", linewidths=0.5,
                    label=f"C{cid} n={len(sub)}")
    noise = df[df["cluster"] == -1]
    if len(noise) > 0:
        ax.scatter(noise["pca1"], noise["pca2"], c="lightgray",
                    s=15, alpha=0.4, label=f"noise n={len(noise)}")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=12)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=12)
    ax.set_title(f"Chemical space — 2336 mol, {n_clusters} clusters",
                  fontsize=13, weight="bold")
    if n_clusters < 15:
        ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "chemical_space_pca.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\n✅ figures_r13/chemical_space_pca.png")

    print(f"\n[Top 10 cluster medoids by size]")
    for _, r in medoids_df.head(10).iterrows():
        smi = str(r["medoid_smiles"])[:50]
        print(f"  C{r['cluster']:2d} (n={r['size']:3d}) QED={r['medoid_qed']:.3f} "
              f"SA={r['medoid_sa']:.2f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
