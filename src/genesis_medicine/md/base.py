"""MD refinement 공통 인터페이스."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class MDRefineRequest(BaseModel):
    complex_pdb: Path = Field(description="docked protein-ligand 복합체")
    ligand_resname: str = "UNL"
    ns: float = 10.0                  # simulation length (ns)
    temperature_k: float = 310.0
    output_dir: Path
    seed: int = 42


class MDRefineResult(BaseModel):
    engine: str
    final_pdb: Path
    rmsd_ligand_mean: float = 0.0
    rmsf_pocket_mean: float = 0.0
    binding_energy_mm: float | None = None  # MM-GBSA proxy
    binding_energy_ml: float | None = None  # ML potential
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)


@runtime_checkable
class MDRefiner(Protocol):
    engine_name: str

    def refine(self, req: MDRefineRequest) -> MDRefineResult: ...

    def supports_ml_potential(self) -> bool: ...
