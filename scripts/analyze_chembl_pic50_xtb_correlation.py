"""ChEMBL MMP-1 pIC50 vs xtb gap_eV / energy_au_min correlation analysis.

Uses outputs from cpu_xtb_chembl_mmp1_refine_432.py.
Produces:
  pilot/cpu_meaningful/chembl_pic50_xtb_correlation.json
  pilot/cpu_meaningful/chembl_pic50_xtb_correlation.png (Spearman scatter)

This is paper #A H2 direct activity-data validation.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

ROOT = Path("/home/crazat/genesis_medicine")
CHEMBL = ROOT / "pilot/cpu_queue/chembl_mmp1_extended.csv"
XTB = ROOT / "pilot/cpu_meaningful/xtb_chembl_mmp1_refine_432conf.csv"
OUT_JSON = ROOT / "pilot/cpu_meaningful/chembl_pic50_xtb_correlation.json"
OUT_PNG = ROOT / "pilot/cpu_meaningful/chembl_pic50_xtb_correlation.png"


def main():
    chembl = pd.read_csv(CHEMBL)
    xtb = pd.read_csv(XTB)
    xtb_ok = xtb[xtb["status"] == "ok"].copy()
    xtb_ok = xtb_ok.rename(columns={"idx": "chembl_id"})
    merged = chembl.merge(xtb_ok, on="chembl_id", how="inner", suffixes=("", "_xtb"))
    print(f"merged: {len(merged)} mol with both pIC50 and xtb refine")

    feats = ["energy_au_min", "energy_kcal_min", "HOMO_eV", "LUMO_eV",
             "gap_eV_min", "gap_eV_mean", "gap_eV_max"]
    results = {"n": int(len(merged)), "correlations": {}}
    for f in feats:
        sp = spearmanr(merged["pIC50"], merged[f])
        pe = pearsonr(merged["pIC50"], merged[f])
        results["correlations"][f] = {
            "spearman_rho": round(sp.statistic, 4),
            "spearman_p": round(sp.pvalue, 6),
            "pearson_r": round(pe.statistic, 4),
            "pearson_p": round(pe.pvalue, 6),
        }
        print(f"  pIC50 vs {f}: Spearman={sp.statistic:+.4f} (p={sp.pvalue:.2e}), Pearson={pe.statistic:+.4f}")

    OUT_JSON.write_text(json.dumps(results, indent=2))
    print(f"saved: {OUT_JSON.relative_to(ROOT)}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for ax, f, label in zip(axes, ["gap_eV_mean", "energy_kcal_min"],
                                 ["gap_eV_mean (mass-indep)", "energy_kcal_min (mass-bias caveat)"]):
            ax.scatter(merged[f], merged["pIC50"], alpha=0.6, s=30)
            sp = results["correlations"][f]["spearman_rho"]
            pe = results["correlations"][f]["pearson_r"]
            ax.set_xlabel(label)
            ax.set_ylabel("pIC50 (ChEMBL MMP-1)")
            ax.set_title(f"n={len(merged)}, Spearman ρ={sp:+.3f}, Pearson r={pe:+.3f}")
            ax.grid(True, alpha=0.3)
        fig.suptitle("ChEMBL MMP-1 pIC50 vs xtb GFN2 432-conf refine — paper #A H2 validation")
        fig.tight_layout()
        fig.savefig(OUT_PNG, dpi=120, bbox_inches="tight")
        print(f"saved: {OUT_PNG.relative_to(ROOT)}")
    except ImportError:
        print("matplotlib unavailable — skipping plot")


if __name__ == "__main__":
    main()
