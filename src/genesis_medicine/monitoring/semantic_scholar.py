"""Semantic Scholar API (free tier, key 없이 사용 가능).

가장 광범위한 학술 검색. PubMed 외 conference proceedings, ArXiv 등 포함.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

CACHE = Path.home() / "genesis_medicine" / ".cache" / "monitoring" / "s2"
CACHE.mkdir(parents=True, exist_ok=True)


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
    r = requests.get(url, params=params, timeout=30)
    if r.status_code == 429:
        # rate limit
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
