"""Stage 7 — 한약 / 천연물 네트워크 약리학.

상업 빌드 (commercial-safe):
- COCONUT 2.0 + LOTUS + NPASS 3 + NPAtlas (CC0/CC-BY)
- Reactome + WikiPathways (KEGG 대체)
- Dr. Duke (USDA, public domain)
- KHP/KP (한국 정부 저작물)

연구 빌드 (research-only):
- HERB 2.0 + TCMSP + KTKP + BATMAN-TCM + SymMap + ETCM
- KEGG (유료)
"""

from .network_pharmacology import (
    PathwayHit,
    compute_pathway_enrichment,
    overlay_compounds_on_pathways,
)
from .reverse_mapping import (
    HerbHit,
    map_compounds_to_herbs,
    regulatory_score,
)

__all__ = [
    "HerbHit",
    "PathwayHit",
    "compute_pathway_enrichment",
    "map_compounds_to_herbs",
    "overlay_compounds_on_pathways",
    "regulatory_score",
]
