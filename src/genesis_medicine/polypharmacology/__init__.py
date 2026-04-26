"""Polypharmacology / off-target adapters (Round 8 — 2nd gap closure).

Whole-proteome off-target prediction. Korean herbal compounds are
definitionally polypharmacological — berberine 26 targets, EGCG 30+.

Tools:
    SwissTargetPrediction, SuperPred, SPRINT, KinomeMETA — proteome scale.
"""

from .swisstarget_adapter import SwissTargetAdapter, SwissTargetResult
from .dealbreaker_panel import DealbreakerPanelAdapter, DealbreakerResult

__all__ = [
    "SwissTargetAdapter", "SwissTargetResult",
    "DealbreakerPanelAdapter", "DealbreakerResult",
]
