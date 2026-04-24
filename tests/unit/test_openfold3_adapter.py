"""OpenFold3 어댑터 단위 테스트."""

from __future__ import annotations

from genesis_medicine.structure import OpenFold3Adapter
from genesis_medicine.structure.base import LigandSpec, StructurePredictionRequest


def test_openfold3_supports_ligands() -> None:
    from pathlib import Path
    adapter = OpenFold3Adapter(cache_dir=Path("/tmp/test_of3"))
    assert adapter.supports_ligands() is True
    assert adapter.supports_affinity() is False
    assert adapter.engine_name == "openfold3"
