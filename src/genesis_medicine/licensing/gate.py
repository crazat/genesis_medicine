"""상업 빌드에서 비허용 의존성 사용을 런타임에 차단."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from loguru import logger

from .registry import LICENSE_REGISTRY, Component, LicenseTag, get_component


class LicenseViolation(RuntimeError):
    """Commercial 빌드에서 비허용 라이선스 사용 시 발생."""


@dataclass(frozen=True)
class BuildProfile:
    name: str
    allowed_tags: frozenset[LicenseTag]
    denied_components: frozenset[str]
    conditional_allowlist: frozenset[str]

    @classmethod
    def commercial(cls) -> "BuildProfile":
        return cls(
            name="commercial",
            allowed_tags=frozenset({
                LicenseTag.COMMERCIAL_SAFE,
                LicenseTag.COMMERCIAL_SHARE_ALIKE,
                LicenseTag.COMMERCIAL_CONDITIONAL,
            }),
            denied_components=frozenset({
                "alphafold3_weights", "chai1_weights", "chai2_weights",
                "herb_2_0", "tcmsp", "tcmid", "batman_tcm_2",
                "symmap_v2", "etcm_v2", "ktkp_raw",
                "kegg_pathways", "colabfold_public_msa",
            }),
            conditional_allowlist=frozenset({"txgemma", "esm3_cambrian", "esm_c_300m"}),
        )

    @classmethod
    def research(cls) -> "BuildProfile":
        return cls(
            name="research",
            allowed_tags=frozenset({
                LicenseTag.COMMERCIAL_SAFE,
                LicenseTag.COMMERCIAL_SHARE_ALIKE,
                LicenseTag.COMMERCIAL_CONDITIONAL,
                LicenseTag.RESEARCH_ONLY,
            }),
            denied_components=frozenset(),
            conditional_allowlist=frozenset({"txgemma", "esm3_cambrian", "esm_c_300m"}),
        )

    @classmethod
    def from_name(cls, name: str) -> "BuildProfile":
        if name == "commercial":
            return cls.commercial()
        if name == "research":
            return cls.research()
        raise ValueError(f"Unknown build profile: {name}")


class LicenseGate:
    """사용 직전 check — 위반 시 `LicenseViolation` 발생.

    사용 예:
        gate = LicenseGate(profile=BuildProfile.commercial())
        gate.require("boltz2")          # OK
        gate.require("herb_2_0")        # raises LicenseViolation
    """

    def __init__(self, profile: BuildProfile) -> None:
        self.profile = profile

    def require(self, component_key: str) -> Component:
        comp = get_component(component_key)
        if component_key in self.profile.denied_components:
            raise LicenseViolation(
                f"[{self.profile.name}] '{component_key}' is on the denied list. "
                f"License: {comp.license}. Consider substitution or switch to research profile."
            )
        if comp.tag == LicenseTag.BLOCKED:
            raise LicenseViolation(
                f"[{self.profile.name}] '{component_key}' is BLOCKED regardless of profile "
                f"(license: {comp.license})."
            )
        if comp.tag not in self.profile.allowed_tags:
            raise LicenseViolation(
                f"[{self.profile.name}] '{component_key}' has tag '{comp.tag.value}' "
                f"which is not allowed. License: {comp.license}."
            )
        if comp.tag == LicenseTag.COMMERCIAL_CONDITIONAL and component_key not in self.profile.conditional_allowlist:
            raise LicenseViolation(
                f"[{self.profile.name}] '{component_key}' is conditional-commercial "
                f"({comp.license}) but not on the conditional allowlist. "
                f"Legal review required before enabling."
            )
        logger.debug("License OK: {} ({}) for profile {}", component_key, comp.license, self.profile.name)
        return comp

    def audit(self, component_keys: Iterable[str]) -> list[Component]:
        """여러 component를 한 번에 검사. 위반이 있으면 첫 번째에서 실패."""
        return [self.require(k) for k in component_keys]
