"""Stage 1.5 — 약물 재창출 (TxGNN) 단위 테스트.

실제 TxGNN 가중치 로드 없이 어댑터 형태와 Protocol 충족만 검증.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_medicine.repurposing import (
    RepurposingHit,
    RepurposingRequest,
    RepurposingResult,
    Repurposer,
    TxGNNAdapter,
)


def test_request_validation() -> None:
    req = RepurposingRequest(disease_id="MONDO_0004975", top_k=10)
    assert req.relation == "indication"
    assert req.top_k == 10


def test_hit_basic_fields() -> None:
    hit = RepurposingHit(drug_id="DB00316", drug_name="Donepezil", score=0.87)
    assert hit.drug_id == "DB00316"
    assert hit.score == pytest.approx(0.87)


def test_txgnn_protocol(tmp_path: Path) -> None:
    adapter = TxGNNAdapter(cache_dir=tmp_path / "cache")
    assert isinstance(adapter, Repurposer)
    assert adapter.engine_name == "txgnn"
    assert adapter.supports_explanation()


def test_txgnn_graceful_when_uninstalled(tmp_path: Path) -> None:
    """txgnn 패키지 미설치 시 빈 결과 + 메타 에러 반환."""
    adapter = TxGNNAdapter(cache_dir=tmp_path / "cache")
    req = RepurposingRequest(disease_id="MONDO_0004975", top_k=5)
    result = adapter.repurpose(req)
    assert isinstance(result, RepurposingResult)
    assert result.engine == "txgnn"
    # 미설치 시 빈 hits + error metadata
    assert result.hits == []
    assert "error" in result.metadata or result.hits
