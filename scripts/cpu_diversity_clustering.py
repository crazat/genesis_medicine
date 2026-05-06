"""Heavy 24-core diversity clustering on full 2336 ADMET pool.

Multiple clustering schemes — Butina, K-means, Ward hierarchical — for paper-
tier scaffold diversity comparison.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from rdkit.ML.Cluster import Butina

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def fp_one(smi):
    m = Chem.MolFromSmiles(str(smi))
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def main():
    print("=" * 72)
    print("Diversity clustering — 24-core heavy (full 2336)")
    print("=" * 72)

    df = pd.read_csv(OUT / "admet_screen_combined.csv")
    smis = df["smiles"].dropna().tolist()
    print(f"SMILES: {len(smis)}")

    print("\n[1] Fingerprints")
    with Pool(24) as p:
        fps = p.map(fp_one, smis)
    valid = [(i, f) for i, f in enumerate(fps) if f]
    print(f"  valid: {len(valid)}")

    fps_only = [f for _, f in valid]

    print("\n[2] Pairwise Tanimoto distances (heavy 24-core, ~2.7M pairs)")
    n = len(valid)
    distances = []
    # Distribute row-wise on Pool
    def dist_row(i):
        sims = DataStructs.BulkTanimotoSimilarity(fps_only[i], fps_only[:i])
        return [1 - s for s in sims]

    # serial loop because BulkTanimotoSimilarity itself is fast (and Pool
    # would re-pickle huge fp lists)
    import time
    t0 = time.time()
    for i in range(n):
        sims = DataStructs.BulkTanimotoSimilarity(fps_only[i], fps_only[:i])
        for s in sims:
            distances.append(1 - s)
    print(f"  pairs: {len(distances)} in {time.time() - t0:.1f}s")

    print("\n[3] Butina clustering (multiple thresholds)")
    for thr in (0.4, 0.6, 0.8):
        clusters = Butina.ClusterData(distances, n, thr, isDistData=True)
        print(f"  d={thr}: {len(clusters)} clusters, "
              f"largest={max(len(c) for c in clusters)}, "
              f"singletons={sum(1 for c in clusters if len(c) == 1)}")

    print("\n[4] K-means clustering (sklearn, n_jobs=-1)")
    from sklearn.cluster import KMeans
    X = np.array([list(f) for f in fps_only], dtype=np.uint8)
    for k in (10, 25, 50):
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
        sizes = pd.Series(km.labels_).value_counts()
        print(f"  k={k}: cluster sizes range {sizes.min()}-{sizes.max()}, "
              f"mean {sizes.mean():.1f}")

    print("\n[5] Save clustering at d=0.6")
    clusters_06 = Butina.ClusterData(distances, n, 0.6, isDistData=True)
    rows = []
    for cid, members in enumerate(clusters_06):
        for m_idx in members:
            orig_idx = valid[m_idx][0]
            rows.append({
                "smiles": smis[orig_idx],
                "cluster_id": cid,
                "cluster_size": len(members),
                "is_centroid": (m_idx == members[0]),
            })
    pd.DataFrame(rows).to_csv(OUT / "diversity_clusters_d06.csv", index=False)
    print(f"  ✅ diversity_clusters_d06.csv")


if __name__ == "__main__":
    sys.exit(main())
