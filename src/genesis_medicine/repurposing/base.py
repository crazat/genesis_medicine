"""약물 재창출 공통 인터페이스."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class RepurposingRequest(BaseModel):
    disease_id: str = Field(description="MONDO/EFO/MeSH ID")
    disease_name: str | None = None
    relation: str = Field(default="indication", description="indication | contraindication")
    top_k: int = 100
    seed: int = 42


class RepurposingHit(BaseModel):
    drug_id: str = Field(description="DrugBank/ChEMBL/Pubchem CID")
    drug_name: str | None = None
    smiles: str | None = None
    score: float = Field(description="모델 prediction score (높을수록 강한 indication)")
    explanation: str | None = Field(default=None, description="GNN multi-hop 설명")
    targets: list[str] = Field(default_factory=list, description="제안 타겟 UniProt")


class RepurposingResult(BaseModel):
    engine: str
    disease_id: str
    hits: list[RepurposingHit]
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


@runtime_checkable
class Repurposer(Protocol):
    engine_name: str

    def repurpose(self, req: RepurposingRequest) -> RepurposingResult: ...

    def supports_explanation(self) -> bool: ...
