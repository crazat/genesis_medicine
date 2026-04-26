"""Production Open Targets integration — agent-callable + pipeline-attached.

Wraps Open Targets v4 GraphQL API for use in:
1. Disease → target enrichment (preprint #9 cross-disease)
2. Target → disease association (canonical anti-fibrotic axis audit)
3. On-demand from agent: "what targets does Open Targets associate with IPF?"

Replaces ad-hoc scripts/query_open_targets.py with a real production module.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

API_URL = "https://api.platform.opentargets.org/api/v4/graphql"
CACHE = Path.home() / ".genesis_medicine" / "open_targets_cache"
CACHE.mkdir(parents=True, exist_ok=True)

DISEASE_QUERY = """
query AssociatedTargets($efoId: String!, $size: Int!) {
  disease(efoId: $efoId) {
    id name
    associatedTargets(page: { index: 0, size: $size }) {
      count
      rows {
        target { id approvedSymbol approvedName }
        score
      }
    }
  }
}
"""

TARGET_QUERY = """
query AssociatedDiseases($ensemblId: String!, $size: Int!) {
  target(ensemblId: $ensemblId) {
    id approvedSymbol
    associatedDiseases(page: { index: 0, size: $size }) {
      count
      rows { disease { id name } score }
    }
  }
}
"""

# Curated disease ID map (validated 2026-04-26)
DISEASE_IDS = {
    "skin_keloid": "EFO_0009551",
    "IPF": "EFO_0000768",
    "scleroderma_systemic": "EFO_0000717",
    "renal_fibrosis": "EFO_0009566",
    "hepatic_fibrosis": "EFO_0008502",
    "atopic_dermatitis": "EFO_0000274",
    "psoriasis": "EFO_0000676",
    "alopecia_areata": "EFO_0004192",
    "androgenetic_alopecia": "EFO_0009603",
    "acne_vulgaris": "EFO_0003894",
    "melasma": "EFO_1001124",
}

# Canonical target Ensembl IDs (skin/fibrosis-relevant)
TARGET_IDS = {
    "TGFB1":  "ENSG00000105329",
    "MMP1":   "ENSG00000196611",
    "MMP3":   "ENSG00000149968",
    "MMP9":   "ENSG00000100985",
    "CTGF":   "ENSG00000118523",
    "SMAD3":  "ENSG00000166949",
    "PDGFRB": "ENSG00000113721",
    "LOX":    "ENSG00000113083",
    "COL1A1": "ENSG00000108821",
    "TYR":    "ENSG00000077498",
    "MITF":   "ENSG00000187098",
    "SRD5A2": "ENSG00000277893",
    "AR":     "ENSG00000169083",
    "CTNNB1": "ENSG00000168036",
    "SIRT1":  "ENSG00000096717",
}


@dataclass
class OTAssociation:
    target_or_disease_id: str
    name: str
    score: float


@dataclass
class OTQueryResult:
    query_kind: str
    query_id: str
    n_associations: int
    associations: list = field(default_factory=list)
    error: str = ""


def _cached_post(query: str, variables: dict, kind: str,
                  identifier: str, ttl_hours: int = 168) -> dict:
    cache_path = CACHE / f"{kind}_{identifier.replace(':', '_')}.json"
    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < ttl_hours:
            return json.loads(cache_path.read_text())
    try:
        r = requests.post(API_URL, json={"query": query, "variables": variables},
                          timeout=30)
        if r.status_code == 200:
            data = r.json()
            cache_path.write_text(json.dumps(data, indent=2))
            return data
    except Exception as e:
        return {"error": str(e)}
    return {"error": f"HTTP {r.status_code}"}


def disease_associated_targets(disease_key_or_efo: str,
                                 score_min: float = 0.4,
                                 size: int = 50) -> OTQueryResult:
    """Get targets associated with a disease at OT score >= score_min."""
    efo = DISEASE_IDS.get(disease_key_or_efo, disease_key_or_efo)
    raw = _cached_post(DISEASE_QUERY, {"efoId": efo, "size": size},
                        "disease", efo)
    if "error" in raw:
        return OTQueryResult(query_kind="disease",
                              query_id=efo, n_associations=0,
                              error=raw["error"])
    if "data" not in raw or raw["data"].get("disease") is None:
        return OTQueryResult(query_kind="disease",
                              query_id=efo, n_associations=0,
                              error="not_found_or_empty")
    rows = raw["data"]["disease"]["associatedTargets"]["rows"]
    assocs = [
        OTAssociation(target_or_disease_id=r["target"]["id"],
                       name=r["target"]["approvedSymbol"],
                       score=r["score"])
        for r in rows if r["score"] >= score_min
    ]
    return OTQueryResult(query_kind="disease",
                          query_id=efo,
                          n_associations=len(assocs),
                          associations=assocs)


def target_associated_diseases(target_symbol_or_ensembl: str,
                                 score_min: float = 0.4,
                                 size: int = 100) -> OTQueryResult:
    ens = TARGET_IDS.get(target_symbol_or_ensembl, target_symbol_or_ensembl)
    raw = _cached_post(TARGET_QUERY, {"ensemblId": ens, "size": size},
                        "target", ens)
    if "error" in raw:
        return OTQueryResult(query_kind="target",
                              query_id=ens, n_associations=0,
                              error=raw["error"])
    if "data" not in raw or raw["data"].get("target") is None:
        return OTQueryResult(query_kind="target",
                              query_id=ens, n_associations=0,
                              error="not_found_or_empty")
    rows = raw["data"]["target"]["associatedDiseases"]["rows"]
    assocs = [
        OTAssociation(target_or_disease_id=r["disease"]["id"],
                       name=r["disease"]["name"],
                       score=r["score"])
        for r in rows if r["score"] >= score_min
    ]
    return OTQueryResult(query_kind="target",
                          query_id=ens,
                          n_associations=len(assocs),
                          associations=assocs)


def emb3_cross_disease_audit() -> dict:
    """Re-compute EMB-3 cross-disease overlap with cached OT data.

    EMB-3 binding profile (real Round-1 data):
      TGFB1=0.749, MMP1=0.674, CTGF=0.678, SMAD3=0.649, PDGFRB=0.640,
      LOX=0.579, JUN=0.497, FGF2=0.484, VEGFA=0.563
    """
    EMB3 = {"TGFB1": 0.749, "MMP1": 0.674, "CTGF": 0.678, "SMAD3": 0.649,
             "PDGFRB": 0.640, "LOX": 0.579}
    audit = {}
    for disease in ["skin_keloid", "IPF", "scleroderma_systemic",
                     "renal_fibrosis", "hepatic_fibrosis"]:
        result = disease_associated_targets(disease, score_min=0.4)
        ot_targets = {a.name for a in result.associations}
        emb3_engaged = {t for t, p in EMB3.items() if p >= 0.55}
        overlap = ot_targets & emb3_engaged
        audit[disease] = {
            "n_ot_targets": result.n_associations,
            "n_emb3_engaged_overlap": len(overlap),
            "overlap_targets": sorted(overlap),
            "fraction": len(overlap) / max(1, len(ot_targets)),
            "error": result.error,
        }
    return audit


# Agent-callable wrappers
def query_disease_natural(disease: str) -> dict:
    """Natural language: 'IPF에 어떤 타겟이 연관되어있어?'"""
    r = disease_associated_targets(disease)
    return {
        "tool": "open_targets_disease",
        "query": disease,
        "n_targets": r.n_associations,
        "top_targets": [{"symbol": a.name, "score": round(a.score, 3)}
                          for a in r.associations[:10]],
        "natural_summary": (
            f"{disease}: {r.n_associations} targets at OT score≥0.4. "
            f"Top: {', '.join(a.name for a in r.associations[:5])}"
            if r.n_associations > 0 else
            f"{disease}: no associations or query failed ({r.error})"
        ),
    }
