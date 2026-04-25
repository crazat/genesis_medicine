"""지속적 모니터링 orchestrator.

매일/매주 실행하여 우리 hits·시스템 토픽에 대해 새 paper 자동 감지.
이전 실행과 diff 자동 alert.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from .biorxiv_feed import biorxiv_recent, medrxiv_recent
from .semantic_scholar import semantic_scholar_search
from .kci_search import kci_search

STATE_DIR = Path.home() / "genesis_medicine" / ".cache" / "monitoring" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class MonitoringTopic:
    """단일 모니터링 주제 — 화합물 + 질환 또는 시스템 키워드."""
    name: str                                    # human-readable label
    keywords: list[str] = field(default_factory=list)
    biorxiv: bool = True
    semantic_scholar: bool = True
    kci: bool = False                             # 한국 검색 필요할 때만


@dataclass
class TopicHit:
    title: str
    source: str
    year: int | None = None
    venue: str | None = None
    url: str | None = None
    doi: str | None = None
    abstract: str = ""


@dataclass
class TopicReport:
    topic: str
    biorxiv_hits: list[TopicHit] = field(default_factory=list)
    s2_hits: list[TopicHit] = field(default_factory=list)
    kci_url: str | None = None
    n_total: int = 0


@dataclass
class ContinuousMonitorReport:
    date: str
    topics: list[TopicReport] = field(default_factory=list)
    diff_against_previous: dict | None = None
    n_new_papers: int = 0


def _query_to_hits(papers: list[dict], source: str) -> list[TopicHit]:
    out = []
    for p in papers:
        title = p.get("title", "")
        if isinstance(title, dict):
            title = title.get("name") or str(title)
        # bioRxiv 형식
        doi = p.get("doi") or p.get("DOI")
        # S2 형식
        ext_ids = p.get("externalIds", {})
        if not doi and ext_ids:
            doi = ext_ids.get("DOI")
        out.append(TopicHit(
            title=title[:200] if isinstance(title, str) else str(title)[:200],
            source=source,
            year=p.get("date", "")[:4] if isinstance(p.get("date"), str) else p.get("year"),
            venue=p.get("server") or p.get("venue"),
            url=f"https://doi.org/{doi}" if doi else None,
            doi=doi,
            abstract=(p.get("abstract") or "")[:500],
        ))
    return out


def run_monitoring(topics: list[MonitoringTopic], *,
                   days: int = 7,
                   s2_year_min: int | None = 2025) -> ContinuousMonitorReport:
    """모든 토픽에 대해 새 paper 검색."""
    report = ContinuousMonitorReport(date=date.today().isoformat())
    for t in topics:
        tr = TopicReport(topic=t.name)
        query = " ".join(t.keywords)

        if t.biorxiv:
            try:
                bx = biorxiv_recent(t.keywords, days=days)
                tr.biorxiv_hits = _query_to_hits(bx, "bioRxiv")
            except Exception as e:
                print(f"  biorxiv error [{t.name}]: {e}")

        if t.semantic_scholar:
            try:
                s2 = semantic_scholar_search(query, limit=10, year_min=s2_year_min)
                tr.s2_hits = _query_to_hits(s2.get("data", []), "Semantic Scholar")
            except Exception as e:
                print(f"  s2 error [{t.name}]: {e}")

        if t.kci:
            tr.kci_url = kci_search(query).get("search_url")

        tr.n_total = len(tr.biorxiv_hits) + len(tr.s2_hits)
        report.topics.append(tr)

    return report


def save_state(report: ContinuousMonitorReport, path: Path | None = None) -> Path:
    if path is None:
        path = STATE_DIR / f"state_{report.date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "date": report.date,
        "topics": [
            {
                "topic": t.topic,
                "biorxiv": [{"title": h.title, "doi": h.doi, "url": h.url}
                            for h in t.biorxiv_hits],
                "s2": [{"title": h.title, "doi": h.doi, "url": h.url}
                       for h in t.s2_hits],
                "n_total": t.n_total,
            }
            for t in report.topics
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return path


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def diff_against_state(report: ContinuousMonitorReport,
                       previous_path: Path | None = None) -> dict:
    """가장 최근 state와 비교 → 새로 등장한 paper 식별."""
    if previous_path is None:
        # 가장 최근 state 자동 검색
        candidates = sorted(STATE_DIR.glob("state_*.json"))
        # 오늘 자체 제외
        today_path = STATE_DIR / f"state_{report.date}.json"
        candidates = [c for c in candidates if c != today_path]
        if not candidates:
            return {"is_first_run": True}
        previous_path = candidates[-1]

    prev = load_state(previous_path)
    prev_dois = set()
    for t in prev.get("topics", []):
        for h in t.get("biorxiv", []) + t.get("s2", []):
            if h.get("doi"):
                prev_dois.add(h["doi"])

    new_hits = []
    for t in report.topics:
        for h in t.biorxiv_hits + t.s2_hits:
            if h.doi and h.doi not in prev_dois:
                new_hits.append({
                    "topic": t.topic, "title": h.title, "doi": h.doi,
                    "source": h.source, "url": h.url,
                })

    return {
        "previous_date": prev.get("date"),
        "current_date": report.date,
        "n_new_papers": len(new_hits),
        "new_papers": new_hits,
    }
