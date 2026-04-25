"""Stage 2.5 — 컨포메이셔널 앙상블 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_medicine.ensemble import (
    AlphaFlowAdapter,
    BioEmuAdapter,
    ConformerSpec,
    EnsembleRequest,
    EnsembleResult,
    compute_pocket_diversity,
)


def test_request_defaults() -> None:
    req = EnsembleRequest(protein_sequence="MAGV")
    assert req.n_samples == 50
    assert req.cluster is True


def test_alphaflow_adapter_protocol(tmp_path: Path) -> None:
    adapter = AlphaFlowAdapter(cache_dir=tmp_path / "af")
    assert adapter.engine_name == "alphaflow"


def test_bioemu_adapter_protocol(tmp_path: Path) -> None:
    adapter = BioEmuAdapter(cache_dir=tmp_path / "be")
    assert adapter.engine_name == "bioemu"


def test_alphaflow_uninstalled_returns_empty(tmp_path: Path) -> None:
    adapter = AlphaFlowAdapter(cache_dir=tmp_path / "af", binary="not_a_real_binary")
    req = EnsembleRequest(protein_sequence="MAGV", n_samples=2)
    result = adapter.sample(req)
    assert isinstance(result, EnsembleResult)
    assert result.conformers == []


def test_pocket_diversity_empty() -> None:
    assert compute_pocket_diversity([]) == []


def test_pocket_diversity_with_dummy_conformers(tmp_path: Path) -> None:
    confs = [
        ConformerSpec(cif_path=tmp_path / f"c{i}.cif", pocket_volumes=[100.0, 50.0])
        for i in range(3)
    ]
    pockets = compute_pocket_diversity(confs)
    # 더미 좌표 모두 (0,0,0)이라 1개 클러스터로 합쳐짐
    assert len(pockets) == 1
    assert pockets[0].n_conformers_with_pocket > 0
