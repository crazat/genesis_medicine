"""Final lead panel — consolidated paper-tier summary.

Aggregates ALL outputs:
  - refined_top20 (linear weighted)
  - pareto_top50 (multi-objective)
  - bayesian_round4_candidates (active learning)
  - selectivity_top20 (off-target)
  - quantum_top20 (conformer + xtb)
  - round4_top100 (REINVENT)
  - integrated_top_candidates_per_target (per-target winners)

Output: paper_tier_lead_panel.csv with EVERY lead's score from EVERY ranker.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def canon(smi):
    try:
        m = Chem.MolFromSmiles(str(smi))
        return Chem.MolToSmiles(m) if m else None
    except Exception:
        return None


def main():
    print("=" * 72)
    print("Final lead panel — paper-tier consolidated summary")
    print("=" * 72)

    # All 7 ranker tables
    sources = {
        "refined": "refined_top20.csv",
        "pareto": "pareto_top50.csv",
        "bayesian_AL": "bayesian_round4_candidates.csv",
        "selectivity": "selectivity_top20.csv",
        "quantum": "quantum_top20.csv",
        "round4_design": "round4_top100.csv",
        "per_target": "integrated_top_candidates_per_target.csv",
    }

    panels = {}
    for name, fn in sources.items():
        path = OUT / fn
        if not path.exists():
            print(f"  ⚠️ {name}: {fn} missing")
            continue
        df = pd.read_csv(path)
        if "smiles" in df.columns:
            df["canon"] = df["smiles"].apply(canon)
        elif "smi" in df.columns:
            df["canon"] = df["smi"].apply(canon)
        else:
            print(f"  ⚠️ {name}: no smiles column")
            continue
        df = df.dropna(subset=["canon"]).drop_duplicates("canon")
        panels[name] = df
        print(f"  {name}: {len(df)} mol from {fn}")

    # All unique compounds
    all_smis = set()
    for df in panels.values():
        all_smis.update(df["canon"].tolist())
    print(f"\nTotal unique mol across all rankers: {len(all_smis)}")

    # Build panel: for each mol, score from each ranker (or NaN)
    rows = []
    for smi in all_smis:
        row = {"smiles": smi}
        rank_count = 0
        for name, df in panels.items():
            sub = df[df["canon"] == smi]
            if len(sub) > 0:
                rank_count += 1
                first = sub.iloc[0]
                if "refined_score" in first:
                    row[f"{name}_score"] = first["refined_score"]
                elif "pareto_score" in first:
                    row[f"{name}_score"] = first["pareto_score"]
                elif "expected_improvement" in first:
                    row[f"{name}_score"] = first["expected_improvement"]
                elif "selectivity_index" in first:
                    row[f"{name}_score"] = first["selectivity_index"]
                elif "quantum_score" in first:
                    row[f"{name}_score"] = first["quantum_score"]
                elif "round4_score" in first:
                    row[f"{name}_score"] = first["round4_score"]
                elif "paper_tier_score" in first:
                    row[f"{name}_score"] = first["paper_tier_score"]
        row["n_rankers_in_top"] = rank_count
        rows.append(row)

    panel = pd.DataFrame(rows)
    panel.sort_values("n_rankers_in_top", ascending=False, inplace=True)
    panel.to_csv(OUT / "paper_tier_lead_panel.csv", index=False)

    print(f"\n✅ paper_tier_lead_panel.csv ({len(panel)} unique mol)")

    # Multi-ranker leaders (mol that appear in ≥4 rankers)
    multi = panel[panel["n_rankers_in_top"] >= 4]
    multi.to_csv(OUT / "multi_ranker_leaders.csv", index=False)
    print(f"✅ multi_ranker_leaders.csv ({len(multi)} mol in ≥4 rankers)")

    if len(multi) > 0:
        print(f"\n[Top 10 mol by # rankers in top]")
        for _, r in multi.head(10).iterrows():
            smi = str(r["smiles"])[:55]
            print(f"  n={r['n_rankers_in_top']}/7 | {smi}")

    # Distribution stats
    print(f"\n[Ranker overlap distribution]")
    for n in range(1, 8):
        c = (panel["n_rankers_in_top"] == n).sum()
        print(f"  appears in exactly {n} rankers: {c}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
