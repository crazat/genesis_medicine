"""R15 master triage: ADMET + xtb + composite score → ranked CSV.

분리 실행된 ADMET (no-Pool) + xtb (Pool) 결과 통합.
Composite score: (1-AMES)*0.3 + (1-hERG)*0.2 + (1-DILI)*0.15 +
                 skin_window*0.15 + (gap_eV>2.5)*0.1 + QED*0.1

Output: pilot/cpu_meaningful/r15_master_triage.csv
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def main():
    admet = pd.read_csv(OUT / "r15_admet_only.csv")
    xtb = pd.read_csv(OUT / "r15_xtb_only.csv")
    print(f"ADMET: {len(admet)} rows, xtb: {len(xtb)} rows")

    xtb_keep = ["derivative_smiles", "HOMO_eV", "LUMO_eV", "gap_eV", "energy_au"]
    xtb_keep = [c for c in xtb_keep if c in xtb.columns]
    df = admet.merge(xtb[xtb_keep], on="derivative_smiles", how="left")

    # Composite score
    def safe(col, default=0.5):
        return df.get(col, pd.Series([default]*len(df))).fillna(default)

    df["score"] = (
        (1 - safe("AMES", 0.5)) * 0.30 +
        (1 - safe("hERG", 0.5)) * 0.20 +
        (1 - safe("DILI", 0.5)) * 0.15 +
        df.get("skin_window", pd.Series([False]*len(df))).astype(float) * 0.15 +
        (safe("gap_eV", 3.0) > 2.5).astype(float) * 0.10 +
        safe("QED", 0.5) * 0.10
    )
    df = df.sort_values("score", ascending=False).reset_index(drop=True)

    out_path = OUT / "r15_master_triage.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {out_path} ({len(df)} rows)")

    cols = ["leader_seed", "derivative_smiles", "MW", "logP", "QED",
            "AMES", "hERG", "DILI", "gap_eV", "skin_window", "score"]
    cols = [c for c in cols if c in df.columns]
    print("\n=== Top 10 R15 leads (composite score) ===")
    print(df[cols].head(10).to_string(index=False))

    print("\n=== Triple-safe (AMES+hERG+DILI < 0.3) ===")
    triple = (df["AMES"] < 0.3) & (df["hERG"] < 0.3) & (df["DILI"] < 0.3)
    print(df[triple][cols].to_string(index=False))

    print(f"\nTriple-safe count: {triple.sum()}/{len(df)}")
    print(f"\nLeader distribution:")
    print(df.groupby("leader_seed").size().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
