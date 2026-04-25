"""Stage 8' (ML-MD) + Stage 8.5 (ABFE) 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_medicine.md import (
    ABFEAdapter,
    ABFERequest,
    ABFEResult,
    MDRefineRequest,
    OpenMMMLRefiner,
)


def test_md_refine_request_defaults(tmp_path: Path) -> None:
    req = MDRefineRequest(complex_pdb=tmp_path / "c.pdb", output_dir=tmp_path / "out")
    assert req.ns == 10.0
    assert req.temperature_k == 310.0


def test_openmm_ml_protocol_fields() -> None:
    refiner = OpenMMMLRefiner(ml_potential="mace-off24-medium")
    assert refiner.engine_name == "openmm_ml"
    assert refiner.supports_ml_potential()


def test_abfe_adapter_creates(tmp_path: Path) -> None:
    adapter = ABFEAdapter(backend="fep_spell", cache_dir=tmp_path / "abfe")
    assert adapter.engine_name == "fep_spell_abfe"
    assert adapter.backend == "fep_spell"


def test_abfe_uninstalled(tmp_path: Path) -> None:
    adapter = ABFEAdapter(backend="fep_spell", cache_dir=tmp_path / "abfe")
    req = ABFERequest(
        receptor_pdb=tmp_path / "r.pdb",
        ligand_sdf=tmp_path / "l.sdf",
        output_dir=tmp_path / "out",
        prod_ns=0.1,
    )
    # fep-spell-abfe 미설치 시 delta_g=0 + error metadata
    result = adapter.compute(req)
    assert isinstance(result, ABFEResult)


def test_abfe_unknown_backend_raises(tmp_path: Path) -> None:
    adapter = ABFEAdapter(backend="unknown_backend", cache_dir=tmp_path / "abfe")
    req = ABFERequest(
        receptor_pdb=tmp_path / "r.pdb",
        ligand_sdf=tmp_path / "l.sdf",
        output_dir=tmp_path / "out",
    )
    with pytest.raises(ValueError):
        adapter.compute(req)
