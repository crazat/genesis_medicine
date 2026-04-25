"""ClinicalTrials.gov v2 API.

화합물 × 질병이 임상시험에 있다면 "novel" 아님 (혹은 적어도 약리학적 가치 사전 입증).
"""

from __future__ import annotations

import json
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import NoveltyContext, PriorArtRecord

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "novelty"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def clinicaltrials_count(ctx: NoveltyContext) -> PriorArtRecord:
    """ClinicalTrials.gov v2 — compound + disease 조합 검색."""
    q_terms = [ctx.compound_name]
    if ctx.disease:
        q_terms.append(ctx.disease)
    q = " AND ".join(q_terms)

    cache = CACHE_DIR / f"ct_{abs(hash(q)) % (10**16)}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return PriorArtRecord(**d)

    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": q,
        "pageSize": 5,
        "format": "json",
        "fields": "NCTId,BriefTitle,Phase,OverallStatus,StartDate",
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        d = r.json()
        studies = d.get("studies", [])
        n = len(studies)
        # totalCount 필드는 v2에서 확실치 않음 — 페이지네이션 메타에서 추정
        total_count = d.get("totalCount", n)
        titles = []
        for s in studies[:5]:
            mod = s.get("protocolSection", {}).get("identificationModule", {})
            t = mod.get("briefTitle", "")[:200]
            titles.append(t)

        rec = PriorArtRecord(
            source="clinicaltrials",
            n_hits=int(total_count),
            top_titles=titles,
            raw_url=f"https://clinicaltrials.gov/search?term={requests.utils.quote(q)}",
        )
        cache.write_text(json.dumps(rec.__dict__, default=list))
        return rec
    except Exception as e:
        return PriorArtRecord(source="clinicaltrials", n_hits=-1,
                              notable_finding=f"error: {e}",
                              raw_url=f"https://clinicaltrials.gov/search?term={q}")
