"""JUMP Cell Painting consortium S3 fetch (Round 7, public bucket).

Verified S3 path (2026-04-27):
    s3://cellpainting-gallery/cpg0016-jump/source_<N>/workspace/profiles/
        <BatchDate>/<PlateID>/<PlateID>.parquet

Each plate parquet ≈ 12-13 MiB, 384 wells × 4765 CellProfiler features.
Total scope: ~1100 plates across 10 sources ≈ 14 GB profiles + much larger
images (~30 TB).

License: Public-domain (CC0); JUMP-CP consortium, hosted on AWS S3.
Refs   : Chandrasekaran et al. Nat Methods 2025.

Why this matters (Round 6 Tier 0 audit, +5-7 pp acceptance):
    Querying our 102 + scaffold-hop compounds against JUMP profiles yields
    nearest-neighbor MoA hypothesis without wet-lab.

Usage:
    python scripts/fetch_jump_cp.py --sample        # 1 plate (12 MB) demo
    python scripts/fetch_jump_cp.py --source 4       # full source_4 (~1 GB)
    python scripts/fetch_jump_cp.py --all            # ~14 GB total
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/jump_cp"
OUT.mkdir(parents=True, exist_ok=True)

JUMP_BUCKET = "s3://cellpainting-gallery/cpg0016-jump"
SAMPLE_PLATE = (
    f"{JUMP_BUCKET}/source_4/workspace/profiles/"
    "2021_04_26_Batch1/BR00117035/BR00117035.parquet"
)


def aws() -> str:
    aws_bin = shutil.which("aws")
    if not aws_bin:
        print("❌ aws CLI not on PATH. uv pip install awscli")
        sys.exit(1)
    return aws_bin


def fetch_sample():
    out_file = OUT / "sample_BR00117035.parquet"
    if out_file.exists():
        print(f"  ✓ already present: {out_file}")
        return
    cmd = [aws(), "s3", "cp", "--no-sign-request",
           SAMPLE_PLATE, str(out_file)]
    subprocess.run(cmd, check=True, timeout=600)
    print(f"  ✅ {out_file}")


def fetch_source(source_id: int):
    src = f"{JUMP_BUCKET}/source_{source_id}/workspace/profiles/"
    out = OUT / f"source_{source_id}"
    out.mkdir(exist_ok=True)
    cmd = [aws(), "s3", "sync", "--no-sign-request",
           "--exclude", "*",
           "--include", "*/profiles/*/*/*.parquet",
           src, str(out)]
    print(f"  syncing {src} → {out}")
    subprocess.run(cmd, check=True, timeout=7200)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true",
                    help="fetch single plate demo (12 MB)")
    ap.add_argument("--source", type=int,
                    help="fetch all plates from one JUMP source")
    ap.add_argument("--all", action="store_true",
                    help="fetch all profiles ~14 GB")
    args = ap.parse_args()

    print("=" * 72)
    print("JUMP Cell Painting consortium S3 fetch")
    print("=" * 72)

    if args.sample or (not args.source and not args.all):
        fetch_sample()
        # Quick inspection
        try:
            import pandas as pd
            df = pd.read_parquet(OUT / "sample_BR00117035.parquet")
            print(f"\n  rows: {len(df)}, cols: {len(df.columns)}")
            print(f"  ~384 wells × 4,765 CellProfiler features per plate")
        except Exception:
            pass

    if args.source:
        fetch_source(args.source)

    if args.all:
        for sid in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15]:
            try:
                fetch_source(sid)
            except Exception as e:
                print(f"  source_{sid} failed: {e}")

    print(f"\n✅ {OUT}")


if __name__ == "__main__":
    sys.exit(main())
