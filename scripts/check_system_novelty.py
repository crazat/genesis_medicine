"""시스템·방법론 단위 novelty 검증.

화합물 단위가 아니라 **컨셉 / 방법론 / 토픽** 단위로 PubMed + Europe PMC를 폭넓게 조회.
"이런 시스템을 누가 이미 만들었나?"에 답하기.
"""

from __future__ import annotations

import sys

import requests

QUERIES = {
    # ---- 한방 + 흉터 + AI 컨셉 자체 ----
    "1. 한방 + 흉터 + virtual screening": (
        '("Korean traditional medicine"[All Fields] OR "한방"[All Fields] OR '
        '"traditional Chinese medicine"[All Fields]) AND '
        '("hypertrophic scar"[All Fields] OR "keloid"[All Fields]) AND '
        '("virtual screening"[All Fields] OR "molecular docking"[All Fields] OR '
        '"in silico"[All Fields])'
    ),
    "2. 자운고/자초 + AI/docking": (
        '("Jaungo"[All Fields] OR "Zicao"[All Fields] OR "shikonin"[All Fields]) AND '
        '("hypertrophic scar"[All Fields] OR "keloid"[All Fields]) AND '
        '("docking"[All Fields] OR "molecular"[All Fields] OR "AI"[All Fields])'
    ),
    "3. 천연물 라이브러리 + 흉터 multi-target": (
        '("natural products"[All Fields]) AND '
        '("hypertrophic scar"[All Fields] OR "keloid"[All Fields] OR '
        '"scar formation"[All Fields]) AND '
        '("multi-target"[All Fields] OR "multitarget"[All Fields] OR '
        '"network pharmacology"[All Fields])'
    ),
    "4. AlphaFold/Boltz + 흉터": (
        '("AlphaFold"[All Fields] OR "Boltz-2"[All Fields] OR "Boltz2"[All Fields]) AND '
        '("scar"[All Fields] OR "fibrosis"[All Fields])'
    ),
    "5. 한방 처방 (자운고 등) network pharmacology": (
        '("Jaungo"[All Fields] OR "Sa-mul-tang"[All Fields] OR '
        '"Hwang-ryeon-hae-dok-tang"[All Fields] OR "Danggui"[All Fields]) AND '
        '"network pharmacology"[All Fields]'
    ),
    "6. KHP + AI 신약개발": (
        '("Korean Herbal Pharmacopoeia"[All Fields] OR "KHP"[All Fields]) AND '
        '("drug discovery"[All Fields] OR "in silico"[All Fields])'
    ),
    "7. centella + scar + TGF + docking": (
        '"Centella asiatica"[All Fields] AND '
        '("scar"[All Fields] OR "TGF"[All Fields]) AND '
        '("docking"[All Fields] OR "in silico"[All Fields])'
    ),
    "8. 흉터 재생 한약 외용제 분자수준": (
        '("scar"[All Fields] OR "wound healing"[All Fields]) AND '
        '("topical"[All Fields] OR "외용"[All Fields]) AND '
        '("herbal"[All Fields] OR "phytochemical"[All Fields]) AND '
        '("TGF-beta"[All Fields] OR "MMP"[All Fields] OR "collagen"[All Fields])'
    ),
    "9. AI + Korean medicine drug discovery (general)": (
        '("Korean medicine"[All Fields] OR "한의학"[All Fields]) AND '
        '("artificial intelligence"[All Fields] OR "deep learning"[All Fields] OR '
        '"machine learning"[All Fields]) AND '
        '("drug discovery"[All Fields] OR "drug design"[All Fields])'
    ),
    "10. 한약 + skin + AI 종합": (
        '("herbal medicine"[All Fields] OR "phytomedicine"[All Fields]) AND '
        '"skin"[All Fields] AND '
        '("artificial intelligence"[All Fields] OR "machine learning"[All Fields])'
    ),
}


def pubmed_search(query: str, fetch_titles: int = 3) -> dict:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r = requests.get(url, params={"db": "pubmed", "term": query, "retmax": fetch_titles,
                                   "retmode": "json", "sort": "relevance"}, timeout=30)
    es = r.json().get("esearchresult", {})
    pmids = es.get("idlist", [])
    titles = []
    if pmids:
        s = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": ",".join(pmids), "retmode": "json"},
            timeout=30,
        ).json().get("result", {})
        for pid in pmids:
            item = s.get(pid, {})
            if isinstance(item, dict) and "title" in item:
                titles.append(item["title"][:120])
    return {"n_hits": int(es.get("count", 0)), "top_titles": titles, "pmids": pmids}


def europe_pmc_search(query_simple: str) -> dict:
    """Europe PMC — full-text + preprint 포함, PubMed 보다 넓음."""
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    r = requests.get(url, params={"query": query_simple, "format": "json",
                                   "pageSize": 3, "resultType": "lite"}, timeout=30)
    d = r.json()
    return {
        "n_hits": int(d.get("hitCount", 0)),
        "top_titles": [hit.get("title", "")[:120]
                       for hit in d.get("resultList", {}).get("result", [])[:3]],
    }


def main() -> int:
    print("=" * 90)
    print("시스템 단위 novelty 검증 — '한약 + AI + 흉터 신약' 토픽이 이미 있나?")
    print("=" * 90)

    for label, q in QUERIES.items():
        print(f"\n## {label}")
        try:
            pm = pubmed_search(q)
            print(f"  PubMed: {pm['n_hits']} hits")
            for i, t in enumerate(pm["top_titles"], 1):
                print(f"    [{i}] {t}")
        except Exception as e:
            print(f"  PubMed error: {e}")

    # Europe PMC 핵심 5개
    print("\n\n" + "=" * 90)
    print("Europe PMC (preprint 포함, 더 넓음)")
    print("=" * 90)
    epmc_queries = [
        '("Korean traditional medicine" OR "한방") AND scar AND ("virtual screening" OR docking)',
        '"Centella asiatica" AND "TGF-beta" AND docking',
        '"Boltz-2" AND scar',
        '"natural products" AND keloid AND ("network pharmacology" OR "multi-target")',
        '"shikonin" AND keloid',
    ]
    for q in epmc_queries:
        print(f"\n## {q[:60]}...")
        try:
            r = europe_pmc_search(q)
            print(f"  EPMC: {r['n_hits']} hits")
            for i, t in enumerate(r["top_titles"], 1):
                print(f"    [{i}] {t}")
        except Exception as e:
            print(f"  EPMC error: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
