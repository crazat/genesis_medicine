"""T10-1 AI Safety / Hallucination Guard — 의료 LLM output 검증.

근거: Stanford 2025 medical hallucination 23–64% rates, MLCommons AILuminate
Jailbreak Benchmark v0.5 (2025). Genesis_Medicine은 환자 직결 의료 결정에
사용되므로 환각·jailbreak 차단이 critical.

설계:
  - 모든 LLM agent output을 본 모듈로 통과시켜 검증
  - 분자 SMILES, 화합물명, 단백질명, p-value 등 fact claim에 source citation 강제
  - 위험 jailbreak 패턴 (e.g., "ignore previous instructions") 차단
  - 위반 시 reject + 사용자에게 audit log 표시

자연어 호출:
  "이 답변 환각 검증해줘"
  → guard_output(text)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# 차단 패턴 — jailbreak (MLCommons AILuminate 기반)
JAILBREAK_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+(instructions|rules)",
    r"(disregard|override|bypass)\s+(safety|guideline|policy)",
    r"act\s+as\s+(if|though|a)\s+(unrestricted|jailbroken|no\s+filter)",
    r"DAN\s+mode",   # "Do Anything Now" jailbreak
    r"pretend\s+(you|to)\s+(have|are)\s+(no|different)\s+(rules|guidelines)",
    r"system\s+prompt\s+(reveal|leak|show)",
]

# 의료 위험 claim 패턴 — citation 필요
MEDICAL_FACT_PATTERNS = [
    r"\b(IC50|EC50|Ki|Kd)\s*[=:]\s*\d",      # 정량 affinity
    r"\bp\s*[<>=]\s*0\.\d+",                  # p-value
    r"\b\d+(\.\d+)?\s*(nM|µM|uM|mM)\b",      # 농도
    r"\bphase\s+[I1V]+\b",                    # 임상 phase
    r"\bFDA\s+(approved|cleared)\b",
    r"\bMFDS\s+(승인|허가)\b",
]

# 안전 source 화이트리스트 (citation으로 인정)
TRUSTED_SOURCES = [
    "PubMed", "PMC", "ChEMBL", "DrugBank", "Boltz-2", "ABFE",
    "ADMET-AI", "MD simulation", "REINVENT", "openmmtools",
    "FDA", "MFDS", "EMA", "Recover 한의원", "Genesis_Medicine",
    "facial_dx", "동의보감", "KP", "KHP", "doi:", "arxiv:", "github.com",
]


@dataclass
class GuardResult:
    """환각/jailbreak 검증 결과."""

    safe: bool = True
    flagged_jailbreak: list = field(default_factory=list)
    fact_claims_without_source: list = field(default_factory=list)
    audit_log: list = field(default_factory=list)
    recommendation: str = ""


def guard_output(text: str, *, strict: bool = False) -> GuardResult:
    """LLM 출력 검증 — jailbreak + medical hallucination 차단.

    strict=True 면 fact claim 없는 의료 발언을 거부.
    """
    r = GuardResult(safe=True)

    # 1) jailbreak 패턴
    text_lower = text.lower()
    for pat in JAILBREAK_PATTERNS:
        if re.search(pat, text_lower):
            r.flagged_jailbreak.append(pat)
            r.safe = False

    if r.flagged_jailbreak:
        r.audit_log.append(
            f"⛔ JAILBREAK 차단 ({len(r.flagged_jailbreak)} 패턴 매칭)"
        )

    # 2) 의료 fact claim citation 검증
    for pat in MEDICAL_FACT_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            ctx_start = max(0, match.start() - 100)
            ctx_end = min(len(text), match.end() + 200)
            ctx = text[ctx_start:ctx_end]
            has_source = any(s.lower() in ctx.lower() for s in TRUSTED_SOURCES)
            if not has_source:
                r.fact_claims_without_source.append({
                    "claim": match.group(),
                    "position": match.start(),
                    "context": ctx[:150] + "...",
                })

    if r.fact_claims_without_source:
        r.audit_log.append(
            f"⚠️ 인용 없는 의료 claim {len(r.fact_claims_without_source)}건"
        )
        if strict:
            r.safe = False

    # 3) 권장
    if r.safe:
        r.recommendation = "✅ Output 안전. 사용자에게 노출 가능."
    elif r.flagged_jailbreak:
        r.recommendation = (
            "⛔ Jailbreak 시도 차단. 사용자 입력 재작성 요청. "
            "Audit team에 보고 권장."
        )
    elif r.fact_claims_without_source:
        r.recommendation = (
            "⚠️ Fact claim에 source citation 추가 필요. "
            "Boltz-2/ABFE/PubMed 등 명시 후 재시도."
        )
    return r


def enforce_citation(claim: str, sources: list[str]) -> str:
    """주어진 claim에 자동 citation 부착."""
    if not sources:
        return f"⚠️ {claim} (source 미명시 — 검증 필요)"
    cite = "; ".join(sources[:3])
    return f"{claim} (출처: {cite})"


# 자연어 호출 wrapper
def hallucination_check_natural(text: str) -> dict:
    """자연어: 'X 답변 환각 검증해줘' → GuardResult dict."""
    r = guard_output(text, strict=True)
    return {
        "safe": r.safe,
        "n_jailbreak_flags": len(r.flagged_jailbreak),
        "n_unsourced_claims": len(r.fact_claims_without_source),
        "audit_log": r.audit_log,
        "recommendation": r.recommendation,
        "natural_summary": (
            f"검증 결과: {'안전' if r.safe else '위험'}. "
            f"{len(r.audit_log)} flag. "
            f"{r.recommendation}"
        ),
    }
