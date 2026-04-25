"""KCI (한국학술지인용색인) 검색.

공식 API가 제한적이므로 검색 URL만 제공 (수동 확인 또는 web scraping 필요).
한방 paper의 한국어 검색에 핵심.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import requests

CACHE = Path.home() / "genesis_medicine" / ".cache" / "monitoring" / "kci"
CACHE.mkdir(parents=True, exist_ok=True)


def kci_search(query: str) -> dict:
    """KCI 검색 URL 제공 (수동 검증).

    공식 API는 NRF가 제공하지만 IP 등록 필요. 여기서는 URL only.
    추후 자동화는 NRF KCI Open API key 발급 후 (무료):
    https://www.kci.go.kr/kciportal/po/openapi/openApiList.kci
    """
    cache = CACHE / f"{abs(hash(query)) % 10**16}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    base = "https://www.kci.go.kr/kciportal/po/search/poArtiSear.kci"
    url = f"{base}?query={quote(query)}"
    result = {
        "query": query,
        "search_url": url,
        "n_hits": -1,   # API key 필요
        "note": "KCI Open API key 발급 후 자동 카운트 가능 — 현재는 URL만",
    }
    cache.write_text(json.dumps(result, ensure_ascii=False))
    return result
