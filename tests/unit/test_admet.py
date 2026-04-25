"""Stage 6 — ADMET-AI v2 단위 테스트."""

from __future__ import annotations

from pathlib import Path

from genesis_medicine.admet import (
    ADMETAIAdapter,
    ADMETPrediction,
    ADMETRequest,
    ADMETResult,
)
from genesis_medicine.admet.admet_ai_adapter import filter_by_admet


def test_prediction_convenience_flags() -> None:
    pred = ADMETPrediction(
        smiles="CCO",
        properties={"hERG": 0.1, "DILI": 0.2, "BBB_Martins": 0.8, "QED": 0.7, "Lipinski": 1.0},
    )
    assert pred.herg_safe
    assert pred.dili_safe
    assert pred.bbb_permeable
    assert pred.lipinski_pass


def test_prediction_unsafe() -> None:
    pred = ADMETPrediction(
        smiles="X",
        properties={"hERG": 0.9, "DILI": 0.8, "BBB_Martins": 0.2, "QED": 0.1},
    )
    assert not pred.herg_safe
    assert not pred.dili_safe
    assert not pred.bbb_permeable


def test_admet_ai_adapter_constructs(tmp_path: Path) -> None:
    adapter = ADMETAIAdapter(cache_dir=tmp_path)
    assert adapter.engine_name == "admet_ai_v2"


def test_admet_ai_adapter_uninstalled_returns_empty(tmp_path: Path) -> None:
    adapter = ADMETAIAdapter(cache_dir=tmp_path)
    result = adapter.predict(ADMETRequest(smiles_list=["CCO"]))
    assert isinstance(result, ADMETResult)


def test_filter_by_admet_filters() -> None:
    admet = ADMETResult(
        engine="test",
        predictions=[
            ADMETPrediction(smiles="A", properties={"hERG": 0.1, "DILI": 0.1, "BBB_Martins": 0.9, "QED": 0.6}),
            ADMETPrediction(smiles="B", properties={"hERG": 0.9, "DILI": 0.1, "BBB_Martins": 0.9, "QED": 0.6}),
            ADMETPrediction(smiles="C", properties={"hERG": 0.1, "DILI": 0.1, "BBB_Martins": 0.1, "QED": 0.6}),
        ],
    )
    scores = {"A": -10.0, "B": -9.0, "C": -8.0}
    filtered = filter_by_admet(scores, admet, require_bbb=True)
    assert "A" in filtered
    assert "B" not in filtered  # hERG 차단
    assert "C" not in filtered  # BBB 통과 실패
