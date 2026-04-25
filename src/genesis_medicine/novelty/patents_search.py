"""특허 검색 — Lens.org Public API (free tier).

API 키 없이 일반 검색 페이지를 통한 가벼운 카운트만 (HTML 파싱).
실제 출시용은 Lens.org / Google Patents BigQuery / EPO OPS 같은
정식 API 사용 권장.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import NoveltyContext, PriorArtRecord

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "novelty"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=10))
def lens_patent_count(ctx: NoveltyContext) -> PriorArtRecord:
    """간단한 Lens.org 검색 — 정식 API 키 없이는 정확도 제한.

    *구현 노트*: Lens.org는 API 키 발급(무료)이 권장. 이 함수는 placeholder로
    "검색 URL만 제공 + n_hits=-1 (확인 필요)" 형태를 반환.
    """
    q_terms = [ctx.compound_name]
    if ctx.disease:
        q_terms.append(ctx.disease)
    q = "+AND+".join(t.replace(" ", "+") for t in q_terms)
    url = f"https://www.lens.org/lens/search/patent/list?q={q}"

    cache = CACHE_DIR / f"lens_{abs(hash(q)) % (10**16)}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return PriorArtRecord(**d)

    rec = PriorArtRecord(
        source="lens_patent",
        n_hits=-1,                     # API 키 없이 정확한 카운트 불가
        notable_finding=("Lens.org API 키 발급 권장 (무료). "
                         "현재는 검색 URL만 제공 — 사용자 수동 확인 필요."),
        raw_url=url,
    )
    cache.write_text(json.dumps(rec.__dict__, default=list))
    return rec


def google_patents_url(ctx: NoveltyContext) -> str:
    """Google Patents 검색 URL (UI 클릭 검증용)."""
    q_terms = [f'"{ctx.compound_name}"']
    if ctx.disease:
        q_terms.append(f'"{ctx.disease}"')
    q = " ".join(q_terms)
    return f"https://patents.google.com/?q={requests.utils.quote(q)}"
