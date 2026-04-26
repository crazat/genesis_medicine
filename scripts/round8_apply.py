"""Round 8 — 5 신규 빈틈 모두 production sweep (real artifacts).

Closes Round 8 ultrathink-identified gaps:
  1. Drug-target kinetics (τRAMD residence time)
  2. Polypharmacology (SwissTarget + Dealbreaker panel)
  3. DDI (DDInter + curated 한약 17 pairs)
  4. Topical formulation (CPE-DB + HSP + KCID)
  5. PK-PD (httk + Hill fit)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/round8_application"
OUT.mkdir(parents=True, exist_ok=True)


def kinetics_sweep():
    from genesis_medicine.kinetics import TauRAMDAdapter
    a = TauRAMDAdapter()
    pairs = [
        ("EMB-3", "MMP1"), ("Embelin", "MMP1"),
        ("Asiaticoside", "TGFB1"), ("EGCG", "MMP1"),
        ("Berberine", "SRD5A2"), ("Shikonin", "MMP9"),
    ]
    rows = []
    for c, t in pairs:
        r = a.predict_residence_time(compound=c, target=t)
        rows.append({
            "compound": c, "target": t,
            "relative_tau_us": r.relative_tau_us,
            "log10_relative_tau": r.log10_relative_tau,
            "n_replicas": r.n_replicas,
            "available": r.available,
            "reference": r.references[0] if r.references else "",
        })
    df = pd.DataFrame(rows).sort_values("relative_tau_us", ascending=False)
    df.to_csv(OUT / "kinetics_residence_time.csv", index=False)
    print(f"  ✅ kinetics_residence_time.csv ({len(df)} pairs, "
          f"top: {df.iloc[0]['compound']} × {df.iloc[0]['target']} τ={df.iloc[0]['relative_tau_us']:.1f}μs)")


def polypharmacology_sweep():
    from genesis_medicine.polypharmacology import (
        SwissTargetAdapter, DealbreakerPanelAdapter,
    )
    swisstarget = SwissTargetAdapter()
    dealbreak = DealbreakerPanelAdapter()
    compounds = ["berberine", "EGCG", "curcumin", "embelin",
                  "EMB-3", "asiaticoside", "baicalein"]
    smiles_map = {
        "berberine": "COc1ccc2cc3[n+](cc2c1OC)CCc1cc2c(cc1-3)OCO2",
        "EGCG": "OC1=CC(=CC(=C1O)O)C2OC3=CC(=CC(=C3CC2OC(=O)c4cc(O)c(O)c(O)c4)O)O",
        "curcumin": "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O",
        "embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        "EMB-3": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
        "asiaticoside": "CC(=O)O[C@@H]1[C@H](C)C[C@@]2(C)C[C@H]3O[C@@H](OC4OC(CO)C(O)C(O)C4O)C(=O)O3",
        "baicalein": "Oc1cc2oc(-c3ccccc3)cc(=O)c2c(O)c1O",
    }
    rows_targets, rows_dealbreakers = [], []
    for c in compounds:
        smi = smiles_map[c]
        r_st = swisstarget.predict_targets(compound=c, smiles=smi)
        for hit in r_st.top_k(15):
            rows_targets.append({
                "compound": c, "target_name": hit.target_name,
                "target_class": hit.target_class,
                "probability": hit.probability,
                "uniprot": hit.target_uniprot,
            })
        r_db = dealbreak.screen(compound=c, smiles=smi,
                                  polypharmacology_hits=r_st.hits,
                                  target_disease="")
        rows_dealbreakers.append({
            "compound": c, "n_dealbreakers": r_db.n_dealbreakers,
            "severity": r_db.severity,
            "flags": json.dumps(r_db.flags),
        })
    pd.DataFrame(rows_targets).to_csv(
        OUT / "polypharmacology_targets.csv", index=False)
    pd.DataFrame(rows_dealbreakers).to_csv(
        OUT / "polypharmacology_dealbreakers.csv", index=False)
    print(f"  ✅ polypharmacology_targets.csv ({len(rows_targets)} hits)")
    print(f"  ✅ polypharmacology_dealbreakers.csv "
          f"({sum(1 for r in rows_dealbreakers if r['n_dealbreakers']>0)}/"
          f"{len(rows_dealbreakers)} flagged)")


def ddi_sweep():
    from genesis_medicine.ddi import DDInterAdapter, HerbalDDICurated
    a = DDInterAdapter()
    # Recover-realistic medication combos
    queries = [
        ["berberine", "warfarin"],
        ["EGCG", "warfarin"],
        ["EGCG", "irinotecan"],
        ["baicalein", "rosuvastatin", "methotrexate"],
        ["curcumin", "tacrolimus"],
        ["ginsenoside_Rb1", "warfarin"],
        ["EMB-3", "MMP_inhibitors"],
    ]
    rows = []
    for q in queries:
        r = a.check_interactions(q)
        for p in r.pairs:
            rows.append({
                "queried": "|".join(q),
                "drug_a": p.drug_a, "drug_b": p.drug_b,
                "severity": p.severity, "mechanism": p.mechanism,
                "cyp_or_transporter": p.cyp_involved or "",
                "description": p.description,
            })
    pd.DataFrame(rows).to_csv(OUT / "ddi_interactions.csv", index=False)
    HerbalDDICurated.export_csv(OUT / "ddi_herbal_curated_full.csv")
    print(f"  ✅ ddi_interactions.csv ({len(rows)} interactions)")
    print(f"  ✅ ddi_herbal_curated_full.csv "
          f"({len(HerbalDDICurated.to_dataframe())} curated pairs)")


def formulation_sweep():
    from genesis_medicine.formulation import (
        CPEDBAdapter, HSPVehicleAdapter, KCIDAdapter,
    )
    cpe = CPEDBAdapter()
    hsp = HSPVehicleAdapter()
    kcid = KCIDAdapter()

    compounds = [
        ("EMB-3", "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"),
        ("EGCG", "OC1=CC(=CC(=C1O)O)C2OC3=CC(=CC(=C3CC2OC(=O)c4cc(O)c(O)c(O)c4)O)O"),
        ("Asiaticoside", "CC1(C)CC[C@@]2(CC[C@@]3(C)C(=CC[C@@H]4[C@@]5(C)CC[C@H](O)C(C)(C)[C@@H]5CC[C@@]34C)[C@@H]2C1)C(=O)O[C@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@@H]1O"),
        ("Berberine", "COc1ccc2cc3[n+](cc2c1OC)CCc1cc2c(cc1-3)OCO2"),
        ("Curcumin", "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O"),
    ]
    rows_pe, rows_hsp, rows_kcid = [], [], []
    for c, smi in compounds:
        for pe in cpe.recommend_for_compound(compound=c, smiles=smi, k=3):
            rows_pe.append({
                "compound": c, "pe_name": pe.name,
                "pe_inci": pe.inci_name,
                "enhancement": pe.enhancement_factor_range,
                "safety": pe.skin_safety_class,
            })
        for v, red in hsp.recommend_vehicles(smiles=smi, k=3):
            rows_hsp.append({
                "compound": c, "vehicle": v.name,
                "vehicle_inci": v.inci_name,
                "type": v.type, "RED_distance": round(red, 2),
            })
        s = kcid.lookup(c)
        rows_kcid.append({
            "compound": c, "inci_name": s.inci_name or "",
            "kcid_listed": s.kcid_listed,
            "kfda_status": s.kfda_status,
            "eu_status": s.eu_cosing_status,
            "annex_restriction": s.eu_annex_restriction or "",
            "note": s.note,
        })
    pd.DataFrame(rows_pe).to_csv(OUT / "formulation_pe.csv", index=False)
    pd.DataFrame(rows_hsp).to_csv(OUT / "formulation_vehicles.csv", index=False)
    pd.DataFrame(rows_kcid).to_csv(OUT / "formulation_kcid_status.csv", index=False)
    print(f"  ✅ formulation_pe.csv ({len(rows_pe)} PE recs)")
    print(f"  ✅ formulation_vehicles.csv ({len(rows_hsp)} vehicle recs)")
    print(f"  ✅ formulation_kcid_status.csv ({len(rows_kcid)} compounds)")


def pkpd_sweep():
    from genesis_medicine.pkpd import HTTKAdapter, HillDoseResponseAdapter
    httk = HTTKAdapter()
    hill = HillDoseResponseAdapter()
    compounds = [("EGCG", 200), ("Curcumin", 8000), ("Resveratrol", 25),
                 ("Berberine", 500), ("EMB-3", 50)]
    rows_pk = []
    for c, dose in compounds:
        r = httk.predict(compound=c, dose_mg_kg=dose, species="human")
        rows_pk.append({
            "compound": c, "dose_mg": dose,
            "cmax_uM": r.cmax_uM, "auc_uM_h": r.auc_uM_h,
            "half_life_h": r.half_life_h,
            "clearance_l_h_kg": r.clearance_l_h_kg,
            "available": r.available, "note": r.note,
        })
    pd.DataFrame(rows_pk).to_csv(OUT / "pkpd_httk.csv", index=False)

    # Demo Hill fit on synthetic dose-response (Marimastat-like)
    import numpy as np
    np.random.seed(42)
    dose = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    response = [hill_eq_demo(d, 5, 95, 0.5, 1.2) for d in dose]
    response = [r + np.random.normal(0, 2) for r in response]
    fit = hill.fit(compound="EMB-3_synthetic", target="MMP1",
                    dose_uM=dose, response_pct=response)
    rows_hill = [{
        "compound": fit.compound, "target": fit.target,
        "ic50_uM": fit.ic50_uM, "hill_slope": fit.hill_slope,
        "r_squared": fit.r_squared,
        "ed50_estimated_uM": fit.ed50_estimated_uM,
        "n_points": fit.n_points, "note": fit.note,
    }]
    pd.DataFrame(rows_hill).to_csv(OUT / "pkpd_hill_fit_demo.csv", index=False)
    print(f"  ✅ pkpd_httk.csv ({len(rows_pk)} compounds)")
    print(f"  ✅ pkpd_hill_fit_demo.csv (IC50={fit.ic50_uM:.3f} µM)")


def hill_eq_demo(x, bottom, top, ic50, slope):
    return bottom + (top - bottom) / (1 + (ic50 / x) ** slope)


def main():
    print("=" * 72)
    print("Round 8 production sweep — 5 신규 빈틈 모두")
    print("=" * 72)

    print("\n[1/5] Kinetics — τRAMD residence time")
    kinetics_sweep()

    print("\n[2/5] Polypharmacology — SwissTarget + Dealbreaker")
    polypharmacology_sweep()

    print("\n[3/5] DDI — DDInter + curated 한약")
    ddi_sweep()

    print("\n[4/5] Formulation — CPE-DB + HSP + KCID")
    formulation_sweep()

    print("\n[5/5] PK-PD — httk + Hill fit")
    pkpd_sweep()

    print(f"\n✅ All artifacts in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
