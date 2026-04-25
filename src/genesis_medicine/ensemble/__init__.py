"""Stage 2.5 — Conformational Ensemble.

apo→holo conformational ensemble으로 cryptic / allosteric pocket 발굴.

- AlphaFlow (MIT): apo→holo flow matching
- BioEmu (MIT, Microsoft 2026-01): Boltzmann emulator

ultrathink 2026-04-25 추가.
"""

from .alphaflow_adapter import AlphaFlowAdapter
from .base import (
    ConformerSpec,
    EnsembleProvider,
    EnsembleRequest,
    EnsembleResult,
)
from .bioemu_adapter import BioEmuAdapter
from .pocket_diversity import compute_pocket_diversity

__all__ = [
    "AlphaFlowAdapter",
    "BioEmuAdapter",
    "ConformerSpec",
    "EnsembleProvider",
    "EnsembleRequest",
    "EnsembleResult",
    "compute_pocket_diversity",
]
