"""Master publication table — single CSV with all paper-tier hits combined.

Output: pilot/cpu_meaningful/MASTER_R12_publication_table.csv
        pilot/cpu_meaningful/MASTER_R12_publication_table.html
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def main():
    full = pd.read_csv(OUT / "full_cofold_ranking.csv")
    xref = pd.read_csv(OUT / "korean_herbal_xref.csv")
    integ = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")

    print(f"Full ranking: {len(full)}")
    print(f"Korean xref: {len(xref)}")
    print(f"Integrated top: {len(integ)}")

    # Master table: top 5 per target from each source
    rows = []

    # Source 1: BRICS top100 integrated
    for tgt, sub in integ.groupby("target"):
        for _, r in sub.head(5).iterrows():
            xref_match = xref[(xref["compound"] == r["compound"]) &
                                (xref["target"] == tgt)]
            herbal = xref_match["best_herbal_match"].iloc[0] if len(xref_match) else ""
            herbal_T = float(xref_match["tanimoto_best"].iloc[0]) if len(xref_match) else None
            rows.append({
                "target": tgt,
                "rank_within_target": 0,
                "source": "BRICS_top100",
                "compound": r["compound"],
                "smiles": r.get("smiles"),
                "boltz_affinity_pred": r.get("affinity_pred"),
                "boltz_affinity_prob": r.get("affinity_prob_binary"),
                "admet_safety_score": r.get("safety_score"),
                "novelty_combined": r.get("novelty_score"),
                "paper_tier_score": r.get("paper_tier_score"),
                "korean_herbal_proxy": herbal,
                "korean_herbal_tanimoto": herbal_T,
            })

    # Source 2: ChEMBL extended high-confidence
    chembl = full[full["compound"].astype(str).str.startswith("CHEMBL")]
    chembl = chembl[chembl["target"] != "unknown"]
    for tgt, sub in chembl.groupby("target"):
        for _, r in sub.sort_values("paper_tier_score",
                                      ascending=False).head(5).iterrows():
            rows.append({
                "target": tgt,
                "rank_within_target": 0,
                "source": "ChEMBL_extended",
                "compound": r["compound"],
                "smiles": r.get("smiles"),
                "boltz_affinity_pred": r.get("affinity_pred"),
                "boltz_affinity_prob": r.get("affinity_prob_binary"),
                "admet_safety_score": r.get("safety_score"),
                "novelty_combined": None,
                "paper_tier_score": r.get("paper_tier_score"),
                "korean_herbal_proxy": "(reference inhibitor)",
                "korean_herbal_tanimoto": None,
            })

    # Source 3: Direct Korean herbal cofolds
    herbal = full[~full["compound"].astype(str).str.startswith(
        ("top", "CHEMBL", "bace1", "egfr"))]
    herbal = herbal[herbal["target"] != "unknown"]
    for tgt, sub in herbal.groupby("target"):
        for _, r in sub.sort_values("paper_tier_score",
                                      ascending=False).head(5).iterrows():
            rows.append({
                "target": tgt,
                "rank_within_target": 0,
                "source": "Korean_herbal_direct",
                "compound": r["compound"],
                "smiles": r.get("smiles"),
                "boltz_affinity_pred": r.get("affinity_pred"),
                "boltz_affinity_prob": r.get("affinity_prob_binary"),
                "admet_safety_score": r.get("safety_score"),
                "novelty_combined": None,
                "paper_tier_score": r.get("paper_tier_score"),
                "korean_herbal_proxy": "(self)",
                "korean_herbal_tanimoto": 1.0,
            })

    master = pd.DataFrame(rows).sort_values(
        ["target", "source", "paper_tier_score"],
        ascending=[True, True, False])

    # Rank within (target, source)
    master["rank_within_target"] = master.groupby(
        ["target", "source"])["paper_tier_score"].rank(method="dense",
                                                        ascending=False).astype(int)

    master.to_csv(OUT / "MASTER_R12_publication_table.csv", index=False)
    print(f"\n✅ MASTER_R12_publication_table.csv ({len(master)} rows)")

    # HTML for preprint embedding
    html = master.to_html(index=False, classes="table", escape=False,
                           float_format="%.3f")
    (OUT / "MASTER_R12_publication_table.html").write_text(
        f"<style>"
        f"table.table {{ border-collapse: collapse; font-family: sans-serif; }}"
        f"table.table th, table.table td {{ padding: 4px 8px; "
        f"border: 1px solid #ddd; font-size: 11px; }}"
        f"table.table th {{ background: #f5f5f5; }}"
        f"</style>" + html
    )
    print(f"✅ MASTER_R12_publication_table.html")

    # Summary stats
    print("\n[Summary by source]")
    for src, sub in master.groupby("source"):
        print(f"  {src:25s} n={len(sub):3d}  "
              f"mean_score={sub['paper_tier_score'].mean():.3f}")

    print("\n[Summary by target]")
    for tgt, sub in master.groupby("target"):
        print(f"  {tgt:12s} n={len(sub):3d}  "
              f"top_score={sub['paper_tier_score'].max():.3f}")


if __name__ == "__main__":
    sys.exit(main())
