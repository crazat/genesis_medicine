"""Dermatology-specific adapters for skin permeability, sensitization,
fibroblast atlas, and clinical photo workflow.

Modules:
    pbk_dermal_adapter — 3-compartment dermal PK (NIH/NIEHS public-domain)
    sara_ice_adapter   — OECD TG 497 Part III skin sensitization Bayesian DA
    skin_fibroblast_atlas — Reynolds 2025 350k cell atlas (Nat Immunol, CC-BY)
    panderm_adapter    — PanDerm multimodal foundation (CC-BY-NC-ND, research-only)

Round 5 SOTA integration sprint, 2026-04-26.
"""

from .panderm_adapter import (
    SkinImageAnalysis,
    analyze_skin_image,
    integrate_with_genesis_medicine,
)
from .pbk_dermal_adapter import DermalPBKAdapter, DermalPBKResult
from .sara_ice_adapter import SARAICEAdapter, SARAICEResult
from .skin_fibroblast_atlas import (
    CrossTissueFibrosisEvidence,
    FibroblastSubtypeExpression,
    SkinFibroblastAtlasAdapter,
)

__all__ = [
    "CrossTissueFibrosisEvidence",
    "DermalPBKAdapter",
    "DermalPBKResult",
    "FibroblastSubtypeExpression",
    "SARAICEAdapter",
    "SARAICEResult",
    "SkinFibroblastAtlasAdapter",
    "SkinImageAnalysis",
    "analyze_skin_image",
    "integrate_with_genesis_medicine",
]
