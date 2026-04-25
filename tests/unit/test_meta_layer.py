"""Meta-layer 모듈 단위 테스트 (monitoring/intent/diary/conflict).

네트워크 호출 테스트는 @pytest.mark.network로 별도.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---- Intent parser ----
def test_intent_parse_pilot_korean():
    from genesis_medicine.intent import parse_intent
    intent = parse_intent("흉터 파일럿 돌려줘")
    assert intent.intent_type == "run_pilot"
    assert intent.slots.get("disease") == "scar"
    assert intent.confidence > 0


def test_intent_parse_md_english():
    from genesis_medicine.intent import parse_intent
    intent = parse_intent("MD molecular dynamics 안정성 검증 Embelin")
    assert intent.intent_type == "run_md"
    assert intent.slots.get("compound") == "Embelin"


def test_intent_parse_unknown():
    from genesis_medicine.intent import parse_intent
    intent = parse_intent("?? 모름")
    assert intent.intent_type == "unknown"
    assert intent.suggestions


def test_intent_to_command():
    from genesis_medicine.intent import parse_intent, intent_to_command
    intent = parse_intent("기미 파일럿")
    cmd = intent_to_command(intent)
    assert cmd["command"] is not None
    assert cmd["expected_minutes"] > 0


def test_workflow_builder():
    from genesis_medicine.intent import parse_intent
    from genesis_medicine.intent.workflow_builder import build_workflow
    intents = [parse_intent("흉터 파일럿"), parse_intent("manuscript 작성")]
    wf = build_workflow(intents)
    assert wf["n_steps"] == 2
    assert wf["total_expected_minutes"] > 0


# ---- Decision log ----
def test_log_decision_append(tmp_path):
    from genesis_medicine.diary.decision_log import (
        log_decision, list_recent_decisions,
    )
    log = tmp_path / "log.jsonl"
    log_decision("pivot", "흉터 → 기미 우선", "blue ocean novelty",
                 log_path=log)
    log_decision("pilot", "기미 파일럿 완료",
                 evidence=["pigment_consensus.csv"], log_path=log)
    items = list_recent_decisions(n=10, log_path=log)
    assert len(items) == 2
    assert items[0].category in ("pivot", "pilot")


# ---- Session summary ----
def test_session_summary(tmp_path):
    from genesis_medicine.diary import (log_decision,
                                         generate_session_summary)
    log = tmp_path / "log.jsonl"
    log_decision("pilot", "흉터", log_path=log)
    log_decision("hit_selection", "Embelin", log_path=log)
    md = generate_session_summary(out_path=tmp_path / "summary.md")
    assert "세션 요약" in md
    # decision_log가 default path 사용 시 비어있을 수 있으므로 raw 확인 only


# ---- Conflict detector logic ----
def test_classify_paper():
    from genesis_medicine.conflict.regression_detector import _classify_paper
    assert _classify_paper("Embelin inhibits TGF-beta") == "supporting"
    assert _classify_paper("Embelin shows no effect") == "contradicting"
    assert _classify_paper("Embelin was investigated") == "neutral"


# ---- Network-marked tests ----
@pytest.mark.network
def test_biorxiv_recent():
    from genesis_medicine.monitoring import biorxiv_recent
    out = biorxiv_recent(["centella scar"], days=14, max_papers=20)
    assert isinstance(out, list)


@pytest.mark.network
def test_semantic_scholar_search():
    from genesis_medicine.monitoring import semantic_scholar_search
    out = semantic_scholar_search("centella asiatica scar", limit=5)
    assert isinstance(out, dict)
    assert "data" in out


@pytest.mark.network
def test_check_hypothesis():
    from genesis_medicine.conflict import (Hypothesis, check_against_papers)
    h = Hypothesis(name="test", statement="?",
                   keywords=["centella asiatica scar"])
    chk = check_against_papers(h, max_papers=5)
    assert chk.alert_level in ("ok", "warning", "critical")
