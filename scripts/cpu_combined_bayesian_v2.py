"""Bayesian AL v2 — combined R1+R2+R3+R4+R5 training, predict on full ADMET pool."""
import sys
from pathlib import Path
from multiprocessing import Pool
import numpy as np, pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.decomposition import TruncatedSVD
from scipy.stats import norm

RDLogger.DisableLog('rdApp.*')
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


def main():
    print("=" * 72)
    print("Bayesian AL v2 — combined R1-R5 training (~2077 cofold rows)")
    print("=" * 72)

    cofold = pd.read_csv(OUT / "all_boltz2_affinity_consolidated_r5.csv")
    integ = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    smi_map = integ.set_index("compound")["smiles"].to_dict()
    cofold["smiles"] = cofold["compound"].map(smi_map)

    # Use compounds with smiles + take per-compound MAX affinity across targets
    train = cofold.dropna(subset=["smiles", "affinity_prob_binary"])
    train_max = (train.groupby("compound").agg(
        max_aff=("affinity_prob_binary", "max"),
        smi=("smiles", "first")).reset_index())
    train_max = train_max.dropna(subset=["smi"]).drop_duplicates("smi")
    print(f"Training (per-compound max): {len(train_max)} mol")

    with Pool(processes=12) as p:
        train_fps = p.map(fp, train_max["smi"].tolist())
    valid = [(i, f) for i, f in enumerate(train_fps) if f is not None]
    X_train = np.array([f for _, f in valid])
    y_train = train_max.iloc[[i for i, _ in valid]]["max_aff"].values
    print(f"Train shape: {X_train.shape}, target {y_train.min():.3f}-{y_train.max():.3f}")

    # Test pool: 2336 ADMET + 194 R4 expanded
    pool = pd.read_csv(OUT / "admet_screen_combined.csv").dropna(subset=["smiles"])
    try:
        r4 = pd.read_csv(OUT / "round4_expanded.csv")
        pool = pd.concat([pool, r4[["smiles"]]], ignore_index=True)
    except Exception:
        pass
    pool = pool.drop_duplicates("smiles").reset_index(drop=True)
    print(f"\nTest pool (ADMET + R4): {len(pool)}")

    with Pool(processes=12) as p:
        pool_fps = p.map(fp, pool["smiles"].tolist())
    pv = [(i, f) for i, f in enumerate(pool_fps) if f is not None]
    X_pool = np.array([f for _, f in pv])
    pool_v = pool.iloc[[i for i, _ in pv]].reset_index(drop=True)
    print(f"Pool valid: {X_pool.shape}")

    # SVD reduction
    print("\nSVD reduction 2048 → 150 components...")
    svd = TruncatedSVD(n_components=150, random_state=42)
    X_train_red = svd.fit_transform(X_train)
    X_pool_red = svd.transform(X_pool)

    print("\nFitting GP regression (Matern 5/2)...")
    kernel = ConstantKernel(1.0) * Matern(length_scale=10.0, nu=2.5) + WhiteKernel(0.05)
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2,
                                    alpha=1e-3, random_state=42, normalize_y=True)
    gp.fit(X_train_red, y_train)
    print(f"  GP score (train): {gp.score(X_train_red, y_train):.3f}")

    print("\nPredicting on pool...")
    y_pred, y_std = gp.predict(X_pool_red, return_std=True)
    print(f"  Mean pred: {y_pred.mean():.3f} ± {y_std.mean():.3f}")
    print(f"  Max pred: {y_pred.max():.3f}")

    f_star = y_train.max()
    z = (y_pred - f_star) / (y_std + 1e-9)
    ei = (y_pred - f_star) * norm.cdf(z) + y_std * norm.pdf(z)
    pool_v["gp_pred"] = y_pred
    pool_v["gp_uncertainty"] = y_std
    pool_v["expected_improvement"] = ei
    pool_v["upper_confidence"] = y_pred + 2 * y_std
    pool_v.sort_values("expected_improvement", ascending=False, inplace=True)

    pool_v.head(200).to_csv(OUT / "bayesian_v2_round6_candidates.csv", index=False)
    pool_v.to_csv(OUT / "bayesian_v2_pool_predictions.csv", index=False)
    print(f"\n✅ bayesian_v2_round6_candidates.csv (top 200)")
    print(f"\n[Top 10 EI candidates]")
    for _, r in pool_v.head(10).iterrows():
        smi = str(r["smiles"])[:55]
        print(f"  EI={r['expected_improvement']:.4f} pred={r['gp_pred']:.3f}±{r['gp_uncertainty']:.3f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
