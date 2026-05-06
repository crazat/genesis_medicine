"""ECFP4 + UMAP + DBSCAN chemical space mapping on 2336 ADMET molecules.

Paper-tier output: 2D chemical space figure with cluster annotation.
Multi-core via Pool(24) for fingerprints + n_jobs=-1 for UMAP/DBSCAN.
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


def fp_one(smi):
    from rdkit import Chem, RDLogger
    from rdkit.Chem import AllChem
    RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return None
    return np.array(AllChem.GetMorganFingerprintAsBitVect(m, 2, 1024),
                     dtype=np.uint8)


def main():
    print("=" * 72)
    print("Chemical space mapping (ECFP4 + UMAP + DBSCAN)")
    print("=" * 72)

    df = pd.read_csv(OUT / "admet_screen_combined.csv")
    smiles = df["smiles"].dropna().tolist()
    print(f"SMILES: {len(smiles)}")

    print("\n[1] ECFP4 fingerprints (Pool 24)")
    with Pool(24) as p:
        fps = p.map(fp_one, smiles)
    valid_idx = [i for i, f in enumerate(fps) if f is not None]
    X = np.array([fps[i] for i in valid_idx])
    print(f"  fps: {X.shape}")

    print("\n[2] UMAP 2D")
    try:
        import umap
        reducer = umap.UMAP(n_neighbors=20, min_dist=0.1,
                             metric="jaccard", n_jobs=-1, random_state=42)
        emb = reducer.fit_transform(X)
        print(f"  UMAP embedding: {emb.shape}")
    except ImportError:
        from sklearn.decomposition import PCA
        emb = PCA(n_components=2).fit_transform(X)
        print(f"  PCA fallback: {emb.shape}")

    print("\n[3] DBSCAN clustering")
    from sklearn.cluster import DBSCAN
    cl = DBSCAN(eps=0.5, min_samples=10, n_jobs=-1).fit(emb)
    n_clusters = len(set(cl.labels_)) - (1 if -1 in cl.labels_ else 0)
    n_noise = (cl.labels_ == -1).sum()
    print(f"  DBSCAN: {n_clusters} clusters, {n_noise} noise points")

    # Export embedding
    emb_df = pd.DataFrame({
        "smiles": [smiles[i] for i in valid_idx],
        "source": [df.iloc[i].get("source", "?") for i in valid_idx],
        "umap_x": emb[:, 0],
        "umap_y": emb[:, 1],
        "cluster": cl.labels_,
    })
    emb_df.to_csv(OUT / "chemical_space_umap.csv", index=False)
    print(f"  ✅ chemical_space_umap.csv")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    sources = emb_df["source"].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(sources)))
    for src, c in zip(sources, colors):
        sub = emb_df[emb_df["source"] == src]
        ax.scatter(sub["umap_x"], sub["umap_y"], s=8, c=[c],
                    label=src, alpha=0.6, edgecolors="none")
    ax.set_xlabel("UMAP-1")
    ax.set_ylabel("UMAP-2")
    ax.set_title(f"Chemical space — {len(emb_df)} molecules across "
                 f"{n_clusters} DBSCAN clusters",
                 fontweight="bold")
    ax.legend(loc="upper right", fontsize=10)
    plt.tight_layout()
    plt.savefig(OUT / "figures/06_chemical_space_umap.png", dpi=300)
    plt.close()
    print(f"  ✅ figures/06_chemical_space_umap.png")

    # Distribution by cluster
    print("\n[4] Cluster composition")
    for cl_id in sorted(set(cl.labels_)):
        if cl_id == -1:
            continue
        mask = cl.labels_ == cl_id
        sub = emb_df[mask]
        src_counts = sub["source"].value_counts()
        print(f"  Cluster {cl_id} (n={mask.sum()}): {dict(src_counts)}")


if __name__ == "__main__":
    sys.exit(main())
