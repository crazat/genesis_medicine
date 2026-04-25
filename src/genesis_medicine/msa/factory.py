"""MSA Provider 팩토리 — build_profile 인지."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from ..licensing import LicenseGate
from ..licensing.gate import BuildProfile
from .base import MSAProvider
from .colabfold_public import ColabFoldPublicProvider
from .mmseqs2_local import MMseqs2LocalProvider


def get_msa_provider(cfg: Any, profile_name: str = "commercial") -> MSAProvider:
    """build_profile에 맞는 MSA provider 반환.

    commercial → mmseqs2_local 강제
    research → cfg.provider 그대로 (colabfold_public 허용)
    """
    profile = BuildProfile.from_name(profile_name)
    gate = LicenseGate(profile)

    requested = cfg.get("provider", "mmseqs2_local")

    if profile_name == "commercial" and requested == "colabfold_public":
        logger.warning(
            "Commercial 빌드에서 colabfold_public 요청됨 — mmseqs2_local로 강제 전환."
        )
        requested = "mmseqs2_local"

    if requested == "mmseqs2_local":
        gate.require("mmseqs2")
        return MMseqs2LocalProvider(
            db_dir=Path(cfg.get("db_dir", "./.cache/mmseqs2_db")),
            binary=cfg.get("binary", "mmseqs"),
            threads=cfg.get("threads", 16),
            gpu=cfg.get("gpu", True),
            cache_dir=Path(cfg.get("cache_dir", "./.cache/msa")),
        )
    if requested == "colabfold_public":
        gate.require("colabfold_public_msa")  # research에서만 통과
        return ColabFoldPublicProvider(
            cache_dir=Path(cfg.get("cache_dir", "./.cache/msa_colabfold")),
        )
    raise ValueError(f"Unknown MSA provider: {requested}")
