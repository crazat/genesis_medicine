"""FlowDock 어댑터 (MIT, ISMB 2025).

https://github.com/BioinfoMachineLearning/FlowDock

Geometric flow matching 기반 도킹 + affinity 동시 예측.
DiffDock-L 대비 3배 빠르고, DynamicBind보다 정확.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import DockingPose, ScreeningRequest, ScreeningResult


class FlowDockAdapter:
    """FlowDock CLI 래퍼."""

    engine_name = "flowdock"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/flowdock"),
        samples_per_ligand: int = 10,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.samples_per_ligand = samples_per_ligand
        self.device = device

    def supports_affinity(self) -> bool:
        return True

    def supports_pose(self) -> bool:
        return True

    def screen(self, req: ScreeningRequest) -> ScreeningResult:
        t0 = time.time()
        poses: list[DockingPose] = []

        with TemporaryDirectory(prefix="flowdock_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)

            # 입력 CSV: protein_path, ligand_smiles
            input_csv = tmp_dir / "inputs.csv"
            lines = ["protein_path,ligand_smiles,ligand_name"]
            for i, smi in enumerate(req.ligand_smiles_list):
                name = req.ligand_names[i] if i < len(req.ligand_names) else f"lig_{i}"
                lines.append(f"{req.protein_structure},{smi},{name}")
            input_csv.write_text("\n".join(lines))

            out_dir = tmp_dir / "output"
            out_dir.mkdir()

            cmd = [
                "python", "-m", "flowdock.predict",
                "--input_csv", str(input_csv),
                "--output_dir", str(out_dir),
                "--samples_per_complex", str(self.samples_per_ligand),
                "--device", self.device,
                "--seed", str(req.seed),
            ]

            logger.info("FlowDock 실행: {} 화합물", len(req.ligand_smiles_list))

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
            except FileNotFoundError:
                logger.error(
                    "FlowDock 미설치. "
                    "https://github.com/BioinfoMachineLearning/FlowDock 참고"
                )
                return ScreeningResult(
                    engine=self.engine_name,
                    poses=[],
                    wall_seconds=time.time() - t0,
                    metadata={"error": "flowdock not installed"},
                )
            except subprocess.TimeoutExpired:
                logger.error("FlowDock 타임아웃 (3600s)")
                return ScreeningResult(
                    engine=self.engine_name, poses=[], wall_seconds=time.time() - t0,
                )

            poses = self._parse_output(out_dir, req)

        # top_n 필터
        poses.sort(key=lambda p: p.score)
        if req.top_n:
            poses = poses[: req.top_n]

        return ScreeningResult(
            engine=self.engine_name,
            poses=poses,
            wall_seconds=time.time() - t0,
        )

    def _parse_output(
        self, out_dir: Path, req: ScreeningRequest
    ) -> list[DockingPose]:
        """FlowDock 출력 SDF + score 파싱."""
        poses: list[DockingPose] = []
        for sdf in sorted(out_dir.rglob("*.sdf")):
            # FlowDock은 각 리간드별 디렉터리에 rank_*.sdf 출력
            score_json = sdf.parent / "scores.json"
            score = 0.0
            confidence = 0.0
            affinity = None
            if score_json.exists():
                data = json.loads(score_json.read_text())
                score = float(data.get("binding_energy", data.get("score", 0.0)))
                confidence = float(data.get("confidence", 0.0))
                affinity = data.get("affinity_pkd")

            # 리간드 이름에서 SMILES 역추적
            lig_name = sdf.parent.name
            smi = ""
            for i, name in enumerate(req.ligand_names or []):
                if name == lig_name:
                    smi = req.ligand_smiles_list[i]
                    break
            if not smi and req.ligand_smiles_list:
                try:
                    idx = int(lig_name.split("_")[-1])
                    smi = req.ligand_smiles_list[idx]
                except (ValueError, IndexError):
                    smi = lig_name

            poses.append(
                DockingPose(
                    ligand_smiles=smi,
                    ligand_name=lig_name,
                    protein_id=req.protein_id,
                    pose_sdf=sdf,
                    score=score,
                    confidence=confidence,
                    affinity_pkd=affinity,
                    engine=self.engine_name,
                )
            )
        return poses
