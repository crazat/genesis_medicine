"""세션 종료 시 자동 요약 생성."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .decision_log import list_recent_decisions


def generate_session_summary(session_id: str | None = None,
                             since: datetime | None = None,
                             out_path: Path | None = None) -> str:
    """현재 세션 또는 일정 시점 이후의 의사결정 요약."""
    decisions = list_recent_decisions(n=200)
    if since:
        decisions = [d for d in decisions
                     if datetime.fromisoformat(d.timestamp) >= since]
    if session_id:
        decisions = [d for d in decisions if d.session_id == session_id]

    by_cat: dict[str, list] = {}
    for d in decisions:
        by_cat.setdefault(d.category, []).append(d)

    md = ["# 세션 요약", "",
          f"생성: {datetime.now().isoformat(timespec='seconds')}",
          f"의사결정 수: {len(decisions)}", ""]
    for cat in ("pivot", "pilot", "hit_selection", "config", "external", "other"):
        items = by_cat.get(cat, [])
        if not items:
            continue
        md.append(f"## {cat} ({len(items)})")
        for d in items[:10]:
            md.append(f"- **{d.timestamp[5:16]}** — {d.summary}")
            if d.rationale:
                md.append(f"  - *근거*: {d.rationale}")
        md.append("")

    text = "\n".join(md)
    if out_path:
        out_path.write_text(text, encoding="utf-8")
    return text
