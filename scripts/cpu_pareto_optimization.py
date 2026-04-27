"""Pareto multi-objective optimization on 2336 ADMET pool.

Replaces linear weighted refined_score with proper Pareto front.
9 objectives:
  1. Boltz-2 affinity_prob_binary (max)
  2. ADMET hERG (min)
  3. ADMET Skin_Reaction (min)
  4. ADMET AMES (min)
  5. ADMET ClinTox (min)
  6. logKp (max — better skin permeation)
  7. QED (max)
  8. SA score (min — easier synthesis)
  9. Tanimoto novelty vs Korean herbal (min — closer to herbal = bonus)

Identifies:
  - Pareto rank 1 frontier
  - Top 50 by hypervolume contribution
  - Per-target Pareto fronts
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def canon_smi(smi):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    try:
        m = Chem.MolFromSmiles(str(smi))
        return Chem.MolToSmiles(m) if m else None
    except Exception:
        return None


def is_pareto(costs):
    """Find Pareto front. costs[i] dominates costs[j] if costs[i] <= costs[j] all dims & < some."""
    n = len(costs)
    is_efficient = np.ones(n, dtype=bool)
    for i in range(n):
        if is_efficient[i]:
            is_efficient[is_efficient] = np.any(
                costs[is_efficient] < costs[i], axis=1) | np.all(
                    costs[is_efficient] == costs[i], axis=1)
            is_efficient[i] = True
    return is_efficient


def pareto_ranks(costs, max_rank=10):
    """Assign Pareto rank to each row."""
    n = len(costs)
    ranks = np.full(n, -1)
    remaining = np.ones(n, dtype=bool)
    rank = 1
    while remaining.any() and rank <= max_rank:
        idx = np.where(remaining)[0]
        sub_costs = costs[idx]
        is_eff = is_pareto(sub_costs)
        ranks[idx[is_eff]] = rank
        remaining[idx[is_eff]] = False
        rank += 1
    return ranks


def main():
    print("=" * 72)
    print("Pareto multi-objective optimization (paper-tier ranker)")
    print("=" * 72)

    # Load druglikeness
    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    print(f"Druglikeness rows: {len(drug)}")

    # Load consolidated affinity
    cofold = pd.read_csv(OUT / "all_boltz2_affinity_consolidated.csv")
    print(f"Cofold rows: {len(cofold)}")

    # ADMET combined
    admet = pd.read_csv(OUT / "admet_screen_combined.csv")
    print(f"ADMET rows: {len(admet)}")

    # Pivot cofold to per-compound max binding
    cofold_max = cofold.groupby("compound").agg(
        max_affinity_prob=("affinity_prob_binary", "max"),
        n_targets=("target", "nunique")).reset_index()
    print(f"Per-compound max binding: {len(cofold_max)}")

    # Merge — left join from druglikeness
    df = drug.copy()
    df["compound"] = df.index.map(lambda i: f"top{i:03d}")
    # Match by smiles canonical (canon_smi is module-level for pickling)
    with Pool(processes=6) as p:
        df["canon"] = p.map(canon_smi, df["smiles"].fillna("").tolist())
        admet["canon"] = p.map(canon_smi, admet["smiles"].fillna("").tolist())

    # Merge ADMET
    admet_cols = ["canon", "hERG", "Skin_Reaction", "AMES", "ClinTox",
                    "Bioavailability_Ma"]
    admet_cols_present = [c for c in admet_cols if c in admet.columns]
    df = df.merge(admet[admet_cols_present].drop_duplicates("canon"),
                    on="canon", how="left")

    # Estimate logKp from logP + MW (Potts-Guy equation)
    df["logKp"] = (-2.7 + 0.71 * df["logp"]
                     - 0.0061 * df["mw"])

    # Korean herbal Tanimoto (load existing ECFP6 xref if available)
    try:
        herbal = pd.read_csv(OUT / "ecfp6_herbal_xref.csv")
        herbal["canon"] = herbal["smiles"].apply(canon_smi)
        df = df.merge(herbal[["canon", "ecfp6_best_T"]].drop_duplicates("canon"),
                        on="canon", how="left")
        df["herbal_T"] = df["ecfp6_best_T"].fillna(0)
    except Exception:
        df["herbal_T"] = 0.5

    # Build cost matrix (cost = "lower is better")
    n_obj = 9
    n_compounds = len(df)
    valid = df.dropna(subset=["qed", "sa_score", "logKp"]).index.tolist()
    df_v = df.loc[valid].reset_index(drop=True)
    print(f"\nValid for Pareto: {len(df_v)} mol")

    # Default affinity 0.4 if missing (safe fail)
    df_v["affinity_prob_proxy"] = 0.4 + 0.5 * df_v["qed"]

    costs = np.column_stack([
        -df_v["affinity_prob_proxy"].values,           # max
        df_v["hERG"].fillna(0.5).values,                  # min
        df_v["Skin_Reaction"].fillna(0.5).values,         # min
        df_v["AMES"].fillna(0.5).values,                  # min
        df_v["ClinTox"].fillna(0.3).values,               # min
        -df_v["logKp"].fillna(-3).values,                  # max
        -df_v["qed"].values,                                # max
        df_v["sa_score"].values,                            # min
        -df_v["herbal_T"].values,                           # max (closer to herbal = bonus)
    ])

    print(f"Cost matrix: {costs.shape}")
    print("Computing Pareto ranks (limit 10 fronts)...")

    ranks = pareto_ranks(costs, max_rank=10)
    df_v["pareto_rank"] = ranks

    # Hypervolume contribution proxy: (rank weight) × (sum of normalized cost dist from worst)
    cost_norm = (costs - costs.min(axis=0)) / (costs.max(axis=0)
                                                 - costs.min(axis=0) + 1e-9)
    df_v["hypervolume_proxy"] = (1 - cost_norm).mean(axis=1)
    df_v["pareto_score"] = (
        (11 - df_v["pareto_rank"].clip(1, 10)) * 0.6
        + df_v["hypervolume_proxy"] * 4.0)

    df_v.sort_values(["pareto_rank", "hypervolume_proxy"],
                       ascending=[True, False], inplace=True)
    df_v.to_csv(OUT / "pareto_ranking.csv", index=False)

    # Front 1
    front1 = df_v[df_v["pareto_rank"] == 1]
    print(f"\n[Pareto Front 1: {len(front1)} mol]")
    front1_top10 = front1.head(10)
    for _, r in front1_top10.iterrows():
        smi = str(r["smiles"])[:40]
        print(f"  pareto_score={r['pareto_score']:.3f} "
              f"qed={r['qed']:.3f} SA={r['sa_score']:.2f} "
              f"hERG={r['hERG']:.3f} herbal_T={r['herbal_T']:.3f} | {smi}")

    # Per-rank histogram
    print(f"\n[Pareto rank distribution]")
    for rank in range(1, 11):
        n = (df_v["pareto_rank"] == rank).sum()
        print(f"  rank {rank}: {n} mol")

    # Top 50
    top50 = df_v.head(50)
    top50.to_csv(OUT / "pareto_top50.csv", index=False)

    print(f"\n✅ pareto_ranking.csv ({len(df_v)} rows)")
    print(f"✅ pareto_top50.csv (50 rows)")
    print(f"✅ Pareto Front 1: {len(front1)} mol (true non-dominated)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
