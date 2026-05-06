"""
F3: DUD-E decoy enrichment benchmark for our screening pipeline.

DUD-E (Database of Useful Decoys, Enhanced) provides target-specific decoys —
inactive compounds that are physico-chemically similar to actives but should
not bind. Standard VS benchmark.

For MMP-1 (no DUD-E entry directly), we generate decoys via:
  1. Pull CHEMBL231 actives
  2. Use DEcoy Maker (ZINC15-based) to generate property-matched decoys
  3. Or fall back to: random sample from ZINC15 'in-stock' subset matched by MW±25, logP±1.0

Score:
  - EF1%, EF5%, EF10% — enrichment factor at top X%
  - AUC — full ROC area under curve
  - BEDROC — early-recognition weighted

Inputs:
  data/chembl_mmp1_calibration.csv (15 actives)
  + 1500 generated decoys

Pipeline:
  Score all 1515 with our xtb_npass topical_refine_score AND with Boltz-2 affinity_pred.
  Compute enrichment metrics for both.
  Compare with random ranking baseline.

Output:
  pilot/dude_benchmark_mmp1/decoys.csv     (1500 decoy SMILES)
  pilot/dude_benchmark_mmp1/scored_all.csv (active+decoy with scores)
  pilot/dude_benchmark_mmp1/enrichment_summary.json (EF1, EF5, EF10, AUC, BEDROC)
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/crazat/genesis_medicine")
ACTIVES_CSV = ROOT / "data/chembl_mmp1_calibration.csv"
OUT_DIR = ROOT / "pilot/dude_benchmark_mmp1"


def load_actives() -> pd.DataFrame:
    return pd.read_csv(ACTIVES_CSV)


def property_match_decoys(actives: pd.DataFrame, n_decoys: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Generate property-matched decoys from a generic ZINC15 sampling.

    Without ZINC download, we use NPAtlas as the decoy source — this is a weaker
    benchmark (NPAtlas compounds may include active scaffolds), but still
    yields meaningful enrichment if we filter strictly.
    """
    np_atlas_csv = None
    for cand in [
        ROOT / "data/np_atlas_consolidated.csv",
        ROOT / "data/npatlas_master.csv",
        ROOT / "pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_48conf.csv",
    ]:
        if cand.exists():
            np_atlas_csv = cand
            break
    if np_atlas_csv is None:
        print("FAIL: no NPAtlas / ZINC source for decoys")
        return pd.DataFrame()

    print(f"sampling decoys from {np_atlas_csv}")
    df = pd.read_csv(np_atlas_csv)

    # Compute properties of actives for matching window
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    def props(smi):
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return None
        return {"mw": Descriptors.MolWt(m), "logp": Descriptors.MolLogP(m)}

    active_props = [props(s) for s in actives["smiles"]]
    active_props = [p for p in active_props if p is not None]
    mw_mean = np.mean([p["mw"] for p in active_props])
    mw_std = np.std([p["mw"] for p in active_props])
    logp_mean = np.mean([p["logp"] for p in active_props])
    logp_std = np.std([p["logp"] for p in active_props])
    print(f"  actives: MW={mw_mean:.0f}±{mw_std:.0f}  logP={logp_mean:.2f}±{logp_std:.2f}")

    # Filter to property-matched window
    rng = np.random.default_rng(seed)
    cand_smiles = df["smiles"].tolist() if "smiles" in df.columns else []
    decoy_pool = []
    for smi in cand_smiles:
        p = props(smi)
        if p is None:
            continue
        if abs(p["mw"] - mw_mean) > 1.5 * mw_std + 50:
            continue
        if abs(p["logp"] - logp_mean) > 1.5 * logp_std + 1.0:
            continue
        decoy_pool.append({"smiles": smi, **p})
    print(f"  decoy pool (property-matched): n={len(decoy_pool)}")

    sampled = rng.choice(decoy_pool, min(n_decoys, len(decoy_pool)), replace=False).tolist()
    return pd.DataFrame(sampled)


def compute_enrichment(scores: list[tuple[float, int]]) -> dict:
    """scores = [(score, is_active), ...]; higher score = better predicted binder.

    Sort descending, compute EF at 1/5/10%, AUC, BEDROC.
    """
    sorted_scores = sorted(scores, key=lambda x: -x[0])
    n_total = len(sorted_scores)
    n_actives = sum(1 for _, a in sorted_scores if a)
    if n_actives == 0 or n_total == 0:
        return {"error": "no actives or empty"}

    def ef_at(pct: float) -> float:
        n_top = max(1, int(n_total * pct / 100.0))
        n_top_actives = sum(1 for s, a in sorted_scores[:n_top] if a)
        active_frac_top = n_top_actives / n_top
        active_frac_overall = n_actives / n_total
        return active_frac_top / active_frac_overall

    # AUC via trapezoidal
    tpr = [0.0]
    fpr = [0.0]
    cum_actives = 0
    cum_decoys = 0
    n_decoys = n_total - n_actives
    for s, a in sorted_scores:
        if a:
            cum_actives += 1
        else:
            cum_decoys += 1
        tpr.append(cum_actives / max(n_actives, 1))
        fpr.append(cum_decoys / max(n_decoys, 1))
    auc = sum((fpr[i+1] - fpr[i]) * (tpr[i] + tpr[i+1]) / 2 for i in range(len(fpr) - 1))

    # BEDROC alpha=20 (default, emphasizes top 10%)
    alpha = 20.0
    sum_term = sum(math.exp(-alpha * (i + 1) / n_total) for i, (_, a) in enumerate(sorted_scores) if a)
    Ra = n_actives / n_total
    if Ra > 0 and Ra < 1:
        rie_max = (1 - math.exp(-alpha * Ra)) / (Ra * (1 - math.exp(-alpha)))
        rie_min = (1 - math.exp(alpha * Ra)) / (Ra * (1 - math.exp(alpha)))
        # BEDROC: see Truchon & Bayly 2007
        bedroc_factor = (Ra * (1 - math.exp(-alpha))) / (math.exp(alpha / n_total) - 1)
        rie = sum_term / bedroc_factor if bedroc_factor != 0 else 0
        bedroc = (rie - rie_min) / (rie_max - rie_min) if (rie_max - rie_min) > 0 else 0
    else:
        bedroc = None

    return {
        "n_total": n_total,
        "n_actives": n_actives,
        "ef_1pct": round(ef_at(1.0), 3),
        "ef_5pct": round(ef_at(5.0), 3),
        "ef_10pct": round(ef_at(10.0), 3),
        "auc_roc": round(auc, 3),
        "bedroc_alpha20": round(bedroc, 3) if bedroc is not None else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-decoys", type=int, default=1500)
    ap.add_argument("--score-csv",
                    help="optional: existing score CSV with 'smiles' + score column to compute enrichment "
                         "(if not provided, just generates decoys)")
    ap.add_argument("--score-col", default="topical_refine_score")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    actives = load_actives()
    print(f"actives: n={len(actives)}")

    # Generate decoys
    decoys_csv = OUT_DIR / "decoys.csv"
    if not decoys_csv.exists():
        decoys = property_match_decoys(actives, n_decoys=args.n_decoys)
        decoys.to_csv(decoys_csv, index=False)
        print(f"saved decoys -> {decoys_csv}")
    else:
        decoys = pd.read_csv(decoys_csv)
        print(f"reused decoys ({len(decoys)} rows)")

    # If score CSV provided, compute enrichment
    if args.score_csv:
        score_path = args.score_csv if Path(args.score_csv).is_absolute() else str(ROOT / args.score_csv)
        if not Path(score_path).exists():
            print(f"no score CSV at {score_path} — skip enrichment")
            return 0
        scored = pd.read_csv(score_path)
        active_smiles = set(actives["smiles"])

        scores = []
        for _, row in scored.iterrows():
            smi = row.get("smiles")
            if smi is None:
                continue
            sc = row.get(args.score_col)
            if sc is None or pd.isna(sc):
                continue
            scores.append((float(sc), 1 if smi in active_smiles else 0))
        print(f"scored entries: {len(scores)} (actives in scored: {sum(s[1] for s in scores)})")

        if sum(s[1] for s in scores) >= 3:
            enr = compute_enrichment(scores)
            print("\n=== enrichment ===")
            for k, v in enr.items():
                print(f"  {k}: {v}")
            (OUT_DIR / "enrichment_summary.json").write_text(json.dumps(enr, indent=2))

    summary = {
        "phase": "F3 DUD-E decoy benchmark setup",
        "n_actives": len(actives),
        "n_decoys": len(decoys),
        "decoys_csv": str(decoys_csv.relative_to(ROOT)),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
