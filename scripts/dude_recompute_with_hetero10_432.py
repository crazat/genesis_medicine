"""DUD-E F3 enrichment recompute using hetero10 432-conf refine outputs as decoys.

Active set: 15 ChEMBL MMP-1 hydroxamates from existing actives csv.
Decoy set: 314 property-matched from hetero10 432-conf refine cohort.

Outputs paper #A §3.2 final-table values.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path("/home/crazat/genesis_medicine")
ACTIVES = ROOT / "pilot/cpu_meaningful/dude_actives_xtb_refine_432.csv"
DECOYS_HETERO = ROOT / "pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_432conf.csv"
OUT = ROOT / "pilot/cpu_meaningful/dude_f3_recomputed_hetero10_432.json"


def enrichment(scores: np.ndarray, labels: np.ndarray, fraction: float):
    n = len(scores)
    k = max(1, int(round(n * fraction)))
    order = np.argsort(-scores)  # highest first
    top_k = order[:k]
    n_actives_topk = labels[top_k].sum()
    n_actives_total = labels.sum()
    if n_actives_total == 0:
        return None
    return (n_actives_topk / k) / (n_actives_total / n)


def main():
    if not ACTIVES.exists():
        print(f"FAIL: {ACTIVES} missing — DUD-E actives 432-conf refine required first")
        return
    a_df = pd.read_csv(ACTIVES)
    d_df = pd.read_csv(DECOYS_HETERO)
    a_ok = a_df[a_df["status"] == "ok"].copy()
    d_ok = d_df[d_df["status"] == "ok"].copy()
    print(f"actives 432-conf ok: {len(a_ok)}")
    print(f"hetero10 decoys 432-conf ok: {len(d_ok)}")

    # Pick 314 property-matched decoys (random seed = paper #A's earlier choice)
    rng = np.random.default_rng(42)
    if len(d_ok) > 314:
        d_sample = d_ok.sample(n=314, random_state=42)
    else:
        d_sample = d_ok

    a_ok["label"] = 1
    d_sample["label"] = 0
    common_cols = ["status", "energy_au_min", "gap_eV_min", "gap_eV_mean", "gap_eV_max", "label"]
    combined = pd.concat([a_ok[common_cols], d_sample[common_cols]], ignore_index=True)
    print(f"combined: {len(combined)} rows ({combined['label'].sum()} actives)")

    results = {"n_actives": int(combined["label"].sum()),
               "n_decoys": int((combined["label"] == 0).sum())}

    for metric in ["gap_eV_mean", "gap_eV_min", "gap_eV_max", "energy_au_min"]:
        if metric not in combined.columns:
            continue
        # higher = better predicted active. for energy_au_min lower (more negative) = better, so flip
        scores = combined[metric].values.astype(float)
        if metric == "energy_au_min":
            scores = -scores
        labels = combined["label"].values.astype(int)
        ef5 = enrichment(scores, labels, 0.05)
        ef10 = enrichment(scores, labels, 0.10)
        auc = roc_auc_score(labels, scores)
        results[metric] = {
            "EF_5pct": round(float(ef5), 3) if ef5 else None,
            "EF_10pct": round(float(ef10), 3) if ef10 else None,
            "AUC_ROC": round(float(auc), 4),
        }
        print(f"  {metric}: EF5={ef5:.2f} EF10={ef10:.2f} AUC={auc:.4f}")

    OUT.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
