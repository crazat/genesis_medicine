"""컨포메이셔널 앙상블 공통 인터페이스."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class ConformerSpec(BaseModel):
    cif_path: Path
    plddt_mean: float = 0.0
    rmsd_to_apo: float = 0.0
    pocket_volumes: list[float] = Field(default_factory=list, description="P2Rank 포켓 볼륨")
    cluster_id: int = -1


class EnsembleRequest(BaseModel):
    protein_sequence: str
    apo_cif: Path | None = None
    n_samples: int = 50
    seed: int = 42
    cluster: bool = True
    n_clusters: int = 5


class EnsembleResult(BaseModel):
    engine: str
    conformers: list[ConformerSpec]
    cluster_centers: list[int] = Field(default_factory=list, description="대표 conformer index")
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


@runtime_checkable
class EnsembleProvider(Protocol):
    engine_name: str

    def sample(self, req: EnsembleRequest) -> EnsembleResult: ...
