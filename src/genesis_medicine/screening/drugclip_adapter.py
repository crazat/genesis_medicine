"""DrugCLIP 프리필터 어댑터 (Science 2026).

https://drugclip.com

대조학습 기반 단백질-리간드 적합성 초고속 스크리닝.
도킹 대비 1000만배 빠름. 8 GPU로 5억 화합물/일 처리 가능.
대규모 라이브러리(COCONUT, ZINC)를 수천 개로 축소하는 프리필터 역할.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from loguru import logger

from .base import DockingPose, ScreeningRequest, ScreeningResult


class DrugCLIPAdapter:
    """DrugCLIP 대조학습 프리필터."""

    engine_name = "drugclip"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/drugclip"),
        model_path: Path | None = None,
        batch_size: int = 512,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = model_path
        self.batch_size = batch_size
        self.device = device
        self._model = None

    def supports_affinity(self) -> bool:
        return False

    def supports_pose(self) -> bool:
        return False

    def screen(self, req: ScreeningRequest) -> ScreeningResult:
        """SMILES 목록에서 단백질 포켓과의 적합성 점수로 필터링."""
        t0 = time.time()

        try:
            scores = self._score_batch(req)
        except ImportError:
            logger.error(
                "DrugCLIP 미설치. "
                "pip install drugclip 또는 소스 빌드 필요."
            )
            return ScreeningResult(
                engine=self.engine_name, poses=[], wall_seconds=time.time() - t0,
                metadata={"error": "drugclip not installed"},
            )

        # 점수 → DockingPose 변환 (score: 높을수록 좋음 → 부호 반전해서 저장)
        poses: list[DockingPose] = []
        for i, (smi, score) in enumerate(zip(req.ligand_smiles_list, scores)):
            name = req.ligand_names[i] if i < len(req.ligand_names) else None
            poses.append(
                DockingPose(
                    ligand_smiles=smi,
                    ligand_name=name,
                    protein_id=req.protein_id,
                    score=-score,  # 부호 반전: ECR에서 낮을수록 좋음 관례
                    confidence=float(score),
                    engine=self.engine_name,
                )
            )

        poses.sort(key=lambda p: p.score)

        # top_n 또는 top_fraction 적용
        if req.top_n:
            poses = poses[: req.top_n]
        elif req.top_fraction:
            n = max(1, int(len(poses) * req.top_fraction))
            poses = poses[:n]

        logger.info(
            "DrugCLIP: {} → {} 화합물 (top {})",
            len(req.ligand_smiles_list),
            len(poses),
            req.top_n or f"{(req.top_fraction or 1.0) * 100:.0f}%",
        )

        return ScreeningResult(
            engine=self.engine_name,
            poses=poses,
            wall_seconds=time.time() - t0,
        )

    def _score_batch(self, req: ScreeningRequest) -> list[float]:
        """DrugCLIP 모델로 배치 스코어링.

        DrugCLIP이 설치되지 않은 경우 CLI fallback 시도.
        """
        try:
            return self._score_python_api(req)
        except ImportError:
            return self._score_cli_fallback(req)

    def _score_python_api(self, req: ScreeningRequest) -> list[float]:
        """DrugCLIP Python API 직접 호출."""
        from drugclip import DrugCLIPModel  # type: ignore[import-untyped]

        if self._model is None:
            self._model = DrugCLIPModel.from_pretrained(
                str(self.model_path) if self.model_path else "drugclip-base"
            )
            self._model = self._model.to(self.device)

        all_scores: list[float] = []
        smiles_list = req.ligand_smiles_list
        protein_file = str(req.protein_structure)

        for batch_start in range(0, len(smiles_list), self.batch_size):
            batch = smiles_list[batch_start: batch_start + self.batch_size]
            scores = self._model.predict(
                protein_path=protein_file,
                smiles_list=batch,
            )
            all_scores.extend(float(s) for s in scores)

        return all_scores

    def _score_cli_fallback(self, req: ScreeningRequest) -> list[float]:
        """CLI 기반 fallback."""
        with TemporaryDirectory(prefix="drugclip_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            smi_file = tmp_dir / "ligands.smi"
            smi_file.write_text("\n".join(req.ligand_smiles_list))
            out_file = tmp_dir / "scores.npy"

            cmd = [
                "drugclip", "screen",
                "--protein", str(req.protein_structure),
                "--ligands", str(smi_file),
                "--output", str(out_file),
                "--device", self.device,
                "--batch_size", str(self.batch_size),
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            scores = np.load(out_file).tolist()

        return scores
