"""Lipinski / PAINS / 필터링 단위 테스트."""

from __future__ import annotations

from genesis_medicine.ligand.filters import (
    canonical_smiles,
    filter_library,
    inchikey,
    qed,
)


def test_canonical_smiles() -> None:
    assert canonical_smiles("C(C)O") == canonical_smiles("CCO")
    assert canonical_smiles("not-a-smiles") is None


def test_inchikey_stable() -> None:
    assert inchikey("CCO") == inchikey("OCC")
    assert inchikey("bad") is None


def test_qed_range() -> None:
    from rdkit import Chem
    mol = Chem.MolFromSmiles("CC(=O)OC1=CC=CC=C1C(=O)O")  # aspirin
    assert 0.0 <= qed(mol) <= 1.0


def test_filter_library_keeps_drug_like() -> None:
    smiles = [
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # ibuprofen (drug-like, PAINS clean)
        "CC(C)Cc1ccc(C(C)C(=O)O)cc1",  # 동일 분자 다른 표기
        "C" * 60,                       # 파싱 실패 기대
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",  # MW 초과
    ]
    kept = filter_library(smiles)
    assert any(k["inchikey"].startswith("HEFNNWSXXWATRW") for k in kept)  # ibuprofen InChIKey
    assert all(150 <= k["mw"] <= 700 for k in kept)
