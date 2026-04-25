"""StudyContext + ManuscriptResult 공통 데이터 클래스."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StudyContext:
    """단일 pilot study를 한 편의 논문으로 보는 추상화."""

    name: str                           # 식별자, e.g. "skin_scar"
    title: str                          # manuscript title
    short_title: str = ""               # running head
    disease: str = ""                   # e.g. "Hypertrophic scar"
    description: str = ""               # 1~2 문장 요약

    # 입력 결과 파일들 (모두 pilot/<name>/results/ 하위)
    results_dir: Path = Path(".")
    consensus_csv: Path | None = None   # target × compound 매트릭스
    full_csv: Path | None = None        # long-form
    compounds_csv: Path | None = None   # 사용 천연물 metadata

    # 타겟 (UniProt + 모드 + AFDB 등)
    targets: list[dict] = field(default_factory=list)

    # 사용된 모델/도구의 라이선스 키 (citations.py가 BibTeX 생성)
    components_used: list[str] = field(
        default_factory=lambda: ["boltz2", "admet_ai", "rdkit", "openmm"]
    )

    # Hydra config snapshot (Methods 섹션에 노출)
    config_snapshot: dict[str, Any] = field(default_factory=dict)

    # MLflow run id (있으면)
    mlflow_run_id: str | None = None

    # 재현성 메타
    seed: int = 42
    license_profile: str = "commercial"

    # 출력 디렉터리
    output_dir: Path = Path("manuscript")

    # 저자 정보 (placeholder, 사용자가 채움)
    authors: list[dict] = field(
        default_factory=lambda: [
            {"name": "TBD", "affiliation": "Recover Clinic", "orcid": ""},
        ]
    )
    correspondence_email: str = "tbd@recover-clinic.kr"
    funding: str = "Self-funded R&D, Recover Clinic."
    conflicts: str = "The authors declare no conflicts of interest."

    def __post_init__(self) -> None:
        if not isinstance(self.results_dir, Path):
            self.results_dir = Path(self.results_dir)
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        if self.consensus_csv and not isinstance(self.consensus_csv, Path):
            self.consensus_csv = Path(self.consensus_csv)
        if self.full_csv and not isinstance(self.full_csv, Path):
            self.full_csv = Path(self.full_csv)
        if self.compounds_csv and not isinstance(self.compounds_csv, Path):
            self.compounds_csv = Path(self.compounds_csv)


@dataclass
class ManuscriptResult:
    """build_manuscript() 출력."""

    manuscript_md: Path
    figures: list[Path] = field(default_factory=list)
    tables: list[Path] = field(default_factory=list)
    references_bib: Path | None = None
    checklist_md: Path | None = None
    methods_md: Path | None = None
    statistics_csv: Path | None = None
    word_count: int = 0
    n_compounds: int = 0
    n_targets: int = 0
