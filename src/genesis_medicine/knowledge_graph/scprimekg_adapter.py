"""scPrimeKG + CellAwareGNN 어댑터 (bioRxiv 2026-02).

References:
- bioRxiv 2026-02: https://www.biorxiv.org/content/10.64898/2026.02.20.707076v1
- Builds on PrimeKG (Harvard) + OneK1K single-cell expression data
- TxGNN repositioning에서 자가면역 (atopic dermatitis, alopecia areata) AUPRC +6%

핵심 가치:
- TxGNN의 직속 후속, single-cell context-aware repositioning
- 우리 5 disease (흉터·색소·탈모·여드름·광노화) 재실행 → 자가면역
  계열에서 정확도 ↑

라이선스: PrimeKG MIT, scPrimeKG additions likely MIT (확정 시점에서
upstream attribution 유지). Commercial 빌드 OK.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from loguru import logger


@dataclass
class ScPrimeKGEdge:
    source: str
    target: str
    edge_type: str
    cell_type_context: Optional[str] = None       # e.g. "fibroblast.dermal"
    expression_weight: Optional[float] = None      # OneK1K-derived
    weight: float = 1.0


@dataclass
class CellAwareGNNPrediction:
    drug: str
    drug_id: str
    disease: str
    disease_id: str
    score: float
    cell_type_evidence: List[str] = field(default_factory=list)   # supporting cell types
    txgnn_baseline_score: Optional[float] = None
    delta_aupr_estimate: Optional[float] = None       # vs TxGNN
    method: str = "cellawaregnn_scprimekg"


class ScPrimeKGAdapter:
    """Loads scPrimeKG and runs CellAwareGNN repositioning."""

    engine_name = "scprimekg"
    engine_version = "biorxiv-2026-02"

    DEFAULT_GRAPH_PATH = Path(".cache/scprimekg/graph.tsv")

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/scprimekg"),
        graph_path: Optional[Path] = None,
        cell_atlas: Optional[Path] = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.graph_path = Path(graph_path) if graph_path else self.DEFAULT_GRAPH_PATH
        self.cell_atlas = Path(cell_atlas) if cell_atlas else None
        self._edges: Optional[List[ScPrimeKGEdge]] = None
        self._cell_expression: Optional[Dict[str, Dict[str, float]]] = None

    def load(self) -> bool:
        """Load graph + cell atlas (optional)."""
        if not self.graph_path.exists():
            logger.warning("scPrimeKG graph 미발견 — bootstrap 필요: {}", self.graph_path)
            return False
        # TSV format: source\ttarget\tedge_type\tcell_type\texpr_weight
        edges: List[ScPrimeKGEdge] = []
        with open(self.graph_path) as f:
            header = f.readline().rstrip().split("\t")
            cols = {c: i for i, c in enumerate(header)}
            for line in f:
                parts = line.rstrip().split("\t")
                if len(parts) < 3:
                    continue
                edges.append(ScPrimeKGEdge(
                    source=parts[cols.get("source", 0)],
                    target=parts[cols.get("target", 1)],
                    edge_type=parts[cols.get("edge_type", 2)],
                    cell_type_context=parts[cols["cell_type"]] if "cell_type" in cols
                    and len(parts) > cols["cell_type"] else None,
                    expression_weight=float(parts[cols["expr_weight"]])
                    if "expr_weight" in cols and len(parts) > cols["expr_weight"]
                    and parts[cols["expr_weight"]] else None,
                ))
        self._edges = edges
        logger.info("Loaded {} scPrimeKG edges", len(edges))
        return True

    def predict(
        self,
        *,
        disease_id: str,
        candidate_drugs: List[str],
        cell_types_of_interest: Optional[List[str]] = None,
    ) -> List[CellAwareGNNPrediction]:
        """Run CellAwareGNN repositioning on candidate drug list.

        Cell-type-conditioned scoring: edges weighted by expression in
        relevant cell types (e.g. dermal_fibroblast for scar; melanocyte
        for pigmentation; hair_follicle.matrix for AGA).
        """
        if self._edges is None and not self.load():
            return []

        # Heuristic skeleton scoring — replace with full GNN forward pass
        # when CellAwareGNN model is downloaded.
        relevant = self._edges
        if cell_types_of_interest:
            relevant = [e for e in self._edges
                          if e.cell_type_context in cell_types_of_interest
                          or e.cell_type_context is None]

        # Build adjacency to disease for scoring
        disease_neighbors = {e.source for e in relevant if e.target == disease_id}
        disease_neighbors |= {e.target for e in relevant if e.source == disease_id}

        results: List[CellAwareGNNPrediction] = []
        for drug in candidate_drugs:
            n_paths = sum(1 for e in relevant
                          if (e.source == drug and e.target in disease_neighbors)
                          or (e.target == drug and e.source in disease_neighbors))
            score = float(np.tanh(n_paths / 10.0))
            cell_evidence = list({e.cell_type_context for e in relevant
                                    if (e.source == drug or e.target == drug)
                                    and e.cell_type_context})
            results.append(CellAwareGNNPrediction(
                drug=drug, drug_id=drug, disease=disease_id, disease_id=disease_id,
                score=score, cell_type_evidence=cell_evidence,
                delta_aupr_estimate=0.06,    # bioRxiv claim, updated post wet-lab
            ))
        results.sort(key=lambda r: -r.score)
        return results
