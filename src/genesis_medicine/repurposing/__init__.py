"""Stage 1.5 — 약물 재창출 (Drug Repurposing).

TxGNN (Nature Med 2024, MIT) zero-shot 약물 재창출.
17,080 질병 × 7,957 후보. indication +49.2%, contraindication +35.1%.

ultrathink 2026-04-25 추가.
"""

from .base import RepurposingHit, RepurposingRequest, RepurposingResult, Repurposer
from .txgnn_adapter import TxGNNAdapter

__all__ = [
    "RepurposingHit",
    "RepurposingRequest",
    "RepurposingResult",
    "Repurposer",
    "TxGNNAdapter",
]
