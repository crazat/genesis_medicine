"""pytest 공통 fixture."""

from __future__ import annotations

import os
import random
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def _deterministic_seed() -> None:
    random.seed(42)
    np.random.seed(42)
    try:
        import torch

        torch.manual_seed(42)
    except ImportError:
        pass


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def pytest_collection_modifyitems(config, items):
    if not os.environ.get("GENESIS_RUN_GPU"):
        skip_gpu = pytest.mark.skip(reason="GPU 테스트: GENESIS_RUN_GPU=1 지정 시 실행")
        for item in items:
            if "gpu" in item.keywords:
                item.add_marker(skip_gpu)
