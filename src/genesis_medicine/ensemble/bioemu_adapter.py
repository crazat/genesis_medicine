"""BioEmu — Microsoft Boltzmann emulator (MIT, 2026-01).

https://github.com/microsoft/bioemu

특징
----
- 물리 기반 Boltzmann 분포 직접 학습
- AlphaFlow 대비 고온 컨포머·전이 상태 더 잘 잡음
- 단백질 동적 ensemble 생성

용도 (Stage 2.5 — A2)
---------------------
AlphaFlow와 직교적 신호 → 둘 모두로 conformer 생성, 합집합으로 cryptic pocket 탐색.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import ConformerSpec, EnsembleRequest, EnsembleResult


class BioEmuAdapter:
    engine_name = "bioemu"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/bioemu"),
        weights_dir: Path | None = None,
        device: str = "cuda:0",
        binary: str = "bioemu",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.weights_dir = weights_dir
        self.device = device
        self.binary = binary

    def sample(self, req: EnsembleRequest) -> EnsembleResult:
        t0 = time.time()
        try:
            conformers = self._run_bioemu(req)
        except FileNotFoundError:
            logger.warning(
                "BioEmu 미설치. pip install -e git+https://github.com/microsoft/bioemu"
            )
            return EnsembleResult(
                engine=self.engine_name, conformers=[],
                wall_seconds=time.time() - t0,
                metadata={"error": "bioemu not installed"},
            )
        logger.info("BioEmu: {} 컨포머", len(conformers))
        return EnsembleResult(
            engine=self.engine_name,
            conformers=conformers,
            wall_seconds=time.time() - t0,
            metadata={"n_samples": req.n_samples},
        )

    def _run_bioemu(self, req: EnsembleRequest) -> list[ConformerSpec]:
        with TemporaryDirectory(prefix="bioemu_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            fasta = tmp_dir / "input.fasta"
            fasta.write_text(f">query\n{req.protein_sequence}\n")
            out_dir = tmp_dir / "out"
            out_dir.mkdir()

            cmd = [
                self.binary, "sample",
                "--sequence", req.protein_sequence,
                "--output", str(out_dir),
                "--num_samples", str(req.n_samples),
                "--seed", str(req.seed),
            ]
            if self.weights_dir:
                cmd += ["--weights", str(self.weights_dir)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            persistent_dir = self.cache_dir / f"{abs(hash(req.protein_sequence)) % 10**12}"
            persistent_dir.mkdir(exist_ok=True)
            cif_paths = sorted(out_dir.rglob("sample_*.cif")) or sorted(out_dir.rglob("sample_*.pdb"))
            conformers: list[ConformerSpec] = []
            for i, p in enumerate(cif_paths):
                target = persistent_dir / f"sample_{i:03d}{p.suffix}"
                target.write_bytes(p.read_bytes())
                conformers.append(ConformerSpec(cif_path=target))
            return conformers
