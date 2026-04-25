"""Novelty 패키지 단위 테스트.

네트워크 호출 테스트는 @pytest.mark.network로 표시 (CI에서 skip 가능).
"""

from __future__ import annotations

from pathlib import Path

import pytest


def test_novelty_context_basic() -> None:
    from genesis_medicine.novelty import NoveltyContext

    ctx = NoveltyContext(
        compound_name="Curcumin",
        disease="hypertrophic scar",
        target_uniprot="P01137",
        target_gene="TGFB1",
    )
    assert ctx.compound_name == "Curcumin"
    assert ctx.disease == "hypertrophic scar"


def test_prior_art_record_defaults() -> None:
    from genesis_medicine.novelty.base import PriorArtRecord

    rec = PriorArtRecord(source="pubmed", n_hits=5, top_titles=["X", "Y"])
    assert rec.source == "pubmed"
    assert rec.n_hits == 5
    assert len(rec.top_titles) == 2


def test_count_to_novelty_score() -> None:
    from genesis_medicine.novelty.novelty_score import _count_to_novelty

    assert _count_to_novelty(0) == 1.0       # 완전 novel
    assert _count_to_novelty(-1) == 0.5      # 에러는 중립
    s5 = _count_to_novelty(5)
    s50 = _count_to_novelty(50)
    s200 = _count_to_novelty(200)
    assert 0.5 < s5 < 1.0
    assert 0.0 < s50 < s5
    assert s200 < s50


def test_novelty_score_classification() -> None:
    from genesis_medicine.novelty import NoveltyScore

    score = NoveltyScore(compound_name="X", disease="Y", composite_score=0.8)
    score.classification = "novel" if score.composite_score >= 0.7 else "partially_novel"
    assert score.classification == "novel"

    explanation = NoveltyScore(
        compound_name="X", disease="Y",
        composite_score=0.8, classification="novel"
    ).explanation()
    assert "novel" in explanation.lower() or "발견" in explanation


def test_render_prior_art_table_empty() -> None:
    from genesis_medicine.novelty import render_prior_art_table
    md = render_prior_art_table([])
    assert "Compound" in md
    assert "Composite" in md


@pytest.mark.network
def test_pubmed_count_real_query() -> None:
    """실 PubMed 호출 — Curcumin × hypertrophic scar (잘 알려진 조합)."""
    from genesis_medicine.novelty import NoveltyContext, pubmed_count

    ctx = NoveltyContext(
        compound_name="Curcumin",
        disease="hypertrophic scar",
    )
    rec = pubmed_count(ctx, mode="compound_disease", fetch_titles=False)
    # Curcumin × HTS는 수십~수백개 보고됨
    assert rec.source == "pubmed"
    if rec.n_hits >= 0:  # network OK
        assert rec.n_hits >= 5, f"unexpectedly few hits: {rec.n_hits}"


@pytest.mark.network
def test_compute_novelty_score_real() -> None:
    """End-to-end novelty — 실 네트워크."""
    from genesis_medicine.novelty import NoveltyContext, compute_novelty_score

    ctx = NoveltyContext(
        compound_name="Curcumin",
        disease="hypertrophic scar",
        target_uniprot="P01137",
        target_gene="TGFB1",
    )
    score = compute_novelty_score(ctx, parallel=True)
    assert score.compound_name == "Curcumin"
    assert 0.0 <= score.composite_score <= 1.0
    assert score.classification in ("novel", "partially_novel", "known")
    assert len(score.records) >= 3   # pubmed + epmc + chembl + clinical + patent
