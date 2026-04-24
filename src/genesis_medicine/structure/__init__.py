"""구조 예측 어댑터.

사용법:

    from genesis_medicine.structure import get_predictor

    predictor = get_predictor(cfg.structure)
    result = predictor.predict(req)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .alphafold_db_adapter import AlphaFoldDBAdapter
from .base import (
    LigandSpec,
    StructurePredictionRequest,
    StructurePredictionResult,
    StructurePredictor,
)
from .boltz2_adapter import Boltz2Adapter
from .openfold3_adapter import OpenFold3Adapter
from .protenix_adapter import ProtenixAdapter

__all__ = [
    "AlphaFoldDBAdapter",
    "Boltz2Adapter",
    "LigandSpec",
    "OpenFold3Adapter",
    "ProtenixAdapter",
    "StructurePredictionRequest",
    "StructurePredictionResult",
    "StructurePredictor",
    "get_predictor",
]


def get_predictor(cfg: Any) -> StructurePredictor:
    engine = cfg.engine
    cache_dir = Path(cfg.get("cache_dir", "./.cache/structure"))
    if engine == "boltz2":
        return Boltz2Adapter(
            cache_dir=cache_dir,
            msa_server=cfg.get("msa_server", "colabfold"),
            num_recycles=cfg.get("num_recycles", 10),
            num_samples=cfg.get("num_samples", 5),
            num_diffn_samples=cfg.get("num_diffn_samples", 25),
            predict_affinity=cfg.get("predict_affinity", True),
        )
    if engine == "protenix":
        return ProtenixAdapter(
            cache_dir=cache_dir,
            num_recycles=cfg.get("num_recycles", 10),
            diffusion_samples=cfg.get("diffusion_samples", 25),
            num_samples=cfg.get("num_samples", 5),
            use_msa=cfg.get("use_msa", True),
            msa_server=cfg.get("msa_server", "colabfold"),
        )
    if engine == "openfold3":
        return OpenFold3Adapter(
            cache_dir=cache_dir,
            num_recycles=cfg.get("num_recycles", 10),
            num_samples=cfg.get("num_samples", 5),
            use_msa=cfg.get("use_msa", True),
        )
    raise ValueError(f"Unknown structure engine: {engine}")
