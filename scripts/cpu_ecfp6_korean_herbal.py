"""ECFP6 (radius 3, 4096 bits) Tanimoto: 2336 × 102 Korean herbal.
Stronger fingerprint than ECFP4 used previously — captures larger substructures.
"""
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


def fp6(smi):
    m = Chem.MolFromSmiles(str(smi))
    return AllChem.GetMorganFingerprintAsBitVect(m, 3, 4096) if m else None


def sim_row(args):
    fp_q, herbal_fps = args
    return DataStructs.BulkTanimotoSimilarity(fp_q, herbal_fps)


def main():
    print("ECFP6 (r=3, 4096b) full 2336 × 102 herbal")
    admet = pd.read_csv(OUT / "admet_screen_combined.csv")
    herbal = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")

    admet_smis = admet["smiles"].dropna().tolist()
    herbal_smis = herbal["smiles"].dropna().tolist()
    herbal_names = herbal["name"].tolist()
    herbal_korean = herbal["source_korean"].fillna("").tolist()
    herbal_target = herbal["target_hint"].fillna("").tolist()

    with Pool(24) as p:
        admet_fps = p.map(fp6, admet_smis)
        herbal_fps = p.map(fp6, herbal_smis)
    admet_valid = [(i, f) for i, f in enumerate(admet_fps) if f]
    herbal_v = [f for f in herbal_fps if f]

    print(f"  valid: {len(admet_valid)} × {len(herbal_v)}")

    args_list = [(fp, herbal_v) for _, fp in admet_valid]
    with Pool(24) as p:
        rows = p.map(sim_row, args_list)
    M = np.array(rows, dtype=np.float32)
    np.save(OUT / "ecfp6_herbal_tanimoto.npy", M)
    print(f"  matrix: {M.shape}, mean {M.mean():.3f}, max {M.max():.3f}")

    # Per-mol top match
    rows_out = []
    for k, (idx, _) in enumerate(admet_valid):
        sims = M[k]
        top3 = sims.argsort()[-3:][::-1]
        rows_out.append({
            "smiles": admet_smis[idx],
            "source": admet["source"].iloc[idx],
            "ecfp6_best_T": float(sims[top3[0]]),
            "ecfp6_best_match": herbal_names[top3[0]],
            "ecfp6_best_korean": herbal_korean[top3[0]],
            "ecfp6_best_target": herbal_target[top3[0]],
            "ecfp6_2nd_T": float(sims[top3[1]]) if len(top3) > 1 else 0,
            "ecfp6_2nd_match": herbal_names[top3[1]] if len(top3) > 1 else "",
        })
    out = pd.DataFrame(rows_out)
    out.to_csv(OUT / "ecfp6_herbal_xref.csv", index=False)
    print(f"  ✅ ecfp6_herbal_xref.csv ({len(out)} rows)")

    # ECFP6 high-similarity hits (threshold higher than ECFP4 because radius 3)
    high = out[out["ecfp6_best_T"] > 0.4].sort_values(
        "ecfp6_best_T", ascending=False)
    print(f"\n[ECFP6 T > 0.4 hits: {len(high)}]")
    for _, r in high.head(15).iterrows():
        print(f"  T={r['ecfp6_best_T']:.3f}  [{r['source']:18s}] → "
              f"{r['ecfp6_best_match']:20s} ({r['ecfp6_best_korean']:8s})")
    high.to_csv(OUT / "ecfp6_herbal_high.csv", index=False)


if __name__ == "__main__":
    sys.exit(main())
