"""학술 통계 분석 — Mann-Whitney, FDR, ROC AUC, hit-rate.

scipy를 우선 시도, 없으면 numpy fallback.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class StatisticalResult:
    test_name: str
    statistic: float
    p_value: float
    n1: int
    n2: int = 0
    notes: str = ""


def mann_whitney_test(
    actives: np.ndarray | list[float],
    baseline: np.ndarray | list[float],
    *,
    alternative: str = "greater",
) -> StatisticalResult:
    """양측 Mann-Whitney U test (default: actives > baseline 가정).

    scipy 미설치 환경에서도 작동 (numpy로 직접 계산).
    """
    a = np.asarray(actives, dtype=float)
    b = np.asarray(baseline, dtype=float)
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return StatisticalResult("MannWhitneyU", float("nan"), float("nan"),
                                 n1, n2, notes="empty group")
    try:
        from scipy.stats import mannwhitneyu
        u, p = mannwhitneyu(a, b, alternative=alternative)
        return StatisticalResult("MannWhitneyU", float(u), float(p), n1, n2,
                                 notes=f"alternative={alternative}")
    except ImportError:
        # 비모수 — 간단히 rank 합
        all_vals = np.concatenate([a, b])
        order = np.argsort(all_vals)
        ranks = np.empty(len(all_vals), dtype=float)
        ranks[order] = np.arange(1, len(all_vals) + 1)
        r1 = ranks[: n1].sum()
        u1 = r1 - n1 * (n1 + 1) / 2
        return StatisticalResult("MannWhitneyU(approx)", float(u1), float("nan"),
                                 n1, n2, notes="scipy unavailable, p-value omitted")


def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> dict:
    """BH FDR 보정.

    Returns: {"q_values": [...], "rejected": [bool], "n_significant": int}
    """
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked_p = p[order]
    q = ranked_p * n / (np.arange(n) + 1)
    # 단조 보정
    q = np.minimum.accumulate(q[::-1])[::-1]
    q_full = np.empty(n)
    q_full[order] = q
    rejected = q_full < alpha
    return {
        "q_values": q_full.tolist(),
        "rejected": rejected.tolist(),
        "n_significant": int(rejected.sum()),
        "alpha": alpha,
    }


def roc_auc_with_baseline(
    actives_scores: list[float],
    baseline_scores: list[float],
) -> dict:
    """단순 ROC + AUC 계산. sklearn 미설치 환경에서도 작동."""
    a = np.asarray(actives_scores, dtype=float)
    b = np.asarray(baseline_scores, dtype=float)
    if len(a) == 0 or len(b) == 0:
        return {"auc": float("nan"), "n_actives": len(a), "n_baseline": len(b)}

    scores = np.concatenate([a, b])
    labels = np.concatenate([np.ones(len(a)), np.zeros(len(b))])
    order = np.argsort(-scores)
    labels = labels[order]
    n_pos, n_neg = labels.sum(), (1 - labels).sum()
    if n_pos == 0 or n_neg == 0:
        return {"auc": float("nan"), "n_actives": int(n_pos), "n_baseline": int(n_neg)}

    cum_pos, cum_neg = 0, 0
    tpr, fpr = [0.0], [0.0]
    for lab in labels:
        if lab == 1:
            cum_pos += 1
        else:
            cum_neg += 1
        tpr.append(cum_pos / n_pos)
        fpr.append(cum_neg / n_neg)
    auc = float(np.trapz(tpr, fpr))

    # Effect size (Cohen's d) — group difference
    pooled_sd = np.sqrt(((len(a) - 1) * a.var(ddof=1) +
                         (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / pooled_sd if pooled_sd > 0 else float("nan")
    return {
        "auc": auc,
        "n_actives": len(a),
        "n_baseline": len(b),
        "actives_mean": float(a.mean()),
        "baseline_mean": float(b.mean()),
        "cohens_d": float(d),
    }


def hit_rate(
    scores: list[float],
    threshold: float = 0.6,
) -> dict:
    """단순 hit-rate."""
    arr = np.asarray(scores, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return {"n": 0, "hits": 0, "rate": float("nan"), "threshold": threshold}
    hits = int((arr >= threshold).sum())
    return {
        "n": int(len(arr)),
        "hits": hits,
        "rate": hits / len(arr),
        "threshold": threshold,
    }


def summarize_per_target(
    full_df: pd.DataFrame,
    *,
    score_col: str = "affinity_probability_binary",
    group_col: str = "target",
    hit_threshold: float = 0.6,
) -> pd.DataFrame:
    """타겟별 요약 통계 — 학술 Table용."""
    rows = []
    for grp, sub in full_df.groupby(group_col):
        vals = sub[score_col].dropna().values
        if len(vals) == 0:
            continue
        rows.append({
            group_col: grp,
            "n": len(vals),
            "mean": float(vals.mean()),
            "median": float(np.median(vals)),
            "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            "min": float(vals.min()),
            "max": float(vals.max()),
            "hit_rate@%.1f" % hit_threshold: float((vals >= hit_threshold).mean()),
        })
    return pd.DataFrame(rows)
