"""자연어 → workflow 매개 layer.

사용자 자연어 요청을 표준 intent JSON으로 파싱 + workflow YAML을 자동 생성.
LLM 없이 키워드 매칭 기반 — 빠르고 결정적.
"""

from .parser import (
    Intent,
    parse_intent,
    INTENT_TEMPLATES,
)
from .workflow_builder import build_workflow, intent_to_command

__all__ = [
    "Intent", "parse_intent", "INTENT_TEMPLATES",
    "build_workflow", "intent_to_command",
]
