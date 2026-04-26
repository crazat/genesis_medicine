"""Unit tests for Round 5 SOTA adapters (2026-04-26).

9 adapters added in feat(round5) commit. All follow the license-gated
graceful-import pattern: they should never raise on instantiation,
should return result dataclasses with `.available` boolean and `.note`
field even when underlying tool is missing.
"""

from __future__ import annotations

import pytest


def test_boltz_abfe_adapter_importable_and_graceful():
    from genesis_medicine.md import BoltzABFEAdapter, BoltzABFEResult
    a = BoltzABFEAdapter()
    assert a.engine_name == "boltz_abfe"
    # underlying CLI is not installed in test env
    assert hasattr(a, "_available")
    # if unavailable, predict() returns a stub result, not an exception
    if not a._available:
        from pathlib import Path
        r = a.predict(compound="EMB-3", target="MMP1",
                      smiles="CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
                      receptor_pdb=Path("/tmp/nonexistent.pdb"))
        assert isinstance(r, BoltzABFEResult)
        assert r.available is False
        assert "boltz-abfe" in r.note.lower() or "boltz" in r.note.lower()


def test_moldais_adapter_backend_selection():
    from genesis_medicine.generation import MolDAISAdapter, MolDAISCampaign
    a = MolDAISAdapter(library_smiles=["CCO", "CCC", "CCCC"])
    assert a.backend in ("moldais", "botorch_saasbo", "lhs_fallback")
    feats = a.featurize(["CCO", "CCC"])
    assert feats.shape == (2, 1024)


def test_atom_openmm_adapter_graceful():
    from genesis_medicine.md import ATOMOpenMMAdapter, ATMResult
    a = ATOMOpenMMAdapter()
    assert a.engine_name == "atom_openmm"
    from pathlib import Path
    r = a.predict(compound="EMB-3", target="MMP1",
                  receptor_pdb=Path("/tmp/nonexistent.pdb"),
                  ligand_smiles="CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O")
    assert isinstance(r, ATMResult)
    # may be available=False (no AToM repo) or True (scaffold present)


def test_aimnet2_adapter_singlepoint_graceful():
    from genesis_medicine.md import AIMNet2Adapter, AIMNet2Result
    a = AIMNet2Adapter()
    assert a.engine_name == "aimnet2"
    r = a.singlepoint(compound="EMB-3",
                       smiles="CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O")
    assert isinstance(r, AIMNet2Result)
    if not a._available:
        assert r.available is False
        assert r.energy_hartree is None


def test_carsidock_cov_warhead_detection():
    from genesis_medicine.md import CarsiDockCovAdapter, CovalentDockingResult
    a = CarsiDockCovAdapter()
    # EMB-3 has p-quinone + alpha-beta unsat carbonyl warheads
    r = a.score(compound="EMB-3",
                smiles="CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
                target="MMP1")
    assert isinstance(r, CovalentDockingResult)
    assert r.has_covalent_warhead is True
    assert "p_quinone" in r.detected_warheads
    assert r.proposed_residue_cys == "Cys278"


def test_pbk_dermal_simulate_emb3():
    from genesis_medicine.dermatology import DermalPBKAdapter, DermalPBKResult
    a = DermalPBKAdapter()
    r = a.simulate(compound="EMB-3",
                    smiles="CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
                    logkp_cm_h=-2.5, dose_pmol=1000.0)
    assert isinstance(r, DermalPBKResult)
    assert r.available is True
    assert r.cmax_dermis_pmol_per_mL is not None
    assert r.cmax_dermis_pmol_per_mL > 0
    assert r.tmax_h is not None
    assert 0 < r.tmax_h < 24


def test_sara_ice_emb3_classification():
    from genesis_medicine.dermatology import SARAICEAdapter, SARAICEResult
    a = SARAICEAdapter()
    r = a.predict(compound="EMB-3",
                   smiles="CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O")
    assert isinstance(r, SARAICEResult)
    # quinone + alpha-beta-unsat carbonyl → at least 2 alerts expected
    assert len(r.in_silico_alerts) >= 2
    assert "michael_acceptor" in r.in_silico_alerts
    assert "quinone" in r.in_silico_alerts
    assert r.ghs_category in ("1A", "1B", "None")


def test_skin_fibroblast_atlas_rank_scar_targets():
    from genesis_medicine.dermatology import SkinFibroblastAtlasAdapter
    a = SkinFibroblastAtlasAdapter()
    df = a.rank_targets_for_scar(["TGFB1", "MMP1", "CTGF",
                                    "COL1A1", "PDGFRB"])
    assert len(df) == 5
    assert df.iloc[0]["scar_priority"] >= df.iloc[-1]["scar_priority"]
    # COL1A1 and ACTA2 are F6-enriched per literature → should rank top
    top_targets = df.head(2)["target_gene"].tolist()
    assert any(t in {"COL1A1", "ACTA2", "CTGF", "POSTN"} for t in top_targets)


def test_skin_fibroblast_atlas_cross_tissue():
    from genesis_medicine.dermatology import SkinFibroblastAtlasAdapter
    a = SkinFibroblastAtlasAdapter()
    e = a.cross_tissue_evidence("MMP1")
    assert e.cross_tissue_conserved is True   # MMP1 in literature conserved
    assert e.lung_inflammatory_fibroblast_score > 0


def test_cellaware_gnn_adapter_graceful():
    from genesis_medicine.repurposing import CellAwareGNNAdapter, CellAwareGNNResult
    a = CellAwareGNNAdapter()
    assert a.engine_name == "cellaware_gnn"
    r = a.predict_disease_drugs(disease_efo="EFO_0000274",
                                  top_k=10)
    assert isinstance(r, CellAwareGNNResult)
    if not a._available:
        assert r.available is False
        assert "CellAwareGNN" in r.note or "scPrimeKG" in r.note
