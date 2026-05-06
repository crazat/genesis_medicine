"""PoseBusters validation on all completed Boltz-2 cofold poses (24-core).

Paper-tier task: physical validity of generated poses per target. Outputs
pass/fail ratios suitable for preprint figures.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def validate_one(args):
    """Run PoseBusters on a single Boltz-2 output directory."""
    target, compound, pose_path = args
    try:
        from posebusters import PoseBusters
        buster = PoseBusters(config="dock")  # docking-style checks
        df = buster.bust([str(pose_path)])
        # df is a single-row DataFrame with check results
        passed = bool(df.iloc[0].all())
        return {
            "target": target,
            "compound": compound,
            "pose_path": str(pose_path),
            "passed": passed,
            "n_checks": len(df.columns),
            "n_passed": int(df.iloc[0].sum()),
            **{c: bool(df.iloc[0][c]) for c in df.columns},
        }
    except Exception as e:
        return {
            "target": target,
            "compound": compound,
            "pose_path": str(pose_path),
            "passed": False,
            "error": str(e)[:120],
        }


def main():
    print("=" * 72)
    print("PoseBusters paper-tier validation")
    print("=" * 72)

    # Collect all CIF poses from boltz_results dirs
    args_list = []
    for cif in ROOT.glob("pilot/**/boltz_results_*/predictions/**/*.cif"):
        # Skip affinity-only files
        if "affinity" in cif.name.lower():
            continue
        # Parse target/compound
        parts = cif.stem.split("__")
        if len(parts) < 2:
            continue
        target = parts[0]
        compound = parts[-1].replace("_model_0", "")
        args_list.append((target, compound, cif))

    # Limit to top 300 by deterministic ordering
    args_list = sorted(set(args_list))[:300]
    print(f"PoseBusters tasks: {len(args_list)} (capped at 300)")

    if len(args_list) == 0:
        print("No CIF poses found — nothing to validate")
        return

    with Pool(processes=12) as pool:    # 12 to leave headroom
        results = pool.map(validate_one, args_list)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "posebusters_validation.csv", index=False)
    print(f"\n✅ posebusters_validation.csv ({len(df)} rows)")

    # Summary per target
    print("\n[Pass rate per target]")
    summary = df.groupby("target")["passed"].agg(
        ["count", "sum", "mean"]).rename(columns={"sum": "n_passed",
                                                    "mean": "pass_rate"})
    summary.to_csv(OUT / "posebusters_summary.csv")
    print(summary.round(3).to_string())

    # Overall
    overall = df["passed"].mean()
    print(f"\nOverall pose validity: {overall:.1%} ({df['passed'].sum()}/{len(df)})")


if __name__ == "__main__":
    sys.exit(main())
