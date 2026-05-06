"""Korean herbal cross-reference: top integrated candidates vs 102 curated
Korean herbal compounds (TGF-β1/MMP/COL1A1/TYR/AR/SREBP1 etc.).

Paper-tier output: which top candidates resemble known Korean herbal scaffolds,
informing potential plant origin OR semi-synthesis from herbal precursors.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def fp_one(smi):
    m = Chem.MolFromSmiles(smi)
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def murcko_one(smi):
    m = Chem.MolFromSmiles(smi)
    if not m:
        return None
    try:
        sc = MurckoScaffold.GetScaffoldForMol(m)
        return Chem.MolToSmiles(sc)
    except Exception:
        return None


def xref_one(args):
    """For a single integrated candidate, find best Korean herbal match."""
    cand_smi, herbal_fps, herbal_smiles, herbal_names, herbal_targets, herbal_korean = args
    cand_fp = fp_one(cand_smi)
    if cand_fp is None:
        return None
    sims = DataStructs.BulkTanimotoSimilarity(cand_fp, herbal_fps)
    if not sims:
        return None
    sims_arr = np.array(sims)
    top_idx = int(sims_arr.argmax())
    top3 = sims_arr.argsort()[-3:][::-1]
    return {
        "candidate_smiles": cand_smi,
        "best_herbal_match": herbal_names[top_idx],
        "best_herbal_korean": herbal_korean[top_idx],
        "best_herbal_target": herbal_targets[top_idx],
        "best_herbal_smiles": herbal_smiles[top_idx],
        "tanimoto_best": float(sims_arr[top_idx]),
        "tanimoto_2nd": float(sims_arr[top3[1]]) if len(top3) > 1 else None,
        "second_match": herbal_names[top3[1]] if len(top3) > 1 else None,
    }


def main():
    print("=" * 72)
    print("Korean herbal cross-reference (102 curated × top integrated 45)")
    print("=" * 72)

    # Load integrated top candidates
    top = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    top = top.dropna(subset=["smiles"])
    print(f"Top integrated candidates: {len(top)}")

    # Load Korean herbal curated DB
    herbal = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    herbal = herbal.dropna(subset=["smiles"])
    print(f"Korean herbal compounds: {len(herbal)}")

    # Compute fingerprints for herbal
    print("\n[1] Korean herbal fingerprints")
    with Pool(24) as p:
        herbal_fps = p.map(fp_one, herbal["smiles"].tolist())
    valid_idx = [i for i, f in enumerate(herbal_fps) if f is not None]
    herbal_fps = [herbal_fps[i] for i in valid_idx]
    herbal_clean = herbal.iloc[valid_idx].reset_index(drop=True)
    print(f"  valid herbal fps: {len(herbal_fps)}")

    # Cross-reference each top candidate against all herbals
    print("\n[2] Cross-reference Tanimoto search")
    args_list = [(s, herbal_fps,
                  herbal_clean["smiles"].tolist(),
                  herbal_clean["name"].tolist(),
                  herbal_clean["target_hint"].fillna("").tolist(),
                  herbal_clean["source_korean"].fillna("").tolist())
                  for s in top["smiles"]]
    with Pool(24) as p:
        xref_results = p.map(xref_one, args_list)

    xref_df = pd.DataFrame([r for r in xref_results if r])
    # Merge target context from top
    xref_df = pd.concat([
        top[["target", "compound", "smiles", "paper_tier_score",
              "affinity_prob_binary", "safety_score"]].reset_index(drop=True),
        xref_df.reset_index(drop=True).drop(columns=["candidate_smiles"]),
    ], axis=1)

    xref_df.to_csv(OUT / "korean_herbal_xref.csv", index=False)
    print(f"  ✅ korean_herbal_xref.csv ({len(xref_df)} rows)")

    # Report top matches per target
    print("\n[3] Best herbal matches per integrated candidate (top 10 highest Tanimoto)")
    high = xref_df.sort_values("tanimoto_best", ascending=False).head(10)
    for _, r in high.iterrows():
        print(f"  [{r['target']}] {r['compound']:10s} → "
              f"{r['best_herbal_match']:25s} ({r['best_herbal_korean']:8s}) "
              f"T={r['tanimoto_best']:.3f}  target_hint={r['best_herbal_target'][:40]}")

    # Per-target summary
    print("\n[4] Per-target Korean herbal alignment")
    for tgt, sub in xref_df.groupby("target"):
        mean_t = sub["tanimoto_best"].mean()
        max_t = sub["tanimoto_best"].max()
        most_common = sub["best_herbal_match"].value_counts().head(3)
        print(f"\n  [{tgt.upper()}] mean Tanimoto={mean_t:.3f}, max={max_t:.3f}")
        for h, c in most_common.items():
            print(f"    most common match: {h} ({c}/{len(sub)})")

    # Murcko scaffold cross-ref (more lenient)
    print("\n[5] Murcko scaffold overlap")
    with Pool(24) as p:
        cand_scs = p.map(murcko_one, top["smiles"].tolist())
        herbal_scs = p.map(murcko_one, herbal_clean["smiles"].tolist())
    cand_sc_set = set(s for s in cand_scs if s)
    herbal_sc_set = set(s for s in herbal_scs if s)
    overlap = cand_sc_set & herbal_sc_set
    print(f"  Top 45 unique scaffolds: {len(cand_sc_set)}")
    print(f"  Herbal unique scaffolds: {len(herbal_sc_set)}")
    print(f"  Direct Murcko overlap: {len(overlap)}")
    if overlap:
        print(f"  Overlapping scaffolds: {list(overlap)[:5]}")


if __name__ == "__main__":
    sys.exit(main())
