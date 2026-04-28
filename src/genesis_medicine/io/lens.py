"""Lens.org Patent + Scholarly Works API client.

200M patents + 230M scholarly works. 우리 IP prior-art + Korean herbal
patent landscape search.

API token: .env의 LENS_API_TOKEN.
무료 tier: 1000 req/month (academic).

Usage:
    from genesis_medicine.io.lens import LensClient
    lens = LensClient()
    patents = lens.search_patents(query="embelin scar", n=20)
    works = lens.search_scholarly(query="CMS-19 stilbene pyrogallol", n=20)
"""
from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import requests
from loguru import logger


LENS_BASE = "https://api.lens.org"


@dataclass
class LensPatent:
    lens_id: str
    title: str
    abstract: Optional[str] = None
    inventors: List[str] = field(default_factory=list)
    applicants: List[str] = field(default_factory=list)
    publication_date: Optional[str] = None
    patent_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    cpc_classes: List[str] = field(default_factory=list)
    citations_received: Optional[int] = None
    citations_granted: Optional[int] = None
    legal_status: Optional[str] = None


@dataclass
class LensScholarly:
    lens_id: str
    title: str
    authors: List[str] = field(default_factory=list)
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    citation_count: Optional[int] = None


class LensClient:
    def __init__(self, api_token: Optional[str] = None,
                  cache_dir: Path = Path(".cache/lens")):
        self.token = api_token or os.environ.get("LENS_API_TOKEN", "")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not self.token:
            logger.warning("LENS_API_TOKEN 미발견.")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def search_patents(self, query: str, n: int = 20,
                        jurisdiction: Optional[str] = None,
                        date_from: Optional[str] = None) -> List[LensPatent]:
        """Patent search via Lens Patent API.

        Args:
            query: 검색어 (e.g. "embelin scar fibrosis")
            n: 결과 수 (max 1000)
            jurisdiction: 국가 (e.g. "KR" for Korea, "US" for USA)
            date_from: YYYY-MM-DD
        """
        if not self.token:
            return []

        body: Dict = {
            "query": {"query_string": {"query": query}},
            "size": min(n, 1000),
            "include": ["lens_id", "biblio.invention_title",
                          "abstract", "biblio.parties.inventors",
                          "biblio.parties.applicants",
                          "biblio.publication_reference.date",
                          "biblio.publication_reference.doc_number",
                          "biblio.publication_reference.country_code",
                          "biblio.classifications_cpc",
                          "biblio.references_cited.patent_count",
                          "legal_status"],
        }
        if jurisdiction:
            body["query"]["query_string"]["query"] += f" AND jurisdiction:{jurisdiction}"
        if date_from:
            body["query"]["query_string"]["query"] += f" AND date_published:[{date_from} TO *]"

        try:
            resp = requests.post(f"{LENS_BASE}/patent/search",
                                  headers=self._headers(),
                                  data=json.dumps(body), timeout=30)
            if resp.status_code == 429:
                logger.warning("Lens rate limit")
                return []
            resp.raise_for_status()
            data = resp.json()
            return self._parse_patents(data)
        except Exception as e:
            logger.error("Lens patent search failed: {}", e)
            return []

    def search_scholarly(self, query: str, n: int = 20,
                          year_from: Optional[int] = None) -> List[LensScholarly]:
        """Scholarly works search."""
        if not self.token:
            return []
        body: Dict = {
            "query": {"query_string": {"query": query}},
            "size": min(n, 1000),
        }
        if year_from:
            body["query"]["query_string"]["query"] += f" AND year_published:[{year_from} TO *]"

        try:
            resp = requests.post(f"{LENS_BASE}/scholarly/search",
                                  headers=self._headers(),
                                  data=json.dumps(body), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_scholarly(data)
        except Exception as e:
            logger.error("Lens scholarly search failed: {}", e)
            return []

    @staticmethod
    def _parse_patents(data: Dict) -> List[LensPatent]:
        patents = []
        for d in data.get("data", []):
            biblio = d.get("biblio", {})
            patents.append(LensPatent(
                lens_id=d.get("lens_id", ""),
                title=biblio.get("invention_title", [{}])[0].get("text", ""),
                abstract=d.get("abstract", [{}])[0].get("text") if d.get("abstract") else None,
                inventors=[i.get("name") for i in
                            biblio.get("parties", {}).get("inventors", [])],
                applicants=[a.get("name") for a in
                             biblio.get("parties", {}).get("applicants", [])],
                publication_date=biblio.get("publication_reference", {}).get("date"),
                patent_number=biblio.get("publication_reference", {}).get("doc_number"),
                jurisdiction=biblio.get("publication_reference", {}).get("country_code"),
                citations_received=biblio.get("references_cited", {}).get("patent_count"),
            ))
        return patents

    @staticmethod
    def _parse_scholarly(data: Dict) -> List[LensScholarly]:
        works = []
        for d in data.get("data", []):
            works.append(LensScholarly(
                lens_id=d.get("lens_id", ""),
                title=d.get("title", ""),
                authors=[a.get("display_name") for a in d.get("authors", [])],
                publication_year=d.get("year_published"),
                journal=d.get("source", {}).get("title"),
                doi=d.get("external_ids", [{}])[0].get("value")
                    if d.get("external_ids") else None,
                abstract=d.get("abstract"),
                citation_count=d.get("scholarly_citations_count"),
            ))
        return works
