"""Unit tests for Round 7 adapters."""

from __future__ import annotations

import pytest


def test_pocketminer_graceful():
    from genesis_medicine.ensemble import PocketMinerAdapter, PocketMinerResult
    a = PocketMinerAdapter()
    assert a.engine_name == "pocketminer"
    if not a._available:
        from pathlib import Path
        r = a.predict(Path("/tmp/nonexistent.pdb"))
        assert isinstance(r, PocketMinerResult)
        assert r.available is False


def test_cmap_l1000_anti_fibrotic_fallback():
    from genesis_medicine.repurposing import CMapL1000Adapter
    a = CMapL1000Adapter()
    r = a.query_signature(signature_name="anti_fibrotic_skin",
                            up_genes=[], down_genes=[])
    assert r.n_hits >= 6
    perts = [h.perturbation for h in r.hits]
    assert "niclosamide" in perts
    assert "pirfenidone" in perts
    assert "EGCG" in perts


def test_twosample_mr_literature_evidence():
    from genesis_medicine.causal import TwoSampleMRAdapter
    a = TwoSampleMRAdapter()
    r = a.causal_evidence(
        exposures=["MMP1", "TGFB1", "TYR", "SRD5A2", "AR"],
        outcomes=["idiopathic_pulmonary_fibrosis", "hypertrophic_scar",
                    "systemic_sclerosis", "androgenetic_alopecia",
                    "cutaneous_melanoma"],
    )
    assert r.exposures_outcomes_tested >= 5
    assert r.significant_at_p_05 == r.exposures_outcomes_tested
    # AR → AGA should be in the evidence
    ar_aga = [x for x in r.rows
              if "AR" in x.exposure and "alopecia" in x.outcome]
    assert len(ar_aga) >= 1
    assert ar_aga[0].p_ivw < 0.001


def test_tahoe100m_known_overlap():
    from genesis_medicine.foundation import Tahoe100MAdapter
    a = Tahoe100MAdapter()
    r = a.query_compound("EGCG")
    assert r.matched is True
    assert r.profiles[0].compound == "EGCG"
    assert "MMP1" in r.profiles[0].top_down_genes


def test_tahoe100m_niclosamide_anti_fibrotic():
    from genesis_medicine.foundation import Tahoe100MAdapter
    a = Tahoe100MAdapter()
    r = a.query_compound("niclosamide")
    assert r.matched is True
    profile = r.profiles[0]
    # Niclosamide should be enriched for anti_fibrotic / Wnt_inhibition
    assert "anti_fibrotic" in profile.pathway_enrichments
    assert profile.pathway_enrichments["anti_fibrotic"] > 4.0


def test_medsam_graceful():
    from genesis_medicine.clinical import MedSAMAdapter, ScarMetrics
    a = MedSAMAdapter()
    assert a.engine_name == "medsam_v2"
    from pathlib import Path
    r = a.segment_scar(image_path=Path("/tmp/nonexistent.jpg"))
    assert isinstance(r, ScarMetrics)
