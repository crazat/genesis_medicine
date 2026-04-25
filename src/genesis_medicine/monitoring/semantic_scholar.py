"""Semantic Scholar API (Graph v1).

가장 광범위한 학술 검색. PubMed 외 conference proceedings, ArXiv 등 포함.
환경변수 `SEMANTIC_SCHOLAR_API_KEY` 가 .env에 있으면 자동으로 인증 헤더 첨부
(anonymous 100 req/5min → 키 5,000 req/5min).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .._env import load_dotenv_once

CACHE = Path.home() / "genesis_medicine" / ".cache" / "monitoring" / "s2"
CACHE.mkdir(parents=True, exist_ok=True)


def s2_headers() -> dict[str, str]:
    """API 키가 있으면 x-api-key 헤더 포함."""
    load_dotenv_once()
    h: dict[str, str] = {}
    if k := os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        h["x-api-key"] = k
    return h


def has_s2_key() -> bool:
    load_dotenv_once()
    return bool(os.environ.get("SEMANTIC_SCHOLAR_API_KEY"))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=15))
def semantic_scholar_search(
    query: str,
    *,
    limit: int = 20,
    year_min: int | None = None,
    fields: str = "title,abstract,year,authors,venue,externalIds,citationCount",
) -> dict:
    """Semantic Scholar Graph API search."""
    cache_key = f"s2_{abs(hash((query, limit, year_min))) % 10**16}.json"
    cache_path = CACHE / cache_key
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit, "fields": fields}
    if year_min:
        params["year"] = f"{year_min}-"
    r = requests.get(url, params=params, headers=s2_headers(), timeout=30)
    if r.status_code == 429:
        return {"query": query, "error": "rate limited", "data": []}
    r.raise_for_status()
    d = r.json()
    result = {
        "query": query,
        "total": d.get("total", 0),
        "data": d.get("data", []),
    }
    cache_path.write_text(json.dumps(result))
    return result
