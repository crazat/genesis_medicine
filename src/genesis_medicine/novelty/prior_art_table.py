"""Prior-art 표 + manuscript 섹션 자동 생성."""

from __future__ import annotations

from .base import NoveltyScore


def render_prior_art_table(scores: list[NoveltyScore]) -> str:
    """학술 paper용 markdown 표 (Discussion 섹션에 삽입)."""
    rows = []
    rows.append(
        "| Compound | PubMed | EuropePMC | ChEMBL | Clinical | Patent | "
        "Composite | Class |"
    )
    rows.append("|----------|-------:|----------:|-------:|---------:|-------:|----------:|-------|")
    for s in scores:
        rec = {r.source: r for r in s.records}
        rows.append(
            f"| {s.compound_name} | "
            f"{rec.get('pubmed', _empty()).n_hits} | "
            f"{rec.get('europe_pmc', _empty()).n_hits} | "
            f"{rec.get('chembl', _empty()).n_hits} | "
            f"{rec.get('clinicaltrials', _empty()).n_hits} | "
            f"{rec.get('lens_patent', _empty()).n_hits} | "
            f"**{s.composite_score:.2f}** | "
            f"{_emoji(s.classification)} {s.classification} |"
        )
    return "\n".join(rows)


def _empty():
    from .base import PriorArtRecord
    return PriorArtRecord(source="?", n_hits=0)


def _emoji(cls: str) -> str:
    return {"novel": "🆕", "partially_novel": "🟡", "known": "📚"}.get(cls, "")


def render_novelty_section(scores: list[NoveltyScore], disease: str = "") -> str:
    """Discussion 섹션에 들어갈 통합 markdown."""
    n_novel = sum(1 for s in scores if s.classification == "novel")
    n_partial = sum(1 for s in scores if s.classification == "partially_novel")
    n_known = sum(1 for s in scores if s.classification == "known")

    out = [f"### Novelty assessment of top hits", ""]
    out.append(
        f"본 연구가 도출한 상위 {len(scores)}개 후보에 대해 PubMed, Europe PMC, "
        f"ChEMBL bioactivity, ClinicalTrials.gov, Lens.org/Google Patents의 "
        f"5개 데이터 소스를 조회하여 prior-art을 정량 평가했다."
    )
    out.append("")
    out.append(f"전체 평가 결과: **{n_novel}개 novel** (composite ≥ 0.7), "
               f"{n_partial}개 partially novel (0.4-0.7), "
               f"{n_known}개 known (< 0.4).")
    out.append("")
    out.append(render_prior_art_table(scores))
    out.append("")

    # 각 화합물별 자연어 설명
    out.append("**핵심 화합물별 해석:**")
    out.append("")
    for s in scores[:10]:  # 상위 10개만
        out.append(f"- {s.explanation()}")
    return "\n".join(out)
