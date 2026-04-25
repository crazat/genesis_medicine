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
from .consensus import ConsensusPredictor, ConsensusRequest, ConsensusResult
from .neuralplexer3_adapter import NeuralPLexer3Adapter
from .openfold3_adapter import OpenFold3Adapter
from .protenix_adapter import ProtenixAdapter

__all__ = [
    "AlphaFoldDBAdapter",
    "Boltz2Adapter",
    "ConsensusPredictor",
    "ConsensusRequest",
    "ConsensusResult",
    "LigandSpec",
    "NeuralPLexer3Adapter",
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
            sampling_steps_affinity=cfg.get("sampling_steps_affinity", 200),
            diffusion_samples_affinity=cfg.get("diffusion_samples_affinity", 5),
            affinity_mw_correction=cfg.get("affinity_mw_correction", True),
            no_kernels=cfg.get("no_kernels", False),
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
    if engine == "neuralplexer3":
        # research-only — LicenseGate가 commercial 빌드에서 차단해야 함
        from ..licensing import LicenseGate
        from ..licensing.gate import BuildProfile

        profile_name = cfg.get("build_profile", "commercial")
        gate = LicenseGate(BuildProfile.from_name(profile_name))
        gate.require("neuralplex3_weights")  # commercial → LicenseViolation
        return NeuralPLexer3Adapter(
            cache_dir=cache_dir,
            weights_dir=cfg.get("weights_dir"),
            device=cfg.get("device", "cuda:0"),
            covalent=cfg.get("covalent", False),
        )
    raise ValueError(f"Unknown structure engine: {engine}")
