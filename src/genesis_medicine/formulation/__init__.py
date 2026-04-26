"""Topical formulation science (Round 8 — 4th gap closure).

Closes "in silico hit" → "Recover 외용제 prototype" gap.

CPE-DB penetration enhancers, HSP vehicle selection, KCID Korean
cosmetic ingredient gating, CosIng EU bans.
"""

from .cpedb_adapter import CPEDBAdapter, PenetrationEnhancer
from .hsp_solubility import HSPVehicleAdapter, HSPVehicle
from .kcid_kfda_adapter import KCIDAdapter, IngredientStatus

__all__ = [
    "CPEDBAdapter", "PenetrationEnhancer",
    "HSPVehicleAdapter", "HSPVehicle",
    "KCIDAdapter", "IngredientStatus",
]
