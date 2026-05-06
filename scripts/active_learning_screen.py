"""
C1: Active learning surrogate for xtb screening.

Trains an XGBoost regressor on (RDKit fingerprint + descriptors) -> xtb refine
score from existing xtb cohort outputs, then predicts on the unscanned remainder
of the NPAtlas corpus. Iterative loop:
  1. Train on current xtb-refined set (n=k)
  2. Predict on remaining corpus
  3. Pick top-N predicted, run xtb on them (validation)
  4. Add validated to training set
  5. Repeat until predicted-vs-actual Spearman ρ stabilizes

Deliverable: 10x reduction in xtb compute for same screening enrichment.
Paper venue: feeds into #18 active_learning_multifidelity v1.0 update.

Usage:
  python scripts/active_learning_screen.py \\
    --train pilot/cpu_meaningful/xtb_npass_top9000_hetero9_refine_36conf.csv \\
    --corpus data/np_atlas_consolidated.csv \\
    --target-col topical_refine_score \\
    --out pilot/active_learning/round1
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/crazat/genesis_medicine")


def featurize_smiles(smiles_list: list[str]) -> np.ndarray:
    """Generate Morgan fingerprint (2048 bits, radius 2) + RDKit descriptors."""
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors

    feats = []
    for smi in smiles_list:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            feats.append(np.zeros(2048 + 12))
            continue
        fp = np.array(AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048))
        desc = np.array([
            Descriptors.MolWt(m),
            Descriptors.MolLogP(m),
            Descriptors.TPSA(m),
            Descriptors.NumHDonors(m),
            Descriptors.NumHAcceptors(m),
            Descriptors.NumRotatableBonds(m),
            Descriptors.NumAromaticRings(m),
            Descriptors.NumAliphaticRings(m),
            Descriptors.FractionCSP3(m),
            Descriptors.NumHeteroatoms(m),
            Descriptors.MaxPartialCharge(m) or 0.0,
            Descriptors.MinPartialCharge(m) or 0.0,
        ])
        feats.append(np.concatenate([fp, desc]))
    return np.array(feats)


def train_surrogate(X: np.ndarray, y: np.ndarray) -> tuple:
    """Train XGBoost regressor with cross-validation."""
    try:
        from xgboost import XGBRegressor
    except ImportError:
        print("FAIL: xgboost not installed — pip install xgboost")
        return None, None
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import r2_score
    from scipy.stats import spearmanr

    model = XGBRegressor(
        n_estimators=500, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
        n_jobs=4,
    )
    cv = cross_val_score(model, X, y, cv=5, scoring="r2", n_jobs=4)
    model.fit(X, y)
    pred = model.predict(X)
    rho, p = spearmanr(y, pred)
    return model, {"cv_r2_mean": float(cv.mean()), "cv_r2_std": float(cv.std()),
                   "train_spearman": float(rho), "train_r2": float(r2_score(y, pred))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True, help="CSV with smiles + target column (xtb-refined cohort)")
    ap.add_argument("--corpus", help="CSV with full corpus to predict on (e.g. NPAtlas master)")
    ap.add_argument("--target-col", default="topical_refine_score")
    ap.add_argument("--smiles-col", default="smiles")
    ap.add_argument("--out", default="pilot/active_learning/round1")
    ap.add_argument("--top-n", type=int, default=500, help="top-N predictions to validate next round")
    args = ap.parse_args()

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    print(f"loading training data {args.train}")
    df_train = pd.read_csv(args.train if Path(args.train).is_absolute() else str(ROOT / args.train))
    df_train = df_train.dropna(subset=[args.smiles_col, args.target_col])
    print(f"  n_train={len(df_train)}  target range=[{df_train[args.target_col].min():.3f}, {df_train[args.target_col].max():.3f}]")

    t0 = time.time()
    X_train = featurize_smiles(df_train[args.smiles_col].tolist())
    print(f"  featurized {X_train.shape} in {time.time()-t0:.1f}s")

    model, stats = train_surrogate(X_train, df_train[args.target_col].values)
    if model is None:
        return 1
    print(f"  cv_r2={stats['cv_r2_mean']:.3f}±{stats['cv_r2_std']:.3f}  train_ρ={stats['train_spearman']:.3f}")

    # Save model
    import pickle
    with (out / "model.pkl").open("wb") as f:
        pickle.dump(model, f)

    # Predict on corpus if provided
    predictions = None
    if args.corpus:
        corpus_path = args.corpus if Path(args.corpus).is_absolute() else str(ROOT / args.corpus)
        if Path(corpus_path).exists():
            print(f"\npredicting on corpus {corpus_path}")
            df_corpus = pd.read_csv(corpus_path)
            # Filter out training compounds
            train_ids = set(df_train.get("np_id", df_train.index).tolist())
            id_col = "np_id" if "np_id" in df_corpus.columns else df_corpus.columns[0]
            df_unscanned = df_corpus[~df_corpus[id_col].isin(train_ids)]
            print(f"  unscanned corpus: n={len(df_unscanned)}")
            X_corpus = featurize_smiles(df_unscanned[args.smiles_col].tolist())
            preds = model.predict(X_corpus)
            df_unscanned = df_unscanned.copy()
            df_unscanned["al_predicted_score"] = preds
            top_n = df_unscanned.nlargest(args.top_n, "al_predicted_score")
            top_n.to_csv(out / f"predicted_top{args.top_n}.csv", index=False)
            print(f"  saved top-{args.top_n} predictions -> {out}/predicted_top{args.top_n}.csv")
            predictions = {"corpus_size": len(df_unscanned), "top_n": args.top_n}

    summary = {
        "phase": "C1 active learning round",
        "train_csv": args.train,
        "n_train": len(df_train),
        "model_stats": stats,
        "predictions": predictions,
        "wallclock_minutes": round((time.time() - t0) / 60.0, 2),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nDONE summary -> {out}/summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
