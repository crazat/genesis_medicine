"""Korean Pharmacogenomics Panel (medRxiv 2026-01).

14,490 Korean Biobank Array v2.0 PGx 변이 분석 결과:
  - 모든 한국인이 ≥1 PGx variant 보유
  - 핵심 유전자: CYP2C19, SLCO1B1, CYP3A5, VKORC1
  - HLA-B*15:02 (Asian) — severe cutaneous adverse reaction 위험
  - CYP2D6*10 — East Asian decreased function (drug 30-50% 감소)
  - CYP2C19*17 — 0.7% MAF (백인 22% 대비 매우 드뭄)

Recover 한의원 외용제 IND 자료 필수:
  - 외용제도 systemic absorption (PBPK ratio 36× 외용 vs 2× systemic)
  - 환자별 PGx profile → EMB-3 metabolism prediction
  - HLA panel → SCAR 위험 사전 차단
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Korean PGx 핵심 alleles (medRxiv 2026-01 frequencies)
KOREAN_PGX_ALLELES = {
    "CYP2D6*10": {
        "frequency_kor": 0.45,    # ~45% (East Asian high)
        "function": "decreased",
        "drug_metabolism_change": "30-50% 감소",
        "relevant_drugs": ["codeine", "tamoxifen", "antidepressants",
                            "비스테로이드성 진통제 일부"],
        "topical_relevance": "HIGH if systemic absorption present",
    },
    "CYP2C19*2": {
        "frequency_kor": 0.30,
        "function": "loss_of_function",
        "drug_metabolism_change": "활성 대사 사라짐",
        "relevant_drugs": ["clopidogrel", "PPI 일부"],
        "topical_relevance": "LOW (외용제 대부분 무관)",
    },
    "CYP2C19*17": {
        "frequency_kor": 0.007,    # 0.7% MAF — 매우 드뭄
        "function": "increased",
        "drug_metabolism_change": "활성 증가",
        "topical_relevance": "LOW",
    },
    "CYP3A5*3": {
        "frequency_kor": 0.30,    # nonexpresser
        "function": "loss_of_function",
        "relevant_drugs": ["tacrolimus", "vincristine", "외용 calcineurin inhibitor"],
        "topical_relevance": "MID (외용 tacrolimus 처방 시)",
    },
    "SLCO1B1*5": {
        "frequency_kor": 0.13,
        "function": "decreased_uptake",
        "relevant_drugs": ["statin"],
        "topical_relevance": "LOW",
    },
    "HLA-B*15:02": {
        "frequency_kor": 0.04,    # 4% Korean
        "function": "SCAR_risk",
        "drug_metabolism_change": "Stevens-Johnson Syndrome (SJS) / TEN 위험",
        "relevant_drugs": ["carbamazepine", "phenytoin", "allopurinol"],
        "topical_relevance": "CRITICAL (외용 알레르기 반응)",
    },
    "HLA-B*58:01": {
        "frequency_kor": 0.06,
        "function": "SCAR_risk",
        "relevant_drugs": ["allopurinol"],
        "topical_relevance": "MID",
    },
    "VKORC1": {
        "frequency_kor": 0.92,
        "function": "warfarin_sensitivity",
        "topical_relevance": "LOW",
    },
}


@dataclass
class KoreanPGxProfile:
    """단일 환자 PGx profile."""

    patient_id: str = ""
    alleles: dict = field(default_factory=dict)   # {"CYP2D6*10": "homozygous", ...}
    hla_screen: list = field(default_factory=list)
    drug_recommendations: dict = field(default_factory=dict)
    risk_flags: list = field(default_factory=list)


def evaluate_topical_drug_compatibility(
    patient_alleles: dict, drug_name: str = "EMB-3",
) -> dict:
    """환자 PGx profile + 외용제 호환성 평가.

    EMB-3는 신규 — known CYP metabolism 데이터 없음.
    그러나 1,4-benzoquinone scaffold은 일반적으로 CYP2D6 + CYP3A4 metabolism.
    """
    risks = []
    notes = []

    if patient_alleles.get("CYP2D6*10") == "homozygous":
        notes.append("CYP2D6 활성 30-50% 감소 — EMB-3 systemic 농도 증가 예상")
        risks.append("topical → systemic 노출 증가 가능 (외용제 농도 ↓ 권장)")

    if patient_alleles.get("CYP3A5*3") == "homozygous":
        notes.append("CYP3A5 비발현 — minor metabolism 영향")

    if "HLA-B*15:02" in patient_alleles.get("hla_screen", []):
        risks.append("⚠️ SCAR 고위험 — 외용제 첫 적용 시 patch test 필수")

    if "HLA-B*58:01" in patient_alleles.get("hla_screen", []):
        risks.append("🟡 중간 SCAR 위험 — 모니터링")

    return {
        "drug": drug_name,
        "patient_alleles": patient_alleles,
        "metabolism_notes": notes,
        "safety_flags": risks,
        "recommendation": (
            "정상 dose" if not risks else
            "⚠️ Patch test 후 시작, 농도 50%로 적정 권장"
        ),
        "monitoring": "1주 후 systemic 노출 추적, AE 즉시 reporting",
    }


def korean_pgx_population_summary() -> dict:
    """한국 인구 PGx 분포 (medRxiv 2026-01) summary."""
    return {
        "study_size": "14,490 Korean Biobank Array v2.0 (2026-01)",
        "all_carry_at_least_one_variant": "100% (모든 한국인 ≥1 PGx 변이)",
        "key_findings": {
            "CYP2D6*10 East Asian high": "45% frequency",
            "CYP3A5*3 non-expresser": "30%",
            "HLA-B*15:02 SCAR risk": "4%",
            "CYP2C19*17 (백인 22% 대비)": "0.7% (매우 드뭄)",
        },
        "topical_drug_implications": (
            "외용제 IND 자료 — Korean PGx panel 필수. "
            "서양 임상시험 데이터 그대로 사용 시 안전성 평가 부정확. "
            "MFDS 30영업일 IND 통과 시 한국 PGx 데이터 첨부 권장."
        ),
        "recommended_panel_for_recover": [
            "CYP2D6 (★ 외용제 metabolism)",
            "CYP3A5 (★ topical tacrolimus)",
            "HLA-B*15:02 + HLA-B*58:01 (★ SCAR 사전 screening)",
            "SLCO1B1 (statin 동시 복용 시)",
        ],
        "cost_per_patient_krw": 80_000,   # Korea PGx panel 표준
        "vendor": "Macrogen, KOGES (Korean Genome Epidemiology Study)",
    }
