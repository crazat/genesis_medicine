"""CLAUDE.md NEXT ACTIONS 자동 갱신.

의사결정 로그 + 최근 결과를 기반으로 NEXT ACTIONS 섹션을 자동 갱신.
사용자가 새 세션을 열 때 살아있는 가이드.
"""

from __future__ import annotations

import re
from pathlib import Path

from .decision_log import list_recent_decisions

ROOT = Path(__file__).resolve().parents[3]
CLAUDEMD = ROOT / "CLAUDE.md"


def update_next_actions(actions: list[str], dry_run: bool = False) -> str | None:
    """CLAUDE.md의 '🟡 다음 즉시 실행' 섹션을 새 actions로 교체.

    actions: 1줄 문자열 list (markdown 호환).
    """
    if not CLAUDEMD.exists():
        return None
    text = CLAUDEMD.read_text(encoding="utf-8")

    # 패턴: '### 🟡 다음 즉시 실행' ~ 다음 '###' 또는 '---'
    pattern = (
        r"(### 🟡 [^\n]*\n)"
        r"(.*?)"
        r"(\n###|\n---)"
    )
    m = re.search(pattern, text, flags=re.DOTALL)
    if not m:
        return text  # 섹션 없으면 변경 안 함

    new_body = "\n".join(f"{i+1}. {a}" for i, a in enumerate(actions)) + "\n"
    new_text = text[:m.start(2)] + "\n" + new_body + text[m.end(2):]

    if dry_run:
        return new_text
    CLAUDEMD.write_text(new_text, encoding="utf-8")
    return new_text


def auto_compose_next_actions(n_recent: int = 5) -> list[str]:
    """최근 결정 + pending 작업으로 NEXT ACTIONS 자동 작성."""
    recents = list_recent_decisions(n=n_recent)
    actions = []
    seen = set()
    for d in recents:
        # category 기반 다음 단계 자동 제안
        if d.category == "pilot" and d.summary not in seen:
            actions.append(f"**{d.summary}** — manuscript 자동 갱신 + ADMET 게이트 재계산")
            seen.add(d.summary)
        elif d.category == "hit_selection":
            actions.append(f"Top hit MD 10ns 검증 ({d.summary})")
    if not actions:
        actions = ["새 의사결정 없음 — 사용자 의도 확인 후 진행"]
    return actions
