"""Novelty 검증 패키지.

학술 출판 표준 prior-art 검증을 자동화. 각 hit 화합물에 대해 6개 데이터 소스에서
사전 보고 여부를 조회하고 종합 Novelty Score를 산출.

데이터 소스
-----------
1. PubMed E-utilities — 출판된 paper 카운트
2. Europe PMC REST — 전문(full-text) 검색
3. ChEMBL bioactivity — 알려진 IC50/Ki/Kd
4. ClinicalTrials.gov v2 API — 임상시험
5. Lens.org / Google Patents — 특허 등록
6. DrugBank — 승인 indication

Novelty Score (0~1)
-------------------
- 0.0 = 이미 잘 알려진 것 (paper 100+, 특허 등)
- 0.5 = 부분 알려짐 (paper 5-50)
- 1.0 = 완전 새로운 발견

이 점수는 manuscript의 Discussion 섹션에 자동 삽입되며,
reviewer의 "이미 알려진 것 아닌가?" 질문을 사전 차단.
"""

from .base import (
    NoveltyContext,
    NoveltyScore,
    PriorArtRecord,
)
from .pubmed_search import pubmed_count, europe_pmc_count
from .chembl_bioactivity import chembl_known_activities
from .clinicaltrials_search import clinicaltrials_count
from .patents_search import lens_patent_count
from .novelty_score import compute_novelty_score, batch_novelty_analysis
from .prior_art_table import render_prior_art_table

__all__ = [
    "NoveltyContext",
    "NoveltyScore",
    "PriorArtRecord",
    "pubmed_count", "europe_pmc_count",
    "chembl_known_activities",
    "clinicaltrials_count",
    "lens_patent_count",
    "compute_novelty_score", "batch_novelty_analysis",
    "render_prior_art_table",
]
