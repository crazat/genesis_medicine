"""Affinity heads stacked on top of structure predictors.

These adapters take an OpenFold3 / Boltz-2 / Protenix-style cofold input
(sequence + ligand SMILES/CCD) and return an affinity score (pKd or pIC50
proxy) without requiring an experimental holo structure.

Currently registered:
    - AQAffinityAdapter — SandboxAQ AQAffinity (Apache-2.0), structure-free
      affinity head built on top of OpenFold3 weights.

License gating: see src/genesis_medicine/licensing/registry.py — keys
``aqaffinity_code`` and ``aqaffinity_weights``.
"""
from __future__ import annotations

from .aqaffinity_adapter import (
    AQAffinityAdapter,
    AQAffinityRequest,
    AQAffinityResult,
)

__all__ = [
    "AQAffinityAdapter",
    "AQAffinityRequest",
    "AQAffinityResult",
]
