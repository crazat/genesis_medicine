"""Research Diary — 의사결정 자동 로그.

매 의사결정·실험 결과·hit 후보 변화를 자동 기록.
세션 종료 시 요약 + CLAUDE.md NEXT ACTIONS 자동 갱신.
"""

from .decision_log import (
    DecisionEntry,
    log_decision,
    list_recent_decisions,
)
from .session_summary import generate_session_summary
from .claudemd_updater import update_next_actions

__all__ = [
    "DecisionEntry", "log_decision", "list_recent_decisions",
    "generate_session_summary", "update_next_actions",
]
