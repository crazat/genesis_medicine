"""Novelty 데이터 클래스."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class NoveltyContext:
    """단일 (화합물, 질병/타겟) 쿼리 컨텍스트."""

    compound_name: str           # e.g. "Embelin"
    compound_synonyms: list[str] = field(default_factory=list)  # 보조 검색어
    inchikey: str | None = None
    cid: int | None = None       # PubChem CID

    disease: str = ""             # e.g. "hypertrophic scar"
    disease_synonyms: list[str] = field(default_factory=list)

    target_uniprot: str | None = None    # e.g. "P01137"
    target_gene: str | None = None       # e.g. "TGFB1"
    target_synonyms: list[str] = field(default_factory=list)


@dataclass
class PriorArtRecord:
    """단일 데이터 소스에서 prior-art 정보."""

    source: str                          # "pubmed", "europe_pmc", "chembl", ...
    n_hits: int = 0                      # 검색 결과 수
    top_titles: list[str] = field(default_factory=list)  # 핵심 paper title
    top_year: int | None = None          # 가장 오래된 보고
    notable_finding: str | None = None   # "Known IC50 = 50 nM"
    raw_url: str | None = None           # 검증 가능한 URL


@dataclass
class NoveltyScore:
    """종합 novelty 평가."""

    compound_name: str
    disease: str
    target: str | None = None

    # 차원별 점수 (0=잘알려짐, 1=새로움)
    score_pubmed: float = 1.0          # paper 카운트 기반
    score_chembl: float = 1.0          # 알려진 활성 유무
    score_clinical: float = 1.0        # 임상시험 진행 여부
    score_patent: float = 1.0          # 특허 등록 여부
    score_drugbank: float = 1.0        # 승인 indication
    score_mechanism: float = 1.0       # 알려진 mechanism

    # 종합 (가중 평균)
    composite_score: float = 1.0

    # 정성적 분류
    classification: Literal[
        "novel",          # 0.7+
        "partially_novel", # 0.4-0.7
        "known",           # < 0.4
    ] = "novel"

    # raw records
    records: list[PriorArtRecord] = field(default_factory=list)

    def explanation(self) -> str:
        """1-2 문장 자연어 설명 (manuscript Discussion에 들어감)."""
        if self.classification == "novel":
            return (f"*{self.compound_name}*에 대한 {self.disease} 적응 보고는 "
                    f"PubMed/Europe PMC/ChEMBL/임상시험/특허 6개 데이터 소스에서 "
                    f"발견되지 않았다 (composite novelty = {self.composite_score:.2f}). "
                    f"본 연구가 첫 in silico 보고로 기록될 가능성이 높다.")
        if self.classification == "partially_novel":
            n_papers = next((r.n_hits for r in self.records if r.source == "pubmed"), 0)
            return (f"*{self.compound_name}* — {self.disease}에 대해 사전 문헌 "
                    f"{n_papers}건 보고되었으나 본 연구의 다중 타겟 ECR 접근 및 "
                    f"한방 처방 매핑은 차별점을 가진다 "
                    f"(composite novelty = {self.composite_score:.2f}).")
        return (f"*{self.compound_name}*는 {self.disease} 영역에서 광범위한 사전 "
                f"보고가 있다 (composite novelty = {self.composite_score:.2f}). "
                f"본 연구는 알려진 hit를 다중 타겟 친화도 통합 척도에서 재확인하고 "
                f"한방 처방의 분자 메커니즘 해석에 기여한다.")
