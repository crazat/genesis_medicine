"""PK-PD modeling adapters (Round 8 — 5th gap closure).

httk + Stan + scipy/ECCpy stack for multi-dose virtual trials.
DermalPBPK Bayesian extension above our PBK Dermal HT.
"""

from .httk_adapter import HTTKAdapter, HTTKResult
from .hill_dose_response import HillDoseResponseAdapter, HillFitResult

__all__ = [
    "HTTKAdapter", "HTTKResult",
    "HillDoseResponseAdapter", "HillFitResult",
]
