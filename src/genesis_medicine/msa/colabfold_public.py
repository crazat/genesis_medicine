"""ColabFold 공용 MSA 서버 (학술 전용, research 빌드 한정).

상업 빌드에서는 LicenseGate가 colabfold_public_msa 키로 차단.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import MSAProvider, MSARequest, MSAResult


class ColabFoldPublicProvider(MSAProvider):
    provider_name = "colabfold_public"
    is_commercial_safe = False  # 학술 전용

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/msa_colabfold"),
        endpoint: str = "https://api.colabfold.com",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.endpoint = endpoint

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, max=120))
    def search(self, req: MSARequest) -> MSAResult:
        t0 = time.time()
        h = abs(hash(req.sequence)) % (10**16)
        cached = self.cache_dir / f"{h}.a3m"
        if cached.exists():
            return MSAResult(
                a3m_path=cached,
                n_seqs=sum(1 for _ in cached.read_text().splitlines() if _.startswith(">")),
                wall_seconds=time.time() - t0,
                provider=self.provider_name,
                metadata={"cached": True},
            )

        logger.warning(
            "ColabFold 공용 MSA 서버 사용 — 상업 빌드 금지 (학술 전용). "
            "scripts/setup/install_mmseqs2_gpu.sh로 자체 호스팅 권장."
        )
        # 실제 ColabFold MSA API 호출은 콜라보 프로토콜이 길어서 boltz/protenix 내장 사용 권고
        # 여기서는 placeholder — boltz의 --use_msa_server에 위임하는 게 맞음
        raise NotImplementedError(
            "ColabFold 공용 MSA는 Boltz-2 / Protenix-v2 어댑터의 --use_msa_server 옵션을 사용하세요."
        )
