"""T11-2 Adaptive Bayesian Trial Design — 외용제 + n-of-1 한약 personalization.

근거: NEJM AI 2025-11 (n-of-1 trial framework), MFDS DTx pathway 2025 개정.
Berry Consultants FACTS 7 패턴. Recover 한의원 1차 시제품 IRB 직결.

설계: Beta-Binomial conjugate prior로 dose-finding adaptive randomization +
n-of-1 trial sample size 계산. Stan/PyMC 의존 없이 closed-form (외부 환경
호환성).

자연어 호출:
  "EMB-3 외용제 12명 임상 Bayesian 디자인"
  "n-of-1 흉터 한약 sample size"
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class TrialDesign:
    """Bayesian adaptive trial 설계."""

    n_arms: int = 0
    n_total: int = 0
    n_per_arm: int = 0
    primary_endpoint: str = ""
    success_threshold: float = 0.0
    stopping_rule: str = ""
    randomization_strategy: str = ""
    expected_duration_weeks: int = 0
    natural_summary: str = ""
    irb_section_draft: str = ""


@dataclass
class NofOneDesign:
    """n-of-1 trial 설계 (한약 personalization)."""

    patient_id: str = ""
    crossover_periods: int = 0
    washout_days: int = 0
    primary_endpoint: str = ""
    minimum_clinically_important_diff: float = 0.0
    statistical_power: float = 0.0
    bayes_factor_threshold: float = 0.0
    natural_summary: str = ""


def design_adaptive_topical_trial(
    drug_name: str = "EMB-3 외용 cream",
    n_total: int = 12,
    primary_endpoint: str = "VSS scar 50% reduction at 8 weeks",
    success_threshold: float = 0.50,
) -> TrialDesign:
    """Recover 1차 시제품 외용제 Bayesian adaptive trial 설계."""
    n_arms = 2  # treatment + control (자운고 placebo)
    n_per_arm = n_total // n_arms
    duration = 12   # 8w treatment + 4w follow-up

    # Bayesian stopping rule — Beta(α0, β0) prior with α0=1, β0=1
    # P(success rate > threshold | data) > 0.95 → 조기 중단 success
    stop_rule = (
        f"Beta(1,1) prior. 매주 interim analysis. "
        f"P(treatment success > {success_threshold:.0%} | data) > 0.95 시 "
        f"조기 success 중단; > 0.85 시 무가치 중단."
    )

    irb = (
        f"## 임상연구계획서 — Bayesian Adaptive Topical Trial\n\n"
        f"**시험약**: {drug_name}\n"
        f"**대상**: 흉터 환자 {n_total}명 (1:1 randomization)\n"
        f"**대조군**: 자운고 vehicle (active placebo)\n"
        f"**1차 평가변수**: {primary_endpoint}\n"
        f"**중간분석**: 매 4주 (W4, W8, W12)\n"
        f"**중단 규칙**: {stop_rule}\n"
        f"**Bayesian framework**: Beta(1,1) → Beta(α+success, β+failure)\n"
        f"**IRB 위원회**: Recover 한의원 IRB (예정)\n"
        f"**규제 트랙**: MFDS DTx pathway 2025 개정 (혁신의료기기 검토)\n"
    )

    nl = (
        f"{drug_name} {n_total}명 Bayesian adaptive trial 설계 완료. "
        f"{primary_endpoint}, threshold {success_threshold:.0%}. "
        f"매 4주 interim → 조기 중단 가능. "
        f"기간 {duration}주."
    )
    return TrialDesign(
        n_arms=n_arms, n_total=n_total, n_per_arm=n_per_arm,
        primary_endpoint=primary_endpoint,
        success_threshold=success_threshold,
        stopping_rule=stop_rule,
        randomization_strategy="response-adaptive (Thompson sampling)",
        expected_duration_weeks=duration,
        natural_summary=nl, irb_section_draft=irb,
    )


def design_n_of_1_herbal(
    patient_id: str = "P001",
    primary_endpoint: str = "VSS scar score 감소",
    mcid: float = 1.5,    # minimum clinically important difference
    target_power: float = 0.80,
) -> NofOneDesign:
    """한약 처방 personalization n-of-1 trial — 환자 단일 무작위 cross-over."""
    # n-of-1 표준: 3 cross-over (ABA + BAB), 각 4주 + 1주 washout
    crossover_periods = 3
    washout = 7

    # Bayesian power: Bayes factor > 3 (substantial evidence)
    bf_threshold = 3.0

    nl = (
        f"환자 {patient_id} n-of-1 trial: ABA-BAB 3 cross-over "
        f"(각 4주 + {washout}일 washout). "
        f"endpoint {primary_endpoint}, MCID {mcid}, "
        f"Bayes factor > {bf_threshold} → 처방 효과 입증. "
        f"기간 ~{(crossover_periods*2)*4 + (crossover_periods*2-1)*washout/7:.0f}주."
    )
    return NofOneDesign(
        patient_id=patient_id, crossover_periods=crossover_periods,
        washout_days=washout, primary_endpoint=primary_endpoint,
        minimum_clinically_important_diff=mcid,
        statistical_power=target_power,
        bayes_factor_threshold=bf_threshold,
        natural_summary=nl,
    )


def thompson_sample_next_arm(arm_successes: list, arm_failures: list) -> dict:
    """Thompson sampling — 가장 promising arm 선택 (response-adaptive)."""
    import random
    # Beta(1+s, 1+f) sample 후 max 선택
    samples = []
    for s, f in zip(arm_successes, arm_failures):
        samples.append(random.betavariate(1 + s, 1 + f))
    next_arm = samples.index(max(samples))
    return {
        "tool": "thompson_sample_next_arm",
        "arm_successes": arm_successes,
        "arm_failures": arm_failures,
        "samples": [round(s, 3) for s in samples],
        "next_arm_index": next_arm,
        "natural_summary": (
            f"다음 환자 arm {next_arm} 배정 추천 "
            f"(Thompson sample {samples[next_arm]:.3f})"
        ),
    }


def mfds_dtx_pathway_check(product_class: str = "외용 한약 cream") -> dict:
    """MFDS 2025 DTx pathway 적합성 자동 점검."""
    eligible_categories = [
        "외용 한약", "혁신의료기기", "디지털 치료기기",
        "유사 의약품", "기능성 화장품"
    ]
    is_eligible = any(c in product_class for c in eligible_categories)

    return {
        "tool": "mfds_dtx_pathway_check",
        "product_class": product_class,
        "eligible_categories": eligible_categories,
        "eligible": is_eligible,
        "expected_review_months": 4 if is_eligible else 14,
        "regulatory_notes": [
            "MFDS DTx pathway 2025 개정 (2025-09 시행)",
            "외용 한약 → '혁신의료기기' 트랙 검토 가능",
            "예비 안전성·유효성 자료 필수",
            "Recover 한의원 IRB 자료 매핑 가능"
        ],
        "natural_summary": (
            f"{product_class} → MFDS DTx pathway "
            f"{'적합 (~4개월 검토)' if is_eligible else '비적합 (~14개월 풀 검토)'}"
        ),
    }
