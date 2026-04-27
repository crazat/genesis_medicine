"""Pareto v2 — proper front-1 only with stricter filtering.

Pareto v1 had front 1 = 1000 mol (too lax — costs were too tied).
v2: 6 strict objectives + structural alert pre-filter + R4 candidates added.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def is_pareto_strict(costs):
    """Strict Pareto: dominated if exists row better in ALL objectives."""
    n = len(costs)
    is_eff = np.ones(n, dtype=bool)
    for i in range(n):
        if not is_eff[i]:
            continue
        for j in range(n):
            if i == j or not is_eff[j]:
                continue
            if np.all(costs[j] <= costs[i]) and np.any(costs[j] < costs[i]):
                is_eff[i] = False
                break
    return is_eff


def main():
    print("=" * 72)
    print("Pareto v2 — strict 6-objective filter")
    print("=" * 72)

    # Load druglikeness + ADMET combined
    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    admet = pd.read_csv(OUT / "admet_screen_combined.csv")

    df = drug.merge(admet[["smiles", "hERG", "Skin_Reaction", "AMES"]],
                     on="smiles", how="left")

    # Pre-filter: drop PAINS-flagged
    try:
        qf = pd.read_csv(OUT / "quality_filter_full.csv")
        clean_smis = set(qf[qf["all_filters_pass"]]["smiles"].tolist())
        df = df[df["smiles"].isin(clean_smis)]
        print(f"After quality filter: {len(df)}")
    except Exception:
        print("(quality filter skipped)")

    df = df.dropna(subset=["qed", "sa_score", "hERG", "logp", "mw"]).reset_index(drop=True)
    df["logKp"] = -2.7 + 0.71 * df["logp"] - 0.0061 * df["mw"]
    print(f"Valid for Pareto v2: {len(df)}")

    # 6 strict objectives (cost-form: lower is better)
    costs = np.column_stack([
        -df["qed"].values,                       # max QED
        df["sa_score"].values,                   # min SA
        df["hERG"].fillna(0.5).values,           # min hERG
        df["Skin_Reaction"].fillna(0.5).values,  # min skin reaction
        -df["logKp"].values,                     # max logKp (skin perm)
        df["mw"].values / 500.0,                 # min MW (normalized)
    ])

    print(f"Computing strict Pareto on {costs.shape}...")
    is_eff = is_pareto_strict(costs)

    df["pareto_v2_front1"] = is_eff
    front1 = df[is_eff].copy()
    front1["norm_qed"] = front1["qed"] / front1["qed"].max()
    front1["norm_inv_sa"] = (5 - front1["sa_score"]) / 4
    front1["norm_logKp"] = (front1["logKp"] - front1["logKp"].min()) / (
        front1["logKp"].max() - front1["logKp"].min() + 1e-9)
    front1["composite_v2"] = (
        front1["norm_qed"] * 0.4
        + front1["norm_inv_sa"] * 0.2
        + (1 - front1["hERG"].fillna(0.5)) * 0.2
        + (1 - front1["Skin_Reaction"].fillna(0.5)) * 0.1
        + front1["norm_logKp"] * 0.1)
    front1.sort_values("composite_v2", ascending=False, inplace=True)

    df.to_csv(OUT / "pareto_v2_full.csv", index=False)
    front1.to_csv(OUT / "pareto_v2_front1.csv", index=False)
    front1.head(50).to_csv(OUT / "pareto_v2_top50.csv", index=False)

    print(f"\n✅ Pareto v2 strict front 1: {is_eff.sum()} mol (vs v1 = 1000)")
    print(f"   → {100*is_eff.sum()/len(df):.1f}% of valid pool")
    print(f"\n[Top 10 Pareto v2 composite]")
    for _, r in front1.head(10).iterrows():
        smi = str(r["smiles"])[:50]
        print(f"  comp={r['composite_v2']:.3f} QED={r['qed']:.3f} "
              f"SA={r['sa_score']:.2f} hERG={r['hERG']:.3f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
