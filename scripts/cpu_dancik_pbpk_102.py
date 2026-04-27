"""Dancik 4-layer skin PBPK on 102 curated skin compounds × 4 vehicles.

Tier B #3 Dancik PBPK 102-compound 일괄 실행 — preprint #14 v0.2 데이터.

각 compound × {ointment, cream, gel, aqueous} = 408 row.
출력: pilot/cpu_meaningful/dancik_pbpk_102.csv + summary plot.
"""
from __future__ import annotations
import sys
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.genesis_medicine.dermatology.skin_pbpk_dancik import (
    DancikSkinPBPK, TopicalFormulation,
)


VEHICLES = [
    ("ointment", True, 1.0),       # name, occluded, donor_factor
    ("cream", False, 0.7),
    ("gel", False, 0.85),
    ("aqueous", False, 0.5),
]


def evaluate(args):
    name, smiles, vehicle, occluded, donor_factor = args
    pbpk = DancikSkinPBPK()
    formulation = TopicalFormulation(
        smiles=smiles,
        dose_ug_per_cm2=100.0 * donor_factor,
        vehicle=vehicle,
        occluded=occluded,
        application_time_hours=8.0,
    )
    r = pbpk.predict(formulation)
    return {
        "name": name,
        "smiles": smiles,
        "vehicle": vehicle,
        "occluded": occluded,
        "log_kp_cm_s": r.log_kp_cm_s,
        "flux_ss_ug_cm2_h": r.flux_ss_ug_cm2_h,
        "lag_time_h": r.lag_time_h,
        "cum_24h_ug_cm2": r.cumulative_dose_24h_ug_cm2,
        "sc_conc_ug_cm3": r.sc_concentration_ug_cm3,
        "ep_conc_ug_cm3": r.epidermis_concentration_ug_cm3,
        "de_conc_ug_cm3": r.dermis_concentration_ug_cm3,
        "bioavailability": r.bioavailability_topical,
        "available": r.available,
    }


def main() -> int:
    df = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    df = df.dropna(subset=["smiles"]).drop_duplicates("smiles")
    print(f"Skin compounds: {len(df)}")

    args = []
    for _, row in df.iterrows():
        for veh, occ, fac in VEHICLES:
            args.append((row["name"], row["smiles"], veh, occ, fac))
    print(f"Total Dancik runs: {len(args)} (= {len(df)} × {len(VEHICLES)} vehicles)")

    with Pool(processes=12) as p:
        results = p.map(evaluate, args)

    out = pd.DataFrame(results)
    csv_out = ROOT / "pilot/cpu_meaningful/dancik_pbpk_102.csv"
    out.to_csv(csv_out, index=False)
    print(f"\n✅ {csv_out}")
    print(f"   {len(out)} rows × {len(out.columns)} cols")

    # Per-vehicle summary
    print("\n[Per-vehicle bioavailability summary]")
    summ = out.groupby("vehicle").agg(
        median_logkp=("log_kp_cm_s", "median"),
        median_flux=("flux_ss_ug_cm2_h", "median"),
        median_bioavail=("bioavailability", "median"),
        n_high_perm=("log_kp_cm_s", lambda s: (s > -3.5).sum()),
    )
    print(summ)

    # Top 15 by 24h cumulative dose (ointment, occluded → best vehicle)
    oint = out[out["vehicle"] == "ointment"].nlargest(15, "cum_24h_ug_cm2")
    print("\n[Top 15 by 24h cumulative dose (ointment, occluded)]")
    print(oint[["name", "log_kp_cm_s", "flux_ss_ug_cm2_h",
                  "lag_time_h", "cum_24h_ug_cm2", "bioavailability"]].to_string(
        index=False))

    # Compounds suitable vs unsuitable for topical
    suitable = out[(out["vehicle"] == "ointment")
                    & (out["log_kp_cm_s"] > -5.0)]["name"].tolist()
    unsuitable = out[(out["vehicle"] == "ointment")
                      & (out["log_kp_cm_s"] <= -5.0)]["name"].tolist()
    print(f"\nTopical-suitable compounds (logKp > -5.0): {len(suitable)}/{len(df)}")
    print(f"Topical-unsuitable: {len(unsuitable)} (large/polar)")

    # Save summary JSON
    import json
    summary_json = {
        "n_compounds": len(df),
        "n_vehicles": len(VEHICLES),
        "n_runs": len(out),
        "topical_suitable_n": len(suitable),
        "topical_suitable_names": suitable[:30],
        "topical_unsuitable_n": len(unsuitable),
    }
    json_out = ROOT / "pilot/cpu_meaningful/dancik_pbpk_102_summary.json"
    json_out.write_text(json.dumps(summary_json, indent=2, ensure_ascii=False))
    print(f"\n✅ {json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
