"""Dancik 4-layer skin PBPK on universal scaffold 5 leaders × 4 vehicles.

Output: pilot/universal_scaffold_admet/dancik_pbpk.csv
Reports: logKp (cm/s), flux_ss (µg/cm²/h), C_blood after 24h
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "pilot/universal_scaffold_admet"
OUT.mkdir(parents=True, exist_ok=True)

LEADERS = [
    ("R12_4",  "OCC1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R12_11", "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"),
    ("R12_23", "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R14_5",  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"),
    ("R13_13", "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1"),
]

VEHICLES = [
    ("ointment", True, 1.0),
    ("cream", False, 0.7),
    ("gel", False, 0.85),
    ("aqueous", False, 0.5),
]


def main():
    from src.genesis_medicine.dermatology.skin_pbpk_dancik import (
        DancikSkinPBPK, TopicalFormulation,
    )
    pbpk = DancikSkinPBPK()
    rows = []
    for name, smi in LEADERS:
        for vname, occluded, donor_f in VEHICLES:
            try:
                form = TopicalFormulation(
                    smiles=smi,
                    dose_ug_per_cm2=100.0 * donor_f,
                    vehicle=vname,
                    occluded=occluded,
                    application_time_hours=8.0,
                )
                res = pbpk.predict(form)
                rows.append({
                    "leader": name, "smiles": smi,
                    "vehicle": vname, "occluded": occluded,
                    "logKp_cms": res.log_kp_cm_s,
                    "flux_ss_ug_cm2_h": res.flux_ss_ug_cm2_h,
                    "lag_time_h": res.lag_time_h,
                    "cum_24h_ug_cm2": res.cumulative_dose_24h_ug_cm2,
                    "dermis_conc_ug_cm3": res.dermis_concentration_ug_cm3,
                    "bioavailability_topical": res.bioavailability_topical,
                    "available": res.available,
                })
                if res.available:
                    print(f"  ✅ {name}/{vname}: logKp={res.log_kp_cm_s} flux={res.flux_ss_ug_cm2_h}")
                else:
                    print(f"  ⚠️  {name}/{vname}: {res.note}")
            except Exception as e:
                print(f"  ❌ {name}/{vname}: {e}")
                rows.append({"leader": name, "smiles": smi,
                              "vehicle": vname, "error": str(e)[:200]})

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "dancik_pbpk.csv", index=False)
    print(f"\nSaved {OUT/'dancik_pbpk.csv'} ({len(df)} rows)")
    if "logKp_cms" in df.columns:
        print("\nlogKp / vehicle pivot:")
        print(df.pivot_table(values="logKp_cms", index="leader", columns="vehicle").to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
