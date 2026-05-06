"""Active learning round 3: XGBoost on combined ChEMBL + NPAtlas xtb data.

Targets:
  (a) gap_eV_mean (mass-independent ranking proxy) on full master corpus
  (b) pIC50 on ChEMBL MMP-1 95-mol subset (held-out validation)

Features: Morgan2048 + 10 RDKit descriptors.

Comparison vs RF baseline (paper #A §3.5).
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

RDLogger.DisableLog("rdApp.*")

ROOT = Path("/home/crazat/genesis_medicine")
NPATLAS_REFINE = ROOT / "pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_432conf.csv"
CHEMBL_REFINE = ROOT / "pilot/cpu_meaningful/xtb_chembl_mmp1_refine_432conf.csv"
CHEMBL_PIC50 = ROOT / "pilot/cpu_queue/chembl_mmp1_extended.csv"
OUT_JSON = ROOT / "pilot/cpu_meaningful/al_v3_xgboost_results.json"


def featurize(smi: str):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
    fp_arr = np.array(fp, dtype=np.float32)
    desc = np.array([
        Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m),
        Descriptors.NumHDonors(m), Descriptors.NumHAcceptors(m),
        Descriptors.NumRotatableBonds(m), Descriptors.NumAromaticRings(m),
        Descriptors.FractionCSP3(m), Descriptors.NumHeteroatoms(m),
        Descriptors.HeavyAtomCount(m),
    ], dtype=np.float32)
    return np.concatenate([fp_arr, desc])


def main():
    try:
        from xgboost import XGBRegressor
    except ImportError:
        print("xgboost not installed; falling back to sklearn GradientBoostingRegressor")
        from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor  # noqa

    # --- Task A: NPAtlas hetero10 corpus, target gap_eV_mean ---
    np_df = pd.read_csv(NPATLAS_REFINE)
    np_ok = np_df[np_df["status"] == "ok"].copy()
    print(f"NPAtlas hetero10 ok: {len(np_ok)} mol")

    feats = []
    targets = []
    for _, r in np_ok.iterrows():
        x = featurize(r["smiles"])
        if x is not None and pd.notna(r["gap_eV_mean"]):
            feats.append(x)
            targets.append(r["gap_eV_mean"])
    X = np.vstack(feats)
    y = np.array(targets, dtype=np.float32)
    print(f"  features: X={X.shape}, y={y.shape}")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    try:
        model_a = XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.05,
                                subsample=0.8, n_jobs=22)
    except TypeError:
        model_a = XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.05,
                                subsample=0.8)
    model_a.fit(X_tr, y_tr)
    p_te = model_a.predict(X_te)
    r2_a = r2_score(y_te, p_te)
    sp_a = spearmanr(y_te, p_te).statistic
    print(f"  Task A (NPAtlas gap_eV_mean): held-out R²={r2_a:.3f}, Spearman ρ={sp_a:.3f}")

    # --- Task B: ChEMBL MMP-1, target pIC50 ---
    cm_pic = pd.read_csv(CHEMBL_PIC50)
    cm_ref = pd.read_csv(CHEMBL_REFINE)
    cm_ref_ok = cm_ref[cm_ref["status"] == "ok"].rename(columns={"idx": "chembl_id"})
    cm_merged = cm_pic.merge(cm_ref_ok, on="chembl_id", how="inner", suffixes=("", "_xtb"))
    print(f"ChEMBL pIC50 + 432-refine merged: {len(cm_merged)} mol")
    if len(cm_merged) < 10:
        print("  too few to train; skipping Task B")
        results = {
            "task_a_npatlas_gap_eV_mean": {
                "n_train": int(len(X_tr)), "n_test": int(len(X_te)),
                "held_out_r2": round(float(r2_a), 4),
                "held_out_spearman": round(float(sp_a), 4),
                "model": "XGBoost",
            },
            "task_b_chembl_pic50": "skipped (insufficient data)",
        }
        OUT_JSON.write_text(json.dumps(results, indent=2))
        print(json.dumps(results, indent=2))
        return

    feats_b = []
    targets_b = []
    for _, r in cm_merged.iterrows():
        x = featurize(r["smiles"])
        if x is not None and pd.notna(r["pIC50"]):
            feats_b.append(x)
            targets_b.append(r["pIC50"])
    X_b = np.vstack(feats_b)
    y_b = np.array(targets_b, dtype=np.float32)
    X_btr, X_bte, y_btr, y_bte = train_test_split(X_b, y_b, test_size=0.3, random_state=42)
    try:
        model_b = XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                                subsample=0.8, n_jobs=22)
    except TypeError:
        model_b = XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8)
    model_b.fit(X_btr, y_btr)
    p_bte = model_b.predict(X_bte)
    r2_b = r2_score(y_bte, p_bte)
    sp_b = spearmanr(y_bte, p_bte).statistic
    print(f"  Task B (ChEMBL pIC50): held-out R²={r2_b:.3f}, Spearman ρ={sp_b:.3f}")

    results = {
        "task_a_npatlas_gap_eV_mean": {
            "n_train": int(len(X_tr)), "n_test": int(len(X_te)),
            "held_out_r2": round(float(r2_a), 4),
            "held_out_spearman": round(float(sp_a), 4),
            "model": "XGBoost (n_estimators=400, max_depth=6)",
        },
        "task_b_chembl_pic50": {
            "n_train": int(len(X_btr)), "n_test": int(len(X_bte)),
            "held_out_r2": round(float(r2_b), 4),
            "held_out_spearman": round(float(sp_b), 4),
            "model": "XGBoost (n_estimators=300, max_depth=4)",
        },
    }
    OUT_JSON.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
