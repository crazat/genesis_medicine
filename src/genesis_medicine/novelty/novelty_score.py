"""종합 Novelty Score 계산.

각 차원의 prior-art 카운트를 [0, 1] novelty 척도로 정규화 후 가중 평균.

가중치 (학술 paper review 비중 기반)
- pubmed:        0.30  (가장 권위)
- europe_pmc:    0.10  (보충 풀텍스트)
- chembl:        0.20  (정량 활성)
- clinical:      0.20  (실제 임상 진행)
- patent:        0.15  (산업 IP)
- drugbank:      0.05  (승인 indication)
"""

from __future__ import annotations

import math
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable

import pandas as pd

from .base import NoveltyContext, NoveltyScore, PriorArtRecord
from .chembl_bioactivity import chembl_known_activities
from .clinicaltrials_search import clinicaltrials_count
from .patents_search import lens_patent_count
from .pubmed_search import europe_pmc_count, pubmed_count

WEIGHTS = {
    "pubmed":         0.30,
    "europe_pmc":     0.10,
    "chembl":         0.20,
    "clinicaltrials": 0.20,
    "lens_patent":    0.15,
    "drugbank":       0.05,
}


def _count_to_novelty(n: int, *, low: int = 0, high: int = 100) -> float:
    """카운트 → novelty (0~1).

    0 hits → 1.0 (완전 새로움)
    1-5 hits → 0.7 (조금 보고됨)
    50+ hits → 0.0 (잘 알려짐)
    log scale.
    """
    if n < 0:
        return 0.5  # 에러 시 중립
    if n == 0:
        return 1.0
    # log1p 스케일
    s = 1.0 - math.log1p(n) / math.log1p(high)
    return float(max(0.0, min(1.0, s)))


def compute_novelty_score(
    ctx: NoveltyContext,
    *,
    parallel: bool = True,
    include: Iterable[str] = ("pubmed", "europe_pmc", "chembl",
                              "clinicaltrials", "lens_patent"),
) -> NoveltyScore:
    """6개 차원 prior-art 조회 + 종합 점수."""
    fetchers: dict[str, callable] = {
        "pubmed":         lambda: pubmed_count(ctx, mode="compound_disease"),
        "europe_pmc":     lambda: europe_pmc_count(ctx, mode="compound_disease"),
        "chembl":         lambda: chembl_known_activities(ctx),
        "clinicaltrials": lambda: clinicaltrials_count(ctx),
        "lens_patent":    lambda: lens_patent_count(ctx),
    }
    fetchers = {k: v for k, v in fetchers.items() if k in include}

    if parallel:
        with ThreadPoolExecutor(max_workers=len(fetchers)) as ex:
            results = {k: r for k, r in zip(fetchers.keys(),
                                             ex.map(lambda f: f(),
                                                    fetchers.values()))}
    else:
        results = {k: f() for k, f in fetchers.items()}

    # 각 차원 score
    score = NoveltyScore(
        compound_name=ctx.compound_name,
        disease=ctx.disease,
        target=ctx.target_gene,
    )
    score.records = list(results.values())

    score.score_pubmed     = _count_to_novelty(results.get("pubmed",     PriorArtRecord("pubmed")).n_hits)
    score.score_chembl     = _count_to_novelty(results.get("chembl",     PriorArtRecord("chembl")).n_hits, high=20)
    score.score_clinical   = _count_to_novelty(results.get("clinicaltrials", PriorArtRecord("clinicaltrials")).n_hits, high=50)
    score.score_patent     = _count_to_novelty(results.get("lens_patent", PriorArtRecord("lens_patent")).n_hits, high=30)

    # europe_pmc + drugbank — 단순화 (drugbank 미구현은 1.0 default)
    epmc_n = results.get("europe_pmc", PriorArtRecord("europe_pmc")).n_hits
    score_epmc = _count_to_novelty(epmc_n, high=100)

    # composite (weighted)
    composite = 0.0
    weight_sum = 0.0
    for k, w in WEIGHTS.items():
        if k == "pubmed":          s = score.score_pubmed
        elif k == "europe_pmc":    s = score_epmc
        elif k == "chembl":        s = score.score_chembl
        elif k == "clinicaltrials": s = score.score_clinical
        elif k == "lens_patent":   s = score.score_patent
        else:                       s = score.score_drugbank
        composite += s * w
        weight_sum += w
    score.composite_score = composite / weight_sum if weight_sum else 0.0

    if score.composite_score >= 0.7:
        score.classification = "novel"
    elif score.composite_score >= 0.4:
        score.classification = "partially_novel"
    else:
        score.classification = "known"
    return score


def batch_novelty_analysis(
    contexts: list[NoveltyContext],
    *,
    parallel_within: bool = True,
) -> list[NoveltyScore]:
    """여러 (화합물, 질병/타겟) 조합 일괄 분석."""
    out = []
    for i, ctx in enumerate(contexts, 1):
        print(f"  [{i}/{len(contexts)}] {ctx.compound_name} × {ctx.disease}")
        out.append(compute_novelty_score(ctx, parallel=parallel_within))
    return out


def to_dataframe(scores: list[NoveltyScore]) -> pd.DataFrame:
    rows = []
    for s in scores:
        records_by_src = {r.source: r for r in s.records}
        rows.append({
            "compound": s.compound_name,
            "disease": s.disease,
            "target": s.target,
            "novelty_composite": round(s.composite_score, 3),
            "classification": s.classification,
            "pubmed_hits": records_by_src.get("pubmed",
                                              PriorArtRecord("pubmed")).n_hits,
            "europe_pmc_hits": records_by_src.get("europe_pmc",
                                                  PriorArtRecord("europe_pmc")).n_hits,
            "chembl_hits": records_by_src.get("chembl",
                                              PriorArtRecord("chembl")).n_hits,
            "chembl_notable": records_by_src.get("chembl",
                                                  PriorArtRecord("chembl")).notable_finding,
            "clinical_hits": records_by_src.get("clinicaltrials",
                                                PriorArtRecord("clinicaltrials")).n_hits,
            "patent_hits": records_by_src.get("lens_patent",
                                              PriorArtRecord("lens_patent")).n_hits,
        })
    return pd.DataFrame(rows)
