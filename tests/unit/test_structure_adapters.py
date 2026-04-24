"""구조 예측 어댑터 단위 테스트 (외부 호출 mock)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from genesis_medicine.structure import (
    LigandSpec,
    StructurePredictionRequest,
)
from genesis_medicine.structure.alphafold_db_adapter import AlphaFoldDBAdapter


def test_ligand_spec_round_trip() -> None:
    spec = LigandSpec(smiles="CCO", name="ethanol")
    assert spec.smiles == "CCO"
    assert spec.name == "ethanol"
    assert spec.ccd_code is None


def test_prediction_request_defaults() -> None:
    req = StructurePredictionRequest(protein_sequences=["MKL"])
    assert req.num_recycles == 10
    assert req.num_samples == 5
    assert req.use_msa is True
    assert req.seed == 42


def test_afdb_cache_hit(tmp_path: Path) -> None:
    cache = tmp_path / "afdb"
    adapter = AlphaFoldDBAdapter(cache_dir=cache)
    uniprot = "P56817"
    (cache / f"{uniprot}.cif").write_text("FAKE CIF")
    (cache / f"{uniprot}.json").write_text('{"plddt_mean": 91.2}')

    hit = adapter.lookup(uniprot)
    assert hit is not None
    assert hit.plddt_mean == pytest.approx(91.2)
    assert hit.engine == "alphafold_db"


def test_afdb_miss_returns_none(tmp_path: Path) -> None:
    adapter = AlphaFoldDBAdapter(cache_dir=tmp_path)
    with patch.object(adapter, "_fetch_meta", return_value=None):
        assert adapter.lookup("FAKE_UNIPROT") is None
