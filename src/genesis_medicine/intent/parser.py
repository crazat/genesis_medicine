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
