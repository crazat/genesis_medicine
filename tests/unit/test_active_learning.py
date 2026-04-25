"""Active Learning Deep Docking 단위 테스트."""

from __future__ import annotations

import numpy as np

from genesis_medicine.screening import (
    ActiveLearningConfig,
    ActiveLearningResult,
    ActiveLearningScreener,
    report_active_learning,
)


def _fake_docking_fn(smiles: list[str]) -> dict[str, float]:
    """SMILES 길이를 뒤집어서 score처럼 사용 (결정적 기준)."""
    return {s: -float(len(s)) for s in smiles}


def _fake_embedding_fn(smiles: list[str]) -> np.ndarray:
    """SMILES 길이 + 해시 기반 임베딩."""
    rng = np.random.default_rng(42)
    return np.stack([
        [len(s), abs(hash(s)) % 1000] + rng.standard_normal(8).tolist()
        for s in smiles
    ])


def test_active_learning_converges() -> None:
    library = [f"C{i}" * (i % 15 + 1) for i in range(500)]
    cfg = ActiveLearningConfig(
        initial_fraction=0.02, rounds=2, batch_fraction=0.02,
    )
    screener = ActiveLearningScreener(cfg, _fake_docking_fn, _fake_embedding_fn)
    result = screener.run(library, rng=np.random.default_rng(0))

    assert isinstance(result, ActiveLearningResult)
    # 초기 0.02 + 라운드마다 0.02 추가 (rounds=2) → 최소 6% 도킹
    assert result.n_docked >= int(len(library) * 0.05)
    assert result.n_docked < len(library)
    # history 길이 = 라운드 완료 수 + 1 (라운드 0 포함)
    assert len(result.history) >= 2
    # report DataFrame 생성 가능
    df = report_active_learning(result)
    assert "round" in df.columns
    assert len(df) == len(result.history)


def test_active_learning_empty_library() -> None:
    cfg = ActiveLearningConfig(rounds=1)
    screener = ActiveLearningScreener(cfg, _fake_docking_fn, _fake_embedding_fn)
    result = screener.run([])
    assert result.n_total == 0
    assert result.n_docked == 0
