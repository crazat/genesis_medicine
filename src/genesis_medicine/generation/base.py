"""분자 생성기 공통 인터페이스.

DiffSBDD / FlowMol3 / DecompDiff / REINVENT 4 어댑터가 이 Protocol을 구현.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class GeneratedMolecule(BaseModel):
    """생성된 분자."""

    smiles: str
    score: float = Field(default=0.0, description="생성 모델 내부 점수")
    sa_score: float | None = Field(default=None, description="합성 가능성 (1=쉬움, 10=어려움)")
    qed: float | None = None
    novelty: bool | None = Field(default=None, description="학습 데이터에 없는 새 분자인가")
    engine: str = ""
    extra: dict = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    """생성 요청."""

    protein_structure: Path = Field(description="타겟 포켓 PDB/CIF")
    protein_sequence: str | None = None
    pocket_center: tuple[float, float, float] | None = None
    pocket_radius: float = 10.0
    seed_smiles: list[str] = Field(default_factory=list, description="시드 분자 (scaffold hop 등)")
    num_molecules: int = 100
    seed: int = 42


class GenerationResult(BaseModel):
    """생성 결과."""

    engine: str
    molecules: list[GeneratedMolecule]
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


@runtime_checkable
class MoleculeGenerator(Protocol):
    """분자 생성 엔진 Protocol."""

    engine_name: str

    def generate(self, req: GenerationRequest) -> GenerationResult:
        ...

    def supports_scaffold_hopping(self) -> bool:
        ...

    def supports_linker_design(self) -> bool:
        ...
