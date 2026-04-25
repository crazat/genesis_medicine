"""ADMET 예측 공통 인터페이스."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class ADMETRequest(BaseModel):
    smiles_list: list[str]
    seed: int = 42


class ADMETPrediction(BaseModel):
    smiles: str
    properties: dict[str, float] = Field(
        default_factory=dict,
        description="endpoint name → 예측 값 (확률 또는 회귀 점수)",
    )

    @property
    def lipinski_pass(self) -> bool:
        return bool(self.properties.get("Lipinski", 0) >= 0.5)

    @property
    def bbb_permeable(self) -> bool:
        return bool(self.properties.get("BBB_Martins", 0) >= 0.5)

    @property
    def herg_safe(self) -> bool:
        # ADMET-AI: hERG 차단 확률 — 낮을수록 안전
        return bool(self.properties.get("hERG", 1.0) < 0.5)

    @property
    def dili_safe(self) -> bool:
        return bool(self.properties.get("DILI", 1.0) < 0.5)


class ADMETResult(BaseModel):
    engine: str
    predictions: list[ADMETPrediction]
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


@runtime_checkable
class ADMETPredictor(Protocol):
    engine_name: str

    def predict(self, req: ADMETRequest) -> ADMETResult: ...
