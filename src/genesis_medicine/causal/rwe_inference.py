"""Causal inference + Real-World Evidence for EMB-3 efficacy.

Springer Nature 2025 (Causal ML drug development) 패턴:
  - Target Trial Emulation (observational → RCT-like)
  - Targeted Maximum Likelihood Estimation (TMLE)
  - Doubly robust inference
  - Adaptive Bayesian historical-control

Use case (Recover 한의원):
  - 자운고 시술 환자 (~100-200명/년) — historical control
  - EMB-3 강화 처방 환자 (~50명) — treatment group
  - Causal estimation of EMB-3 effect on scar improvement (PSCR/POSAS score)
  - → MFDS 30영업일 IND 자료 강화

라이브러리:
  - DoWhy (MIT, Microsoft) — causal inference framework
  - EconML (MIT, Microsoft) — heterogeneous treatment effect
  - causalpy (MIT) — Bayesian causal inference

라이선스: 모두 MIT — commercial OK.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Optional

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd


@dataclass
class CausalEstimateResult:
    """Causal effect estimate (ATE, ATT)."""

    treatment: str = ""           # e.g. "EMB-3 강화"
    control: str = ""             # e.g. "자운고 단독"
    outcome: str = ""             # e.g. "PSCR_improvement"
    n_treated: int = 0
    n_control: int = 0
    ate_estimate: float = 0.0     # Average Treatment Effect
    ate_std_error: float = 0.0
    ate_ci_low: float = 0.0
    ate_ci_high: float = 0.0
    p_value: float = 1.0
    method: str = ""              # "TMLE" | "PS_matching" | "AIPW" | "naive"
    confounders_adjusted: list = field(default_factory=list)
    interpretation: str = ""


def propensity_score_matching(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    confounders: list[str],
    caliper: float = 0.1,
) -> CausalEstimateResult:
    """Propensity score matching — 가장 표준 인과 추정.

    1. Logistic regression: P(treatment=1 | confounders)
    2. 1:1 matching within caliper
    3. Matched outcome difference = ATE
    """
    try:
        from sklearn.linear_model import LogisticRegression
        from scipy import stats
    except ImportError:
        return CausalEstimateResult(method="error: sklearn/scipy 미설치")

    # Step 1: Propensity score
    X = df[confounders].values
    T = df[treatment_col].astype(int).values
    Y = df[outcome_col].astype(float).values

    lr = LogisticRegression(max_iter=500)
    lr.fit(X, T)
    ps = lr.predict_proba(X)[:, 1]

    # Step 2: 1:1 matching
    treated_idx = np.where(T == 1)[0]
    control_idx = np.where(T == 0)[0]

    matched_pairs = []
    used_controls = set()
    for ti in treated_idx:
        ps_t = ps[ti]
        # find nearest control within caliper
        candidates = [(ci, abs(ps[ci] - ps_t)) for ci in control_idx
                       if ci not in used_controls and
                          abs(ps[ci] - ps_t) <= caliper]
        if not candidates:
            continue
        ci, dist = min(candidates, key=lambda x: x[1])
        matched_pairs.append((ti, ci))
        used_controls.add(ci)

    if not matched_pairs:
        return CausalEstimateResult(
            method="PS_matching",
            interpretation="❌ 매칭 0 pair — caliper 늘리거나 confounders 줄이기")

    # Step 3: ATE on matched pairs
    diffs = np.array([Y[t] - Y[c] for t, c in matched_pairs])
    ate = float(diffs.mean())
    std_err = float(diffs.std(ddof=1) / np.sqrt(len(diffs)))
    ci = stats.t.interval(0.95, len(diffs)-1, loc=ate, scale=std_err)
    t_stat, p_val = stats.ttest_1samp(diffs, 0)

    return CausalEstimateResult(
        treatment=f"{treatment_col}=1", control=f"{treatment_col}=0",
        outcome=outcome_col, n_treated=len(matched_pairs),
        n_control=len(matched_pairs),
        ate_estimate=ate, ate_std_error=std_err,
        ate_ci_low=float(ci[0]), ate_ci_high=float(ci[1]),
        p_value=float(p_val), method="PS_matching",
        confounders_adjusted=confounders,
        interpretation=(
            f"ATE = {ate:+.2f} (95% CI [{ci[0]:.2f}, {ci[1]:.2f}], p={p_val:.3f}, "
            f"matched {len(matched_pairs)} pairs). "
            f"{'✅ 통계 유의' if p_val < 0.05 else '⚠️ 통계 미유의'}"
        ),
    )


def doubly_robust_aipw(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    confounders: list[str],
) -> CausalEstimateResult:
    """AIPW (Augmented Inverse Probability Weighting) — doubly robust.

    Springer 2025 reviewed: TMLE/AIPW가 RWE causal inference SOTA.
    """
    try:
        from sklearn.linear_model import LogisticRegression, LinearRegression
    except ImportError:
        return CausalEstimateResult(method="error: sklearn 미설치")

    X = df[confounders].values
    T = df[treatment_col].astype(int).values
    Y = df[outcome_col].astype(float).values

    # Outcome model E[Y | X, T=t]
    lr_y0 = LinearRegression().fit(X[T == 0], Y[T == 0])
    lr_y1 = LinearRegression().fit(X[T == 1], Y[T == 1])
    mu0 = lr_y0.predict(X)
    mu1 = lr_y1.predict(X)

    # Propensity P(T=1 | X)
    ps_model = LogisticRegression(max_iter=500).fit(X, T)
    ps = np.clip(ps_model.predict_proba(X)[:, 1], 0.05, 0.95)

    # AIPW estimator
    aipw = (T * (Y - mu1) / ps + mu1) - ((1 - T) * (Y - mu0) / (1 - ps) + mu0)
    ate = float(aipw.mean())
    std_err = float(aipw.std(ddof=1) / np.sqrt(len(aipw)))

    return CausalEstimateResult(
        treatment=f"{treatment_col}=1", outcome=outcome_col,
        n_treated=int(T.sum()), n_control=int(len(T) - T.sum()),
        ate_estimate=ate, ate_std_error=std_err,
        ate_ci_low=ate - 1.96 * std_err,
        ate_ci_high=ate + 1.96 * std_err,
        method="AIPW_doubly_robust",
        confounders_adjusted=confounders,
        interpretation=(
            f"AIPW ATE = {ate:+.2f} ± {std_err:.2f} (Springer 2025 권장). "
            f"Outcome model + propensity model 둘 중 하나만 맞아도 일관 추정."
        ),
    )


# Recover 한의원 가상 데이터 생성 (실제 환자 데이터 사용 시 대체)
def simulate_recover_emb3_trial(n_patients: int = 200, true_ate: float = 1.5,
                                  seed: int = 42) -> pd.DataFrame:
    """Recover 한의원 EMB-3 강화 처방 가상 환자 데이터.

    Confounders:
      age, sex, scar_size_cm, scar_age_months, baseline_pscr
    Treatment: EMB-3 강화 = 1, 자운고 단독 = 0 (probability depends on confounders)
    Outcome: 6개월 후 PSCR (Patient Scar Assessment Scale, 0-5, 낮을수록 좋음)
    """
    rng = np.random.RandomState(seed)
    age = rng.normal(40, 12, n_patients).clip(20, 70)
    sex = rng.binomial(1, 0.55, n_patients)   # 1=female
    scar_size = rng.exponential(3, n_patients).clip(0.5, 20)
    scar_age = rng.exponential(12, n_patients).clip(1, 60)
    baseline = rng.normal(3.5, 0.7, n_patients).clip(1, 5)

    # 환자가 EMB-3 강화 받을 확률 (의사가 더 큰 흉터에 처방하는 경향 — confounding)
    logit = -0.5 + 0.05 * (age - 40) + 0.1 * scar_size + 0.02 * scar_age - 0.2 * sex
    ps = 1 / (1 + np.exp(-logit))
    treatment = rng.binomial(1, ps, n_patients)

    # outcome: baseline 개선 — true effect + noise + confounders
    improvement = (true_ate * treatment
                    + 0.02 * (60 - age)
                    + 0.1 * (5 - baseline)
                    - 0.05 * scar_size
                    + rng.normal(0, 0.5, n_patients))

    # 6개월 후 PSCR = baseline - improvement (낮을수록 좋음)
    pscr_6mo = (baseline - improvement).clip(0, 5)

    return pd.DataFrame({
        "patient_id": range(n_patients),
        "age": age, "sex": sex,
        "scar_size_cm": scar_size,
        "scar_age_months": scar_age,
        "baseline_pscr": baseline,
        "treatment_emb3": treatment,
        "pscr_6mo": pscr_6mo,
        "improvement": improvement,
    })


def run_emb3_causal_analysis() -> dict:
    """EMB-3 효과 인과 추정 demo (가상 데이터)."""
    df = simulate_recover_emb3_trial(n_patients=200, true_ate=1.5)
    confounders = ["age", "sex", "scar_size_cm", "scar_age_months",
                    "baseline_pscr"]

    # Naive comparison (편향)
    naive_t = df[df["treatment_emb3"] == 1]["improvement"].mean()
    naive_c = df[df["treatment_emb3"] == 0]["improvement"].mean()
    naive_ate = naive_t - naive_c

    # PS matching
    ps_result = propensity_score_matching(
        df, "treatment_emb3", "improvement", confounders)

    # AIPW
    aipw_result = doubly_robust_aipw(
        df, "treatment_emb3", "improvement", confounders)

    return {
        "n_patients": len(df),
        "n_treated": int(df["treatment_emb3"].sum()),
        "true_ate (생성 시 설정)": 1.5,
        "naive_ate (confounded)": round(naive_ate, 3),
        "ps_matching_ate": ps_result.ate_estimate,
        "ps_matching_ci": [ps_result.ate_ci_low, ps_result.ate_ci_high],
        "ps_matching_p": ps_result.p_value,
        "aipw_ate": aipw_result.ate_estimate,
        "aipw_ci": [aipw_result.ate_ci_low, aipw_result.ate_ci_high],
        "interpretation": (
            f"True ATE = 1.50 → naive {naive_ate:.2f} (편향), "
            f"PS matching {ps_result.ate_estimate:.2f} (보정), "
            f"AIPW {aipw_result.ate_estimate:.2f} (doubly robust)."
        ),
    }
