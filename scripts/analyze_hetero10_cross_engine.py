"""hetero10 cross-engine consistency: 432-conf refine vs single-point.

Recomputes Spearman for paper #B §3.6 with the now-complete hetero10 cohort.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

ROOT = Path("/home/crazat/genesis_medicine")
SINGLEPT = ROOT / "pilot/cpu_meaningful/xtb_npass_9997_singlept.csv"
REFINE_432 = ROOT / "pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_432conf.csv"
OUT = ROOT / "pilot/cpu_meaningful/hetero10_cross_engine_summary.json"


def main():
    sp = pd.read_csv(SINGLEPT)
    rf = pd.read_csv(REFINE_432)
    rf_ok = rf[rf["status"] == "ok"].copy()
    print(f"singlept master: {len(sp)} mol")
    print(f"hetero10 432-conf ok: {len(rf_ok)} mol")

    sp_id = "np_id" if "np_id" in sp.columns else "idx"
    sp_smi = "smiles" if "smiles" in sp.columns else "smi"
    sp_e = "energy_au" if "energy_au" in sp.columns else ("energy_h_min" if "energy_h_min" in sp.columns else None)
    sp_g = "gap_eV" if "gap_eV" in sp.columns else "gap_ev_mean"
    print(f"singlept cols: id={sp_id} smi={sp_smi} energy={sp_e} gap={sp_g}")

    merge_key = "smiles"
    rf_ok["smiles"] = rf_ok["smiles"].astype(str)
    sp[merge_key] = sp[sp_smi].astype(str)
    merged = rf_ok.merge(sp[[merge_key, sp_e, sp_g]], on=merge_key, how="inner",
                          suffixes=("_refine", "_singlept"))
    print(f"merged on smiles: {len(merged)} mol")

    rho_e = spearmanr(merged["energy_au_min"], merged[sp_e]).statistic
    rho_g_mean = spearmanr(merged["gap_eV_mean"], merged[sp_g]).statistic

    summary = {
        "n_merged": int(len(merged)),
        "n_refine_432_ok": int(len(rf_ok)),
        "n_singlept_master": int(len(sp)),
        "spearman_energy_refine_vs_singlept": round(float(rho_e), 6),
        "spearman_gap_mean_refine_vs_singlept_gap": round(float(rho_g_mean), 6),
        "interpretation": (
            "If energy ρ ≈ 1.0: single-point pass is rank-preserving compression of full refinement. "
            "If gap ρ ≈ 0.9 and refine adds detail, gap channel benefits from ensemble while energy doesn't."
        ),
    }
    OUT.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
