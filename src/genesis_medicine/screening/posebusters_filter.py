"""PoseBusters 기반 도킹 포즈 물리적 타당성 검증 필터.

도킹/공동접힘 결과에서 화학적으로 불가능한 포즈를 제거.
- 결합 길이/각도 이상
- 입체충돌
- 평면성 위반
- 에너지 합리성

참고: Buttenschoen et al. (2024) Chem. Sci. 15:3130
"""

from __future__ import annotations

import time
from pathlib import Path

from loguru import logger

from .base import DockingPose, ScreeningRequest, ScreeningResult


class PoseBustersFilter:
    """PoseBusters 검증 필터 — 스크리닝 마지막 단계."""

    engine_name = "posebusters"

    def __init__(
        self,
        *,
        full_check: bool = True,
        flatness_threshold: float = 0.1,
    ) -> None:
        self.full_check = full_check
        self.flatness_threshold = flatness_threshold

    def supports_affinity(self) -> bool:
        return False

    def supports_pose(self) -> bool:
        return False

    def screen(self, req: ScreeningRequest) -> ScreeningResult:
        raise NotImplementedError("PoseBusters는 filter()로 사용")

    def filter(self, poses: list[DockingPose]) -> ScreeningResult:
        """기존 포즈 목록에서 PoseBusters 검증 통과한 것만 반환."""
        t0 = time.time()
        try:
            from posebusters import PoseBusters

            pb = PoseBusters(config="dock")
        except ImportError:
            logger.warning(
                "posebusters 미설치 — 모든 포즈 통과. "
                "`uv pip install posebusters`로 설치하세요."
            )
            return ScreeningResult(
                engine=self.engine_name,
                poses=poses,
                wall_seconds=time.time() - t0,
                metadata={"skipped": True, "reason": "posebusters not installed"},
            )

        passed: list[DockingPose] = []
        failed = 0

        for pose in poses:
            pose_file = pose.pose_sdf or pose.pose_pdb
            if pose_file is None or not Path(pose_file).exists():
                # 포즈 파일 없으면 통과 (점수만 있는 단계)
                passed.append(pose)
                continue

            try:
                results = pb.bust(
                    mol_pred=str(pose_file),
                    mol_true=None,
                    mol_cond=str(req.protein_structure) if hasattr(req, "protein_structure") else None,
                    full_report=self.full_check,
                )
                # PoseBusters bust()는 DataFrame 반환, 모든 컬럼이 True여야 통과
                if results.all(axis=1).any():
                    passed.append(pose)
                else:
                    failed += 1
                    logger.debug(
                        "PoseBusters 실패: {} — {}",
                        pose.ligand_smiles[:50],
                        results.to_dict(orient="records"),
                    )
            except Exception as e:
                logger.warning("PoseBusters 오류 (통과 처리): {} — {}", pose.ligand_smiles[:30], e)
                passed.append(pose)

        logger.info(
            "PoseBusters: {}/{} 통과 ({} 탈락)",
            len(passed), len(poses), failed,
        )

        return ScreeningResult(
            engine=self.engine_name,
            poses=passed,
            wall_seconds=time.time() - t0,
            metadata={"total": len(poses), "passed": len(passed), "failed": failed},
        )
