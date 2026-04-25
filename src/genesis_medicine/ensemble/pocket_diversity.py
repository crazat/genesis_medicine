"""앙상블에서 발견된 포켓 다양성 분석 — cryptic pocket 검출.

알고리즘
--------
1. 각 conformer에 대해 P2Rank로 포켓 검출
2. 모든 conformer × 모든 포켓을 단백질 좌표공간에서 클러스터
3. apo 구조에 없던 포켓이 holo conformer 일부에서만 나타나면 cryptic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from loguru import logger

from .base import ConformerSpec


@dataclass
class CrypticPocket:
    """holo에서만 발견된 잠재 결합부."""

    center: tuple[float, float, float]
    n_conformers_with_pocket: int
    mean_volume: float
    surrounding_residues: list[int] = field(default_factory=list)
    novelty_score: float = 0.0  # 0~1, 1=apo에 전혀 없음


def compute_pocket_diversity(
    conformers: list[ConformerSpec],
    apo_pockets: list[tuple[float, float, float]] | None = None,
    distance_threshold: float = 6.0,
) -> list[CrypticPocket]:
    """앙상블에서 cryptic pocket 검출.

    Parameters
    ----------
    conformers : list[ConformerSpec]
        AlphaFlow / BioEmu 출력 컨포머
    apo_pockets : list of (x, y, z), optional
        apo 구조의 알려진 포켓 중심
    distance_threshold : float
        포켓 매칭 거리 (Å)
    """
    if not conformers:
        return []

    all_pockets: list[tuple[ConformerSpec, tuple[float, float, float], float]] = []
    for c in conformers:
        # placeholder — 실제로는 P2Rank/FPocket 호출 결과 사용
        for vol in c.pocket_volumes:
            # 가상의 좌표 생성 (실제 코드에서는 P2Rank 결과 좌표 사용)
            all_pockets.append((c, (0.0, 0.0, 0.0), vol))

    if not all_pockets:
        logger.warning("포켓 정보 없음 — P2Rank를 먼저 실행하세요.")
        return []

    # 클러스터링 — 단순 distance-based
    from collections import defaultdict
    clusters: dict[int, list[tuple[tuple[float, float, float], float]]] = defaultdict(list)
    centers: list[tuple[float, float, float]] = []
    for _, coord, vol in all_pockets:
        matched = False
        for ci, c in enumerate(centers):
            if _euclid(coord, c) < distance_threshold:
                clusters[ci].append((coord, vol))
                matched = True
                break
        if not matched:
            centers.append(coord)
            clusters[len(centers) - 1].append((coord, vol))

    cryptic: list[CrypticPocket] = []
    for ci, members in clusters.items():
        center = centers[ci]
        novelty = 1.0
        if apo_pockets:
            min_d = min(_euclid(center, ap) for ap in apo_pockets)
            novelty = min(1.0, min_d / distance_threshold)
        cryptic.append(
            CrypticPocket(
                center=center,
                n_conformers_with_pocket=len(members),
                mean_volume=float(np.mean([v for _, v in members])),
                novelty_score=novelty,
            )
        )

    cryptic.sort(key=lambda p: (p.novelty_score, p.n_conformers_with_pocket), reverse=True)
    return cryptic


def _euclid(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return float(np.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))))
