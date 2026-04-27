"""Cross-Tanimoto matrix: NPASS 9,997 × R7 candidates (200) — find natural-product
analogs of our top R7 hits.
"""
from __future__ import annotations
import sys
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def fp(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)


def main():
    npass = pd.read_csv(OUT / "npass_2026_pottsguy_logkp_10k.csv")
    r7 = pd.read_csv(OUT / "bayesian_v3_round7_candidates.csv").head(200)
    print(f"NPASS: {len(npass)}, R7: {len(r7)}")

    print("Featurizing NPASS...")
    with Pool(processes=12) as p:
        npass_fps = p.map(fp, npass["smiles"].tolist())
    npass_valid = [(i, f) for i, f in enumerate(npass_fps) if f is not None]
    print(f"  NPASS valid: {len(npass_valid)}")

    print("Featurizing R7...")
    with Pool(processes=12) as p:
        r7_fps = p.map(fp, r7["smiles"].tolist())
    r7_valid = [(i, f) for i, f in enumerate(r7_fps) if f is not None]
    print(f"  R7 valid: {len(r7_valid)}")

    print("\nComputing cross-Tanimoto...")
    rows = []
    npass_fps_only = [f for _, f in npass_valid]
    for ri, rfp in r7_valid:
        sims = DataStructs.BulkTanimotoSimilarity(rfp, npass_fps_only)
        order = np.argsort(sims)[::-1]
        top = order[:5]
        for rank, idx in enumerate(top, start=1):
            ni = npass_valid[idx][0]
            rows.append({
                "r7_idx": ri,
                "r7_smiles": r7.iloc[ri]["smiles"],
                "rank": rank,
                "tanimoto": float(sims[idx]),
                "npass_id": npass.iloc[ni]["np_id"],
                "npass_smiles": npass.iloc[ni]["smiles"],
                "npass_logkp": npass.iloc[ni]["log_kp_pottsguy"],
                "npass_logp": npass.iloc[ni]["logp"],
                "npass_mw": npass.iloc[ni]["mw"],
            })

    df = pd.DataFrame(rows)
    out_csv = OUT / "tanimoto_npass_vs_r7_top5.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n✅ {out_csv} ({len(df)} rows)")

    top1 = df[df["rank"] == 1].sort_values("tanimoto", ascending=False).head(15)
    print(f"\n[Top 15 R7 candidates with highest NPASS analog similarity]")
    print(top1[["r7_idx", "tanimoto", "npass_id", "npass_logkp"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
