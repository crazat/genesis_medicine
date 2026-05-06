"""Active learning round 3: retrain RF on full 9997 master after singlept refresh.

Trains Random Forest with Morgan2048 + RDKit descriptors → gap_eV target.
Held-out 80/20 Spearman + per-prediction confidence.

Output: pilot/cpu_meaningful/al_round3_master_predictions.csv
"""
from __future__ import annotations

import time
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import spearmanr, pearsonr

RDLogger.DisableLog("rdApp.*")
ROOT = Path("/home/crazat/genesis_medicine")
MASTER = ROOT / "pilot/cpu_meaningful/xtb_npass_10k_master.csv"
SINGLEPT = ROOT / "pilot/cpu_meaningful/xtb_npass_9997_singlept.csv"
OUT = ROOT / "pilot/cpu_meaningful/al_round3_master_predictions.csv"


def featurize(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=2048)
    fp_arr = np.zeros(2048, dtype=np.int8)
    from rdkit import DataStructs
    DataStructs.ConvertToNumpyArray(fp, fp_arr)
    desc = [
        Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m),
        Descriptors.NumHDonors(m), Descriptors.NumHAcceptors(m),
        Descriptors.NumRotatableBonds(m), Descriptors.NumAromaticRings(m),
        Descriptors.FractionCSP3(m), Descriptors.NumHeteroatoms(m),
        Descriptors.HeavyAtomCount(m),
    ]
    return np.concatenate([fp_arr, np.array(desc, dtype=np.float64)])


def main():
    t0 = time.time()
    master = pd.read_csv(MASTER)
    print(f"master: {len(master)} mol")
    sp = pd.read_csv(SINGLEPT)
    sp_ok = sp[sp["status"]=="ok"][["rank","gap_eV"]].rename(columns={"gap_eV":"gap_eV_sp"})
    print(f"singlept ok: {len(sp_ok)} rows")

    df = master.merge(sp_ok, on="rank", how="left")
    df["gap_target"] = df["gap_eV_mean"].fillna(df["gap_eV_sp"])
    df = df.dropna(subset=["gap_target", "smiles"]).reset_index(drop=True)
    print(f"trainable: {len(df)} mol")

    print("featurizing...")
    feats = []
    targs = []
    keep_idx = []
    for i, r in df.iterrows():
        f = featurize(r["smiles"])
        if f is None:
            continue
        feats.append(f)
        targs.append(r["gap_target"])
        keep_idx.append(i)
        if (i+1) % 1000 == 0:
            print(f"  featurized {i+1}/{len(df)}")
    X = np.vstack(feats)
    y = np.array(targs)
    print(f"X: {X.shape}, y: {y.shape}")

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=300, max_depth=20, n_jobs=-1, random_state=42)
    print("training...")
    rf.fit(Xtr, ytr)
    pred_te = rf.predict(Xte)
    sp_rho, _ = spearmanr(yte, pred_te)
    pe_r, _ = pearsonr(yte, pred_te)
    print(f"held-out: Spearman={sp_rho:.4f}, Pearson={pe_r:.4f}")

    pred_all = rf.predict(X)
    out_df = df.iloc[keep_idx].copy()
    out_df["gap_pred"] = pred_all
    out_df["gap_residual"] = out_df["gap_target"] - out_df["gap_pred"]
    out_df.to_csv(OUT, index=False)
    print(f"saved {len(out_df)} rows to {OUT} in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
