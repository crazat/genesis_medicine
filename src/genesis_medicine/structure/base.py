"""구조 예측기 공통 인터페이스.

Protenix / Boltz-2 / ESMFold / AlphaFold DB 어댑터가 전부 이 Protocol을 구현한다.
파이프라인은 엔진 선택과 무관하게 동일 방식으로 호출한다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class LigandSpec(BaseModel):
    """공동접힘 대상 리간드."""

    smiles: str
    name: str | None = None
    ccd_code: str | None = Field(
        default=None,
        description="PDB CCD 코드. 있으면 Protenix/Boltz-2에서 CCD 템플릿 활용.",
    )


class StructurePredictionRequest(BaseModel):
    protein_sequences: list[str]
    ligands: list[LigandSpec] = Field(default_factory=list)
    rna_sequences: list[str] = Field(default_factory=list)
    dna_sequences: list[str] = Field(default_factory=list)
    template_cif: Path | None = None
    seed: int = 42
    num_recycles: int = 10
    num_samples: int = 5
    use_msa: bool = True


class StructurePredictionResult(BaseModel):
    cif_path: Path
    plddt_mean: float
    plddt_per_residue: list[float]
    confidence_json: Path
    affinity_pkd: float | None = None
    affinity_confidence: float | None = None
    engine: str
    engine_version: str
    wall_seconds: float


@runtime_checkable
class StructurePredictor(Protocol):
    """구조 예측 엔진 Protocol."""

    engine_name: str

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        ...

    def supports_ligands(self) -> bool:
        ...

    def supports_affinity(self) -> bool:
        ...
