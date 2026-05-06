"""Integrated paper-tier ranker: combine Boltz-2 affinity + ADMET-AI safety
+ Tanimoto novelty + scaffold clustering → top candidates per disease target.

Inputs:
  - pilot/cpu_meaningful/all_boltz2_affinity_consolidated.csv (1043 rows)
  - pilot/cpu_meaningful/admet_screen_combined.csv (2336 rows × 107 endpoints)
  - pilot/cpu_queue_v5/brics_with_novelty.csv (Tanimoto novelty)

Outputs:
  - pilot/cpu_meaningful/integrated_top_candidates_per_target.csv
  - pilot/cpu_meaningful/scaffold_clusters.csv (Butina, Tanimoto < 0.6)
  - pilot/cpu_meaningful/preprint_integration_summary.csv
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


def fp(smi):
    m = Chem.MolFromSmiles(smi)
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def main():
    print("=" * 72)
    print("Integrated paper-tier ranker")
    print("=" * 72)

    # --- Load data ---
    aff = pd.read_csv(OUT / "all_boltz2_affinity_consolidated.csv")
    admet = pd.read_csv(OUT / "admet_screen_combined.csv")
    novelty = pd.read_csv(ROOT / "pilot/cpu_queue_v5/brics_with_novelty.csv")
    print(f"Boltz-2 affinity rows: {len(aff)}")
    print(f"ADMET-AI rows: {len(admet)} × {len(admet.columns)} cols")
    print(f"BRICS novelty rows: {len(novelty)}")

    # admet smiles is the canonical we passed in; build a lookup
    admet_lookup = admet.set_index("smiles")
    novelty_lookup = novelty.set_index("smiles")

    # --- Map BRICS top100 → SMILES → integrate per target ---
    top100 = pd.read_csv(ROOT / "pilot/cpu_queue_v5/top100_novel_candidates.csv")
    top100["compound_id"] = [f"top{i:03d}" for i in range(len(top100))]

    smi_by_id = dict(zip(top100["compound_id"], top100["smiles"]))

    aff["smiles"] = aff["compound"].map(smi_by_id)
    aff_with_smiles = aff.dropna(subset=["smiles"]).copy()
    print(f"Affinity rows w/ resolvable SMILES: {len(aff_with_smiles)}")

    # Merge ADMET endpoints (logP, hERG, AMES, Skin_Reaction)
    safety_cols = ["logP", "hERG", "AMES", "Skin_Reaction"]
    safety = admet_lookup[safety_cols].reset_index().rename(
        columns={"smiles": "smi"})
    aff_with_smiles = aff_with_smiles.merge(
        safety, left_on="smiles", right_on="smi", how="left").drop(
        columns=["smi"], errors="ignore")

    # Merge novelty
    novelty_cols = ["max_sim", "mean_sim", "combined", "qed", "mw", "logp"]
    nv = novelty_lookup[novelty_cols].reset_index().rename(
        columns={"smiles": "smi"})
    aff_with_smiles = aff_with_smiles.merge(
        nv, left_on="smiles", right_on="smi", how="left").drop(
        columns=["smi"], errors="ignore")

    # --- Integrated paper-tier score ---
    # affinity_pred is pIC50-like (Boltz-2 trained on pKi/pIC50/pKd in [0,10])
    # safety: hERG and AMES are probabilities of toxicity (we want LOW).
    # Skin_Reaction: probability of irritation (we want LOW for topical).
    # novelty: combined = qed - max_sim (already pre-computed, want HIGH).
    aff_with_smiles["safety_score"] = (
        (1 - aff_with_smiles["hERG"].fillna(0.5)) * 0.4
        + (1 - aff_with_smiles["AMES"].fillna(0.5)) * 0.3
        + (1 - aff_with_smiles["Skin_Reaction"].fillna(0.5)) * 0.3
    )
    aff_with_smiles["affinity_score"] = (
        aff_with_smiles["affinity_prob_binary"].fillna(0)
    )
    aff_with_smiles["novelty_score"] = aff_with_smiles["combined"].fillna(0)
    aff_with_smiles["paper_tier_score"] = (
        aff_with_smiles["affinity_score"] * 0.5
        + aff_with_smiles["safety_score"] * 0.3
        + (aff_with_smiles["novelty_score"].clip(0, 1)) * 0.2
    )

    # Top per target
    top_per_target = (aff_with_smiles
        .sort_values("paper_tier_score", ascending=False)
        .groupby("target")
        .head(15)
        .sort_values(["target", "paper_tier_score"], ascending=[True, False]))
    top_per_target.to_csv(OUT / "integrated_top_candidates_per_target.csv",
                          index=False)
    print(f"\n✅ integrated_top_candidates_per_target.csv ({len(top_per_target)} rows)")
    print("\nTop 5 per target by paper-tier score:")
    for tgt, sub in top_per_target.groupby("target"):
        top5 = sub.head(5)
        if len(top5) > 0:
            print(f"\n  [{tgt}] (top 5)")
            for _, r in top5.iterrows():
                print(f"    {r['compound']:15s} aff={r.get('affinity_pred', 0):.3f} "
                      f"prob={r.get('affinity_prob_binary', 0):.3f} "
                      f"safe={r.get('safety_score', 0):.3f} "
                      f"score={r['paper_tier_score']:.3f}")

    # --- Scaffold clustering via Pool(24) ---
    print("\n[Scaffold clustering: Tanimoto Butina threshold 0.4 on novelty BRICS]")
    smi_list = novelty.head(2000)["smiles"].tolist()
    with Pool(24) as p:
        fps = p.map(fp, smi_list)
    valid = [(i, f) for i, f in enumerate(fps) if f]
    print(f"  valid fps: {len(valid)}")

    n = len(valid)
    dists = []
    for i in range(n):
        sims = DataStructs.BulkTanimotoSimilarity(valid[i][1],
                                                   [f for _, f in valid[:i]])
        for s in sims:
            dists.append(1 - s)
    print(f"  pairwise distances: {len(dists)}")

    clusters = Butina.ClusterData(dists, n, 0.6, isDistData=True)
    print(f"  Butina clusters at d=0.6: {len(clusters)}")

    cluster_rows = []
    for cid, members in enumerate(clusters):
        for m_idx in members:
            orig_idx = valid[m_idx][0]
            cluster_rows.append({
                "cluster_id": cid,
                "cluster_size": len(members),
                "smiles": novelty.iloc[orig_idx]["smiles"],
                "is_centroid": (m_idx == members[0]),
            })
    cdf = pd.DataFrame(cluster_rows)
    cdf.to_csv(OUT / "scaffold_clusters.csv", index=False)
    print(f"  ✅ scaffold_clusters.csv ({len(cdf)} mol → {cdf['cluster_id'].nunique()} clusters)")
    print(f"  largest cluster: {cdf['cluster_size'].max()}, mean size: {cdf['cluster_size'].mean():.1f}")

    # --- Preprint integration summary ---
    summary = []
    for tgt in top_per_target["target"].unique():
        sub = top_per_target[top_per_target["target"] == tgt]
        if len(sub) == 0:
            continue
        best = sub.iloc[0]
        summary.append({
            "target": tgt,
            "n_candidates": len(sub),
            "best_compound": best["compound"],
            "best_smiles": best.get("smiles"),
            "best_affinity_pred": best.get("affinity_pred"),
            "best_affinity_prob": best.get("affinity_prob_binary"),
            "best_safety": best.get("safety_score"),
            "best_paper_score": best["paper_tier_score"],
            "mean_paper_score": sub["paper_tier_score"].mean(),
        })
    sdf = pd.DataFrame(summary)
    sdf.to_csv(OUT / "preprint_integration_summary.csv", index=False)
    print(f"\n✅ preprint_integration_summary.csv ({len(sdf)} target rows)")
    print(sdf.to_string())


if __name__ == "__main__":
    sys.exit(main())
