"""STRING DB protein-protein interactions.

각 타겟의 결합 파트너 → multi-target 확장 후보 발굴.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "external_apis" / "string"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://string-db.org/api"


def string_partners(gene_symbol: str, *, n_partners: int = 10,
                    species: int = 9606) -> dict:
    """STRING에서 high-confidence 결합 파트너 N개."""
    cache = CACHE_DIR / f"partners_{gene_symbol}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    url = f"{BASE}/json/network"
    try:
        r = requests.get(url, params={
            "identifiers": gene_symbol,
            "species": species,
            "limit": n_partners,
            "required_score": 700,    # high confidence
            "caller_identity": "genesis_medicine",
        }, timeout=30)
        r.raise_for_status()
        data = r.json()
        partners = []
        seen = {gene_symbol}
        for edge in data:
            for k in ("preferredName_A", "preferredName_B"):
                p = edge.get(k)
                if p and p not in seen:
                    seen.add(p)
                    partners.append({
                        "gene": p,
                        "score": float(edge.get("score", 0)),
                    })
        partners.sort(key=lambda x: -x["score"])
        result = {
            "gene": gene_symbol,
            "n_partners": len(partners),
            "partners": partners[:n_partners],
            "url": f"https://string-db.org/network/{gene_symbol}",
        }
        cache.write_text(json.dumps(result))
        return result
    except Exception as e:
        return {"gene": gene_symbol, "error": str(e), "partners": []}


def string_enrichment(gene_symbols: list[str], *, species: int = 9606) -> dict:
    """STRING functional enrichment — 우리 타겟 set의 기능 enrichment."""
    cache = CACHE_DIR / f"enrich_{abs(hash(tuple(gene_symbols))) % 10**12}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    url = f"{BASE}/json/enrichment"
    try:
        r = requests.get(url, params={
            "identifiers": "%0d".join(gene_symbols),
            "species": species,
            "caller_identity": "genesis_medicine",
        }, timeout=60)
        r.raise_for_status()
        data = r.json()
        # category별 그룹
        by_cat: dict[str, list] = {}
        for entry in data:
            cat = entry.get("category", "other")
            by_cat.setdefault(cat, []).append({
                "term": entry.get("term"),
                "description": entry.get("description"),
                "p_value": entry.get("p_value"),
                "fdr": entry.get("fdr"),
                "n_genes": entry.get("number_of_genes"),
            })
        # 카테고리별 fdr 낮은 순 5개
        result = {
            "n_genes_input": len(gene_symbols),
            "by_category": {
                cat: sorted(items, key=lambda x: x.get("fdr", 1))[:5]
                for cat, items in by_cat.items()
            },
        }
        cache.write_text(json.dumps(result))
        return result
    except Exception as e:
        return {"error": str(e)}
