"""Validate SAR panel — RDKit sanitization + property computation + ADMET-AI.

Sanity check before launching corrected ABFE on Phase 2 SAR set.
Outputs: pilot/sar_panel/panel_validated.csv with all properties.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/sar_panel_phase2.csv"
OUT_DIR = ROOT / "pilot/sar_panel"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    from rdkit import Chem, RDLogger
    from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski
    RDLogger.DisableLog("rdApp.*")

    df = pd.read_csv(INPUT_CSV)
    print(f"loaded {len(df)} compounds from {INPUT_CSV}")

    rows = []
    for _, r in df.iterrows():
        smi = r["smiles"]
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            print(f"  ❌ {r['compound']}: SMILES invalid")
            continue
        canon = Chem.MolToSmiles(mol)
        rows.append({
            "compound": r["compound"],
            "smiles_input": smi,
            "smiles_canonical": canon,
            "valid": True,
            "MW": round(Descriptors.MolWt(mol), 2),
            "logP": round(Crippen.MolLogP(mol), 3),
            "HBD": Lipinski.NumHDonors(mol),
            "HBA": Lipinski.NumHAcceptors(mol),
            "TPSA": round(Descriptors.TPSA(mol), 2),
            "n_rotatable": Descriptors.NumRotatableBonds(mol),
            "n_aromatic_rings": Descriptors.NumAromaticRings(mol),
            "scaffold_class": r["scaffold_class"],
            "role": r["role"],
            "literature_source": r["literature_source"],
            "literature_ic50_target": r["literature_ic50_target"],
            "notes": r["notes"],
        })
    val_df = pd.DataFrame(rows)
    print(f"\n[1/2] RDKit valid: {len(val_df)}/{len(df)}")
    print(val_df[["compound", "MW", "logP", "HBD", "HBA", "TPSA"]].to_string())

    # ADMET-AI
    print(f"\n[2/2] ADMET-AI prediction…")
    try:
        from admet_ai import ADMETModel
        model = ADMETModel()
        adm = model.predict(val_df["smiles_canonical"].tolist())
        for col in ["hERG", "Skin_Reaction", "AMES", "ClinTox",
                     "Bioavailability_Ma", "Solubility_AqSolDB"]:
            if col in adm.columns:
                val_df[f"admet_{col}"] = [round(v, 4) for v in adm[col].values]
        print(val_df[["compound", "admet_hERG", "admet_Skin_Reaction",
                       "admet_AMES"]].to_string())
    except ImportError:
        print("  ADMET-AI 미설치, skip")

    out = OUT_DIR / "panel_validated.csv"
    val_df.to_csv(out, index=False)
    print(f"\n✅ {out}")

    # Summary stats
    print("\n=== panel summary ===")
    print(f"  N compounds:        {len(val_df)}")
    print(f"  MW range:           [{val_df['MW'].min():.1f}, {val_df['MW'].max():.1f}]")
    print(f"  logP range:         [{val_df['logP'].min():.2f}, {val_df['logP'].max():.2f}]")
    print(f"  topical sweet spot (logP 1.5-3.5):    "
          f"{((val_df['logP'] >= 1.5) & (val_df['logP'] <= 3.5)).sum()}/{len(val_df)}")
    if "admet_hERG" in val_df.columns:
        print(f"  hERG mean ± std:    "
              f"{val_df['admet_hERG'].mean():.3f} ± {val_df['admet_hERG'].std():.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
