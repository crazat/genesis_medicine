"""AQAffinity 어댑터 단위 테스트.

External CLI 호출 + checkpoint 로딩은 환경 의존이므로 monkeypatch로
subprocess.run을 가짜 응답으로 대체한다. 테스트 목적은:
    1. 어댑터가 OpenFold3 query JSON을 metal cofactor와 함께 생성하는지
    2. _parse_output이 SandboxAQ JSON 변형들을 견고히 파싱하는지
    3. supports_affinity / supports_metal_cofactor 플래그가 True 인지
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from genesis_medicine.affinity import AQAffinityAdapter, AQAffinityRequest
from genesis_medicine.structure import (
    LigandSpec,
    StructurePredictionRequest,
    augment_request_with_cofactors,
)


def test_capabilities() -> None:
    a = AQAffinityAdapter(cache_dir=Path("/tmp/aqaffinity_cap"))
    assert a.supports_affinity() is True
    assert a.supports_ligands() is True
    assert a.supports_metal_cofactor() is True


def test_parse_output_pkd_only(tmp_path: Path) -> None:
    a = AQAffinityAdapter(cache_dir=tmp_path)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "predictions.json").write_text(
        json.dumps({"predictions": [{"pkd": 7.42, "confidence": 0.86,
                                     "target": "MMP1", "ligand": "AAA"}]})
    )
    res = a._parse_output(out_dir, t0=0.0)
    assert res.pkd == pytest.approx(7.42)
    assert res.confidence == pytest.approx(0.86)
    assert res.target_label == "MMP1"
    assert res.engine == "aqaffinity"


def test_parse_output_list_root(tmp_path: Path) -> None:
    a = AQAffinityAdapter(cache_dir=tmp_path)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "affinity_results.json").write_text(
        json.dumps([{"binding_affinity_pkd": 6.10, "binding_prob": 0.55}])
    )
    res = a._parse_output(out_dir, t0=0.0)
    assert res.pkd == pytest.approx(6.10)
    assert res.confidence == pytest.approx(0.55)


def test_query_json_includes_metal_cofactors(tmp_path: Path) -> None:
    """Smoke: AQAffinity의 _write_input이 OpenFold3 metal-aware 페이로드를
    그대로 사용하는지 확인."""
    a = AQAffinityAdapter(cache_dir=tmp_path)
    req = StructurePredictionRequest(
        protein_sequences=["MASEKQALSAR"],
        ligands=[LigandSpec(smiles="CC(=O)O", name="acetic")],
    )
    augment_request_with_cofactors(req, "MMP1")
    aq_req = AQAffinityRequest(base_request=req)
    path = a._write_input(aq_req.base_request, tmp_path)
    payload = json.loads(path.read_text())
    chains = payload["queries"]["genesis_aqaffinity"]["chains"]
    types = [c.get("molecule_type") for c in chains]
    assert types.count("protein") == 1
    # 1 ligand + 5 metal cofactors (2 ZN + 3 CA) → 6 ligand entries
    assert types.count("ligand") == 6
    ccd_codes = [c.get("ccd_codes") for c in chains if c.get("molecule_type") == "ligand"]
    assert ccd_codes.count("ZN") == 2
    assert ccd_codes.count("CA") == 3
