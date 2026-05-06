"""Apply integrated paper-tier ranking to ALL 1109+ Boltz-2 cofolds across
all sources (BRICS top100, ChEMBL extended, screen libraries, etc.).

Reveals high-scorers from non-BRICS sources that the original ranker missed.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def canonicalize(smi):
    try:
        m = Chem.MolFromSmiles(str(smi))
        return Chem.MolToSmiles(m) if m else None
    except Exception:
        return None


def main():
    print("=" * 72)
    print("Full cofold ranker — across ALL sources (BRICS + ChEMBL + screens)")
    print("=" * 72)

    # Load all data
    affinity = pd.read_csv(OUT / "all_boltz2_affinity_consolidated.csv")
    deep = pd.read_csv(OUT / "boltz_deep_metrics.csv")
    admet = pd.read_csv(OUT / "admet_screen_combined.csv")

    print(f"Affinity rows: {len(affinity)}")
    print(f"Deep metrics rows: {len(deep)}")
    print(f"ADMET rows: {len(admet)}")

    # Resolve SMILES for affinity (compound is identifier, need to look up)
    # Sources to map compound → SMILES:
    smi_lookups = {}

    # 1. BRICS top100
    try:
        df = pd.read_csv(ROOT / "pilot/cpu_queue_v5/top100_novel_candidates.csv")
        for i, r in df.reset_index(drop=True).iterrows():
            smi_lookups[f"top{i:03d}"] = r["smiles"]
    except Exception:
        pass

    # 2. ChEMBL extended (compound = CHEMBL_ID)
    try:
        df = pd.read_csv(ROOT / "pilot/cpu_queue/chembl_mmp1_extended.csv")
        for _, r in df.iterrows():
            cid = r.get("chembl_id", "")
            smi = r.get("smiles", "")
            if cid and smi:
                smi_lookups[cid] = smi
    except Exception:
        pass

    # 3. Skin compounds curated
    try:
        df = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
        for _, r in df.iterrows():
            smi_lookups[r["name"]] = r["smiles"]
            smi_lookups[r.get("source_korean", "")] = r["smiles"]
    except Exception:
        pass

    print(f"SMILES lookup table: {len(smi_lookups)}")

    # Map affinity rows to SMILES
    affinity["smiles"] = affinity["compound"].map(smi_lookups)
    n_resolved = affinity["smiles"].notna().sum()
    print(f"Resolved: {n_resolved}/{len(affinity)} affinity rows")

    # Canonicalize
    with Pool(24) as p:
        affinity["canonical_smiles"] = p.map(canonicalize, affinity["smiles"].fillna(""))

    # Merge ADMET
    safety_cols = ["logP", "hERG", "AMES", "Skin_Reaction"]
    admet_clean = admet.dropna(subset=safety_cols, how="all").copy()
    with Pool(24) as p:
        admet_clean["canonical_smiles"] = p.map(canonicalize, admet_clean["smiles"].fillna(""))
    admet_match = admet_clean[admet_clean["canonical_smiles"].notna()].drop_duplicates("canonical_smiles")

    merged = affinity.merge(admet_match[["canonical_smiles"] + safety_cols],
                              on="canonical_smiles", how="left")
    print(f"Merged with ADMET: {merged['logP'].notna().sum()}/{len(merged)}")

    # Score
    merged["safety_score"] = (
        (1 - merged["hERG"].fillna(0.5)) * 0.4
        + (1 - merged["AMES"].fillna(0.5)) * 0.3
        + (1 - merged["Skin_Reaction"].fillna(0.5)) * 0.3
    )
    merged["affinity_score"] = merged["affinity_prob_binary"].fillna(0)
    # No novelty for non-BRICS sources, use affinity-only weighting
    merged["paper_tier_score"] = (
        merged["affinity_score"] * 0.6
        + merged["safety_score"] * 0.4
    )

    merged.to_csv(OUT / "full_cofold_ranking.csv", index=False)
    print(f"\n✅ full_cofold_ranking.csv ({len(merged)} rows)")

    # Top 20 across all sources
    print("\n[Top 20 across ALL sources by paper_tier_score]")
    top20 = merged.sort_values("paper_tier_score", ascending=False).head(20)
    for _, r in top20.iterrows():
        smi_short = (r.get("smiles") or "")[:50]
        print(f"  [{r['target']:10s}] {r['compound']:25s} "
              f"aff={r.get('affinity_pred', 0):.2f} "
              f"prob={r.get('affinity_prob_binary', 0):.3f} "
              f"safe={r.get('safety_score', 0):.3f} "
              f"score={r['paper_tier_score']:.3f}")

    # Per target top
    print("\n[Per-target top 5 across all sources]")
    for tgt, sub in merged.groupby("target"):
        top = sub.sort_values("paper_tier_score", ascending=False).head(5)
        print(f"\n  [{tgt.upper()}]")
        for _, r in top.iterrows():
            print(f"    {r['compound']:25s} score={r['paper_tier_score']:.3f}")


if __name__ == "__main__":
    sys.exit(main())
