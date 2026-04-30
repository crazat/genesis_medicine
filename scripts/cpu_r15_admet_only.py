"""R15 BRICS ADMET-AI only (no multiprocessing — TF deadlock 회피).

Output: pilot/cpu_meaningful/r15_admet_only.csv
"""
from __future__ import annotations
import sys
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def main():
    r1 = pd.read_csv(OUT / "r15_brics_candidates.csv")
    r2_path = OUT / "r15_brics_round2.csv"
    if r2_path.exists():
        r2 = pd.read_csv(r2_path)
        df = pd.concat([r1, r2], ignore_index=True).drop_duplicates("derivative_smiles").reset_index(drop=True)
    else:
        df = r1
    print(f"R15 BRICS pool: {len(df)} unique candidates")

    print("Loading ADMET-AI...")
    from admet_ai import ADMETModel
    model = ADMETModel()
    print(f"Predicting on {len(df)} SMILES...")
    preds = model.predict(smiles=df["derivative_smiles"].tolist())
    if isinstance(preds, pd.DataFrame):
        admet_df = preds.reset_index().rename(columns={"index": "smiles_in"})
    else:
        admet_df = pd.DataFrame(preds)
    admet_df["derivative_smiles"] = df["derivative_smiles"].values[:len(admet_df)]
    keep_cols = ["derivative_smiles", "AMES", "DILI", "hERG", "BBB_Martins",
                 "HIA_Hou", "Lipophilicity_AstraZeneca", "Solubility_AqSolDB",
                 "ClinTox", "Carcinogens_Lagunin", "Skin_Reaction",
                 "CYP3A4_Veith", "CYP2C9_Veith", "CYP2D6_Veith"]
    keep_cols = [c for c in keep_cols if c in admet_df.columns]
    merged = df.merge(admet_df[keep_cols], on="derivative_smiles", how="left")

    out_path = OUT / "r15_admet_only.csv"
    merged.to_csv(out_path, index=False)
    print(f"\nSaved {out_path} ({len(merged)} rows)")
    if "AMES" in merged.columns:
        print(f"\nAMES safe (<0.3): {(merged['AMES'] < 0.3).sum()}/{len(merged)}")
    if "hERG" in merged.columns:
        print(f"hERG safe (<0.3): {(merged['hERG'] < 0.3).sum()}/{len(merged)}")
    if "AMES" in merged.columns and "hERG" in merged.columns:
        triple = (merged['AMES'] < 0.3) & (merged['hERG'] < 0.3)
        if "DILI" in merged.columns:
            triple = triple & (merged['DILI'] < 0.3)
        print(f"Triple safe (AMES+hERG+DILI <0.3): {triple.sum()}/{len(merged)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
