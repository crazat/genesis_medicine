"""MSA Provider 공통 인터페이스."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class MSARequest(BaseModel):
    sequence: str
    mode: str = Field(default="paired", description="paired | unpaired | single_chain")
    max_seqs: int = 4096
    seed: int = 42


class MSAResult(BaseModel):
    a3m_path: Path
    n_seqs: int
    wall_seconds: float = 0.0
    provider: str = ""
    metadata: dict = Field(default_factory=dict)


@runtime_checkable
class MSAProvider(Protocol):
    provider_name: str
    is_commercial_safe: bool

    def search(self, req: MSARequest) -> MSAResult: ...
