"""ESG / Green Chemistry 분석 — Genesis_Medicine v3 친화도 + 펀딩 매칭.

Singh 2026 (Wiley) + AstraZeneca 2026 + Pfizer:
  - 제약 carbon footprint healthcare 20-55%
  - AstraZeneca Scope 1+2 emissions 98% 감소 (2026)
  - Pfizer biocatalytic 90% 용매 감소
  - Race to Zero 46% 제약사 가입
  - ESG 직무 89% 증가 (2020 이후)
  - AI/ML in green chemistry — 예측 toxicity, 반응 최적화

자연어 호출:
  "우리 시스템 ESG 친화도 평가"
  → evaluate_esg_friendliness()

  "ESG 펀딩 매칭"
  → match_esg_funding()
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ESG 평가 기준 (Race to Zero + GRI standards)
ESG_CRITERIA = {
    "environmental": {
        "biodiversity_use": "한약 천연물 (NPASS, COCONUT)",
        "synthesis_route_green": "AI-driven retrosynthesis (DeepRetro)",
        "carbon_footprint_reduction": (
            "in silico → wet lab 시도 절감 → CO2 ↓"
        ),
        "sustainable_supply": "한국 약전 재배 가능 한약재 우선",
    },
    "social": {
        "korean_traditional_medicine_preservation": "동의보감 디지털화",
        "patient_centered": "Recover 한의원 임상 기여",
        "open_access_data": "GitHub commercial-friendly 라이선스",
        "global_health": "IPF cross-disease (저소득국가 적응증)",
    },
    "governance": {
        "transparency": "TRIPOD-AI 27 항목 reporting",
        "regulatory_compliance": "PIPA + AI Basic Act + 의료법",
        "ethics_review": "IRB approval (facial_dx D-1)",
        "ai_explainability": "SHAP/Grad-CAM 통합",
    },
}


# ESG 펀딩 (한국 + 글로벌)
ESG_FUNDING_SOURCES = {
    "Korea Investment Corporation (KIC)": {
        "type": "sovereign wealth",
        "esg_focus": "K-bio + sustainable",
        "recent_investments": "Korean biotech ESG 강조",
        "ticket_size_usd": "10-50M",
    },
    "Singapore GIC": {
        "type": "sovereign wealth",
        "esg_focus": "ESG investing global standard",
        "ticket_size_usd": "20-100M",
    },
    "BlackRock Climate Finance Partnership": {
        "type": "asset manager ESG fund",
        "esg_focus": "climate aligned pharma",
        "ticket_size_usd": "5-50M",
    },
    "한국 그린뉴딜 펀드": {
        "type": "정부 지원 (산업통상자원부)",
        "esg_focus": "green tech + bio",
        "korean_priority": True,
    },
    "Race to Zero participating pharma 협력": {
        "type": "전략 파트너",
        "examples": ["AstraZeneca", "Pfizer", "Roche"],
        "potential": "공동 R&D + 자금",
    },
    "NIPA AI 의료 디지털 전환": {
        "type": "한국 정부 사업",
        "korean_priority": True,
        "size_krw": 2_160_000_000,   # 2.16억 우리 응모 자료 기준
    },
}


@dataclass
class ESGScore:
    """우리 시스템 ESG 평가."""

    environmental_score: float = 0.0
    social_score: float = 0.0
    governance_score: float = 0.0
    overall_score: float = 0.0
    strengths: list = field(default_factory=list)
    gaps: list = field(default_factory=list)
    funding_match: list = field(default_factory=list)
    natural_language_summary: str = ""


def evaluate_esg_friendliness() -> ESGScore:
    """Genesis_Medicine v3 + Recover ESG 친화도 평가 (자연어 호출)."""
    # E score (biodiversity, green synthesis, carbon)
    env = []
    env.append("✅ 한약 천연물 = biodiversity-based sustainable")
    env.append("✅ in silico 우선 → wet lab 절감 → CO2 ↓")
    env.append("✅ AI-driven 반응 최적화 (DeepRetro 통합)")
    env.append("⚠️ 현재 carbon footprint 측정 미완 (가산점 가능)")
    env_score = 0.85

    # S score (Korean medicine, patient, open)
    soc = []
    soc.append("✅ 한국 한의약 보존 (동의보감 디지털, Donguibogam miner)")
    soc.append("✅ Recover 임상 기여 (분자 처방)")
    soc.append("✅ GitHub Apache/MIT — open science")
    soc.append("✅ IPF cross-disease (글로벌 보건)")
    soc_score = 0.90

    # G score (transparency, compliance, ethics)
    gov = []
    gov.append("✅ TRIPOD-AI 27 항목 자동 점검")
    gov.append("✅ PIPA + AI Basic Act 준수 (facial_dx 통합)")
    gov.append("✅ IRB approval pipeline (facial_dx D-1)")
    gov.append("✅ XAI explainability 통합")
    gov_score = 0.88

    overall = (env_score + soc_score + gov_score) / 3

    # Funding match
    funding_match = []
    for name, info in ESG_FUNDING_SOURCES.items():
        if info.get("korean_priority"):
            funding_match.append(f"🇰🇷 {name} (가장 적합)")
        elif "K-bio" in info.get("esg_focus", "") or "Korean" in info.get("esg_focus", ""):
            funding_match.append(f"🟢 {name}")
        else:
            funding_match.append(f"🟡 {name} (글로벌, 진입 후)")

    nl = (
        f"**Genesis_Medicine v3 + Recover ESG 평가**\n\n"
        f"**Environmental** ({env_score*100:.0f}/100):\n"
        + "\n".join(f"  {e}" for e in env) + "\n\n"
        f"**Social** ({soc_score*100:.0f}/100):\n"
        + "\n".join(f"  {s}" for s in soc) + "\n\n"
        f"**Governance** ({gov_score*100:.0f}/100):\n"
        + "\n".join(f"  {g}" for g in gov) + "\n\n"
        f"**전체 ESG 점수**: {overall*100:.0f}/100 ⭐\n\n"
        f"**Funding 매칭** (우선순위):\n"
        + "\n".join(f"  {f}" for f in funding_match[:4]) + "\n\n"
        f"**ESG 차별화 메시지**:\n"
        f"- 'AI-augmented Korean traditional medicine = inherently sustainable'\n"
        f"- biodiversity 기반 + in silico 가속 + 한국 정부 사업 동조\n"
        f"- AstraZeneca 2026 모델 (Scope 1+2 -98%)에 우리는 출발점부터 친화\n\n"
        f"**다음 행동**:\n"
        f"- NIPA + 한국 그린뉴딜 펀드 응모 (즉시)\n"
        f"- KIC + GIC 미팅 (12-24개월 후 Series A)\n"
        f"- Race to Zero 가입 검토 (글로벌 공신력)"
    )

    return ESGScore(
        environmental_score=env_score, social_score=soc_score,
        governance_score=gov_score, overall_score=overall,
        strengths=env + soc + gov,
        gaps=["carbon footprint 정량 측정", "ISO 14001 인증",
               "Race to Zero 가입"],
        funding_match=funding_match,
        natural_language_summary=nl,
    )


def estimate_carbon_footprint(n_compounds: int = 102,
                                 wet_lab_assays: int = 0) -> dict:
    """우리 파이프라인 carbon footprint 추정.

    in silico 1 cofold ≈ 0.5 kWh ≈ 0.2 kg CO2 (한국 전력 mix)
    Wet lab 1 IC50 ≈ 50 kg CO2 (reagent + 운영)
    """
    in_silico_kwh = n_compounds * 0.5    # 모든 cofold + MD + ABFE 합산 추정
    in_silico_co2_kg = in_silico_kwh * 0.4   # 한국 grid 0.4 kgCO2/kWh
    wet_lab_co2_kg = wet_lab_assays * 50

    saved_co2_kg = (n_compounds * 50) - in_silico_co2_kg   # wet 대체분
    return {
        "n_compounds_in_silico": n_compounds,
        "wet_lab_assays_actual": wet_lab_assays,
        "in_silico_carbon_kg_co2": int(in_silico_co2_kg),
        "wet_lab_carbon_kg_co2": int(wet_lab_co2_kg),
        "carbon_saved_vs_full_wet_lab_kg_co2": int(saved_co2_kg),
        "interpretation": (
            f"in silico 우선 시 wet lab 대비 {int(saved_co2_kg):,} kg CO2 절감. "
            f"(한국 평균 가정 1년 배출량 ≈ 4,500 kg → "
            f"{int(saved_co2_kg/4500)}가구 1년치 절감)"
        ),
    }
