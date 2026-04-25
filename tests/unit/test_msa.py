"""Stage S4 — MSA 인프라 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_medicine.licensing import LicenseViolation
from genesis_medicine.msa import (
    MSAProvider,
    MSARequest,
    MMseqs2LocalProvider,
    get_msa_provider,
)


def test_mmseqs2_local_protocol(tmp_path: Path) -> None:
    provider = MMseqs2LocalProvider(
        db_dir=tmp_path / "db",
        binary="not_a_real_binary",  # 설치 없어도 생성 가능
    )
    assert isinstance(provider, MSAProvider)
    assert provider.is_commercial_safe
    assert provider.provider_name == "mmseqs2_local"


def test_factory_commercial_forces_local(tmp_path: Path) -> None:
    """Commercial 빌드에서 colabfold_public 요청해도 local로 강제 전환."""
    from omegaconf import OmegaConf

    cfg = OmegaConf.create({
        "provider": "colabfold_public",
        "db_dir": str(tmp_path / "db"),
        "cache_dir": str(tmp_path / "cache"),
        "binary": "not_a_real_binary",
    })
    provider = get_msa_provider(cfg, profile_name="commercial")
    assert provider.provider_name == "mmseqs2_local"


def test_factory_research_allows_colabfold_public(tmp_path: Path) -> None:
    from omegaconf import OmegaConf

    cfg = OmegaConf.create({
        "provider": "colabfold_public",
        "cache_dir": str(tmp_path / "cache"),
    })
    provider = get_msa_provider(cfg, profile_name="research")
    assert provider.provider_name == "colabfold_public"


def test_factory_unknown_provider_raises(tmp_path: Path) -> None:
    from omegaconf import OmegaConf

    cfg = OmegaConf.create({"provider": "unknown_xyz"})
    with pytest.raises(ValueError):
        get_msa_provider(cfg, profile_name="commercial")


def test_msa_request_defaults() -> None:
    req = MSARequest(sequence="MAGV")
    assert req.max_seqs == 4096
    assert req.mode == "paired"
