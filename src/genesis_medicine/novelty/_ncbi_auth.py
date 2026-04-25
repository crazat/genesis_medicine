"""NCBI E-utilities 인증/rate-limit helper.

API 키 등록 시 (env: NCBI_API_KEY) 3 req/s → 10 req/s.
프로젝트 루트의 .env 를 자동 로드 (python-dotenv 의존 없이 최소 파서).
"""

from __future__ import annotations

import os

from .._env import load_dotenv_once as _load_dotenv_once


def ncbi_params() -> dict[str, str]:
    """NCBI eutils 호출에 merge할 인증 파라미터 dict."""
    _load_dotenv_once()
    p: dict[str, str] = {}
    if k := os.environ.get("NCBI_API_KEY"):
        p["api_key"] = k
    if e := os.environ.get("NCBI_EMAIL"):
        p["email"] = e
    if tool := os.environ.get("NCBI_TOOL", "Genesis_Medicine"):
        p["tool"] = tool
    return p


def ncbi_sleep_seconds() -> float:
    """API 키 유무에 따른 권장 sleep (초)."""
    _load_dotenv_once()
    return 0.11 if os.environ.get("NCBI_API_KEY") else 0.34


def has_api_key() -> bool:
    _load_dotenv_once()
    return bool(os.environ.get("NCBI_API_KEY"))
