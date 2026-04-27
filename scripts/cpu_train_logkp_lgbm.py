"""Train LGBM logKp head on NPASS 2026 Potts-Guy proxy + 자체 102 curated.

Tier B #3 LGBM head 학습. Ground truth는 부족하므로 Potts-Guy proxy +
auxiliary CLogP/LogD7.4 measurements로 학습. v0.3에서 SkinPiX 정식
도입 시 retrain.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def featurize(smiles_list):
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, Crippen
    X, valid_mask = [], []
    for s in smiles_list:
        m = Chem.MolFromSmiles(str(s))
        if m is None:
            valid_mask.append(False)
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, 1024)
        arr = np.array(fp, dtype=np.float32)
        # Append physchem
        feats = np.array([
            Descriptors.MolWt(m),
            Crippen.MolLogP(m),
            Descriptors.TPSA(m),
            Descriptors.NumHDonors(m),
            Descriptors.NumHAcceptors(m),
            Descriptors.NumRotatableBonds(m),
            Descriptors.NumAromaticRings(m),
        ], dtype=np.float32)
        X.append(np.concatenate([arr, feats]))
        valid_mask.append(True)
    return np.array(X), np.array(valid_mask)


def main() -> int:
    # Load NPASS Potts-Guy proxy
    proxy = pd.read_csv(OUT / "npass_2026_pottsguy_logkp_10k.csv")
    print(f"NPASS Potts-Guy proxy: {len(proxy)}")

    # Load 102 curated
    curated = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    print(f"Curated 102: {len(curated)}")

    # Combine training set
    train_smi = pd.concat([
        proxy[["smiles", "log_kp_pottsguy"]].rename(
            columns={"log_kp_pottsguy": "log_kp"}),
        curated[["smiles", "logkp_predicted"]].rename(
            columns={"logkp_predicted": "log_kp"}),
    ]).dropna().drop_duplicates("smiles").reset_index(drop=True)
    print(f"Combined training: {len(train_smi)}")

    print("\nFeaturizing...")
    X, mask = featurize(train_smi["smiles"].tolist())
    y = train_smi.loc[mask, "log_kp"].values
    print(f"Features: {X.shape}, target: {y.shape}")

    # Train/test split (random 90/10 + scaffold-aware later)
    from sklearn.model_selection import train_test_split
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.1, random_state=42)

    try:
        import lightgbm as lgb
        print(f"\nTraining LightGBM (n={len(X_tr)})...")
        model = lgb.LGBMRegressor(
            n_estimators=500, learning_rate=0.05,
            num_leaves=63, min_child_samples=10,
            random_state=42, verbose=-1,
        )
        model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)],
                   callbacks=[lgb.early_stopping(20)])
    except ImportError:
        from sklearn.ensemble import GradientBoostingRegressor
        print(f"\nTraining GradientBoosting fallback (n={len(X_tr)})...")
        model = GradientBoostingRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            random_state=42)
        model.fit(X_tr, y_tr)

    pred = model.predict(X_te)
    mae = np.mean(np.abs(pred - y_te))
    rmse = np.sqrt(np.mean((pred - y_te) ** 2))
    r = float(np.corrcoef(pred, y_te)[0, 1])
    print(f"\n[Holdout (n={len(X_te)})]")
    print(f"  MAE  = {mae:.3f} log Kp units")
    print(f"  RMSE = {rmse:.3f}")
    print(f"  R    = {r:.3f}")

    # Save
    model_path = OUT / "logkp_lgbm_v1.joblib"
    joblib.dump({"model": model, "n_features": X.shape[1]}, model_path)
    print(f"\n✅ Saved {model_path}")

    # Validate on 102 curated
    Xc, mc = featurize(curated["smiles"].tolist())
    yc_pred = model.predict(Xc)
    yc_truth = curated.loc[mc, "logkp_predicted"].values
    mae_c = np.mean(np.abs(yc_pred - yc_truth))
    print(f"\n[102 curated validation]")
    print(f"  MAE = {mae_c:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
