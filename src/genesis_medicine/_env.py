"""프로젝트 루트 `.env` 1회 로드 (의존성 없음).

NCBI / Semantic Scholar / Firecrawl 등 외부 API 키 공통 진입점.
"""

from __future__ import annotations

import os
from pathlib import Path

_LOADED = False


def load_dotenv_once() -> None:
    """프로젝트 루트의 .env 파일을 1회만 파싱해 os.environ에 주입."""
    global _LOADED
    if _LOADED:
        return
    _LOADED = True

    # src/genesis_medicine/_env.py → 3단계 위가 프로젝트 루트
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        pass
