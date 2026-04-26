"""Stage 1.5 — 약물 재창출 (Drug Repurposing).

TxGNN (Nature Med 2024, MIT) zero-shot 약물 재창출.
17,080 질병 × 7,957 후보. indication +49.2%, contraindication +35.1%.

CellAwareGNN (bioRxiv 2026, MIT) — TxGNN successor with cell-type-aware
inference via scPrimeKG. +6% AUPRC on autoimmune diseases.

ultrathink 2026-04-25 추가; Round 5 (CellAwareGNN) 2026-04-26.
"""

from .base import RepurposingHit, RepurposingRequest, RepurposingResult, Repurposer
from .cellaware_gnn_adapter import (
    CellAwareGNNAdapter,
    CellAwareGNNPrediction,
    CellAwareGNNResult,
)
from .txgnn_adapter import TxGNNAdapter

__all__ = [
    "CellAwareGNNAdapter",
    "CellAwareGNNPrediction",
    "CellAwareGNNResult",
    "RepurposingHit",
    "RepurposingRequest",
    "RepurposingResult",
    "Repurposer",
    "TxGNNAdapter",
]
