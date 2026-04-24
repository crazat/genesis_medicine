"""스크리닝 엔진 공통 인터페이스.

모든 스크리닝 어댑터(DrugCLIP, Uni-Mol2, FlowDock, Boltz-2, GNINA, PoseBusters)가
이 Protocol을 구현한다. 파이프라인은 엔진에 무관하게 동일 방식으로 호출.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class DockingPose(BaseModel):
    """도킹/스크리닝 결과의 단일 포즈."""

    ligand_smiles: str
    ligand_name: str | None = None
    protein_id: str
    pose_sdf: Path | None = None
    pose_pdb: Path | None = None
    score: float = Field(description="엔진별 점수 (낮을수록 좋음 = binding energy 부호 관례)")
    confidence: float = Field(default=0.0, description="0~1 신뢰도 (높을수록 좋음)")
    affinity_pkd: float | None = Field(default=None, description="pKd 예측 (있으면)")
    engine: str = ""
    extra: dict = Field(default_factory=dict)


class ScreeningRequest(BaseModel):
    """스크리닝 요청."""

    protein_id: str
    protein_structure: Path = Field(description="PDB/CIF 파일 경로")
    protein_sequence: str | None = None
    ligand_smiles_list: list[str]
    ligand_names: list[str] = Field(default_factory=list)
    top_n: int | None = None
    top_fraction: float | None = None
    seed: int = 42


class ScreeningResult(BaseModel):
    """스크리닝 단계 결과."""

    engine: str
    poses: list[DockingPose]
    wall_seconds: float = 0.0
    metadata: dict = Field(default_factory=dict)

    @property
    def top_smiles(self) -> list[str]:
        """점수 순 SMILES 목록."""
        return [p.ligand_smiles for p in sorted(self.poses, key=lambda p: p.score)]


@runtime_checkable
class Screener(Protocol):
    """가상 스크리닝 엔진 Protocol."""

    engine_name: str

    def screen(self, req: ScreeningRequest) -> ScreeningResult:
        ...

    def supports_affinity(self) -> bool:
        ...

    def supports_pose(self) -> bool:
        """3D 포즈를 출력하는가."""
        ...
