"""Engineered Cutibacterium acnes — autologous live biotherapeutic.

Cell Systems 2025 (Synthetically programmed antioxidant by C. acnes):
  - C. acnes synthetic biology toolbox 검증
  - 모낭 chassis로 antioxidant secretion
  - npj Biofilms 2023 + 2024-2025 후속

Recover 한의원 사업 모델:
  1. 환자 자가 C. acnes 분리 (skin swab)
  2. KAIST/Macrogen syn-bio CRO에 위탁
  3. anti-fibrotic gene + EMB-3 binding domain 삽입
  4. 자가 외용 probiotic 환자 적용

자연어 호출:
  "환자 자가 probiotic 디자인"
  → design_engineered_probiotic(patient_id, target_function)
"""

from __future__ import annotations

from dataclasses import dataclass, field


# C. acnes engineerable functions (Cell Systems 2025 + 후속)
ENGINEERED_FUNCTIONS = {
    "antioxidant_secretion": {
        "transgene": "catalase + SOD",
        "validated_by": "Cell Systems 2025",
        "indication": "광노화, UV stress",
    },
    "anti_fibrotic_secretion": {
        "transgene": "TGF-β decoy receptor (TGFBR2 ectodomain)",
        "validated_by": "Hypothesis (우리 구현 가설)",
        "indication": "흉터, 비후성/켈로이드",
    },
    "biofilm_disruptor": {
        "transgene": "biofilm dispersal enzyme (DNase + alginate lyase)",
        "validated_by": "PMC 12805557",
        "indication": "여드름 (자가 biofilm 제거)",
    },
    "anti_inflammatory_il10": {
        "transgene": "IL-10 secretion",
        "validated_by": "다양한 LBP 연구",
        "indication": "아토피, 만성 염증",
    },
    "porphyrin_block": {
        "transgene": "porphyrin biosynthesis 차단 (CRISPRi)",
        "indication": "여드름 (porphyrin이 acne 유도)",
    },
    "wnt_activator": {
        "transgene": "WNT3A secretion",
        "indication": "탈모 (모낭 줄기세포 자극)",
    },
    "vitamin_d_synthesis": {
        "transgene": "ergosterol → vitamin D2 enzymatic",
        "indication": "vitamin D 부족, 면역 강화",
    },
}


@dataclass
class EngineeredProbioticDesign:
    """단일 환자 맞춤 probiotic 디자인."""

    patient_id: str = ""
    base_strain: str = "C. acnes type II"
    target_function: str = ""
    transgene_design: dict = field(default_factory=dict)
    biocontainment: dict = field(default_factory=dict)
    safety_evaluation: list = field(default_factory=list)
    delivery_format: str = ""
    natural_language_summary: str = ""


def design_engineered_probiotic(
    patient_id: str = "P001",
    target_function: str = "anti_fibrotic_secretion",
    delivery_format: str = "topical_cream",
) -> EngineeredProbioticDesign:
    """환자 자가 C. acnes 엔지니어링 디자인 (자연어 호출).

    Recover 환자 동선:
      1. swab → C. acnes 분리 (clinical lab)
      2. genome sequencing (Macrogen, ₩200K)
      3. 본 디자인 → KAIST syn-bio CRO 위탁
      4. 8-12주 후 자가 strain 제조 → 환자 외용
    """
    func = ENGINEERED_FUNCTIONS.get(target_function)
    if func is None:
        return EngineeredProbioticDesign(
            patient_id=patient_id,
            natural_language_summary=(
                f"❌ {target_function} 미등록. 가용: {list(ENGINEERED_FUNCTIONS.keys())}"
            ),
        )

    # Biocontainment (Frontiers 2022 표준)
    biocontainment = {
        "auxotrophy": "essential gene knockout (e.g. dapA) + complement only on patient skin",
        "kill_switch": "antimicrobial peptide induction at body temp ≠ 37°C",
        "horizontal_gene_transfer": "원형 plasmid 제거, integrative chromosomal only",
        "validated": "Frontiers Bioeng 2022 + Cell Systems 2025",
    }

    # Safety evaluation (PIPA + IRB)
    safety = [
        f"✅ Autologous (환자 자가 strain) — 면역 반응 ↓",
        f"✅ Biocontainment 3-layer (auxotrophy + kill switch + chromosomal)",
        f"⚠️ KFDA LBP 가이드라인 (2024 임시) — IND 필요",
        f"⚠️ PIPA 생체정보 보호 — 환자 동의 필수",
        f"⚠️ BSL-2 시설 운영 필요 (Recover 단독 불가, 협업 CRO)",
    ]

    delivery_options = {
        "topical_cream": "Recover 외용제 ingredient (live bacteria 안정성 4°C)",
        "follicle_injection": "약침 cocktail에 동시 주입",
        "patch": "microneedle patch 통합",
    }

    nl = (
        f"**Engineered C. acnes 자가 probiotic 디자인**\n\n"
        f"환자: {patient_id}\n"
        f"Base strain: C. acnes type II (autologous, 환자 swab)\n"
        f"Target function: {target_function}\n"
        f"  → Transgene: {func['transgene']}\n"
        f"  → Validated: {func['validated_by']}\n"
        f"  → Indication: {func['indication']}\n\n"
        f"Biocontainment 3-layer:\n"
        + "\n".join(f"  - {k}: {v}" for k, v in biocontainment.items()) + "\n\n"
        f"Safety:\n"
        + "\n".join(f"  {s}" for s in safety) + "\n\n"
        f"Delivery: {delivery_format} — {delivery_options.get(delivery_format, '')}\n\n"
        f"**개발 timeline**:\n"
        f"  Week 1-2: 환자 swab + Macrogen 16S 시퀀싱 (₩200K)\n"
        f"  Week 3-4: KAIST syn-bio CRO 위탁 → 형질전환 (₩30M)\n"
        f"  Week 5-8: 검증 + biocontainment 확인\n"
        f"  Week 9-12: 환자 자가 외용 (BSL-2 시설 협업)\n\n"
        f"**Recover 사업 가치**: 한국 first autologous live biotherapeutic 외용제. "
        f"OliX siRNA + ExoCoBio exosome + 본 syn-bio = 한국 신물질 3-축.\n\n"
        f"**Paper**: 'First autologous engineered C. acnes for {func['indication']}'"
    )

    return EngineeredProbioticDesign(
        patient_id=patient_id,
        target_function=target_function,
        transgene_design=func,
        biocontainment=biocontainment,
        safety_evaluation=safety,
        delivery_format=delivery_format,
        natural_language_summary=nl,
    )
