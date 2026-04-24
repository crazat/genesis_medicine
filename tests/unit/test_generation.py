"""생성 모듈 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_medicine.generation.base import (
    GeneratedMolecule,
    GenerationRequest,
    GenerationResult,
)
from genesis_medicine.generation.synthesizability import SynthesizabilityChecker


def test_generated_molecule_defaults() -> None:
    mol = GeneratedMolecule(smiles="CCO")
    assert mol.score == 0.0
    assert mol.sa_score is None
    assert mol.qed is None
    assert mol.engine == ""


def test_generation_request_defaults() -> None:
    req = GenerationRequest(protein_structure=Path("/tmp/test.pdb"))
    assert req.num_molecules == 100
    assert req.seed == 42
    assert req.pocket_radius == 10.0
    assert req.seed_smiles == []


def test_generation_result_molecule_count() -> None:
    mols = [GeneratedMolecule(smiles=f"C{'C' * i}O") for i in range(5)]
    result = GenerationResult(engine="test", molecules=mols)
    assert len(result.molecules) == 5


def test_synthesizability_rdkit_sa() -> None:
    """RDKit SA Score가 합리적 범위 (1~10)를 반환하는지 확인."""
    checker = SynthesizabilityChecker(sa_threshold=6.0, use_aizynthfinder=False)

    smiles_list = [
        "CC(=O)Oc1ccccc1C(=O)O",  # aspirin
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # ibuprofen
        "c1ccccc1",  # benzene (매우 간단)
    ]

    results = checker.check_batch(smiles_list)
    assert len(results) == 3

    for r in results:
        # SA score는 1~10 범위
        assert 1.0 <= r.sa_score <= 10.0
        # aspirin/ibuprofen/benzene은 합성 쉬움
        assert r.is_synthesizable is True


def test_synthesizability_invalid_smiles() -> None:
    """잘못된 SMILES는 최대 SA score (10)를 반환."""
    checker = SynthesizabilityChecker(use_aizynthfinder=False)
    results = checker.check_batch(["invalid_smiles_xyz"])
    assert len(results) == 1
    assert results[0].sa_score == 10.0
    assert results[0].is_synthesizable is False
