"""임상 모듈 단위 테스트."""

from __future__ import annotations

import pytest


def test_clinical_context_default():
    from genesis_medicine.clinical import ClinicalContext
    ctx = ClinicalContext(title="흉터 외용제 시험")
    assert ctx.n_subjects == 30
    assert ctx.duration_weeks == 12
    assert "TGF" in ctx.in_silico_evidence or "Boltz" in ctx.in_silico_evidence


def test_irb_protocol_generation():
    from genesis_medicine.clinical import (ClinicalContext, generate_irb_protocol,
                                            generate_consent_form_korean,
                                            generate_consent_form_english)
    ctx = ClinicalContext(
        title="자운고-기반 외용제 vs 표준치료 (위축성 흉터)",
        pi_name="홍길동", n_subjects=40,
    )
    p = generate_irb_protocol(ctx)
    assert "임상시험 프로토콜" in p
    assert "자운고" in p
    assert "40명" in p or "40" in p
    ck = generate_consent_form_korean(ctx)
    assert "동의서" in ck
    ce = generate_consent_form_english(ctx)
    assert "Informed Consent" in ce


def test_cro_quote_minimum():
    from genesis_medicine.clinical import recommend_assays, estimate_total_cost
    rec = recommend_assays("scar", n_top_hits=5)
    assert "scar" in rec
    assert "general_safety" in rec
    assert len(rec["scar"]) >= 3

    est = estimate_total_cost("scar", n_top_hits=5, tier="standard")
    assert est["total_krw"] > 1_000_000
    assert len(est["breakdown"]) >= 3


def test_cro_render_markdown():
    from genesis_medicine.clinical import estimate_total_cost
    from genesis_medicine.clinical.cro_quote import render_quote_markdown

    est = estimate_total_cost("pigment", n_top_hits=10, tier="standard")
    md = render_quote_markdown(est)
    assert "in vitro" in md.lower() or "견적서" in md
    assert "Tyrosinase" in md or "Mushroom" in md
