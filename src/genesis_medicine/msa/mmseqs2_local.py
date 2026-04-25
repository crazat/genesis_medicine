"""자체 호스팅 MMseqs2-GPU MSA 검색 (BSD-2, 상용 OK).

설치:
    scripts/setup/install_mmseqs2_gpu.sh

데이터베이스 (대용량):
    UniRef30 + ColabFoldDB (또는 BFD/Mgnify)
    setup_databases.sh GPU=1

배치 검색 모드: ~128GB RAM
단일 쿼리 모드: ~768GB RAM (DB 인덱스 메모리 보유)

NVIDIA Nature Methods 2025 — MMseqs2-GPU 1.65× 빠름.
S4 — ultrathink 2026-04-25.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import MSAProvider, MSARequest, MSAResult


class MMseqs2LocalProvider(MSAProvider):
    provider_name = "mmseqs2_local"
    is_commercial_safe = True

    def __init__(
        self,
        *,
        db_dir: Path,
        binary: str = "mmseqs",
        threads: int = 16,
        gpu: bool = True,
        cache_dir: Path = Path(".cache/msa"),
    ) -> None:
        self.db_dir = db_dir
        self.binary = binary
        self.threads = threads
        self.gpu = gpu
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._validate_install()

    def _validate_install(self) -> None:
        if not shutil.which(self.binary):
            logger.warning(
                "mmseqs2 binary '{}' 미발견. scripts/setup/install_mmseqs2_gpu.sh 실행 필요.",
                self.binary,
            )
        if not self.db_dir.exists():
            logger.warning(
                "MMseqs2 DB 디렉터리 미발견: {}. setup_databases.sh GPU=1로 빌드 필요.",
                self.db_dir,
            )

    def search(self, req: MSARequest) -> MSAResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="mmseqs2_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            query_fasta = tmp_dir / "query.fasta"
            query_fasta.write_text(f">query\n{req.sequence}\n")

            out_a3m = self.cache_dir / f"{abs(hash(req.sequence)) % (10**16)}.a3m"
            cmd = self._build_cmd(query_fasta, out_a3m, tmp_dir, req)
            logger.info("MMseqs2-{}: {}", "GPU" if self.gpu else "CPU", " ".join(cmd[:6]))
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
            except subprocess.CalledProcessError as e:
                logger.error("MMseqs2 실패: {}\n{}", e.returncode, e.stderr)
                raise
            n_seqs = sum(1 for _ in out_a3m.read_text().splitlines() if _.startswith(">"))
            return MSAResult(
                a3m_path=out_a3m,
                n_seqs=n_seqs,
                wall_seconds=time.time() - t0,
                provider=self.provider_name,
                metadata={"gpu": self.gpu, "threads": self.threads},
            )

    def _build_cmd(
        self,
        query_fasta: Path,
        out_a3m: Path,
        tmp_dir: Path,
        req: MSARequest,
    ) -> list[str]:
        cmd = [
            self.binary, "easy-search",
            str(query_fasta),
            str(self.db_dir / "uniref30"),
            str(out_a3m),
            str(tmp_dir / "ms_tmp"),
            "--threads", str(self.threads),
            "--max-seqs", str(req.max_seqs),
            "-s", "8.0",
            "--format-mode", "5",  # a3m
        ]
        if self.gpu:
            cmd += ["--gpu", "1"]
        return cmd
