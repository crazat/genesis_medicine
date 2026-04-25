"""PoseBench v2 검증 모듈 (S5 — ultrathink 2026-04-25).

https://github.com/BioinfoMachineLearning/PoseBench (MIT)
참고: Nat Mach Intell 2025 — apo-to-holo 308 복합체 벤치마크.

목적
----
6단계 캐스케이드 (DrugCLIP→Uni-Mol2→FlowDock→Boltz-2→GNINA→PoseBusters)의
신뢰도를 정량 측정. 메트릭:
- RMSD ≤ 2 Å 성공률
- PB-Valid (PoseBusters 22 체크 모두 통과)
- combined success: RMSD ≤ 2 Å AND PB-Valid

실행 흐름
---------
1. PoseBench 데이터셋 로드 (308 PDB 복합체)
2. 각 엔진별 도킹 실행 → 포즈 출력
3. RMSD vs ground truth + PoseBusters 검증
4. 합의 점수 (ECR) 정확도 비교 리포트
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from loguru import logger

from .base import DockingPose, ScreeningRequest, Screener


@dataclass
class PoseBenchMetrics:
    n_total: int
    n_rmsd_success: int  # RMSD ≤ 2 Å
    n_pb_valid: int      # PoseBusters 통과
    n_combined: int      # 둘 다
    rmsd_mean: float
    rmsd_median: float
    per_target: dict[str, dict] = field(default_factory=dict)

    @property
    def rmsd_success_rate(self) -> float:
        return self.n_rmsd_success / max(self.n_total, 1)

    @property
    def pb_valid_rate(self) -> float:
        return self.n_pb_valid / max(self.n_total, 1)

    @property
    def combined_success_rate(self) -> float:
        return self.n_combined / max(self.n_total, 1)


class PoseBenchValidator:
    """PoseBench v2로 스크리너 검증."""

    def __init__(
        self,
        *,
        dataset_dir: Path,
        rmsd_threshold: float = 2.0,
        cache_dir: Path = Path(".cache/posebench"),
    ) -> None:
        self.dataset_dir = dataset_dir
        self.rmsd_threshold = rmsd_threshold
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_targets(self, subset: str = "primary") -> list[dict]:
        """PoseBench v2 308 복합체 메타데이터 로드.

        subset: primary | multi_ligand | dockgen_e
        """
        manifest = self.dataset_dir / f"{subset}_manifest.json"
        if not manifest.exists():
            logger.warning(
                "PoseBench manifest 미발견: {}. "
                "scripts/setup/download_posebench.sh 필요.",
                manifest,
            )
            return []
        return json.loads(manifest.read_text())

    def evaluate(
        self,
        screener: Screener,
        *,
        subset: str = "primary",
        max_targets: int | None = None,
    ) -> PoseBenchMetrics:
        targets = self.load_targets(subset)
        if max_targets:
            targets = targets[:max_targets]

        per_target: dict[str, dict] = {}
        rmsds: list[float] = []
        n_rmsd_success = 0
        n_pb_valid = 0
        n_combined = 0

        for tgt in targets:
            t0 = time.time()
            try:
                rmsd, pb_valid = self._evaluate_one(screener, tgt)
            except Exception as e:
                logger.warning("[{}] 실패: {}", tgt.get("id"), e)
                continue
            rmsds.append(rmsd)
            ok_rmsd = rmsd <= self.rmsd_threshold
            n_rmsd_success += int(ok_rmsd)
            n_pb_valid += int(pb_valid)
            n_combined += int(ok_rmsd and pb_valid)
            per_target[tgt["id"]] = {
                "rmsd": rmsd,
                "pb_valid": pb_valid,
                "wall_seconds": time.time() - t0,
            }

        if not rmsds:
            logger.error("PoseBench 평가 결과 0개. 데이터셋 확인 필요.")
            return PoseBenchMetrics(0, 0, 0, 0, 0.0, 0.0)

        return PoseBenchMetrics(
            n_total=len(rmsds),
            n_rmsd_success=n_rmsd_success,
            n_pb_valid=n_pb_valid,
            n_combined=n_combined,
            rmsd_mean=float(np.mean(rmsds)),
            rmsd_median=float(np.median(rmsds)),
            per_target=per_target,
        )

    def _evaluate_one(self, screener: Screener, tgt: dict) -> tuple[float, bool]:
        req = ScreeningRequest(
            protein_id=tgt["id"],
            protein_structure=Path(tgt["apo_pdb"]),
            ligand_smiles_list=[tgt["smiles"]],
            ligand_names=[tgt.get("ligand_name", "lig")],
            top_n=1,
            seed=42,
        )
        result = screener.screen(req)
        if not result.poses:
            return float("inf"), False
        pose = result.poses[0]
        rmsd = self._compute_rmsd(pose, tgt)
        pb_valid = self._run_posebusters(pose, tgt)
        return rmsd, pb_valid

    def _compute_rmsd(self, pose: DockingPose, tgt: dict) -> float:
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem

            ref = Chem.MolFromMolFile(tgt["holo_sdf"], removeHs=False)
            if pose.pose_sdf is None:
                return float("inf")
            pred = Chem.MolFromMolFile(str(pose.pose_sdf), removeHs=False)
            if ref is None or pred is None:
                return float("inf")
            return float(AllChem.GetBestRMS(pred, ref))
        except Exception as e:
            logger.debug("RMSD 계산 실패: {}", e)
            return float("inf")

    def _run_posebusters(self, pose: DockingPose, tgt: dict) -> bool:
        try:
            from posebusters import PoseBusters

            pb = PoseBusters(config="dock")
            df = pb.bust(
                mol_pred=pose.pose_sdf,
                mol_true=tgt.get("holo_sdf"),
                mol_cond=tgt["apo_pdb"],
                full_report=False,
            )
            return bool(df.iloc[0].all())
        except ImportError:
            logger.warning("posebusters 미설치 — pip install posebusters")
            return False
        except Exception as e:
            logger.debug("PoseBusters 실패: {}", e)
            return False


def report_metrics(metrics: PoseBenchMetrics, engine: str = "") -> pd.DataFrame:
    """단일 엔진 PoseBench 결과 요약 DataFrame."""
    return pd.DataFrame([{
        "engine": engine,
        "n_total": metrics.n_total,
        "rmsd_success_rate": metrics.rmsd_success_rate,
        "pb_valid_rate": metrics.pb_valid_rate,
        "combined_success_rate": metrics.combined_success_rate,
        "rmsd_mean": metrics.rmsd_mean,
        "rmsd_median": metrics.rmsd_median,
    }])


def compare_engines(
    metrics_by_engine: dict[str, PoseBenchMetrics],
) -> pd.DataFrame:
    """여러 엔진 PoseBench 결과 비교."""
    rows = [
        {
            "engine": eng,
            "rmsd_success_rate": m.rmsd_success_rate,
            "pb_valid_rate": m.pb_valid_rate,
            "combined": m.combined_success_rate,
            "n": m.n_total,
        }
        for eng, m in metrics_by_engine.items()
    ]
    return pd.DataFrame(rows).sort_values("combined", ascending=False)
