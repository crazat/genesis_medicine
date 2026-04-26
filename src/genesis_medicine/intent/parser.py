"""자연어 intent 파서.

LLM 없이 키워드 + 패턴 매칭 — 빠르고 결정적. Claude Code가 사용자 요청을 이걸로
표준화한 후 workflow_builder에 넘김.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal


# ---- Intent templates ----
# 각 intent는 키워드 + 필수 슬롯 (예: disease, compound)을 가짐.

INTENT_TEMPLATES: dict[str, dict] = {
    "run_pilot": {
        "keywords": ["파일럿", "pilot", "스크리닝", "screening", "돌려",
                     "실행", "run", "cofolding", "공동접힘"],
        "slots": ["disease"],
        "description": "특정 질환에 대한 Boltz-2 cofolding 파일럿 실행",
    },
    "run_md": {
        "keywords": ["md", "molecular dynamics", "분자동역학", "안정성", "검증",
                     "stability"],
        "slots": ["compound", "target"],
        "description": "Top hit MD 10ns로 안정성 검증",
    },
    "build_manuscript": {
        "keywords": ["manuscript", "논문", "paper", "draft", "작성"],
        "slots": ["pilot"],
        "description": "기존 파일럿 결과 → manuscript 자동 생성",
    },
    "novelty_check": {
        "keywords": ["novelty", "신규", "새로움", "선행연구", "prior art", "문헌검색"],
        "slots": [],
        "description": "화합물·시스템 novelty 자동 검증",
    },
    "monitor": {
        "keywords": ["monitor", "모니터", "추적", "갱신", "update", "최신",
                     "preprint", "biorxiv"],
        "slots": [],
        "description": "지속 prior art 모니터링 (bioRxiv + Semantic Scholar)",
    },
    "extend_to_disease": {
        "keywords": ["다른 질병", "확장", "추가 질환", "expand", "포괄",
                     "tow disease", "new disease"],
        "slots": ["disease"],
        "description": "새 질환에 동일 파이프라인 적용",
    },
    "irb_protocol": {
        "keywords": ["irb", "임상시험", "프로토콜", "동의서", "consent",
                     "임상", "clinical"],
        "slots": ["disease"],
        "description": "IRB 프로토콜 + 동의서 자동 생성",
    },
    "cro_quote": {
        "keywords": ["cro", "견적", "in vitro", "검증 비용", "wet-lab",
                     "assay"],
        "slots": ["disease"],
        "description": "CRO in vitro 검증 견적 자동",
    },
    "scaffold_hop": {
        "keywords": ["scaffold", "유사체", "analog", "최적화", "optimize",
                     "reinvent", "hopping"],
        "slots": ["compound"],
        "description": "REINVENT/SATURN으로 유사체 생성",
    },
    "summary": {
        "keywords": ["요약", "summary", "정리", "현황", "status", "전체"],
        "slots": [],
        "description": "전체 진행 상황 + 결과 종합 리포트",
    },
    # Tier 2-8 추가 intent 패턴
    "panderm_diagnose": {
        "keywords": ["사진", "이미지", "안면", "분석", "진단", "diagnose"],
        "slots": ["image_path"],
        "description": "PanDerm 피부 사진 분류 + 처방 추천",
    },
    "logkp_predict": {
        "keywords": ["logkp", "경피", "외용 흡수", "permeability", "skin perm"],
        "slots": ["smiles"],
        "description": "logKp 외용제 흡수 예측",
    },
    "synergy_chou_talalay": {
        "keywords": ["synergy", "시너지", "조합", "combination", "ci",
                      "chou-talalay"],
        "slots": [],
        "description": "Chou-Talalay 약물 조합 synergy",
    },
    "residence_time": {
        "keywords": ["residence time", "k_off", "결합 시간", "kinetics",
                      "동역학"],
        "slots": [],
        "description": "Residence time / k_off 측정",
    },
    "causal_inference": {
        "keywords": ["causal", "인과", "ate", "rwe", "real-world",
                      "환자 데이터"],
        "slots": [],
        "description": "Causal inference (PS matching, AIPW)",
    },
    "fibroblast_subtype": {
        "keywords": ["fibroblast", "subtype", "papillary", "reticular",
                      "위축", "비후"],
        "slots": ["patient_id"],
        "description": "환자 fibroblast subtype → 자동 처방",
    },
    "microbiome_analysis": {
        "keywords": ["microbiome", "마이크로바이옴", "16s", "미생물"],
        "slots": ["patient_id"],
        "description": "16S 결과 → 한약 처방",
    },
    "korean_pgx": {
        "keywords": ["pgx", "약물유전체", "cyp", "hla", "한국인"],
        "slots": [],
        "description": "Korean PGx panel + 외용제 metabolism",
    },
    "donguibogam_search": {
        "keywords": ["동의보감", "고전", "한방서", "donguibogam", "본초"],
        "slots": ["disease"],
        "description": "동의보감 약재 검색",
    },
    "dq_senolytic": {
        "keywords": ["senolytic", "세놀리틱", "모낭", "탈모 회복",
                      "dasatinib", "quercetin"],
        "slots": [],
        "description": "D+Q senolytic + EMB-3 모낭",
    },
    "tripod_check": {
        "keywords": ["tripod", "checklist", "보고 표준", "publishing"],
        "slots": ["manuscript_path"],
        "description": "TRIPOD-AI 27 항목 점검",
    },
    "xai_explain": {
        "keywords": ["왜", "why", "explain", "이유", "shap", "설명"],
        "slots": [],
        "description": "결정 이유 자연어 설명",
    },
    "hira_qaly": {
        "keywords": ["hira", "보험 수가", "qaly", "icer", "reimbursement"],
        "slots": [],
        "description": "한국 보험 수가 + QALY ICER",
    },
    # Tier 9 + facial_dx integration
    "facial_dx_workflow": {
        "keywords": ["facial_dx", "환자 동선", "통합 plan", "안면 분석",
                      "3d 진단"],
        "slots": ["patient_id"],
        "description": "facial_dx + Genesis_Medicine 통합 환자 동선",
    },
    "protac_design": {
        "keywords": ["protac", "degrader", "단백질 분해"],
        "slots": [],
        "description": "PROTAC TGFB1 degrader 디자인",
    },
    "chronotherapy": {
        "keywords": ["자오류주", "시간대", "chronotherapy", "circadian",
                      "시진", "시간 의학"],
        "slots": ["diagnosis"],
        "description": "자오류주 + circadian 외용 schedule",
    },
    "oct_analysis": {
        "keywords": ["oct", "optical coherence", "단층", "흉터 깊이"],
        "slots": [],
        "description": "OCT 흉터 깊이 + facial_dx 통합",
    },
    "engineered_probiotic": {
        "keywords": ["probiotic", "프로바이오틱", "엔지니어링", "syn-bio",
                      "c. acnes", "live biotherapeutic"],
        "slots": ["patient_id"],
        "description": "Engineered C. acnes 자가 probiotic",
    },
    "esg_evaluation": {
        "keywords": ["esg", "지속가능성", "sustainability", "carbon",
                      "탄소", "green chemistry"],
        "slots": [],
        "description": "ESG 평가 + 펀딩 매칭",
    },
}


# 슬롯 vocab — 한국어/영어 매핑
DISEASE_VOCAB = {
    "scar":       ["흉터", "scar", "keloid", "켈로이드", "cicatrix"],
    "pigment":    ["기미", "색소", "melasma", "pigment", "melanin"],
    "alopecia":   ["탈모", "alopecia", "hair loss", "AGA"],
    "acne":       ["여드름", "acne", "rosacea"],
    "photoaging": ["광노화", "photoaging", "안티에이징", "anti-aging", "주름", "wrinkle"],
    "atopic":     ["아토피", "atopic", "eczema", "습진"],
    # AD 인프라 검증용
    "alzheimer":  ["알츠하이머", "alzheimer", "BACE1"],
    "nsclc":      ["폐암", "NSCLC", "EGFR", "lung cancer"],
}


@dataclass
class Intent:
    """파싱된 사용자 의도."""

    raw_text: str
    intent_type: str = "unknown"
    confidence: float = 0.0
    slots: dict[str, str] = field(default_factory=dict)
    matched_keywords: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


def _detect_disease(text_lower: str) -> str | None:
    for key, vocab in DISEASE_VOCAB.items():
        for term in vocab:
            if term.lower() in text_lower:
                return key
    return None


def _detect_compound(text_lower: str) -> str | None:
    """간단한 compound 매칭 (대문자/특정 명명)."""
    candidates = [
        "embelin", "egcg", "curcumin", "asiaticoside", "shikonin",
        "acetylshikonin", "baicalein", "quercetin", "resveratrol",
        "kojic acid", "arbutin", "ellagic acid", "genistein", "berberine",
        "honokiol", "azelaic acid", "salicylic acid", "retinol",
    ]
    for c in candidates:
        if c in text_lower:
            return c.title()
    return None


def parse_intent(text: str) -> Intent:
    """자연어 → Intent."""
    intent = Intent(raw_text=text)
    text_lower = text.lower()

    # intent type 매칭
    best_match = ("unknown", 0)
    for itype, tpl in INTENT_TEMPLATES.items():
        n_match = 0
        matched = []
        for kw in tpl["keywords"]:
            if kw.lower() in text_lower:
                n_match += 1
                matched.append(kw)
        if n_match > best_match[1]:
            best_match = (itype, n_match)
            intent.matched_keywords = matched

    intent.intent_type = best_match[0]
    intent.confidence = min(1.0, best_match[1] / 2.0)   # 2개 이상 매칭이면 1.0

    # 슬롯 채우기
    disease = _detect_disease(text_lower)
    if disease:
        intent.slots["disease"] = disease
    compound = _detect_compound(text_lower)
    if compound:
        intent.slots["compound"] = compound

    # 빠진 슬롯 안내
    if intent.intent_type in INTENT_TEMPLATES:
        required = INTENT_TEMPLATES[intent.intent_type]["slots"]
        missing = [s for s in required if s not in intent.slots]
        if missing:
            intent.suggestions.append(
                f"누락된 정보: {', '.join(missing)}. 예: '흉터 파일럿 돌려줘'"
            )
    else:
        intent.suggestions.append(
            "Intent 인식 실패. 가능한 명령:\n  - 흉터 파일럿 돌려줘\n  "
            "- Embelin MD 검증\n  - 전체 진행 요약\n  - novelty 갱신"
        )

    return intent
