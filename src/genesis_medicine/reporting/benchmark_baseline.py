"""Random / decoy baseline 비교용 도구.

학술 paper에서는 거의 항상 다음을 요구함:
1. 후보 화합물의 score가 random sampling 보다 유의하게 높은가?
2. ROC AUC vs decoy

이 모듈은:
- 동일 라이브러리에서 N개 random subset 추출
- DUD-E decoy 생성기 위치 (옵션)
- summary stats 비교
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class BaselineComparison:
    n_actives: int
    n_baseline: int
    actives_scores: list[float] = field(default_factory=list)
    baseline_scores: list[float] = field(default_factory=list)
    seed: int = 42


def random_baseline_from_library(
    library_csv: Path,
    *,
    score_col: str = "affinity_probability_binary",
    n_samples: int = 50,
    seed: int = 42,
) -> list[float]:
    """이미 스코어된 화합물 풀에서 random subset.

    이상적으로는 별도 random docking을 돌려야 하지만, in silico 단계에서는
    동일 분포에서 random sample 비교만으로도 충분한 효과 (음성 분포 추정).
    """
    if not library_csv.exists():
        return []
    df = pd.read_csv(library_csv)
    if score_col not in df.columns:
        return []
    valid = df[score_col].dropna().values
    if len(valid) == 0:
        return []
    rng = np.random.default_rng(seed)
    n = min(n_samples, len(valid))
    return rng.choice(valid, size=n, replace=False).tolist()


def synthetic_negative_distribution(
    n: int = 100,
    *,
    mean: float = 0.15,
    sd: float = 0.10,
    seed: int = 42,
) -> list[float]:
    """합성 negative 분포 (학습 단계에서 신속 baseline 시각화용).

    실 paper에서는 실제 random docking 결과로 대체 권장.
    """
    rng = np.random.default_rng(seed)
    arr = rng.normal(mean, sd, size=n)
    return np.clip(arr, 0.0, 1.0).tolist()


def compare_to_baseline(
    actives_scores: list[float],
    baseline_scores: list[float],
) -> dict:
    """두 분포 비교 — paper Result 섹션용 요약."""
    from .statistics_runner import mann_whitney_test, roc_auc_with_baseline

    mw = mann_whitney_test(actives_scores, baseline_scores, alternative="greater")
    roc = roc_auc_with_baseline(actives_scores, baseline_scores)
    return {
        "mann_whitney_u": mw.statistic,
        "mann_whitney_p": mw.p_value,
        "roc_auc": roc.get("auc"),
        "cohens_d": roc.get("cohens_d"),
        "n_actives": len(actives_scores),
        "n_baseline": len(baseline_scores),
        "actives_mean": float(np.mean(actives_scores)) if actives_scores else float("nan"),
        "baseline_mean": float(np.mean(baseline_scores)) if baseline_scores else float("nan"),
    }
