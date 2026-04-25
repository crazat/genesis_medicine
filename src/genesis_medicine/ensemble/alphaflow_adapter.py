"""AlphaFlow — apo→holo flow matching (MIT).

https://github.com/bjing2016/alphaflow
참고: Jing et al. ICML 2024.

목적
----
정적 구조에서 보이지 않는 cryptic pocket 탐색. BACE1처럼 알려진 활성 부위 외에도
알로스테릭 사이트에서 약물 가능성을 발굴.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import ConformerSpec, EnsembleRequest, EnsembleResult


class AlphaFlowAdapter:
    engine_name = "alphaflow"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/alphaflow"),
        weights_dir: Path | None = None,
        device: str = "cuda:0",
        binary: str = "alphaflow",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.weights_dir = weights_dir
        self.device = device
        self.binary = binary

    def sample(self, req: EnsembleRequest) -> EnsembleResult:
        t0 = time.time()
        try:
            conformers = self._run_alphaflow(req)
        except FileNotFoundError:
            logger.warning(
                "AlphaFlow 미설치. pip install -e git+https://github.com/bjing2016/alphaflow"
            )
            return EnsembleResult(
                engine=self.engine_name, conformers=[],
                wall_seconds=time.time() - t0,
                metadata={"error": "alphaflow not installed"},
            )

        cluster_centers: list[int] = []
        if req.cluster and conformers:
            cluster_centers = self._cluster_conformers(conformers, req.n_clusters)

        logger.info(
            "AlphaFlow: {} 컨포머 샘플 → {} 클러스터 중심",
            len(conformers),
            len(cluster_centers),
        )
        return EnsembleResult(
            engine=self.engine_name,
            conformers=conformers,
            cluster_centers=cluster_centers,
            wall_seconds=time.time() - t0,
            metadata={"n_samples": req.n_samples, "device": self.device},
        )

    def _run_alphaflow(self, req: EnsembleRequest) -> list[ConformerSpec]:
        with TemporaryDirectory(prefix="alphaflow_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            fasta = tmp_dir / "input.fasta"
            fasta.write_text(f">query\n{req.protein_sequence}\n")
            out_dir = tmp_dir / "out"
            out_dir.mkdir()

            cmd = [
                self.binary, "predict",
                "--input_fasta", str(fasta),
                "--output_dir", str(out_dir),
                "--num_samples", str(req.n_samples),
                "--seed", str(req.seed),
                "--device", self.device,
            ]
            if self.weights_dir:
                cmd += ["--weights_dir", str(self.weights_dir)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            cif_paths = sorted(out_dir.rglob("sample_*.cif"))
            conformers: list[ConformerSpec] = []
            persistent_dir = self.cache_dir / f"{abs(hash(req.protein_sequence)) % 10**12}"
            persistent_dir.mkdir(exist_ok=True)
            for i, cif in enumerate(cif_paths):
                target = persistent_dir / f"sample_{i:03d}.cif"
                target.write_bytes(cif.read_bytes())
                conformers.append(ConformerSpec(cif_path=target))
            return conformers

    def _cluster_conformers(
        self, conformers: list[ConformerSpec], k: int
    ) -> list[int]:
        """간단한 RMSD 기반 클러스터링 (k-medoids)."""
        if len(conformers) <= k:
            for i, c in enumerate(conformers):
                c.cluster_id = i
            return list(range(len(conformers)))

        try:
            import numpy as np
            from sklearn.cluster import KMeans

            # 단순 placeholder: 실제로는 RMSD distance matrix → spectral clustering
            features = np.array([
                [c.plddt_mean, c.rmsd_to_apo, *c.pocket_volumes[:5]]
                + [0.0] * max(0, 5 - len(c.pocket_volumes))
                for c in conformers
            ])
            km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(features)
            for i, c in enumerate(conformers):
                c.cluster_id = int(km.labels_[i])
            centers: list[int] = []
            for cl in range(k):
                idx = [i for i, lab in enumerate(km.labels_) if lab == cl]
                if idx:
                    centers.append(idx[0])
            return centers
        except ImportError:
            logger.debug("sklearn 미설치 — 클러스터링 생략")
            return list(range(min(k, len(conformers))))
