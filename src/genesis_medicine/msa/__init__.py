"""MSA 생성 모듈.

상업 빌드는 자체 호스팅 MMseqs2-GPU 사용 (BSD-2, 상용 OK).
연구 빌드는 ColabFold 공용 서버 사용 가능.

S4 — 2026-04-25 ultrathink 추가.
"""

from .base import MSAProvider, MSARequest, MSAResult
from .mmseqs2_local import MMseqs2LocalProvider
from .colabfold_public import ColabFoldPublicProvider
from .factory import get_msa_provider

__all__ = [
    "MSAProvider",
    "MSARequest",
    "MSAResult",
    "MMseqs2LocalProvider",
    "ColabFoldPublicProvider",
    "get_msa_provider",
]
