"""ChemBERTa embedding → UMAP + KMeans + downstream analysis.
Heavy CPU 24-core via sklearn n_jobs=-1.
"""
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


def main():
    print("=" * 72)
    print("ChemBERTa embedding → UMAP / KMeans (full 2336)")
    print("=" * 72)

    E = np.load(OUT / "chemberta_embeddings.npy")
    df = pd.read_csv(OUT / "admet_screen_combined.csv")
    df = df.dropna(subset=["smiles"]).reset_index(drop=True)
    print(f"Embeddings: {E.shape}")
    print(f"DF rows: {len(df)}")

    if E.shape[0] != len(df):
        # Need to align — use canonical SMILES intersection
        print("WARN: shape mismatch, using min")
        n = min(E.shape[0], len(df))
        E = E[:n]
        df = df.iloc[:n]

    # KMeans cluster (sklearn n_jobs=-1)
    print("\n[1] KMeans clustering")
    from sklearn.cluster import KMeans
    for k in (10, 20, 50, 100):
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(E)
        sizes = pd.Series(km.labels_).value_counts()
        print(f"  k={k:3d}: sizes {sizes.min()}-{sizes.max()}, mean {sizes.mean():.1f}")

    # k=50 final
    km50 = KMeans(n_clusters=50, random_state=42, n_init=10).fit(E)
    df["chemberta_cluster"] = km50.labels_
    df[["smiles", "source", "chemberta_cluster"]].to_csv(
        OUT / "chemberta_kmeans_clusters.csv", index=False)
    print("  ✅ chemberta_kmeans_clusters.csv")

    # UMAP if available
    print("\n[2] UMAP 2D")
    try:
        import umap
        reducer = umap.UMAP(n_neighbors=20, min_dist=0.1, n_jobs=-1,
                             random_state=42)
        U = reducer.fit_transform(E)
        print(f"  UMAP: {U.shape}")
    except Exception:
        from sklearn.manifold import TSNE
        U = TSNE(n_components=2, n_jobs=-1, random_state=42,
                  init="pca", perplexity=30).fit_transform(E)
        print(f"  TSNE fallback: {U.shape}")

    df["chemberta_x"] = U[:, 0]
    df["chemberta_y"] = U[:, 1]
    df[["smiles", "source", "chemberta_cluster",
         "chemberta_x", "chemberta_y"]].to_csv(
        OUT / "chemberta_2d_embedding.csv", index=False)

    # Plot per source
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    ax = axes[0]
    sources = df["source"].unique()
    for src, color in zip(sources, plt.cm.tab10(np.linspace(0, 1, len(sources)))):
        sub = df[df["source"] == src]
        ax.scatter(sub["chemberta_x"], sub["chemberta_y"], s=8, c=[color],
                    label=f"{src} (n={len(sub)})", alpha=0.6, edgecolors="none")
    ax.set_xlabel("ChemBERTa-2D-1")
    ax.set_ylabel("ChemBERTa-2D-2")
    ax.set_title("ChemBERTa-77M → 2D embedding by source", fontweight="bold")
    ax.legend(fontsize=9)

    ax = axes[1]
    scatter = ax.scatter(df["chemberta_x"], df["chemberta_y"],
                          s=8, c=df["chemberta_cluster"],
                          cmap="tab20", alpha=0.7, edgecolors="none")
    ax.set_xlabel("ChemBERTa-2D-1")
    ax.set_ylabel("ChemBERTa-2D-2")
    ax.set_title("KMeans k=50 clusters on 384-dim embedding", fontweight="bold")
    plt.colorbar(scatter, ax=ax, label="Cluster ID")

    plt.tight_layout()
    plt.savefig(FIG / "15_chemberta_2d.png", dpi=300)
    plt.close()
    print("  ✅ 15_chemberta_2d.png")


if __name__ == "__main__":
    sys.exit(main())
