"""PubMed E-utilities + Europe PMC 검색.

학술 출판 표준 prior-art 검증의 1순위. 화합물 × 질병 (또는 화합물 × 타겟) 조합으로
출판된 paper 수와 핵심 abstract를 가져와 novelty 평가.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ._ncbi_auth import ncbi_params, ncbi_sleep_seconds
from .base import NoveltyContext, PriorArtRecord

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "novelty"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _build_query(ctx: NoveltyContext, mode: str = "compound_disease") -> str:
    """검색 쿼리 빌드. compound + disease (or target).

    PubMed 문법:
      ("Embelin"[All Fields] OR "embelia"[All Fields])
      AND ("hypertrophic scar"[Mesh] OR "keloid"[Mesh])
    """
    comp_terms = [f'"{ctx.compound_name}"[All Fields]']
    for syn in ctx.compound_synonyms:
        comp_terms.append(f'"{syn}"[All Fields]')
    comp_q = "(" + " OR ".join(comp_terms) + ")"

    if mode == "compound_disease" and ctx.disease:
        disease_terms = [f'"{ctx.disease}"[All Fields]']
        for syn in ctx.disease_synonyms:
            disease_terms.append(f'"{syn}"[All Fields]')
        disease_q = "(" + " OR ".join(disease_terms) + ")"
        return f"{comp_q} AND {disease_q}"
    if mode == "compound_target" and ctx.target_gene:
        target_terms = [f'"{ctx.target_gene}"[All Fields]']
        for syn in ctx.target_synonyms:
            target_terms.append(f'"{syn}"[All Fields]')
        target_q = "(" + " OR ".join(target_terms) + ")"
        return f"{comp_q} AND {target_q}"
    return comp_q


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=20))
def _esearch(query: str, retmax: int = 20) -> dict:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed", "term": query, "retmax": retmax,
        "retmode": "json", "sort": "relevance",
        **ncbi_params(),
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("esearchresult", {})


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=20))
def _efetch_titles(pmids: list[str]) -> list[str]:
    if not pmids:
        return []
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "json",
              **ncbi_params()}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json().get("result", {})
    titles = []
    for pmid in pmids:
        item = data.get(pmid, {})
        if isinstance(item, dict) and "title" in item:
            titles.append(item["title"])
    return titles


def pubmed_count(ctx: NoveltyContext, mode: str = "compound_disease",
                  fetch_titles: bool = True) -> PriorArtRecord:
    """PubMed에서 prior-art 카운트 + 상위 5개 title.

    mode: "compound_disease" | "compound_target"
    """
    q = _build_query(ctx, mode=mode)
    cache_key = f"pubmed_{abs(hash((q, mode))) % (10**16)}.json"
    cache = CACHE_DIR / cache_key
    if cache.exists():
        d = json.loads(cache.read_text())
        return PriorArtRecord(**d)

    try:
        es = _esearch(q, retmax=5)
        n_hits = int(es.get("count", 0))
        pmids = es.get("idlist", [])
        titles = _efetch_titles(pmids[:5]) if fetch_titles and pmids else []
        time.sleep(ncbi_sleep_seconds())  # 키 있으면 10/s, 없으면 3/s
    except Exception as e:
        return PriorArtRecord(source="pubmed", n_hits=-1,
                              notable_finding=f"error: {e}",
                              raw_url=f"https://pubmed.ncbi.nlm.nih.gov/?term={q}")

    rec = PriorArtRecord(
        source="pubmed",
        n_hits=n_hits,
        top_titles=titles[:5],
        raw_url=f"https://pubmed.ncbi.nlm.nih.gov/?term={requests.utils.quote(q)}",
    )
    cache.write_text(json.dumps(rec.__dict__, default=list))
    return rec


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=20))
def europe_pmc_count(ctx: NoveltyContext, mode: str = "compound_disease") -> PriorArtRecord:
    """Europe PMC REST — 더 넓은 full-text 검색.

    문법은 다르지만 결과 비교에 가치.
    """
    if mode == "compound_disease" and ctx.disease:
        q = f'"{ctx.compound_name}" AND "{ctx.disease}"'
    elif mode == "compound_target" and ctx.target_gene:
        q = f'"{ctx.compound_name}" AND "{ctx.target_gene}"'
    else:
        q = f'"{ctx.compound_name}"'
    cache = CACHE_DIR / f"epmc_{abs(hash((q, mode))) % (10**16)}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return PriorArtRecord(**d)

    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {"query": q, "format": "json", "pageSize": 5,
              "resultType": "lite"}
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        d = r.json()
        n_hits = int(d.get("hitCount", 0))
        results = d.get("resultList", {}).get("result", [])
        titles = [hit.get("title", "")[:200] for hit in results[:5]]
        time.sleep(0.2)
    except Exception as e:
        return PriorArtRecord(source="europe_pmc", n_hits=-1,
                              notable_finding=f"error: {e}",
                              raw_url=f"https://europepmc.org/search?query={q}")

    rec = PriorArtRecord(
        source="europe_pmc",
        n_hits=n_hits,
        top_titles=titles,
        raw_url=f"https://europepmc.org/search?query={requests.utils.quote(q)}",
    )
    cache.write_text(json.dumps(rec.__dict__, default=list))
    return rec
