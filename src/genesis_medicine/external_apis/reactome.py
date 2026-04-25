"""Reactome pathway 분석 (CC BY 4.0, commercial-safe)."""

from __future__ import annotations

import json
from pathlib import Path

import requests

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "external_apis" / "reactome"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def reactome_pathways_for_targets(uniprot_ids: list[str]) -> dict:
    """Reactome AnalysisService로 multi-protein pathway enrichment."""
    cache = CACHE_DIR / f"pw_{abs(hash(tuple(sorted(uniprot_ids)))) % 10**12}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    # Reactome AnalysisService
    url = "https://reactome.org/AnalysisService/identifiers/projection?interactors=false"
    headers = {"Content-Type": "text/plain"}
    body = "\n".join(uniprot_ids)
    try:
        r = requests.post(url, headers=headers, data=body, timeout=60)
        r.raise_for_status()
        d = r.json()
        token = d.get("summary", {}).get("token")
        if not token:
            return {"error": "no token", "raw": str(d)[:200]}
        # Get top pathways
        pw_url = f"https://reactome.org/AnalysisService/token/{token}/pathways/UNIPROT/9606"
        r2 = requests.get(pw_url, params={"sortBy": "ENTITIES_FDR",
                                          "order": "ASC",
                                          "pageSize": 20,
                                          "page": 1},
                          timeout=30)
        if r2.status_code != 200:
            return {"error": f"pathways HTTP {r2.status_code}"}
        pathways = r2.json().get("pathways", [])
        result = {
            "n_input": len(uniprot_ids),
            "n_pathways": len(pathways),
            "top_pathways": [
                {
                    "id": p.get("stId"),
                    "name": p.get("name"),
                    "fdr": p.get("entities", {}).get("fdr"),
                    "p_value": p.get("entities", {}).get("pValue"),
                    "n_found": p.get("entities", {}).get("found"),
                    "n_total": p.get("entities", {}).get("total"),
                }
                for p in pathways[:15]
            ],
        }
        cache.write_text(json.dumps(result))
        return result
    except Exception as e:
        return {"error": str(e)}
