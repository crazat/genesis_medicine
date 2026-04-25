"""bioRxiv / medRxiv API 모니터링.

API: https://api.biorxiv.org/details/biorxiv/{date_from}/{date_to}/{cursor}
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

CACHE = Path.home() / "genesis_medicine" / ".cache" / "monitoring" / "biorxiv"
CACHE.mkdir(parents=True, exist_ok=True)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_biorxiv(server: str, date_from: str, date_to: str, cursor: int = 0) -> dict:
    url = f"https://api.biorxiv.org/details/{server}/{date_from}/{date_to}/{cursor}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def _filter_keywords(papers: list[dict], keywords: list[str]) -> list[dict]:
    """abstract + title에 키워드 포함된 paper만 필터."""
    out = []
    kw_lower = [k.lower() for k in keywords]
    for p in papers:
        text = (p.get("title", "") + " " + p.get("abstract", "")).lower()
        if any(k in text for k in kw_lower):
            out.append(p)
    return out


def biorxiv_recent(keywords: list[str], *, days: int = 7,
                   server: str = "biorxiv", max_papers: int = 200) -> list[dict]:
    """최근 N일 bioRxiv preprint 중 키워드 매칭.

    실제 API는 모든 paper를 가져온 후 클라이언트 측 filtering이 필요.
    """
    today = date.today()
    date_from = (today - timedelta(days=days)).isoformat()
    date_to = today.isoformat()
    cache_key = f"{server}_{date_from}_{date_to}.json"
    cache_path = CACHE / cache_key

    if cache_path.exists():
        all_papers = json.loads(cache_path.read_text())
    else:
        all_papers = []
        cursor = 0
        while len(all_papers) < max_papers:
            try:
                d = _fetch_biorxiv(server, date_from, date_to, cursor)
                items = d.get("collection", [])
                if not items:
                    break
                all_papers.extend(items)
                msg = d.get("messages", [{}])[0]
                if msg.get("status") != "ok" or len(items) < 100:
                    break
                cursor += 100
            except Exception as e:
                print(f"  biorxiv fetch error at cursor {cursor}: {e}")
                break
        cache_path.write_text(json.dumps(all_papers))

    return _filter_keywords(all_papers, keywords)[:max_papers]


def medrxiv_recent(keywords: list[str], *, days: int = 7,
                   max_papers: int = 200) -> list[dict]:
    return biorxiv_recent(keywords, days=days, server="medrxiv",
                          max_papers=max_papers)
