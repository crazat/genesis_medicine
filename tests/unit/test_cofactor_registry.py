"""Holo cofactor registry 단위 테스트."""
from __future__ import annotations

from genesis_medicine.structure import (
    LigandSpec,
    StructurePredictionRequest,
    augment_request_with_cofactors,
    build_openfold3_query_payload,
    get_cofactors,
    load_registry,
)


def test_registry_loads_known_targets() -> None:
    reg = load_registry()
    # At least the 12 metal/cofactor-dependent skin targets we registered
    assert len(reg.entries) >= 12
    assert "MMP1" in reg.entries
    assert "TYR" in reg.entries
    assert "SIRT1" in reg.entries


def test_mmp1_zinc_calcium_stoichiometry() -> None:
    spec = get_cofactors("MMP1")
    assert list(spec.metal_ions) == ["ZN", "ZN", "CA", "CA", "CA"]
    assert spec.is_holo_required() is True


def test_sirt1_has_zinc_and_nad() -> None:
    spec = get_cofactors("SIRT1")
    assert "ZN" in spec.metal_ions
    assert "NAD" in spec.cofactor_ccds


def test_alias_resolution_trp1_to_tyrp1() -> None:
    via_alias = get_cofactors("TRP1")
    via_canonical = get_cofactors("TYRP1")
    assert tuple(via_alias.metal_ions) == tuple(via_canonical.metal_ions)


def test_apo_target_returns_empty_spec() -> None:
    # PIEZO1 has no metal/cofactor in the registry → not holo required
    spec = get_cofactors("PIEZO1")
    assert spec.is_holo_required() is False


def test_augment_request_appends_metals() -> None:
    req = StructurePredictionRequest(
        protein_sequences=["MASKETLEKQALSAR"],
        ligands=[LigandSpec(smiles="CC(=O)O")],
    )
    augment_request_with_cofactors(req, "MMP1")
    assert req.metal_ions == ["ZN", "ZN", "CA", "CA", "CA"]
    assert req.cofactor_ccds == []


def test_query_payload_emits_metal_chains() -> None:
    req = StructurePredictionRequest(
        protein_sequences=["MASEKQALSAR"],
        ligands=[LigandSpec(smiles="CC(=O)O")],
    )
    augment_request_with_cofactors(req, "TYR")
    payload = build_openfold3_query_payload(req, query_id="t")
    chains = payload["queries"]["t"]["chains"]
    cu_chains = [c for c in chains if c.get("ccd_codes") == "CU"]
    assert len(cu_chains) == 2
    # OpenFold3 schema accepts both list[str] and str for chain_ids; normalize
    # to the first letter to assert global uniqueness across the bioassembly.
    def first_id(v):
        return v[0] if isinstance(v, list) else v
    flat = [first_id(c["chain_ids"]) for c in chains]
    assert len(flat) == len(set(flat)), f"chain_ids must be unique, got {flat}"
