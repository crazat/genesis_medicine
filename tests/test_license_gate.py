"""상업 빌드 라이선스 게이트 — CI 블로커.

`commercial` 프로파일에서 비허용 의존성을 호출하면 반드시 실패해야 한다.
"""

from __future__ import annotations

import pytest

from genesis_medicine.licensing import LicenseGate, LicenseViolation
from genesis_medicine.licensing.gate import BuildProfile


@pytest.fixture
def commercial_gate() -> LicenseGate:
    return LicenseGate(BuildProfile.commercial())


@pytest.fixture
def research_gate() -> LicenseGate:
    return LicenseGate(BuildProfile.research())


# -- 상업 빌드에서 통과해야 하는 것 ------------------------------------------
@pytest.mark.parametrize(
    "key",
    [
        "protenix_v2", "boltz2", "diffdock_l", "gnina", "reinvent4",
        "admet_ai", "chemprop2", "unimol2", "molformer_xl",
        "coconut_2", "lotus", "open_targets", "alphafold_db", "uniprot",
        "reactome", "wikipathways", "rdkit", "openmm", "mmseqs2", "hydra",
        # v2 고도화 추가
        "openfold3", "openfold3_weights_p2",
        "aqaffinity", "aqaffinity_weights",
        "flowdock", "drugclip", "flowmol3", "decompdiff",
        "saturn", "posebusters", "aizynthfinder", "npatlas_3",
        # v2.1 ultrathink 추가
        "txgnn", "alphaflow", "bioemu",
        "mace_off24", "openmm_ml", "aceff", "fep_spell_abfe",
        "bindcraft", "protac_jt_vae",
        "cuequivariance_torch", "boltz_blackwell",
        "deep_docking", "posebench_v2",
    ],
)
def test_commercial_allows_safe(commercial_gate: LicenseGate, key: str) -> None:
    comp = commercial_gate.require(key)
    assert comp.key == key


# -- 상업 빌드에서 반드시 차단되어야 하는 것 ---------------------------------
@pytest.mark.parametrize(
    "key",
    [
        "alphafold3_weights", "chai1_weights", "chai2_weights",
        "herb_2_0", "tcmsp", "tcmid", "batman_tcm_2", "symmap_v2",
        "etcm_v2", "ktkp_raw", "kegg_pathways", "colabfold_public_msa",
        "rfaa",  # mixed license → research only
        "neuralplex3_weights",  # CC-BY-NC-SA → research only
        "enamine_real",  # blocked
        # v2.1 추가
        "pmx",  # GPL-3 → research only (서브프로세스 격리 시 별도 조치)
        "molglue_jtvae",  # 학습 데이터 NC 가능성 → 안전 기본 research
    ],
)
def test_commercial_blocks_denied(commercial_gate: LicenseGate, key: str) -> None:
    with pytest.raises(LicenseViolation):
        commercial_gate.require(key)


# -- ChEMBL: 상업 OK이지만 share-alike 경고 ---------------------------------
def test_chembl_allowed_but_share_alike(commercial_gate: LicenseGate) -> None:
    comp = commercial_gate.require("chembl_35")
    assert comp.tag.value == "commercial-share-alike"


# -- Conditional: 화이트리스트에 있어야만 통과 --------------------------------
def test_commercial_allows_conditional_on_allowlist(commercial_gate: LicenseGate) -> None:
    assert commercial_gate.require("txgemma").key == "txgemma"
    assert commercial_gate.require("esm3_cambrian").key == "esm3_cambrian"
    assert commercial_gate.require("esm_c_300m").key == "esm_c_300m"


def test_commercial_blocks_conditional_off_allowlist() -> None:
    """Conditional 컴포넌트를 allowlist에서 뺀 커스텀 프로파일은 차단해야 함."""
    custom = BuildProfile(
        name="commercial-strict",
        allowed_tags=BuildProfile.commercial().allowed_tags,
        denied_components=BuildProfile.commercial().denied_components,
        conditional_allowlist=frozenset(),  # 조건부 모두 차단
    )
    gate = LicenseGate(custom)
    with pytest.raises(LicenseViolation):
        gate.require("txgemma")


# -- Research 빌드는 거의 모든 것을 허용 --------------------------------------
@pytest.mark.parametrize(
    "key",
    ["alphafold3_weights", "herb_2_0", "tcmsp", "ktkp_raw", "kegg_pathways"],
)
def test_research_allows_nc(research_gate: LicenseGate, key: str) -> None:
    assert research_gate.require(key).key == key


def test_research_still_blocks_hard_blocked(research_gate: LicenseGate) -> None:
    """BLOCKED 태그는 research에서도 차단 (계약 미체결)."""
    with pytest.raises(LicenseViolation):
        research_gate.require("enamine_real")


# -- 레지스트리에 없는 키는 KeyError -----------------------------------------
def test_unknown_component_raises(commercial_gate: LicenseGate) -> None:
    with pytest.raises(KeyError):
        commercial_gate.require("not_a_real_component")
