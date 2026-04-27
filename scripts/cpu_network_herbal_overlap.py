"""Network pharmacology — top 50 lead × Korean herbal target overlap.

For each top 50 mol, compute:
  - ECFP6 Tanimoto to all 102 Korean herbal compounds
  - Predicted shared targets (from herbal target_hint annotations)
  - Network connectivity score (target overlap vs all herbal)
"""
from __future__ import annotations

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
    if not m:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(m, 3, 4096)


def main():
    print("=" * 72)
    print("Network pharmacology — lead × Korean herbal overlap")
    print("=" * 72)

    herbal = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    print(f"Korean herbal compounds: {len(herbal)}")

    # Top 50 candidates
    sources = [
        ("paper_tier_lead_panel.csv", "smiles", 50),
        ("multi_ranker_leaders.csv", "smiles", 5),
        ("round4_top100.csv", "smiles", 30),
    ]
    leads = []
    for fn, col, lim in sources:
        path = OUT / fn
        if path.exists():
            df = pd.read_csv(path)
            if col in df.columns:
                leads.extend(df[col].head(lim).dropna().tolist())
    leads = list(set(leads))
    print(f"Total unique leads: {len(leads)}")

    with Pool(processes=6) as p:
        herbal_fps = p.map(fp6, herbal["smiles"].dropna().tolist())
        lead_fps = p.map(fp6, leads)

    valid_lead = [(i, f) for i, f in enumerate(lead_fps) if f]
    valid_herbal = [(i, f) for i, f in enumerate(herbal_fps) if f]

    rows = []
    for li, lfp in valid_lead:
        sims = np.array([DataStructs.TanimotoSimilarity(lfp, hfp)
                           for _, hfp in valid_herbal], dtype=np.float32)
        top3_idx = sims.argsort()[-3:][::-1]
        # Get target overlap
        top1_herbal = herbal.iloc[valid_herbal[top3_idx[0]][0]]
        rows.append({
            "lead_smiles": leads[li],
            "best_herbal_T": float(sims[top3_idx[0]]),
            "best_herbal_name": top1_herbal.get("name", ""),
            "best_herbal_korean": top1_herbal.get("source_korean", ""),
            "best_herbal_targets": top1_herbal.get("target_hint", ""),
            "n_herbal_hits_T_gt_0p5": int((sims > 0.5).sum()),
            "n_herbal_hits_T_gt_0p7": int((sims > 0.7).sum()),
            "max_T": float(sims.max()),
            "mean_T": float(sims.mean()),
        })

    df = pd.DataFrame(rows).sort_values("best_herbal_T", ascending=False)
    df.to_csv(OUT / "lead_herbal_network.csv", index=False)
    print(f"\n✅ lead_herbal_network.csv ({len(df)} leads)")

    # Counts
    high = df[df["best_herbal_T"] > 0.5]
    very_high = df[df["best_herbal_T"] > 0.7]
    print(f"\n[Network connectivity — Korean herbal]")
    print(f"  Leads with herbal T > 0.5: {len(high)}/{len(df)}")
    print(f"  Leads with herbal T > 0.7: {len(very_high)}/{len(df)}")
    print(f"  Mean best T: {df['best_herbal_T'].mean():.3f}")

    print(f"\n[Top 10 leads × Korean herbal connections]")
    for _, r in df.head(10).iterrows():
        smi = str(r["lead_smiles"])[:40]
        herb = str(r["best_herbal_name"])[:25]
        kor = str(r["best_herbal_korean"])[:10]
        print(f"  T={r['best_herbal_T']:.3f} → {herb:25s} ({kor:10s}) | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
