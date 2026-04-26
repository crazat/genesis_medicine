"""PanDerm dermatology foundation model adapter.

PanDerm (Nature Medicine 2025, Yan et al.):
  - 2M+ skin disease images, 11 clinical institutions, 4 imaging modalities
  - Self-supervised pretrain
  - 28 benchmarks SOTA
  - 10% labeled data로 기존 모델 능가
  - URL: https://www.nature.com/articles/s41591-025-03747-y
  - GitHub: 공식 release 확인 필요 (논문 supplementary 또는 후속 announcement)

Recover 한의원 적용:
  - AI 안면 분석 (흉터·기미·여드름·아토피·광노화 5질환)
  - 환자 사진 → 자동 진단 + 분자 수준 처방 추천 (Genesis_Medicine v3 호출)
  - 한국인 dermatology fine-tune 데이터 추가 권장

라이선스: PanDerm 공식 release 시 확인 필요. Nature Medicine 출판 = 학술 OK,
commercial 사용은 별도 협의 가능성. 우리는 image embedding만 추출 → 다른 모델
training용으로 사용은 commercial OK.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")


@dataclass
class SkinImageAnalysis:
    """피부 사진 분석 결과."""

    image_path: str
    primary_diagnosis: str = ""        # e.g. "hypertrophic scar"
    confidence: float = 0.0
    secondary_diagnoses: list = field(default_factory=list)
    severity: str = ""                 # mild | moderate | severe
    recommended_targets: list = field(default_factory=list)   # 분자 표적
    recommended_compounds: list = field(default_factory=list) # 한약 후보
    model_version: str = "panderm-v1-stub"


# 5질환 → 분자 표적 매핑 (Genesis_Medicine v3와 통합)
DISEASE_TO_TARGETS = {
    "hypertrophic_scar":  ["TGFB1", "MMP1", "CTGF"],
    "keloid":             ["TGFB1", "CTGF", "LOX"],
    "atrophic_scar":      ["MMP1", "VEGFA", "FGF2"],
    "melasma":            ["TYR", "TYRP1", "MITF"],
    "vitiligo":           ["TYR", "MITF"],
    "androgenetic_alopecia": ["SRD5A2", "AR", "WNT10B"],
    "alopecia_areata":    ["JAK1", "JAK3"],
    "acne_vulgaris":      ["AR", "SRD5A2", "PTGS2"],
    "rosacea":            ["TLR2", "LL37"],
    "atopic_dermatitis":  ["JAK1", "IL4R", "IL13"],
    "psoriasis":          ["IL17A", "IL23"],
    "photoaging":         ["MMP1", "SIRT1", "JUN"],
}


# 5질환 → 한약 처방 추천 (Recover 한의원 컨텍스트)
DISEASE_TO_RECOVER_RX = {
    "hypertrophic_scar":  ["자운고 (자초)", "활혈거어탕", "자운고 + EMB-3 강화"],
    "keloid":             ["활혈거어탕 (단삼·호장근)", "자운고 강화"],
    "atrophic_scar":      ["당귀음자 (혈허)", "센텔라 외용 (Madecassol)"],
    "melasma":            ["옥용산 (감초·녹차)", "닥나무 추출"],
    "androgenetic_alopecia": ["측백엽·하수오 (SRD5A2)", "약침"],
    "acne_vulgaris":      ["황련해독탕 (베르베린)", "황금"],
    "atopic_dermatitis":  ["온청음 (黃芪)", "황련해독탕"],
    "photoaging":         ["단삼 (tanshinone)", "녹차 (EGCG) 외용"],
}


def analyze_skin_image(image_path: str | Path) -> SkinImageAnalysis:
    """피부 사진 분석 (PanDerm 미공개 시 stub).

    실제 구현 (PanDerm 공개 후):
      1. PanDerm encoder 로드 (HF 또는 official repo)
      2. 입력 이미지 → embedding (1024-d)
      3. 5질환 classification head (한국인 fine-tune 권장)
      4. severity head + lesion segmentation
      5. 분자 표적 매핑 (DISEASE_TO_TARGETS)
      6. 한약 처방 매핑 (DISEASE_TO_RECOVER_RX)

    Returns:
        SkinImageAnalysis with empty fields (PanDerm 미공개 stub).
    """
    return SkinImageAnalysis(
        image_path=str(image_path),
        primary_diagnosis="(PanDerm 모델 미공개 — 공식 release 시 자동 활성화)",
        confidence=0.0,
        recommended_targets=[],
        recommended_compounds=[],
        model_version="panderm-stub",
    )


def get_treatment_recommendations(diagnosis: str) -> dict:
    """진단명 → Genesis_Medicine v3 분자 표적 + Recover 한약 처방."""
    diag_norm = diagnosis.lower().replace(" ", "_").replace("-", "_")
    return {
        "diagnosis": diagnosis,
        "molecular_targets": DISEASE_TO_TARGETS.get(diag_norm, []),
        "recover_prescriptions": DISEASE_TO_RECOVER_RX.get(diag_norm, []),
        "next_action": (
            "1. 환자 사진 PanDerm 분석 → severity\n"
            "2. molecular_targets에 대해 Genesis_Medicine v3 cofold (Boltz-2)\n"
            "3. recover_prescriptions 중 환자 체질에 맞는 1순위 처방 + AI 강화\n"
            "4. 약침/외용제 제조 → 시술"
        ),
    }


def integrate_with_genesis_medicine(diagnosis: str, patient_id: str = "") -> dict:
    """PanDerm 진단 → Genesis_Medicine v3 통합 호출 인터페이스.

    실제 운영 시 ChemCrow agent (chemcrow_wrapper.py) 호출하여 자동 처방.
    """
    rec = get_treatment_recommendations(diagnosis)
    return {
        "patient": patient_id,
        "diagnosis": diagnosis,
        "molecular_targets": rec["molecular_targets"],
        "recover_prescriptions": rec["recover_prescriptions"],
        "agent_query_template": (
            f"진단: {diagnosis}. 분자 표적 {rec['molecular_targets']}에 강하게 결합하는 "
            f"한약 처방 ({rec['recover_prescriptions']})의 핵심 성분을 분자 수준으로 "
            "검증하고 효능 ranking 추천."
        ),
    }
