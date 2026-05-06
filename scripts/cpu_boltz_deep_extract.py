"""Deep extraction of Boltz-2 cofold confidence + PAE + affinity for all completed runs.

Paper-tier output: full per-cofold metrics suitable for confidence-vs-affinity
calibration figure + ChEMBL pIC50 ground truth correlation when available.
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def extract_one(args):
    """Extract one cofold's full metric suite."""
    target, compound, output_dir = args
    try:
        # affinity json (Boltz-2 affinity head)
        aff_files = list(Path(output_dir).rglob("*affinity*.json"))
        conf_files = list(Path(output_dir).rglob("confidence*.json"))

        result = {
            "target": target,
            "compound": compound,
            "source": str(Path(output_dir).name),
        }
        if aff_files:
            d = json.loads(aff_files[0].read_text())
            result.update({
                "affinity_pred": d.get("affinity_pred_value"),
                "affinity_prob_binary": d.get("affinity_probability_binary"),
                "affinity_pred_value1": d.get("affinity_pred_value1"),
                "affinity_pred_value2": d.get("affinity_pred_value2"),
            })

        if conf_files:
            d = json.loads(conf_files[0].read_text())
            for k, v in d.items():
                if isinstance(v, (int, float, str, bool)):
                    result[f"conf_{k}"] = v
                elif isinstance(v, list) and len(v) <= 100:
                    if all(isinstance(x, (int, float)) for x in v):
                        result[f"conf_{k}_mean"] = float(np.mean(v))
                        result[f"conf_{k}_min"] = float(np.min(v))
                        result[f"conf_{k}_max"] = float(np.max(v))

        # PAE matrix mean (npz or npy if exists)
        pae_files = list(Path(output_dir).rglob("pae_*.npz"))
        if pae_files:
            try:
                data = np.load(pae_files[0])
                if "pae" in data.files:
                    pae = data["pae"]
                    result["pae_mean"] = float(pae.mean())
                    result["pae_max"] = float(pae.max())
            except Exception:
                pass

        return result
    except Exception as e:
        return {"target": target, "compound": compound,
                "error": str(e)[:200]}


def main():
    print("=" * 72)
    print("Deep Boltz-2 cofold extraction (24-core)")
    print("=" * 72)

    # Find all output dirs
    args_list = []
    for output_dir in ROOT.glob("pilot/**/boltz_results_*/predictions/*/"):
        if output_dir.is_dir():
            name = output_dir.name
            parts = name.split("__")
            if len(parts) < 2:
                continue
            target = parts[0]
            compound = parts[-1]
            args_list.append((target, compound, output_dir))

    print(f"Cofold output dirs: {len(args_list)}")

    with Pool(24) as p:
        results = p.map(extract_one, args_list)

    df = pd.DataFrame(results).drop_duplicates(["target", "compound"])
    df.to_csv(OUT / "boltz_deep_metrics.csv", index=False)
    print(f"\n✅ boltz_deep_metrics.csv ({len(df)} rows × {len(df.columns)} cols)")

    # Quality flag: high confidence threshold
    if "conf_complex_plddt_mean" in df.columns:
        hq = df[df["conf_complex_plddt_mean"] > 0.7]
        print(f"  High-confidence (plddt > 0.7): {len(hq)}/{len(df)}")
    if "conf_iptm" in df.columns:
        df["iptm_quality"] = pd.cut(df["conf_iptm"],
                                      bins=[0, 0.5, 0.7, 0.85, 1.0],
                                      labels=["poor", "ok", "good", "high"])
        print("\nipTM quality distribution:")
        print(df["iptm_quality"].value_counts().to_string())

    # Per-target affinity stats
    print("\n[Affinity stats per target]")
    for tgt, sub in df.groupby("target"):
        n = len(sub)
        if "affinity_prob_binary" in sub.columns:
            p_mean = sub["affinity_prob_binary"].mean()
            p_max = sub["affinity_prob_binary"].max()
            print(f"  {tgt:15s} n={n:4d}  prob_mean={p_mean:.3f}  prob_max={p_max:.3f}")


if __name__ == "__main__":
    sys.exit(main())
