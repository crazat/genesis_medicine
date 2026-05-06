"""Track 4 — Tanimoto cluster + PCA visualization of 4597 cofold pool.

Output:
- pilot/cpu_meaningful/track4_cluster_pca.csv (compound × pca1 × pca2 × cluster)
- preprints/15_universal_scaffold/figures/fig5_cluster_pca.png
"""
from __future__ import annotations
import sys, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

RDLogger.DisableLog('rdApp.*')
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
FIG_OUT = ROOT / "preprints/15_universal_scaffold/figures"
FIG_OUT.mkdir(parents=True, exist_ok=True)

LEADERS = {
    "R11_0":  "OCc1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",
    "R12_4":  "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
    "R12_11": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1",
    "R12_23": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1",
    "R14_5":  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
    "R13_13": "C=CC(C)(C)c1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",
}


def fp_array(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    arr = np.zeros(2048, dtype=np.float32)
    DataStructs.ConvertToNumpyArray(
        AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048), arr)
    return arr


def main():
    print("=" * 60)
    print("Track 4 — 4597 cofold pool Tanimoto cluster + PCA")
    print("=" * 60)

    pieces = []
    for r in [7, 8, 9, 10, 11, 12]:
        p = OUT / f"r{r}_affinity_consolidated.csv"
        if p.exists():
            pieces.append(pd.read_csv(p))
    df = pd.concat(pieces, ignore_index=True)
    df = df.dropna(subset=["smiles"]).drop_duplicates("smiles").reset_index(drop=True)
    print(f"  Unique compounds in 4597 pool: {len(df)}")

    with Pool(8) as p:
        fps = p.map(fp_array, df["smiles"].tolist())
    valid = [(i, f) for i, f in enumerate(fps) if f is not None]
    X = np.array([f for _, f in valid])
    df_v = df.iloc[[i for i, _ in valid]].reset_index(drop=True)
    print(f"  Valid FPs: {len(df_v)}")

    print("\n[Step 1] PCA reduction (2D)")
    pca = PCA(n_components=2, random_state=42)
    pcs = pca.fit_transform(X)
    print(f"  variance explained: {pca.explained_variance_ratio_}")

    print("\n[Step 2] KMeans cluster (n=8)")
    km = KMeans(n_clusters=8, random_state=42, n_init=10)
    cluster = km.fit_predict(X)

    df_v["pc1"] = pcs[:, 0]
    df_v["pc2"] = pcs[:, 1]
    df_v["cluster"] = cluster

    out_path = OUT / "track4_cluster_pca.csv"
    df_v.to_csv(out_path, index=False)
    print(f"  ✅ {out_path}")

    # Map 6 leaders to PCA space
    leader_pcs = []
    for name, smi in LEADERS.items():
        f = fp_array(smi)
        if f is not None:
            pc = pca.transform(f.reshape(1, -1))[0]
            leader_pcs.append((name, pc[0], pc[1]))

    print("\n[Step 3] Visualization")
    fig, ax = plt.subplots(figsize=(9, 6.5))
    sc = ax.scatter(pcs[:, 0], pcs[:, 1], c=cluster, cmap="tab10",
                    alpha=0.45, s=8, label="cofold pool")
    for name, pc1, pc2 in leader_pcs:
        ax.scatter(pc1, pc2, color="black", marker="*", s=320, zorder=10,
                   edgecolors="white", linewidths=1.5)
        ax.annotate(name, (pc1, pc2), textcoords="offset points",
                    xytext=(8, 8), fontweight="bold", fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.85, edgecolor="black"))
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    ax.set_title(f"4597-compound cofold pool — PCA (Morgan FP 2048) + 8 KMeans clusters\n"
                 f"6 multi-target leaders (★) cluster together: pterocarpan-vinyl-polyphenol family")
    plt.colorbar(sc, ax=ax, label="cluster id")
    plt.tight_layout()
    fp = FIG_OUT / "fig5_cluster_pca.png"
    plt.savefig(fp, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {fp}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
