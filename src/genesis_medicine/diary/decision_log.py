"""의사결정 자동 로그 (yaml append-only)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

LOG_DIR = Path.home() / "genesis_medicine" / ".cache" / "diary"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_LOG = LOG_DIR / "decision_log.jsonl"


@dataclass
class DecisionEntry:
    timestamp: str
    category: str        # "pivot" | "pilot" | "hit_selection" | "config" | "external"
    summary: str         # 1-2 문장
    rationale: str = ""
    evidence: list[str] = field(default_factory=list)
    related_files: list[str] = field(default_factory=list)
    session_id: str | None = None


def log_decision(category: str, summary: str, rationale: str = "",
                 evidence: list[str] | None = None,
                 related_files: list[str] | None = None,
                 session_id: str | None = None,
                 log_path: Path | None = None) -> Path:
    """append-only 의사결정 로그."""
    entry = DecisionEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        category=category,
        summary=summary,
        rationale=rationale,
        evidence=evidence or [],
        related_files=related_files or [],
        session_id=session_id,
    )
    log_path = log_path or DEFAULT_LOG
    with log_path.open("a") as f:
        f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
    return log_path


def list_recent_decisions(n: int = 20, category: str | None = None,
                          log_path: Path | None = None) -> list[DecisionEntry]:
    """최근 N개 의사결정 (역순)."""
    log_path = log_path or DEFAULT_LOG
    if not log_path.exists():
        return []
    lines = log_path.read_text().strip().splitlines()
    out = []
    for line in reversed(lines):
        if not line:
            continue
        d = json.loads(line)
        if category and d.get("category") != category:
            continue
        out.append(DecisionEntry(**d))
        if len(out) >= n:
            break
    return out
