"""PubMed 배치 수집기.

v1의 문제점 수정:
- 단일 efetch 호출에 20k ID 전달 → 10k 상한 무시하고 하나씩 갈리던 버그. 500건 청크로 분할.
- 재시도·캐시 없음 → 네트워크 끊기면 처음부터. diskcache + tenacity.
- 출력 파일명이 쿼리와 무관하게 'nsclc_abstracts.csv' 하드코딩. 이제 disease key 파생.
- api_key 미사용 → 3 req/s 제한. api_key 있으면 10 req/s.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from Bio import Entrez
from diskcache import Cache
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm


@dataclass
class PubMedConfig:
    query: str
    email: str
    api_key: str | None = None
    retmax: int = 20000
    batch_size: int = 500
    cache_dir: Path = Path(".cache/pubmed")


class PubMedHarvester:
    def __init__(self, cfg: PubMedConfig) -> None:
        self.cfg = cfg
        Entrez.email = cfg.email
        if cfg.api_key:
            Entrez.api_key = cfg.api_key
        Entrez.tool = "genesis_medicine"
        cfg.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = Cache(str(cfg.cache_dir))

    def search(self) -> list[str]:
        cache_key = f"search::{self.cfg.query}::{self.cfg.retmax}"
        if cache_key in self.cache:
            logger.info("PubMed search cache hit")
            return self.cache[cache_key]

        ids: list[str] = []
        retstart = 0
        page = min(self.cfg.batch_size, 9999)  # esearch 자체 상한
        while retstart < self.cfg.retmax:
            handle = Entrez.esearch(
                db="pubmed",
                sort="relevance",
                retmax=min(page, self.cfg.retmax - retstart),
                retstart=retstart,
                retmode="xml",
                term=self.cfg.query,
            )
            results = Entrez.read(handle)
            batch = results["IdList"]
            if not batch:
                break
            ids.extend(batch)
            retstart += len(batch)
            self._throttle()

        self.cache[cache_key] = ids
        logger.info(f"PubMed search 완료: {len(ids)}건")
        return ids

    def fetch_abstracts(self, ids: list[str]) -> pd.DataFrame:
        rows: list[dict] = []
        batches = [ids[i : i + self.cfg.batch_size] for i in range(0, len(ids), self.cfg.batch_size)]
        for batch in tqdm(batches, desc="efetch"):
            records = self._fetch_one_batch(batch)
            for record in records.get("PubmedArticle", []):
                parsed = self._parse_record(record)
                if parsed:
                    rows.append(parsed)
            self._throttle()
        return pd.DataFrame(rows)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=30))
    def _fetch_one_batch(self, batch: list[str]) -> dict:
        cache_key = "efetch::" + ",".join(batch)
        if cache_key in self.cache:
            return self.cache[cache_key]

        handle = Entrez.efetch(
            db="pubmed", retmode="xml", id=",".join(batch)
        )
        records = Entrez.read(handle)
        self.cache[cache_key] = records
        return records

    def _parse_record(self, record: dict) -> dict | None:
        try:
            article = record["MedlineCitation"]["Article"]
            pmid = str(record["MedlineCitation"]["PMID"])
            abstract_parts = article["Abstract"]["AbstractText"]
            abstract = " ".join(str(p) for p in abstract_parts)
            title = str(article.get("ArticleTitle", ""))
            year = (
                article.get("Journal", {})
                .get("JournalIssue", {})
                .get("PubDate", {})
                .get("Year", "")
            )
            return {"pmid": pmid, "title": title, "abstract": abstract, "year": year}
        except (KeyError, TypeError):
            return None

    def _throttle(self) -> None:
        # api_key 있으면 10 req/s, 없으면 3 req/s
        time.sleep(0.11 if self.cfg.api_key else 0.34)
