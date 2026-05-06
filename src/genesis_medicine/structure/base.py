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


class CovalentBondSpec(BaseModel):
    """OpenFold3-style explicit covalent bond between two atom locators.

    각 atom locator는 ``(chain_id, residue_index_or_ligand_index, atom_name)``
    문자열 또는 dict로 표현된다. 한약 cyclic peptide의 head-to-tail bond,
    quinone Michael acceptor의 covalent docking 등에 사용한다.
    """

    atom1_chain: str
    atom1_residue: int | str
    atom1_name: str
    atom2_chain: str
    atom2_residue: int | str
    atom2_name: str
    bond_type: str | None = None  # "covalent" | "disulfide" | "amide" 등 free-form


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
    # --- Holo / cofactor 확장 (2026-05-03) ----------------------------------
    # CCD ion codes (ZN, CU, FE, CA, MG, MN, NI, CO, …). 각 항목은 한 chain
    # 으로 추가된다. 같은 ion이 여러 자리면 list에 같은 코드를 반복.
    metal_ions: list[str] = Field(default_factory=list)
    # 비-ion cofactor CCD code (NDP, NAP, FAD, FMN, HEM, SAM, ATP, GTP, …).
    cofactor_ccds: list[str] = Field(default_factory=list)
    # 명시 covalent bond — cyclic peptide / quinone covalent inhibitor 용.
    covalent_bonds: list[CovalentBondSpec] = Field(default_factory=list)


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
