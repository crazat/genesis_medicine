"""Bayesian Active Learning with Gaussian Process — round 4 candidate prediction.

Train on r1 + r2 + r3 affinity data (33 mol with MMP-1 + TGFB1 affinity),
fit GP regression with Morgan fingerprint kernel,
predict expected affinity + uncertainty for 2336 ADMET pool,
output top 100 candidates by Expected Improvement (EI) acquisition function.
"""
from __future__ import annotations

import sys
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from scipy.stats import norm

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def fp(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    arr = np.zeros(2048, dtype=np.float32)
    DataStructs.ConvertToNumpyArray(
        AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048), arr)
    return arr


def build_training_set():
    """Concatenate r1 + r2 + r3 affinity data."""
    rows = []
    # Round 1 (curcumin baseline + embelin)
    for src, smi, mmp1, tgfb1 in [
        ("emb1_baseline", "CCCCCCCCCCCC1=C(O)C(=O)C(O)=C(O)C1=O", 0.412, 0.561),
        ("emb3", "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O", 0.598, 0.703),
        ("egcg", "OC1=CC(O)=C(C[C@@H](OC(=O)C2=CC(O)=C(O)C(O)=C2)C(O)=C3C(=O)C=CC(=O)C3=C1)O", 0.43, 0.39),
    ]:
        rows.append({"compound": src, "smiles": smi,
                       "MMP1": mmp1, "TGFB1": tgfb1,
                       "mean": (mmp1 + tgfb1) / 2})

    # Round 2 (3 mol)
    try:
        r2 = pd.read_csv(ROOT / "pilot/scaffold_hop_round2/round2_affinity.csv")
        r2_ranked = pd.read_csv(ROOT / "pilot/scaffold_hop_round2/ranked.csv")
        for _, r in r2.iterrows():
            cmpd = r["compound"]
            idx = int(cmpd.split("_")[-1]) - 1 if "_" in str(cmpd) else 0
            smi = r2_ranked.iloc[idx]["smiles"] if idx < len(r2_ranked) else ""
            rows.append({"compound": cmpd, "smiles": smi,
                           "MMP1": r["MMP1"], "TGFB1": r["TGFB1"],
                           "mean": r["mean"]})
    except Exception as e:
        print(f"  r2 load fail: {e}")

    # Round 3 (14 mol)
    try:
        r3 = pd.read_csv(ROOT / "pilot/scaffold_hop_round3/round3_affinity_full.csv")
        for _, r in r3.iterrows():
            rows.append({"compound": r["compound"], "smiles": r["smiles"],
                           "MMP1": r["MMP1"], "TGFB1": r["TGFB1"],
                           "mean": r["mean"]})
    except Exception as e:
        print(f"  r3 load fail: {e}")

    df = pd.DataFrame(rows).drop_duplicates("smiles").reset_index(drop=True)
    return df


def main():
    print("=" * 72)
    print("Bayesian Active Learning — round 4 candidate prediction")
    print("=" * 72)

    train = build_training_set()
    print(f"Training set: {len(train)} mol (r1 + r2 + r3)")
    print(f"Mean target: {train['mean'].mean():.3f} ± {train['mean'].std():.3f}")
    print(f"Best so far: {train['mean'].max():.3f}")

    # Featurize
    with Pool(processes=6) as p:
        train_fps = p.map(fp, train["smiles"].tolist())
    valid_idx = [i for i, f in enumerate(train_fps) if f is not None]
    X_train = np.array([train_fps[i] for i in valid_idx])
    y_train = train.iloc[valid_idx]["mean"].values
    print(f"Train shape: {X_train.shape}, target range: {y_train.min():.3f} - {y_train.max():.3f}")

    # Test set: 2336 ADMET pool
    pool = pd.read_csv(OUT / "admet_screen_combined.csv")
    pool = pool.dropna(subset=["smiles"]).reset_index(drop=True)
    pool = pool.drop_duplicates("smiles").reset_index(drop=True)
    print(f"\nTest pool: {len(pool)} mol")

    with Pool(processes=6) as p:
        pool_fps = p.map(fp, pool["smiles"].tolist())
    pool_valid = [i for i, f in enumerate(pool_fps) if f is not None]
    X_pool = np.array([pool_fps[i] for i in pool_valid])
    pool_v = pool.iloc[pool_valid].reset_index(drop=True)
    print(f"Pool valid: {X_pool.shape}")

    # Reduce dim with truncated SVD (2048 → 100)
    print("\nReducing to 100 PCA components...")
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=min(100, X_train.shape[0] - 1), random_state=42)
    X_train_red = svd.fit_transform(X_train)
    X_pool_red = svd.transform(X_pool)
    print(f"Reduced: {X_train_red.shape}, {X_pool_red.shape}")

    # GP regression
    print("\nFitting GP regression (Matern 5/2 kernel)...")
    kernel = ConstantKernel(1.0) * Matern(length_scale=10.0, nu=2.5) + WhiteKernel(0.05)
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2,
                                    alpha=1e-3, random_state=42, normalize_y=True)
    gp.fit(X_train_red, y_train)
    print(f"  GP score (train): {gp.score(X_train_red, y_train):.3f}")
    print(f"  Final kernel: {gp.kernel_}")

    # Predict on pool
    print("\nPredicting on 2336 pool...")
    y_pred, y_std = gp.predict(X_pool_red, return_std=True)
    print(f"  Mean pred: {y_pred.mean():.3f} ± {y_std.mean():.3f}")
    print(f"  Max pred: {y_pred.max():.3f}")
    print(f"  Mean uncertainty: {y_std.mean():.3f}")

    # Expected Improvement acquisition
    f_star = y_train.max()
    z = (y_pred - f_star) / (y_std + 1e-9)
    ei = (y_pred - f_star) * norm.cdf(z) + y_std * norm.pdf(z)
    ei[y_std < 1e-6] = 0  # certain → no improvement
    pool_v["gp_pred"] = y_pred
    pool_v["gp_uncertainty"] = y_std
    pool_v["expected_improvement"] = ei
    pool_v["upper_confidence"] = y_pred + 2 * y_std
    pool_v.sort_values("expected_improvement", ascending=False, inplace=True)

    # Top 100 by EI
    top100 = pool_v.head(100)
    top100.to_csv(OUT / "bayesian_round4_candidates.csv", index=False)
    print(f"\n✅ bayesian_round4_candidates.csv ({len(top100)} mol)")
    print(f"\n[Top 10 EI candidates]")
    for _, r in top100.head(10).iterrows():
        smi = str(r["smiles"])[:40]
        print(f"  EI={r['expected_improvement']:.4f} pred={r['gp_pred']:.3f}±{r['gp_uncertainty']:.3f} "
              f"UCB={r['upper_confidence']:.3f} | {smi}")

    # Save full pool predictions
    pool_v.to_csv(OUT / "bayesian_pool_predictions.csv", index=False)
    print(f"✅ bayesian_pool_predictions.csv ({len(pool_v)} mol)")

    # Summary stats
    summary = {
        "training_mol": int(len(train)),
        "training_best_mean": float(y_train.max()),
        "pool_size": int(len(pool_v)),
        "max_predicted": float(y_pred.max()),
        "max_ei": float(ei.max()),
        "n_candidates_above_training_best": int((y_pred > y_train.max()).sum()),
        "kernel": str(gp.kernel_),
        "method": "GP Matern 5/2 + Morgan fp 2048 → SVD 100",
    }
    import json
    (OUT / "bayesian_active_learning_summary.json").write_text(
        json.dumps(summary, indent=2))
    print(f"\n✅ bayesian_active_learning_summary.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
