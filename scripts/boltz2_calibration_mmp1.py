"""Boltz-2 calibration on MMP-1 — ChEMBL IC50 vs predicted affinity.

Quantifies what Boltz-2 affinity_probability_binary actually means for our
target. Establishes Spearman/Pearson correlation between Boltz-2 prediction
and experimental pIC50.

Used in the methods section of the paper:
  "Boltz-2 affinity ranking achieved Spearman ρ = X on MMP-1 ChEMBL set
  (n=Y compounds); 0.749 corresponds to ~Z nM IC50 in our hands."

Reference dataset
-----------------
ChEMBL target CHEMBL231 (MMP-1, human collagenase 1).
Filtering:
  - Standard relation '='
  - Standard type 'IC50' or 'Ki' (converted to pIC50/pKi)
  - Active compounds only (excluding inactive/inconclusive)
  - Single-protein assay confidence ≥ 7

Run
---
  python scripts/boltz2_calibration_mmp1.py --out pilot/calibration/boltz2_mmp1/
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MSA_CACHE = DATA / "msa"

MMP1_SEQ = (
    "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFAR"
    "GAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDI"
    "GALMYPSYTFSGDVQLAQDDIDGIQAIYG"
)


def load_calibration_set(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = {"chembl_id", "smiles", "ic50_nm", "reference"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"calibration CSV missing columns: {missing}")
    # pIC50 = -log10(IC50 in M)
    df["pIC50"] = -df["ic50_nm"].apply(lambda x: math.log10(x * 1e-9))
    return df


def run_boltz_cofold(df: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    """Run Boltz-2 cofold on each (compound, MMP-1) pair."""
    import yaml
    inp = out_dir / "boltz_inputs"
    inp.mkdir(parents=True, exist_ok=True)
    boltz_out = out_dir / "boltz_output"
    boltz_out.mkdir(parents=True, exist_ok=True)

    for _, r in df.iterrows():
        payload = {
            "version": 1,
            "sequences": [
                {"protein": {"id": "A", "sequence": MMP1_SEQ,
                              "msa": str((MSA_CACHE / "mmp1.a3m").absolute())}},
                {"ligand": {"id": "B", "smiles": r["smiles"]}},
            ],
            "properties": [{"affinity": {"binder": "B"}}],
        }
        (inp / f"mmp1__{r['chembl_id']}.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False))

    boltz_bin = str(Path(sys.executable).parent / "boltz")
    cmd = [
        boltz_bin, "predict", str(inp),
        "--out_dir", str(boltz_out),
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print(f"  running Boltz-2 on {len(df)} compounds…")
    t0 = time.time()
    subprocess.run(cmd, check=True)
    print(f"  ✅ {(time.time()-t0)/60:.1f}min")

    # collect results
    rows = []
    for aff in sorted(boltz_out.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        _, chembl_id = stem.split("__", 1)
        rows.append({
            "chembl_id": chembl_id,
            "boltz2_affinity_pred": d.get("affinity_pred_value"),
            "boltz2_prob_binary": d.get("affinity_probability_binary"),
        })
    return pd.DataFrame(rows)


def correlate(merged: pd.DataFrame) -> dict:
    """Compute Spearman + Pearson + RMSE between predicted and experimental."""
    from scipy.stats import spearmanr, pearsonr

    # Boltz-2 affinity_pred_value is approximately pIC50-like
    sp_aff = spearmanr(merged["pIC50"], merged["boltz2_affinity_pred"])
    pe_aff = pearsonr(merged["pIC50"], merged["boltz2_affinity_pred"])

    # binary probability — interpret as binder/non-binder confidence
    sp_prob = spearmanr(merged["pIC50"], merged["boltz2_prob_binary"])

    rmse = float(((merged["pIC50"] - merged["boltz2_affinity_pred"])**2).mean()**0.5)

    return {
        "n_compounds": len(merged),
        "pIC50_range": [float(merged["pIC50"].min()),
                         float(merged["pIC50"].max())],
        "spearman_pIC50_vs_affinity": {
            "rho": float(sp_aff.correlation), "p_value": float(sp_aff.pvalue),
        },
        "pearson_pIC50_vs_affinity": {
            "r": float(pe_aff.statistic), "p_value": float(pe_aff.pvalue),
        },
        "spearman_pIC50_vs_prob_binary": {
            "rho": float(sp_prob.correlation), "p_value": float(sp_prob.pvalue),
        },
        "rmse_pIC50_vs_affinity": rmse,
        "interpretation": (
            "ranking validated" if sp_aff.correlation > 0.5 else
            "weak ranking — review compound diversity"
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path,
                    default=ROOT / "pilot/calibration/boltz2_mmp1")
    p.add_argument("--csv", type=Path,
                    default=DATA / "chembl_mmp1_calibration.csv",
                    help="ChEMBL calibration CSV (chembl_id,smiles,ic50_nm,reference)")
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    print("=" * 72)
    print("Boltz-2 Calibration — MMP-1 (ChEMBL)")
    print(f"  csv: {args.csv}")
    print(f"  out: {args.out}")
    print("=" * 72)

    df = load_calibration_set(args.csv)
    print(f"\n[1/3] loaded {len(df)} compounds, "
          f"pIC50 range [{df['pIC50'].min():.1f}, {df['pIC50'].max():.1f}]")

    pred_df = run_boltz_cofold(df, args.out)
    merged = df.merge(pred_df, on="chembl_id", how="inner")
    merged.to_csv(args.out / "calibration_predictions.csv", index=False)
    print(f"\n[2/3] {args.out}/calibration_predictions.csv")

    stats = correlate(merged)
    (args.out / "calibration_stats.json").write_text(
        json.dumps(stats, indent=2))
    print(f"\n[3/3] correlation:")
    print(f"  Spearman ρ (pIC50 vs Boltz-2 affinity_pred) = "
          f"{stats['spearman_pIC50_vs_affinity']['rho']:.3f}")
    print(f"  Pearson r = {stats['pearson_pIC50_vs_affinity']['r']:.3f}")
    print(f"  RMSE      = {stats['rmse_pIC50_vs_affinity']:.2f} pIC50 units")
    print(f"  → {stats['interpretation']}")
    print(f"\n✅ {args.out}/calibration_stats.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
