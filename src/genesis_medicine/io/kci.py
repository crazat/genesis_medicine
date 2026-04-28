"""KCI (Korea Citation Index) OpenAPI 클라이언트.

한국연구재단 운영 무료 API. 등록키 .env의 KCI_API_KEY.

Endpoints:
- Article search by keyword/title/author/journal
- Author detail (h-index, KCI score)
- Journal detail (impact, ranking)
- Reference cited-by tracking

Usage:
    from genesis_medicine.io.kci import KCIClient
    kci = KCIClient()
    results = kci.search(query="centella asiatica scar", n=20)
    print(results)
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

import requests
from loguru import logger


# Base URL (KCI OpenAPI v2)
KCI_BASE = "https://open.kci.go.kr/po/openapi/openApiSearch.kci"


@dataclass
class KCIArticle:
    article_id: str
    title: str
    authors: List[str] = field(default_factory=list)
    journal: Optional[str] = None
    year: Optional[int] = None
    issn: Optional[str] = None
    doi: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    cited_by: Optional[int] = None
    kci_score: Optional[float] = None


class KCIClient:
    def __init__(self, api_key: Optional[str] = None,
                  cache_dir: Path = Path(".cache/kci")):
        self.api_key = api_key or os.environ.get("KCI_API_KEY", "")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not self.api_key:
            logger.warning("KCI_API_KEY 미발견. .env 또는 환경변수 설정 필요.")

    def search(self, query: str, n: int = 20,
                title: bool = True, author: bool = False,
                year_from: Optional[int] = None,
                year_to: Optional[int] = None) -> List[KCIArticle]:
        """KCI 학술논문 검색.

        Args:
            query: 검색어 (한국어/영어)
            n: 결과 수 (max 100)
            title: True면 title field 검색, False면 본문/abstract
            author: True면 author 필드도 검색
            year_from/year_to: 연도 범위
        """
        if not self.api_key:
            return []

        params = {
            "apiCode": "articleSearch",
            "key": self.api_key,
            "query": query,
            "displayCount": min(n, 100),
            "page": 1,
        }
        if title:
            params["searchField"] = "title"
        if year_from:
            params["startYear"] = year_from
        if year_to:
            params["endYear"] = year_to

        try:
            resp = requests.get(KCI_BASE, params=params, timeout=30)
            resp.raise_for_status()
            return self._parse_search(resp.text)
        except Exception as e:
            logger.error("KCI search failed: {}", e)
            return []

    def _parse_search(self, xml_text: str) -> List[KCIArticle]:
        """KCI는 XML 응답."""
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_text)
        except Exception as e:
            logger.error("KCI XML parse: {}", e)
            return []

        articles = []
        for record in root.iter("record"):
            article = KCIArticle(
                article_id=self._get_text(record, "id") or "",
                title=self._get_text(record, "title") or "",
                journal=self._get_text(record, "journalName"),
                year=int(self._get_text(record, "pubYear") or 0) or None,
                issn=self._get_text(record, "issn"),
                doi=self._get_text(record, "doi"),
                abstract=self._get_text(record, "abstract"),
            )
            # Authors (multiple)
            for a in record.iter("author"):
                name = self._get_text(a, "name")
                if name:
                    article.authors.append(name)
            # Keywords
            for k in record.iter("keyword"):
                if k.text:
                    article.keywords.append(k.text.strip())
            articles.append(article)
        return articles

    @staticmethod
    def _get_text(parent, tag: str) -> Optional[str]:
        el = parent.find(tag)
        return el.text.strip() if el is not None and el.text else None
