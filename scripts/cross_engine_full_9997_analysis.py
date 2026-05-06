"""Cross-engine consensus analysis on full 9997 NPAtlas with refreshed singlept data.

Updates the previously top-500-only analysis to full corpus where data overlap permits.

Output: pilot/cpu_meaningful/cross_engine_full_9997_summary.json
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

ROOT = Path("/home/crazat/genesis_medicine")
MASTER = ROOT / "pilot/cpu_meaningful/xtb_npass_10k_master.csv"
SINGLEPT = ROOT / "pilot/cpu_meaningful/xtb_npass_9997_singlept.csv"
BOLTZ = ROOT / "pilot/boltz2_top500_mmp1/affinity_consolidated.csv"
OUT = ROOT / "pilot/cpu_meaningful/cross_engine_full_9997_summary.json"


def main():
    master = pd.read_csv(MASTER)
    sp = pd.read_csv(SINGLEPT)
    sp_ok = sp[sp["status"]=="ok"]
    print(f"master: {len(master)}, singlept ok: {len(sp_ok)}")

    boltz = None
    if BOLTZ.exists():
        boltz = pd.read_csv(BOLTZ)
        print(f"boltz: {len(boltz)} rows, cols: {list(boltz.columns)[:8]}")

    summary = {
        "n_master": int(len(master)),
        "n_singlept_ok": int(len(sp_ok)),
        "n_master_xtb_ok": int((master["status"]=="ok").sum()),
    }

    # singlept stats
    if len(sp_ok) > 0:
        summary["singlept_stats"] = {
            "energy_au_mean": float(sp_ok["xtb_energy_au"].mean()),
            "energy_au_std": float(sp_ok["xtb_energy_au"].std()),
            "gap_eV_mean": float(sp_ok["gap_eV"].mean()),
            "gap_eV_std": float(sp_ok["gap_eV"].std()),
            "homo_eV_mean": float(sp_ok["homo_eV"].mean()),
        }

    # master xtb (refined) vs singlept on overlap
    overlap = master.merge(sp_ok[["rank","xtb_energy_au","gap_eV"]], on="rank", how="inner",
                           suffixes=("_refine","_sp"))
    overlap = overlap[overlap["status"]=="ok"].dropna(subset=["energy_au_min","xtb_energy_au"])
    if len(overlap) > 50:
        rho_e, _ = spearmanr(overlap["energy_au_min"], overlap["xtb_energy_au"])
        rho_g, _ = spearmanr(overlap["gap_eV_mean"], overlap["gap_eV"])
        summary["refine_vs_singlept_overlap"] = {
            "n": int(len(overlap)),
            "spearman_energy_refine_vs_sp": float(rho_e),
            "spearman_gap_mean_refine_vs_sp_1conf": float(rho_g),
        }

    # boltz vs singlept top500 overlap (if data shape consistent)
    if boltz is not None and len(boltz) > 0:
        boltz_id_col = None
        for col in ["np_id", "id", "name"]:
            if col in boltz.columns:
                boltz_id_col = col
                break
        if boltz_id_col:
            boltz_aff_col = None
            for col in ["affinity_pred", "affinity", "predicted_affinity", "boltz_affinity"]:
                if col in boltz.columns:
                    boltz_aff_col = col
                    break
            if boltz_aff_col:
                merged = boltz.merge(sp_ok[["np_id","xtb_energy_au","gap_eV","homo_eV"]],
                                     left_on=boltz_id_col, right_on="np_id", how="inner")
                if len(merged) > 50:
                    rho_e_b, _ = spearmanr(merged[boltz_aff_col], merged["xtb_energy_au"])
                    rho_g_b, _ = spearmanr(merged[boltz_aff_col], merged["gap_eV"])
                    summary["boltz_vs_singlept_full_overlap"] = {
                        "n": int(len(merged)),
                        "spearman_boltz_vs_xtb_energy_au": float(rho_e_b),
                        "spearman_boltz_vs_xtb_gap_eV": float(rho_g_b),
                    }

    OUT.write_text(json.dumps(summary, indent=2))
    print(f"saved {OUT}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
