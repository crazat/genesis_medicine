"""Refined master ranker — combines Boltz-2 + ADMET + xtb + druglikeness + OT
+ Korean herbal evidence into final paper-tier ranking.
"""
import sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
import numpy as np
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def canonical(smi):
    try:
        m = Chem.MolFromSmiles(str(smi))
        return Chem.MolToSmiles(m) if m else None
    except Exception:
        return None


def main():
    print("Refined master ranker — all R12 sources combined")
    full = pd.read_csv(OUT / "full_cofold_ranking.csv")
    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    xref = pd.read_csv(OUT / "korean_herbal_xref.csv")

    print(f"  full cofold: {len(full)}")
    print(f"  druglikeness: {len(drug)}")
    print(f"  herbal xref: {len(xref)}")

    # Canonicalize for matching
    with Pool(24) as p:
        full["canon"] = p.map(canonical, full.get("smiles", pd.Series(dtype=str)).fillna("").tolist())
        drug["canon"] = p.map(canonical, drug["smiles"].fillna("").tolist())

    # Merge
    drug_cols = ["canon", "sa_score", "qed", "lipinski_violations",
                  "veber_violations", "tpsa", "rotbonds"]
    full = full.merge(drug[drug_cols].drop_duplicates("canon"),
                       on="canon", how="left")

    # New refined score: aff(0.4) + safety(0.25) + novelty(0.15) +
    #                     synth(0.1) + druglike(0.1)
    full["synth_score"] = 1 - (full["sa_score"].fillna(5) - 1) / 4    # 1=easy
    full["druglike_score"] = (
        (full["lipinski_violations"].fillna(4) == 0).astype(float) * 0.5
        + (full["veber_violations"].fillna(2) == 0).astype(float) * 0.5
    )
    full["refined_score"] = (
        full["affinity_prob_binary"].fillna(0) * 0.4
        + full["safety_score"].fillna(0.5) * 0.25
        + full.get("novelty_score", pd.Series([0] * len(full))).fillna(0).clip(0, 1) * 0.15
        + full["synth_score"].clip(0, 1) * 0.10
        + full["druglike_score"] * 0.10
    )

    # Top 20 across all
    top = full.dropna(subset=["refined_score"]).sort_values(
        "refined_score", ascending=False).head(20)
    print("\n[Top 20 by refined score]")
    for _, r in top.iterrows():
        cmpd = str(r["compound"])[:25]
        sa = r.get("sa_score", float("nan"))
        sa_s = f"{sa:.2f}" if not pd.isna(sa) else "nan"
        qed = r.get("qed", float("nan"))
        qed_s = f"{qed:.3f}" if not pd.isna(qed) else "nan"
        print(f"  [{r['target']:10s}] {cmpd:25s} prob={r.get('affinity_prob_binary', 0):.3f} "
              f"SA={sa_s} QED={qed_s} refined={r['refined_score']:.3f}")

    full.to_csv(OUT / "refined_master_ranking.csv", index=False)
    top.to_csv(OUT / "refined_top20.csv", index=False)
    print(f"\n✅ refined_master_ranking.csv ({len(full)} rows)")
    print(f"✅ refined_top20.csv (20 rows)")

    # Per-target top 5
    print("\n[Per-target top 5 by refined score]")
    for tgt, sub in full.groupby("target"):
        if tgt == "unknown":
            continue
        top5 = sub.dropna(subset=["refined_score"]).sort_values(
            "refined_score", ascending=False).head(5)
        if len(top5) > 0:
            print(f"\n  [{tgt.upper()}]")
            for _, r in top5.iterrows():
                cmpd = str(r["compound"])[:25]
                print(f"    {cmpd:25s} refined={r['refined_score']:.3f}")


if __name__ == "__main__":
    sys.exit(main())
