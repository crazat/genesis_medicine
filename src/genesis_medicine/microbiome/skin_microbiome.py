"""Skin microbiome AI — 환자별 16S rRNA → 한약 처방 매핑.

Sci Rep 2017+ + 2026 후속:
  - C. acnes biofilm (adolescent acne 핵심)
  - Staphylococcus epidermidis 과발현 (acne 환자)
  - Malassezia (지루성 피부염, 두피 비듬)
  - 미생물 다양성 감소 = dysbiosis

Recover 한의원 적용:
  - 환자 sample 16S sequencing → 미생물 profile
  - dysbiosis pattern → 자동 처방
  - 외용제 효과 추적 (전·후 미생물 비교)
"""

from __future__ import annotations

from dataclasses import dataclass, field


# 핵심 skin microbiome taxa
KEY_TAXA = {
    "Cutibacterium": {"role": "commensal/pathogen", "site": "sebaceous"},
    "Cutibacterium_acnes": {"role": "acne_pathogen", "site": "sebaceous"},
    "Staphylococcus_epidermidis": {"role": "commensal_or_pathogen",
                                     "site": "moist"},
    "Staphylococcus_aureus": {"role": "atopic_pathogen", "site": "lesional"},
    "Malassezia": {"role": "fungal_seborrheic", "site": "scalp"},
    "Streptococcus": {"role": "commensal", "site": "moist"},
    "Corynebacterium": {"role": "commensal", "site": "moist/dry"},
    "Lactobacillus": {"role": "probiotic", "site": "various"},
}


# Dysbiosis pattern → 한약 처방 매핑
DYSBIOSIS_TO_RX = {
    "acne_inflammatory": {
        "marker": "C. acnes biofilm + S. epidermidis 과발현 + 다양성 감소",
        "primary_rx": "황련해독탕 (berberine)",
        "compounds": ["Berberine", "Baicalin", "Baicalein"],
        "topical": "감초 외용 (licochalcone A)",
        "rationale": "Berberine은 anti-biofilm + AR/SREBP1 차단",
    },
    "atopic_aureus": {
        "marker": "S. aureus 과발현 + 다양성 큰 감소",
        "primary_rx": "황련해독탕 + 온청음 보강",
        "compounds": ["Berberine", "Coptisine"],
        "topical": "황련 추출 + 자운고 보호",
        "rationale": "Berberine은 S. aureus biofilm 차단",
    },
    "seborrheic_malassezia": {
        "marker": "Malassezia 과발현 (두피·콧등)",
        "primary_rx": "황금탕 (baicalin)",
        "compounds": ["Baicalin", "Baicalein"],
        "topical": "황금 외용",
        "rationale": "Baicalin antifungal",
    },
    "scar_dysbiosis": {
        "marker": "다양성 감소 + 비-acne 환경",
        "primary_rx": "자운고 + EMB-3 강화",
        "compounds": ["Shikonin", "EMB-3"],
        "topical": "자운고 외용",
        "rationale": "shikonin antimicrobial broad-spectrum",
    },
    "balanced_healthy": {
        "marker": "다양성 정상 + 우점종 균형",
        "primary_rx": "유지 (외용제 최소)",
        "compounds": ["EGCG (universal preventive)"],
        "topical": "녹차 외용 (보존)",
        "rationale": "EGCG는 미생물총 보존 + anti-aging",
    },
}


@dataclass
class MicrobiomeProfile:
    """단일 환자 16S 결과."""

    patient_id: str = ""
    sample_site: str = "lesional"   # lesional | non-lesional | scalp
    shannon_diversity: float = 0.0
    relative_abundance: dict = field(default_factory=dict)
    dysbiosis_pattern: str = ""
    recommended_rx: str = ""
    recommended_compounds: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def classify_dysbiosis(rel_abund: dict, shannon: float) -> str:
    """16S relative abundance → dysbiosis pattern."""
    cutibacterium = rel_abund.get("Cutibacterium_acnes", 0.0)
    s_epidermidis = rel_abund.get("Staphylococcus_epidermidis", 0.0)
    s_aureus = rel_abund.get("Staphylococcus_aureus", 0.0)
    malassezia = rel_abund.get("Malassezia", 0.0)

    if s_aureus > 0.3 and shannon < 1.5:
        return "atopic_aureus"
    if cutibacterium > 0.3 and s_epidermidis > 0.2 and shannon < 2.0:
        return "acne_inflammatory"
    if malassezia > 0.2:
        return "seborrheic_malassezia"
    if shannon < 1.5:
        return "scar_dysbiosis"
    return "balanced_healthy"


def analyze_patient_microbiome(rel_abund: dict, shannon: float,
                                 patient_id: str = "",
                                 site: str = "lesional") -> MicrobiomeProfile:
    """환자 16S 결과 → 처방 추천."""
    pattern = classify_dysbiosis(rel_abund, shannon)
    rx_info = DYSBIOSIS_TO_RX.get(pattern, {})

    return MicrobiomeProfile(
        patient_id=patient_id, sample_site=site,
        shannon_diversity=shannon,
        relative_abundance=rel_abund,
        dysbiosis_pattern=pattern,
        recommended_rx=rx_info.get("primary_rx", ""),
        recommended_compounds=rx_info.get("compounds", []),
        metadata={
            "marker": rx_info.get("marker", ""),
            "topical": rx_info.get("topical", ""),
            "rationale": rx_info.get("rationale", ""),
        },
    )


def korean_microbiome_cro_pricing() -> dict:
    """한국 16S sequencing 위탁 가격 (2026 평균)."""
    return {
        "Macrogen 16S": "₩50,000/sample (V3-V4, 100k reads)",
        "Theragen Bio Shotgun metagenome": "₩200,000/sample (functional analysis)",
        "Bioneer 16S": "₩60,000/sample",
        "처리 시간": "2-3주",
        "데이터 분석 추가": "₩100,000-500,000 (QIIME2 + SILVA + 우리 모듈)",
        "Recover 시범": "환자 30명 × ₩50K = ₩1.5M for paper data",
    }


def integrate_with_genesis_medicine() -> dict:
    """Genesis_Medicine v3 통합 인터페이스."""
    return {
        "step_1_sample": "환자 면봉 swab (병변 + 정상 비교)",
        "step_2_sequencing": "Macrogen 16S V3-V4 (₩50K)",
        "step_3_analysis": "QIIME2 + SILVA → relative abundance + Shannon",
        "step_4_classify": "analyze_patient_microbiome() → dysbiosis pattern",
        "step_5_prescribe": "DYSBIOSIS_TO_RX 매핑 + EMB-3/EGCG 동시 처방",
        "step_6_followup": "치료 후 4-8주 재검 → 미생물 회복 추적",
        "expected_value": (
            "환자 맞춤 처방 + Recover 사업 차별화 + paper "
            "'AI-guided microbiome restoration in Korean medicine practice'"
        ),
    }
