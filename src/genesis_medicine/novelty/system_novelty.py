"""시스템·방법론 단위 novelty 검증.

화합물 단위 (compound × disease)와 별개로 **연구 컨셉 자체**가 이미 다른 사람이
한 것인지 검증. 학술 reviewer의 "이미 비슷한 시스템 paper 있다" 지적 사전 차단.

데이터 흐름
-----------
SystemDescriptor (방법론 + 적용분야 + 핵심도구)
  → 다중 키워드 조합 PubMed + EPMC 검색
  → 가까운 prior art top N 추출
  → 우리 시스템과의 차별점 자동 추출
  → manuscript Introduction 자동 섹션
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "novelty" / "system"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SystemDescriptor:
    """우리 시스템의 메타 묘사."""

    # 적용 분야
    disease: str                     # e.g. "skin scar regeneration"
    disease_synonyms: list[str] = field(default_factory=list)

    # 사용 도구·방법론 (각각 PubMed에서 따로 검색됨)
    methods: list[str] = field(default_factory=lambda: [
        "structure-based virtual screening",
        "molecular docking",
        "AI drug discovery",
    ])

    # 데이터 범주
    data_sources: list[str] = field(default_factory=lambda: [
        "Korean traditional medicine",
        "natural products",
    ])

    # 핵심 모델 (구체적 도구명, 우리만의 차별점 부각)
    unique_tools: list[str] = field(default_factory=lambda: [
        "Boltz-2",
        "AlphaFold",
        "ADMET-AI",
    ])

    # 우리 시스템의 unique value proposition (paper 작성 시 강조)
    differentiators: list[str] = field(default_factory=list)


@dataclass
class PriorArtTopic:
    """단일 키워드 조합 검색 결과."""

    label: str              # 사람이 읽는 검색 카테고리 이름
    pubmed_query: str
    epmc_query: str
    pubmed_hits: int = 0
    epmc_hits: int = 0
    top_titles: list[str] = field(default_factory=list)
    top_pmids: list[str] = field(default_factory=list)
    closest_match: str | None = None  # 가장 가까운 prior art

    @property
    def total_hits(self) -> int:
        return max(self.pubmed_hits, 0) + max(self.epmc_hits, 0)


@dataclass
class SystemNoveltyReport:
    """시스템 단위 novelty 종합 평가."""

    descriptor: SystemDescriptor
    topics: list[PriorArtTopic]

    closest_prior_art: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)
    novelty_summary: str = ""
    composite_score: float = 1.0   # 0=레드오션, 1=블루오션


def _build_topic_queries(d: SystemDescriptor) -> list[tuple[str, str, str]]:
    """다양한 키워드 조합 (label, pubmed_query, epmc_query)."""
    out: list[tuple[str, str, str]] = []

    # 1. 정확히 우리 시스템 = 데이터 + 방법론 + 질환
    for ds in d.data_sources[:2]:
        for m in d.methods[:2]:
            label = f"{ds} × {m} × {d.disease}"
            pm_q = (f'"{ds}"[All Fields] AND "{m}"[All Fields] AND '
                    f'"{d.disease}"[All Fields]')
            ep_q = f'"{ds}" AND "{m}" AND "{d.disease}"'
            out.append((label, pm_q, ep_q))

    # 2. unique tool × 질환 (Boltz-2 × scar 등)
    for tool in d.unique_tools[:3]:
        label = f"{tool} × {d.disease}"
        pm_q = f'"{tool}"[All Fields] AND "{d.disease}"[All Fields]'
        ep_q = f'"{tool}" AND "{d.disease}"'
        out.append((label, pm_q, ep_q))

    # 3. 데이터 + 질환 (한방 + 흉터 일반)
    for ds in d.data_sources:
        label = f"{ds} × {d.disease}"
        pm_q = f'"{ds}"[All Fields] AND "{d.disease}"[All Fields]'
        ep_q = f'"{ds}" AND "{d.disease}"'
        out.append((label, pm_q, ep_q))

    # 4. 종합: 데이터 + 방법론 (적용 분야 무관 — 기존 시스템 paper)
    for ds in d.data_sources[:1]:
        for m in d.methods[:1]:
            label = f"{ds} × {m} (general system)"
            pm_q = (f'"{ds}"[All Fields] AND "{m}"[All Fields]')
            ep_q = f'"{ds}" AND "{m}"'
            out.append((label, pm_q, ep_q))
    return out


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _pubmed(query: str) -> tuple[int, list[str], list[str]]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r = requests.get(url, params={"db": "pubmed", "term": query, "retmax": 5,
                                   "retmode": "json", "sort": "relevance"},
                     timeout=30)
    r.raise_for_status()
    es = r.json().get("esearchresult", {})
    n = int(es.get("count", 0))
    pmids = es.get("idlist", [])
    titles: list[str] = []
    if pmids:
        s = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": ",".join(pmids), "retmode": "json"},
            timeout=30,
        ).json().get("result", {})
        for pid in pmids:
            it = s.get(pid, {})
            if isinstance(it, dict) and "title" in it:
                titles.append(it["title"][:160])
    return n, titles, pmids


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _epmc(query: str) -> tuple[int, list[str]]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    r = requests.get(url, params={"query": query, "format": "json",
                                   "pageSize": 3, "resultType": "lite"}, timeout=30)
    r.raise_for_status()
    d = r.json()
    n = int(d.get("hitCount", 0))
    titles = [hit.get("title", "")[:160]
              for hit in d.get("resultList", {}).get("result", [])[:3]]
    return n, titles


def _topic_to_record(label: str, pm_q: str, ep_q: str) -> PriorArtTopic:
    cache = CACHE_DIR / f"sys_{abs(hash((pm_q, ep_q))) % (10**16)}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return PriorArtTopic(**d)
    topic = PriorArtTopic(label=label, pubmed_query=pm_q, epmc_query=ep_q)
    try:
        topic.pubmed_hits, topic.top_titles, topic.top_pmids = _pubmed(pm_q)
    except Exception:
        topic.pubmed_hits = -1
    try:
        n, ep_titles = _epmc(ep_q)
        topic.epmc_hits = n
        for t in ep_titles:
            if t not in topic.top_titles:
                topic.top_titles.append(t)
    except Exception:
        topic.epmc_hits = -1
    if topic.top_titles:
        topic.closest_match = topic.top_titles[0]
    cache.write_text(json.dumps(topic.__dict__))
    return topic


def evaluate_system_novelty(d: SystemDescriptor) -> SystemNoveltyReport:
    """시스템 단위 novelty 종합 평가 (병렬 검색)."""
    queries = _build_topic_queries(d)
    print(f"[system_novelty] {len(queries)} 토픽 검색 (병렬)")
    with ThreadPoolExecutor(max_workers=min(8, len(queries))) as ex:
        topics = list(ex.map(
            lambda t: _topic_to_record(*t), queries
        ))

    # closest prior art = pubmed_hits > 0 면서 disease와 method 둘 다 포함된 것
    closest = []
    for t in topics:
        if t.pubmed_hits > 0 and t.closest_match:
            closest.append(t.closest_match)
    closest = list(dict.fromkeys(closest))[:5]   # dedup, top 5

    # composite — pubmed direct combo (1번 그룹) 평균 hit log scale
    direct_hits = [t.pubmed_hits for t in topics
                   if "system" not in t.label.lower() and t.pubmed_hits >= 0]
    import math
    if direct_hits:
        avg = sum(direct_hits) / len(direct_hits)
        composite = max(0.0, 1.0 - math.log1p(avg) / math.log1p(50))
    else:
        composite = 0.5

    if composite >= 0.7:
        cls = "blue ocean (거의 첫 시도)"
    elif composite >= 0.4:
        cls = "competitive (인접 paper 다수)"
    else:
        cls = "red ocean (이미 활발히 연구됨)"

    summary = (
        f"본 시스템({d.disease} 대상 {' + '.join(d.unique_tools[:3])} 통합)은 "
        f"{cls} 영역에 위치한다 (composite system-novelty = {composite:.2f}). "
        f"가까운 prior art {len(closest)}건 식별, 차별점은 {len(d.differentiators)}개로 정리됨."
    )

    return SystemNoveltyReport(
        descriptor=d,
        topics=topics,
        closest_prior_art=closest,
        differentiators=d.differentiators,
        novelty_summary=summary,
        composite_score=composite,
    )


def render_system_novelty_section(report: SystemNoveltyReport) -> str:
    """manuscript Introduction에 들어갈 markdown 섹션."""
    d = report.descriptor
    out = ["### Prior systems and our differentiation", ""]
    out.append(report.novelty_summary)
    out.append("")
    out.append("**검색된 인접 prior art:**")
    for i, p in enumerate(report.closest_prior_art, 1):
        out.append(f"{i}. {p}")
    if not report.closest_prior_art:
        out.append("- 동일 시스템 paper 없음.")
    out.append("")
    out.append("**우리 시스템의 차별점:**")
    if report.differentiators:
        for d_ in report.differentiators:
            out.append(f"- {d_}")
    else:
        out.append("- (사용자 입력 필요)")
    out.append("")
    # 토픽별 hit 표
    out.append("| 검색 토픽 | PubMed | EuropePMC | 합계 |")
    out.append("|-----------|-------:|----------:|-----:|")
    for t in report.topics:
        out.append(f"| {t.label} | {t.pubmed_hits} | {t.epmc_hits} | "
                   f"{t.total_hits if t.total_hits >= 0 else '-'} |")
    return "\n".join(out)
