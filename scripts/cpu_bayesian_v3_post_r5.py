"""Bayesian AL v3 — combined R1-R5 phase 2 (LOX+MITF 추가) training.

Tier B 통합 후 첫 BO 재실행. R5 phase 2 (AR/SIRT1/LOX/MITF 100개씩)
data 추가됨. R7 candidates 추출.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.decomposition import TruncatedSVD
from scipy.stats import norm
from multiprocessing import Pool

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
    print("Bayesian v3 — R1-R5 phase 2 + LOX/MITF (post Tier B)")
    print("=" * 72)

    # Try to load consolidated; if not, build from scratch
    consolidated = OUT / "all_boltz2_affinity_consolidated_r5.csv"
    if consolidated.exists():
        cofold = pd.read_csv(consolidated)
        print(f"Pre-R5 cofold rows: {len(cofold)}")
    else:
        cofold = pd.DataFrame()

    # Add R5 phase 2 LOX + MITF (latest)
    new_rows = []
    for tgt in ["lox", "mitf"]:
        out_dir = OUT / f"output_r5_{tgt}/boltz_results_inputs_r5_{tgt}/predictions"
        if not out_dir.exists():
            print(f"  ⏭️  {tgt} predictions missing")
            continue
        for pred_dir in sorted(out_dir.iterdir()):
            if pred_dir.is_dir():
                aff_json = list(pred_dir.glob("affinity_*.json"))
                if aff_json:
                    import json
                    try:
                        d = json.loads(aff_json[0].read_text())
                        new_rows.append({
                            "compound": pred_dir.name,
                            "target": tgt.upper(),
                            "affinity_prob_binary": float(d.get("affinity_probability_binary", 0.5)),
                            "affinity_pred_value": float(d.get("affinity_pred_value", 0.0)),
                        })
                    except Exception:
                        continue
    print(f"R5 phase 2 LOX/MITF rows added: {len(new_rows)}")
    if new_rows:
        cofold = pd.concat([cofold, pd.DataFrame(new_rows)], ignore_index=True)

    # Augment compound→smiles map
    integ = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    smi_map = integ.set_index("compound")["smiles"].to_dict()
    cofold["smiles"] = cofold["compound"].map(smi_map)

    # Per-compound max
    train = cofold.dropna(subset=["smiles", "affinity_prob_binary"])
    train_max = (train.groupby("compound").agg(
        max_aff=("affinity_prob_binary", "max"),
        smi=("smiles", "first")).reset_index())
    train_max = train_max.dropna(subset=["smi"]).drop_duplicates("smi")
    print(f"Training (per-compound max): {len(train_max)}")

    with Pool(processes=12) as p:
        train_fps = p.map(fp, train_max["smi"].tolist())
    valid = [(i, f) for i, f in enumerate(train_fps) if f is not None]
    X_train = np.array([f for _, f in valid])
    y_train = train_max.iloc[[i for i, _ in valid]]["max_aff"].values
    print(f"Train shape: {X_train.shape}, target {y_train.min():.3f}-{y_train.max():.3f}")

    # Test pool: ADMET + R4
    pool = pd.read_csv(OUT / "admet_screen_combined.csv").dropna(subset=["smiles"])
    try:
        r4 = pd.read_csv(OUT / "round4_expanded.csv")
        pool = pd.concat([pool, r4[["smiles"]]], ignore_index=True)
    except Exception:
        pass
    pool = pool.drop_duplicates("smiles").reset_index(drop=True)
    print(f"Test pool: {len(pool)}")

    with Pool(processes=12) as p:
        pool_fps = p.map(fp, pool["smiles"].tolist())
    pv = [(i, f) for i, f in enumerate(pool_fps) if f is not None]
    X_pool = np.array([f for _, f in pv])
    pool_v = pool.iloc[[i for i, _ in pv]].reset_index(drop=True)
    print(f"Pool valid: {X_pool.shape}")

    print("SVD 2048 → 150...")
    svd = TruncatedSVD(n_components=150, random_state=42)
    X_train_red = svd.fit_transform(X_train)
    X_pool_red = svd.transform(X_pool)

    print("GP fit (Matern 5/2)...")
    kernel = ConstantKernel(1.0) * Matern(length_scale=10.0, nu=2.5) + WhiteKernel(0.05)
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2,
                                    alpha=1e-3, random_state=42, normalize_y=True)
    gp.fit(X_train_red, y_train)
    print(f"  GP score: {gp.score(X_train_red, y_train):.3f}")

    y_pred, y_std = gp.predict(X_pool_red, return_std=True)
    f_star = y_train.max()
    z = (y_pred - f_star) / (y_std + 1e-9)
    ei = (y_pred - f_star) * norm.cdf(z) + y_std * norm.pdf(z)
    pool_v["gp_pred"] = y_pred
    pool_v["gp_uncertainty"] = y_std
    pool_v["expected_improvement"] = ei
    pool_v["upper_confidence"] = y_pred + 2 * y_std
    pool_v.sort_values("expected_improvement", ascending=False, inplace=True)

    out_top = OUT / "bayesian_v3_round7_candidates.csv"
    out_full = OUT / "bayesian_v3_pool_predictions.csv"
    pool_v.head(200).to_csv(out_top, index=False)
    pool_v.to_csv(out_full, index=False)
    print(f"\n✅ {out_top} (top 200)")
    print(f"\n[Top 10 EI]")
    for _, r in pool_v.head(10).iterrows():
        smi = str(r["smiles"])[:55]
        print(f"  EI={r['expected_improvement']:.4f} pred={r['gp_pred']:.3f}±{r['gp_uncertainty']:.3f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
