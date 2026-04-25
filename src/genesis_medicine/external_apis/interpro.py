"""InterPro 단백질 도메인 자동 조회.

각 타겟의 catalytic domain / binding site / family 정보 → Methods 섹션 자동.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "external_apis" / "interpro"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def interpro_domains(uniprot: str) -> dict:
    """UniProt ID → InterPro entries."""
    cache = CACHE_DIR / f"{uniprot}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    url = f"https://www.ebi.ac.uk/interpro/api/entry/all/protein/uniprot/{uniprot}/?page_size=20"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return {"uniprot": uniprot, "error": f"HTTP {r.status_code}"}
        d = r.json()
        entries = []
        for item in d.get("results", []):
            md = item.get("metadata", {})
            entries.append({
                "accession": md.get("accession"),
                "name": md.get("name"),
                "type": md.get("type"),       # domain / family / homologous_superfamily / active_site
                "source_database": md.get("source_database"),
            })
        # type별 그룹
        by_type: dict[str, list] = {}
        for e in entries:
            by_type.setdefault(e["type"], []).append(e)

        result = {
            "uniprot": uniprot,
            "n_entries": len(entries),
            "by_type": by_type,
            "url": f"https://www.ebi.ac.uk/interpro/protein/UniProt/{uniprot}/",
        }
        cache.write_text(json.dumps(result))
        return result
    except Exception as e:
        return {"uniprot": uniprot, "error": str(e)}
