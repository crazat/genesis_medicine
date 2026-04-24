"""Exponential Consensus Ranking (ECR) — 다단계 스크리닝 합의 스코어링.

여러 직교적 스크리닝 엔진의 순위를 결합하여 최종 순위를 산출.
Score 기반 평균 대신 rank 기반 결합을 사용하여 스케일 불일치 문제를 회피.

참고: Palacio-Rodriguez et al. (2019) Sci. Rep. 9:5142
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class RankedCompound:
    """합의 스코어링 결과."""

    smiles: str
    name: str | None = None
    ecr_score: float = 0.0
    ranks: dict[str, int] = field(default_factory=dict)
    scores: dict[str, float] = field(default_factory=dict)


def exponential_consensus_ranking(
    stage_results: dict[str, dict[str, float]],
    *,
    sigma: float = 0.05,
) -> list[RankedCompound]:
    """ECR로 여러 스크리닝 단계의 결과를 결합.

    Parameters
    ----------
    stage_results : dict[str, dict[str, float]]
        {stage_name: {smiles: score}} — 점수는 낮을수록 좋음 (binding energy 관례).
    sigma : float
        지수 감쇠 계수. 작을수록 상위 순위에 가중.

    Returns
    -------
    list[RankedCompound]
        ECR 점수 내림차순 정렬 (높을수록 합의 우수).
    """
    all_smiles: set[str] = set()
    for scores in stage_results.values():
        all_smiles.update(scores.keys())

    stage_names = list(stage_results.keys())
    n_stages = len(stage_names)
    if n_stages == 0:
        return []

    # 각 단계별 순위 계산
    stage_ranks: dict[str, dict[str, int]] = {}
    for stage_name in stage_names:
        scores = stage_results[stage_name]
        sorted_smiles = sorted(scores.keys(), key=lambda s: scores[s])
        stage_ranks[stage_name] = {s: rank for rank, s in enumerate(sorted_smiles)}

    # ECR 점수 계산
    compounds: list[RankedCompound] = []
    for smi in all_smiles:
        ranks_dict: dict[str, int] = {}
        scores_dict: dict[str, float] = {}
        ecr = 0.0
        n_present = 0

        for stage_name in stage_names:
            if smi in stage_results[stage_name]:
                n_total = len(stage_results[stage_name])
                rank = stage_ranks[stage_name][smi]
                normalized_rank = rank / max(n_total, 1)
                ecr += math.exp(-normalized_rank / sigma)
                ranks_dict[stage_name] = rank
                scores_dict[stage_name] = stage_results[stage_name][smi]
                n_present += 1

        # 참여 단계 수 보정 — 모든 단계에 존재하는 화합물 우대
        if n_present > 0:
            ecr *= n_present / n_stages

        compounds.append(
            RankedCompound(
                smiles=smi,
                ecr_score=ecr,
                ranks=ranks_dict,
                scores=scores_dict,
            )
        )

    compounds.sort(key=lambda c: c.ecr_score, reverse=True)
    return compounds
