"""Conflict detector — 새 paper로 우리 결론이 뒤집히는지 자동 감지.

monitoring + novelty 위에 layered. 우리 핵심 hits에 대해 부정적 보고가 새로
나오면 alert.
"""

from .regression_detector import (
    Hypothesis,
    HypothesisCheck,
    check_against_papers,
    monitor_main_hypotheses,
)

__all__ = [
    "Hypothesis", "HypothesisCheck",
    "check_against_papers", "monitor_main_hypotheses",
]
