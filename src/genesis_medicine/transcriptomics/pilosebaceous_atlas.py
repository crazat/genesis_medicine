"""Pilosebaceous unit single-cell atlas 어댑터 (bioRxiv 2025-09).

References:
- bioRxiv 2025-09: https://www.biorxiv.org/content/10.1101/2025.09.09.675235v1.full
- 821k cells × 34 datasets, integrated 모낭/피지선/땀샘 atlas

핵심 가치:
- AGA (안드로겐성 탈모) **matrix progenitor / dermal papilla / ORS / IRS**
  세부 컴파트먼트별 타겟 enrichment
- Recover 한의원 탈모 vertical 직격
- PIEZO1 / MYLK / SRD5A1/2 / AR cell-type-specific expression

라이선스: bioRxiv preprint, raw data CELLxGENE CC-BY 4.0 가능성.
       정식 게재 후 라이선스 재확인.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from loguru import logger


@dataclass
class PilosebaceousCellType:
    name: str
    abbreviation: str
    n_cells: int
    parent_compartment: str       # "hair_follicle" | "sebaceous" | "sweat" | "interfollicular"
    marker_genes: List[str] = field(default_factory=list)
    drug_target_enrichment: Dict[str, float] = field(default_factory=dict)


@dataclass
class PilosebaceousQuery:
    target_genes: List[str]
    compartments: Optional[List[str]] = None
    min_expression_pct: float = 0.05


@dataclass
class PilosebaceousResult:
    target_gene: str
    cell_type: str
    expression_mean: float
    expression_pct: float          # fraction of cells expressing
    rank_in_atlas: int             # 1 = highest expressing cell type for this gene
    rationale: str = ""


class PilosebaceousAtlas:
    """Pre-computed atlas summary for fast querying without full h5ad load."""

    engine_name = "pilosebaceous_atlas"
    engine_version = "biorxiv-2025-09"

    # Skeleton catalog — replace with full atlas counts after CELLxGENE download
    DEFAULT_CELL_TYPES: List[PilosebaceousCellType] = [
        PilosebaceousCellType(
            name="hair_follicle.matrix_progenitor",
            abbreviation="HF.MP",
            n_cells=42_350,
            parent_compartment="hair_follicle",
            marker_genes=["LEF1", "WNT10B", "CTNNB1", "SHH", "MKI67"],
        ),
        PilosebaceousCellType(
            name="hair_follicle.dermal_papilla",
            abbreviation="HF.DP",
            n_cells=18_240,
            parent_compartment="hair_follicle",
            marker_genes=["WIF1", "BMP6", "VCAN", "AR", "SRD5A2", "PIEZO1"],
        ),
        PilosebaceousCellType(
            name="hair_follicle.ORS",       # outer root sheath
            abbreviation="HF.ORS",
            n_cells=66_120,
            parent_compartment="hair_follicle",
            marker_genes=["KRT5", "KRT14", "KRT15", "S100A2", "AR"],
        ),
        PilosebaceousCellType(
            name="hair_follicle.IRS",       # inner root sheath
            abbreviation="HF.IRS",
            n_cells=24_550,
            parent_compartment="hair_follicle",
            marker_genes=["KRT25", "KRT27", "TCHH"],
        ),
        PilosebaceousCellType(
            name="sebaceous.sebocyte",
            abbreviation="SEB.S",
            n_cells=89_140,
            parent_compartment="sebaceous",
            marker_genes=["SREBF1", "FASN", "DGAT2", "SRD5A1", "AR"],
        ),
        PilosebaceousCellType(
            name="connective_tissue_sheath.fibroblast",   # CTS — AGA hypercontractility
            abbreviation="CTS.FB",
            n_cells=31_700,
            parent_compartment="hair_follicle",
            marker_genes=["MYLK", "ACTA2", "PIEZO1", "COL1A1"],
        ),
        PilosebaceousCellType(
            name="melanocyte_follicular",
            abbreviation="MEL.F",
            n_cells=12_840,
            parent_compartment="hair_follicle",
            marker_genes=["TYR", "MITF", "DCT", "PMEL"],
        ),
    ]

    # Pre-computed expression heatmap — replace with full atlas .X
    # Format: {(cell_type, gene): (mean_expr, pct_expr)}
    DEFAULT_EXPR: Dict[tuple, tuple] = {
        ("HF.DP", "AR"): (3.2, 0.71),
        ("HF.DP", "SRD5A2"): (2.4, 0.55),
        ("HF.DP", "PIEZO1"): (1.9, 0.42),
        ("HF.DP", "WNT10B"): (3.6, 0.78),
        ("HF.DP", "CTNNB1"): (2.8, 0.85),
        ("HF.MP", "WNT10B"): (1.2, 0.31),
        ("HF.MP", "CTNNB1"): (3.3, 0.91),
        ("HF.MP", "MKI67"): (4.2, 0.95),
        ("HF.ORS", "AR"): (2.1, 0.62),
        ("CTS.FB", "MYLK"): (3.8, 0.82),
        ("CTS.FB", "PIEZO1"): (3.1, 0.74),
        ("CTS.FB", "ACTA2"): (4.5, 0.88),
        ("SEB.S", "SRD5A1"): (3.9, 0.79),
        ("SEB.S", "AR"): (2.7, 0.66),
        ("SEB.S", "SREBF1"): (4.1, 0.91),
        ("MEL.F", "TYR"): (4.6, 0.94),
        ("MEL.F", "MITF"): (4.2, 0.87),
        ("MEL.F", "DCT"): (3.5, 0.78),
    }

    def __init__(
        self,
        *,
        h5ad_path: Optional[Path] = None,
        cache_dir: Path = Path(".cache/pilosebaceous"),
    ) -> None:
        self.h5ad_path = h5ad_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cell_types = list(self.DEFAULT_CELL_TYPES)
        self._expr = dict(self.DEFAULT_EXPR)

    def query_target_compartments(self, q: PilosebaceousQuery) -> List[PilosebaceousResult]:
        """Top expressing cell types per query gene."""
        results: List[PilosebaceousResult] = []
        for gene in q.target_genes:
            scored = []
            for ct in self._cell_types:
                if q.compartments and ct.parent_compartment not in q.compartments:
                    continue
                key = (ct.abbreviation, gene)
                if key not in self._expr:
                    continue
                mean, pct = self._expr[key]
                if pct < q.min_expression_pct:
                    continue
                scored.append((ct.name, mean, pct))
            scored.sort(key=lambda t: -t[1])
            for rank, (ct_name, mean, pct) in enumerate(scored, start=1):
                results.append(PilosebaceousResult(
                    target_gene=gene, cell_type=ct_name,
                    expression_mean=mean, expression_pct=pct, rank_in_atlas=rank,
                    rationale=(f"{gene} 발현 {ct_name} (mean={mean:.2f}, "
                                f"pct={pct*100:.1f}%, rank #{rank})"),
                ))
        return results

    def aga_panel_summary(self) -> Dict[str, List[str]]:
        """AGA target panel — cell type별 marker → 우리 alopecia.yaml 확장 권고."""
        return {
            "hair_follicle.dermal_papilla": ["AR", "SRD5A2", "PIEZO1", "WNT10B", "CTNNB1"],
            "connective_tissue_sheath.fibroblast": ["MYLK", "PIEZO1", "ACTA2"],
            "sebaceous.sebocyte": ["SRD5A1", "AR", "SREBF1"],
            "hair_follicle.matrix_progenitor": ["WNT10B", "CTNNB1", "MKI67"],
        }
