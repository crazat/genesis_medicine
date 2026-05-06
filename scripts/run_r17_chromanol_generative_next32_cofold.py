"""Queue the next 32 balanced R17 generative chromanol Boltz-2 cofolds.

This wrapper is intentionally stdlib-only because the GPU daemon launches GPU
scripts with the genesis-md Python. The actual Boltz-2 runner is invoked through
the project .venv where Boltz is installed.
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
BATCH_SIZE = 32
TARGET_ROWS = int(os.environ.get("GENESIS_R17_GENERATIVE_TARGET_ROWS", "240"))


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def completed_batch_rows() -> int:
    total = 0
    for path in sorted(OUT.glob("r17_chromanol_generative_batch*_cofold.csv")):
        total += csv_row_count(path)
    return total


def main() -> int:
    completed = completed_batch_rows()
    if completed >= TARGET_ROWS:
        print(f"R17 generative cofold target already complete: {completed}/{TARGET_ROWS}")
        return 0

    offset = completed
    batch_index = offset // BATCH_SIZE + 1
    topn = min(BATCH_SIZE, TARGET_ROWS - completed)
    tag = f"batch{batch_index:02d}_rank{offset + 1:03d}_{offset + topn:03d}"
    cmd = [
        str(ROOT / ".venv/bin/python"),
        "-u",
        "scripts/run_r17_chromanol_generative_top_cofold.py",
        "--topn",
        str(topn),
        "--offset",
        str(offset),
        "--tag",
        tag,
    ]
    print(f"R17 next batch: completed={completed} target={TARGET_ROWS} tag={tag}")
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
