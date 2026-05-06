"""Full Tanimoto matrix: all 2336 ADMET molecules × 102 Korean herbals.

Paper-tier output: comprehensive cross-reference identifying ALL BRICS/ChEMBL/
herbal molecules with high similarity to known Korean herbals.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def fp_one(smi):
    m = Chem.MolFromSmiles(str(smi))
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def sim_row(args):
    fp_q, herbal_fps = args
    sims = DataStructs.BulkTanimotoSimilarity(fp_q, herbal_fps)
    return sims


def main():
    print("=" * 72)
    print("Full 2336 × 102 Tanimoto matrix (24-core)")
    print("=" * 72)

    admet = pd.read_csv(OUT / "admet_screen_combined.csv")
    herbal = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")

    admet_smis = admet["smiles"].dropna().tolist()
    herbal_smis = herbal["smiles"].dropna().tolist()
    herbal_names = herbal["name"].tolist()
    herbal_targets = herbal["target_hint"].fillna("").tolist()
    herbal_korean = herbal["source_korean"].fillna("").tolist()

    print(f"ADMET pool: {len(admet_smis)}")
    print(f"Herbal pool: {len(herbal_smis)}")

    print("\n[1] Fingerprints")
    with Pool(24) as p:
        admet_fps = p.map(fp_one, admet_smis)
        herbal_fps = p.map(fp_one, herbal_smis)
    admet_valid = [(i, f) for i, f in enumerate(admet_fps) if f]
    herbal_valid_fps = [f for f in herbal_fps if f]
    print(f"  valid admet fps: {len(admet_valid)}, herbal: {len(herbal_valid_fps)}")

    print("\n[2] Tanimoto matrix")
    args_list = [(fp, herbal_valid_fps) for _, fp in admet_valid]
    with Pool(24) as p:
        rows = p.map(sim_row, args_list)
    M = np.array(rows, dtype=np.float32)
    np.save(OUT / "full_herbal_tanimoto_matrix.npy", M)
    print(f"  matrix: {M.shape}")
    print(f"  mean: {M.mean():.3f}, max: {M.max():.3f}, min: {M.min():.3f}")

    # Per-molecule top-3 herbal matches
    print("\n[3] Per-molecule top-3 herbal matches")
    rows = []
    for k, (idx, _) in enumerate(admet_valid):
        sims = M[k]
        top3_idx = sims.argsort()[-3:][::-1]
        rows.append({
            "smiles": admet_smis[idx],
            "best_match": herbal_names[top3_idx[0]],
            "best_korean": herbal_korean[top3_idx[0]],
            "best_target": herbal_targets[top3_idx[0]],
            "best_T": float(sims[top3_idx[0]]),
            "second_match": herbal_names[top3_idx[1]],
            "second_T": float(sims[top3_idx[1]]),
            "third_match": herbal_names[top3_idx[2]],
            "third_T": float(sims[top3_idx[2]]),
        })
    out_df = pd.DataFrame(rows)
    out_df["source"] = admet["source"].iloc[[i for i, _ in admet_valid]].values
    out_df.to_csv(OUT / "full_herbal_xref.csv", index=False)
    print(f"  ✅ full_herbal_xref.csv ({len(out_df)} rows)")

    # High-similarity hits (T > 0.5)
    high = out_df[out_df["best_T"] > 0.5].sort_values("best_T", ascending=False)
    print(f"\n[4] High-similarity hits (T > 0.5): {len(high)}")
    for _, r in high.head(15).iterrows():
        print(f"  T={r['best_T']:.3f}  [{r['source']:18s}] → "
              f"{r['best_match']:25s} ({r['best_korean']:8s}) "
              f"target={r['best_target'][:30]}")

    high.to_csv(OUT / "full_herbal_high_similarity.csv", index=False)
    print(f"  ✅ full_herbal_high_similarity.csv")


if __name__ == "__main__":
    sys.exit(main())
