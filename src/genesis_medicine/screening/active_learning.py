"""Active Learning Deep Docking (B4 — ultrathink 2026-04-25).

근거: Cherkasov lab Deep Docking + 2026 PyRMD2Dock + arxiv 2406.12919.

목적
----
1.4B+ 화합물 라이브러리에서 0.1~0.5%만 도킹하고 99% 회수.
8000 CPU·28일 → 8 GPU·1일로 단축.

알고리즘
--------
1. 초기 시드: 라이브러리 1% 무작위 샘플 → DrugCLIP/Boltz-2로 점수
2. 학습: Chemprop 2.0 회귀 모델 (분자 임베딩 → docking score)
3. 예측: 잔여 99% 화합물 점수 예측
4. 다음 라운드: 예측 상위 + uncertainty 큰 것 추가 도킹
5. 수렴까지 반복 (보통 3~5라운드)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from loguru import logger


@dataclass
class ActiveLearningConfig:
    initial_fraction: float = 0.01
    rounds: int = 4
    batch_fraction: float = 0.01     # 라운드당 추가 도킹 비율
    exploration_weight: float = 0.3  # 0=greedy, 1=완전 무작위
    target_score_threshold: float | None = None
    cache_dir: Path = Path(".cache/active_learning")


@dataclass
class ActiveLearningResult:
    rounds_executed: int
    n_docked: int
    n_total: int
    final_top_smiles: list[str]
    history: list[dict] = field(default_factory=list)
    wall_seconds: float = 0.0


class ActiveLearningScreener:
    """Active learning loop for ultra-large library docking."""

    def __init__(
        self,
        config: ActiveLearningConfig,
        docking_fn: Callable[[list[str]], dict[str, float]],
        embedding_fn: Callable[[list[str]], np.ndarray],
        surrogate_class: type | None = None,
    ) -> None:
        self.config = config
        self.docking_fn = docking_fn
        self.embedding_fn = embedding_fn
        self.surrogate_class = surrogate_class or _DefaultSurrogate
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

    def run(self, library_smiles: list[str], rng: np.random.Generator | None = None) -> ActiveLearningResult:
        t0 = time.time()
        rng = rng or np.random.default_rng(42)
        n_total = len(library_smiles)
        if n_total == 0:
            return ActiveLearningResult(0, 0, 0, [], [], 0.0)

        # 라운드 0 — 무작위 시드
        seed_n = max(100, int(n_total * self.config.initial_fraction))
        seed_idx = rng.choice(n_total, size=seed_n, replace=False)
        seed_smiles = [library_smiles[i] for i in seed_idx]
        scored: dict[str, float] = self.docking_fn(seed_smiles)
        history = [{
            "round": 0,
            "n_docked": len(scored),
            "min_score": min(scored.values()),
            "median_score": float(np.median(list(scored.values()))),
        }]

        for r in range(1, self.config.rounds + 1):
            # 학습
            X = self.embedding_fn(list(scored.keys()))
            y = np.array(list(scored.values()))
            model = self.surrogate_class().fit(X, y)

            # 예측 — 도킹 안 한 화합물
            remaining = [s for s in library_smiles if s not in scored]
            if not remaining:
                break
            X_rem = self.embedding_fn(remaining)
            mu, sigma = model.predict(X_rem)

            # 획득 함수: -mu + exploration_weight * sigma (낮을수록 좋음 = 더 음의 binding energy)
            acq = -mu + self.config.exploration_weight * sigma

            batch_n = max(50, int(n_total * self.config.batch_fraction))
            top_idx = np.argsort(-acq)[:batch_n]
            picked = [remaining[i] for i in top_idx]
            new_scores = self.docking_fn(picked)
            scored.update(new_scores)

            history.append({
                "round": r,
                "n_docked": len(scored),
                "min_score": min(scored.values()),
                "median_score": float(np.median(list(scored.values()))),
                "acquisition_top_n": batch_n,
            })

            # 조기 종료 — target_score_threshold 도달
            if self.config.target_score_threshold is not None:
                if min(scored.values()) <= self.config.target_score_threshold:
                    logger.info("목표 임계 도달 — 라운드 {} 조기 종료", r)
                    break

        sorted_smiles = sorted(scored.keys(), key=lambda s: scored[s])
        return ActiveLearningResult(
            rounds_executed=len(history) - 1,
            n_docked=len(scored),
            n_total=n_total,
            final_top_smiles=sorted_smiles[:1000],
            history=history,
            wall_seconds=time.time() - t0,
        )


class _DefaultSurrogate:
    """RandomForest fallback — Chemprop 2.0 미설치 환경용."""

    def __init__(self) -> None:
        self.model = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        try:
            from sklearn.ensemble import RandomForestRegressor
            self.model = RandomForestRegressor(
                n_estimators=200, max_depth=20, n_jobs=-1, random_state=0
            )
            self.model.fit(X, y)
        except ImportError:
            logger.error("scikit-learn 미설치 — surrogate 학습 불가")
        return self

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if self.model is None:
            return np.zeros(len(X)), np.ones(len(X))
        # RF — 트리별 예측의 std로 uncertainty 추정
        preds = np.array([t.predict(X) for t in self.model.estimators_])
        return preds.mean(axis=0), preds.std(axis=0)


def report_active_learning(result: ActiveLearningResult) -> pd.DataFrame:
    return pd.DataFrame(result.history)
