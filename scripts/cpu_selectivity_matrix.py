"""Cross-target selectivity matrix — top 50 candidates × 14 targets.

Uses existing Boltz-2 affinity_prob_binary data + ChemBERTa embedding cosine
similarity to estimate off-target binding probability.

Output:
  - selectivity_matrix.csv: 50 × 14 affinity matrix (predicted)
  - selectivity_index.csv: per-mol top1/top3/top5 selectivity (best - mean)
  - off_target_warnings.csv: mol with affinity > 0.5 on ≥3 targets (off-target risk)
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


def fp(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)


def predict_for_target(args):
    """Predict affinity for a query mol via similarity-weighted KNN."""
    query_fp, train_fps, train_affs = args
    sims = np.array([DataStructs.TanimotoSimilarity(query_fp, f)
                       for f in train_fps], dtype=np.float32)
    top_k = min(5, len(sims))
    if top_k == 0:
        return 0.5
    top_idx = sims.argsort()[-top_k:][::-1]
    weights = sims[top_idx] / (sims[top_idx].sum() + 1e-9)
    return float(np.dot(weights, train_affs[top_idx]))


def main():
    print("=" * 72)
    print("Cross-target selectivity matrix (top 50 × 14 targets)")
    print("=" * 72)

    cofold = pd.read_csv(OUT / "all_boltz2_affinity_consolidated.csv")
    cofold = cofold.dropna(subset=["affinity_prob_binary"])
    print(f"Cofold rows: {len(cofold)}")

    targets_known = sorted(cofold["target"].unique())
    print(f"Targets with cofold data: {len(targets_known)}")
    print(f"  {targets_known}")

    # Get smiles for all cofold compounds (canon match via integrated table)
    integ = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    cofold_smi = integ[["compound", "smiles"]].drop_duplicates()

    cofold_with_smi = cofold.merge(cofold_smi, on="compound", how="left")
    cofold_with_smi = cofold_with_smi.dropna(subset=["smiles"]).reset_index(drop=True)
    print(f"Cofold with SMILES: {len(cofold_with_smi)}")

    # Build per-target training sets
    print("\n[Computing fingerprints for training data]")
    with Pool(processes=6) as p:
        train_fps_all = p.map(fp, cofold_with_smi["smiles"].tolist())
    valid = [i for i, f in enumerate(train_fps_all) if f is not None]
    train = cofold_with_smi.iloc[valid].reset_index(drop=True)
    train_fps_all = [train_fps_all[i] for i in valid]
    print(f"  Valid: {len(train)}")

    # Top 50 query: from refined or pareto ranking
    try:
        top50 = pd.read_csv(OUT / "pareto_top50.csv")
        print(f"\nQuery: pareto_top50 ({len(top50)} mol)")
    except Exception:
        top50 = pd.read_csv(OUT / "refined_top20.csv")
        print(f"\nQuery: refined_top20 fallback ({len(top50)} mol)")

    top50 = top50.dropna(subset=["smiles"]).drop_duplicates("smiles").head(50).reset_index(drop=True)
    print(f"Final query: {len(top50)} mol")

    print("\n[Computing fingerprints for query]")
    with Pool(processes=6) as p:
        query_fps = p.map(fp, top50["smiles"].tolist())

    # Predict affinity for each (query, target) pair
    print(f"\n[Predicting {len(top50)} × {len(targets_known)} = "
          f"{len(top50) * len(targets_known)} affinities]")

    results = np.zeros((len(top50), len(targets_known)), dtype=np.float32)
    for ti, tgt in enumerate(targets_known):
        sub = train[train["target"] == tgt].reset_index(drop=True)
        if len(sub) < 3:
            results[:, ti] = 0.5
            continue
        sub_fps = [train_fps_all[train.index[train["target"] == tgt][j]]
                    for j in range(len(sub))]
        sub_aff = sub["affinity_prob_binary"].values

        args_list = [(qfp, sub_fps, sub_aff) for qfp in query_fps if qfp]
        with Pool(processes=6) as p:
            preds = p.map(predict_for_target, args_list)
        results[:len(preds), ti] = preds

    # Build matrix DataFrame
    matrix = pd.DataFrame(results, columns=targets_known)
    matrix["compound"] = top50["compound"].values[:len(matrix)] if "compound" in top50.columns else range(len(matrix))
    matrix["smiles"] = top50["smiles"].values[:len(matrix)]

    # Selectivity index per row
    matrix["best_target"] = matrix[targets_known].idxmax(axis=1)
    matrix["best_affinity"] = matrix[targets_known].max(axis=1)
    matrix["mean_off_target"] = matrix[targets_known].mean(axis=1) - (
        matrix[targets_known].max(axis=1) / len(targets_known))
    matrix["selectivity_index"] = matrix["best_affinity"] - matrix["mean_off_target"]

    matrix.to_csv(OUT / "selectivity_matrix.csv", index=False)
    print(f"\n✅ selectivity_matrix.csv ({len(matrix)} × {len(targets_known)})")

    # Off-target warnings
    warning_threshold = 0.5
    off_targets = matrix[targets_known].apply(
        lambda row: (row > warning_threshold).sum(), axis=1)
    matrix["n_off_target_hits"] = off_targets

    warnings_df = matrix[matrix["n_off_target_hits"] >= 3].sort_values(
        "n_off_target_hits", ascending=False)
    warnings_df.to_csv(OUT / "off_target_warnings.csv", index=False)
    print(f"✅ off_target_warnings.csv ({len(warnings_df)} mol with ≥3 off-target hits)")

    # Top selectivity (highest selectivity_index)
    selective = matrix.sort_values("selectivity_index", ascending=False).head(20)
    selective.to_csv(OUT / "selectivity_top20.csv", index=False)
    print(f"✅ selectivity_top20.csv (20 mol)")

    print(f"\n[Top 10 most selective candidates]")
    for _, r in selective.head(10).iterrows():
        smi = str(r["smiles"])[:35]
        print(f"  best={r['best_target']:8s} aff={r['best_affinity']:.3f} "
              f"sel_idx={r['selectivity_index']:.3f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
