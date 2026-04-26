"""Unit tests for Round 8 5-gap closure adapters."""

import pytest


def test_tau_ramd_emb3_mmp1():
    from genesis_medicine.kinetics import TauRAMDAdapter, TauRAMDResult
    a = TauRAMDAdapter()
    r = a.predict_residence_time(compound="EMB-3", target="MMP1")
    assert isinstance(r, TauRAMDResult)
    assert r.relative_tau_us is not None
    assert r.relative_tau_us > 0
    assert r.references


def test_tau_ramd_asiaticoside_top():
    from genesis_medicine.kinetics import TauRAMDAdapter
    a = TauRAMDAdapter()
    pairs = [("EMB-3", "MMP1"), ("Asiaticoside", "TGFB1"),
             ("EGCG", "MMP1"), ("Berberine", "SRD5A2")]
    taus = []
    for c, t in pairs:
        r = a.predict_residence_time(compound=c, target=t)
        taus.append((c, r.relative_tau_us))
    top = max(taus, key=lambda x: x[1])
    assert top[0] == "Asiaticoside"


def test_seekr2_benzamidine_trypsin_benchmark():
    from genesis_medicine.kinetics import SEEKR2Adapter
    a = SEEKR2Adapter()
    r = a.predict(compound="benzamidine", target="trypsin")
    assert r.koff_per_s == 310.0
    assert r.delta_g_kcal_mol == -6.06


def test_swisstarget_berberine_polypharmacology():
    from genesis_medicine.polypharmacology import SwissTargetAdapter
    a = SwissTargetAdapter()
    smi = "COc1ccc2cc3[n+](cc2c1OC)CCc1cc2c(cc1-3)OCO2"
    r = a.predict_targets(compound="berberine", smiles=smi)
    assert r.n_predicted_targets >= 10
    assert r.has_dealbreaker(), "berberine must show hERG dealbreaker"


def test_dealbreaker_berberine_critical():
    from genesis_medicine.polypharmacology import (
        SwissTargetAdapter, DealbreakerPanelAdapter,
    )
    st = SwissTargetAdapter()
    db = DealbreakerPanelAdapter()
    r_st = st.predict_targets(
        compound="berberine",
        smiles="COc1ccc2cc3[n+](cc2c1OC)CCc1cc2c(cc1-3)OCO2",
    )
    r_db = db.screen(compound="berberine", smiles="X",
                       polypharmacology_hits=r_st.hits)
    assert r_db.severity in ("moderate", "high", "critical")


def test_ddinter_egcg_warfarin():
    from genesis_medicine.ddi import DDInterAdapter
    a = DDInterAdapter()
    r = a.check_interactions(["EGCG", "warfarin"])
    assert r.n_pairs_with_interaction >= 1
    severities = [p.severity for p in r.pairs]
    assert any(s in ("Major", "Moderate") for s in severities)


def test_herbal_ddi_curated_export():
    from genesis_medicine.ddi import HerbalDDICurated
    df = HerbalDDICurated.to_dataframe()
    assert len(df) >= 15
    assert "severity" in df.columns


def test_cpedb_recommendation_emb3():
    from genesis_medicine.formulation import CPEDBAdapter
    a = CPEDBAdapter()
    smi = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"
    pes = a.recommend_for_compound(compound="EMB-3", smiles=smi, k=3)
    assert len(pes) == 3
    assert all(pe.skin_safety_class != "high_irritation" for pe in pes)


def test_hsp_vehicle_egcg_polar():
    from genesis_medicine.formulation import HSPVehicleAdapter
    a = HSPVehicleAdapter()
    egcg_smi = "OC1=CC(=CC(=C1O)O)C2OC3=CC(=CC(=C3CC2OC(=O)c4cc(O)c(O)c(O)c4)O)O"
    ranked = a.recommend_vehicles(smiles=egcg_smi, k=3)
    assert len(ranked) == 3
    assert ranked[0][1] >= 0    # RED distance non-negative


def test_kcid_emb3_not_listed_yet():
    from genesis_medicine.formulation import KCIDAdapter
    a = KCIDAdapter()
    s = a.lookup("EMB-3")
    assert s.kcid_listed is False
    assert "Pre-Notification" in s.note or "not_listed" in s.kfda_status


def test_kcid_hydroquinone_banned():
    from genesis_medicine.formulation import KCIDAdapter
    a = KCIDAdapter()
    s = a.lookup("hydroquinone")
    assert s.kfda_status == "banned_in_cosmetics"
    assert a.is_recover_safe("hydroquinone") is False


def test_httk_egcg_literature():
    from genesis_medicine.pkpd import HTTKAdapter
    a = HTTKAdapter()
    r = a.predict(compound="EGCG", dose_mg_kg=200, species="human")
    assert r.cmax_uM == 4.4
    assert r.available is True


def test_hill_4parameter_fit():
    from genesis_medicine.pkpd import HillDoseResponseAdapter
    a = HillDoseResponseAdapter()
    dose = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    response = [5.0, 10.0, 30.0, 70.0, 90.0, 95.0]
    r = a.fit(compound="test", target="MMP1",
              dose_uM=dose, response_pct=response)
    assert r.ic50_uM is not None
    assert 0 < r.ic50_uM < 100
    assert r.r_squared > 0.7
