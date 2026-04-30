"""Universal scaffold 5 leaders ADMET + Tanimoto + Lipinski/Brenk audit.

Inputs: R12_4, R12_11, R12_23, R14_5, R13_13 SMILES.
Outputs:
- pilot/universal_scaffold_admet/admet_predictions.csv
- pilot/universal_scaffold_admet/tanimoto_korean_herbal.csv
- pilot/universal_scaffold_admet/rule_audit.csv
- pilot/universal_scaffold_admet/summary.csv

Single-process to avoid multiprocessing overhead. Runs in foreground but lightweight.
"""
from __future__ import annotations

import json, sys, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/universal_scaffold_admet"
OUT.mkdir(parents=True, exist_ok=True)

LEADERS = [
    {"name": "R12_4",  "smiles": "OCC1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1",
     "variant": "hydroxymethyl pterocarpan-vinyl-phenol",
     "subA_count": 2, "best_target": "MMP1 (0.73), SIRT1 (0.76)"},
    {"name": "R12_11", "smiles": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1",
     "variant": "methoxy variant",
     "subA_count": 3, "best_target": "TGFB1 (0.93), DCT (1.01), LOX (1.09)"},
    {"name": "R12_23", "smiles": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1",
     "variant": "methyl ester variant",
     "subA_count": 6, "best_target": "AR/SIRT1 (0.68), PTGS2 (0.72), SREBP1 (0.79)"},
    {"name": "R14_5",  "smiles": "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
     "variant": "methoxy variant 2",
     "subA_count": 3, "best_target": "MMP1 (0.56), CTGF (0.68), SREBP1 (0.89)"},
    {"name": "R13_13", "smiles": "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1",
     "variant": "prenyl R11_0 variant (PAINS-flagged)",
     "subA_count": 1, "best_target": "PTGS2 (1.01)"},
]


def admet_predict():
    print("\n=== ADMET-AI prediction ===")
    try:
        from admet_ai import ADMETModel
        model = ADMETModel()
    except Exception as e:
        print(f"  ADMET-AI not available: {e}")
        return None
    rows = []
    for ld in LEADERS:
        try:
            preds = model.predict(smiles=ld["smiles"])
            r = {"leader": ld["name"], "smiles": ld["smiles"],
                 "variant": ld["variant"]}
            r.update(preds)
            rows.append(r)
            print(f"  ✅ {ld['name']}: {len(preds)} endpoints")
        except Exception as e:
            print(f"  ❌ {ld['name']}: {e}")
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUT / "admet_predictions.csv", index=False)
        print(f"  saved {OUT/'admet_predictions.csv'} ({len(df)} rows)")
        return df
    return None


def tanimoto_korean():
    print("\n=== Tanimoto vs Korean herbal master DB ===")
    csv_path = ROOT / "data/skin_compounds_curated.csv"
    if not csv_path.exists():
        print(f"  missing: {csv_path}")
        return None
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, DataStructs
    except Exception as e:
        print(f"  rdkit unavailable: {e}")
        return None

    herb_df = pd.read_csv(csv_path)
    if "smiles" not in herb_df.columns:
        smi_col = next((c for c in herb_df.columns if "smi" in c.lower()), None)
        if not smi_col:
            print(f"  no SMILES column. cols: {list(herb_df.columns)}")
            return None
        herb_df = herb_df.rename(columns={smi_col: "smiles"})
    herb_df = herb_df.dropna(subset=["smiles"]).reset_index(drop=True)
    print(f"  korean herbal DB: {len(herb_df)} compounds")

    herb_fps = []
    for s in herb_df["smiles"]:
        m = Chem.MolFromSmiles(s)
        if m is None:
            herb_fps.append(None); continue
        herb_fps.append(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048))

    rows = []
    for ld in LEADERS:
        m = Chem.MolFromSmiles(ld["smiles"])
        if m is None:
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
        sims = []
        for i, hfp in enumerate(herb_fps):
            if hfp is None: continue
            t = DataStructs.TanimotoSimilarity(fp, hfp)
            sims.append((i, t))
        sims.sort(key=lambda x: -x[1])
        for rank, (idx, t) in enumerate(sims[:5], 1):
            row = {"leader": ld["name"], "rank": rank, "tanimoto": round(t, 3)}
            for c in herb_df.columns:
                row[f"herb_{c}"] = herb_df.iloc[idx][c]
            rows.append(row)
        print(f"  ✅ {ld['name']}: top1 Tanimoto = {sims[0][1]:.3f}")

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUT / "tanimoto_korean_herbal.csv", index=False)
        print(f"  saved {OUT/'tanimoto_korean_herbal.csv'} ({len(df)} rows)")
        return df
    return None


def rule_audit():
    print("\n=== Lipinski / Veber / Brenk / PAINS audit ===")
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors
        from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
    except Exception as e:
        print(f"  rdkit unavailable: {e}")
        return None

    pains_params = FilterCatalogParams()
    pains_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    pains_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
    pains_cat = FilterCatalog(pains_params)

    rows = []
    for ld in LEADERS:
        m = Chem.MolFromSmiles(ld["smiles"])
        if m is None:
            continue
        mw = Descriptors.MolWt(m)
        logp = Descriptors.MolLogP(m)
        hbd = Lipinski.NumHDonors(m)
        hba = Lipinski.NumHAcceptors(m)
        tpsa = Descriptors.TPSA(m)
        rotb = Lipinski.NumRotatableBonds(m)
        aro_rings = rdMolDescriptors.CalcNumAromaticRings(m)
        rings = rdMolDescriptors.CalcNumRings(m)
        lipinski_violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
        veber_pass = (rotb <= 10) and (tpsa <= 140)
        matches = pains_cat.GetMatches(m)
        flags = [m_.GetDescription() for m_ in matches]
        pains_flag = any("PAINS" in f for f in flags)
        brenk_flag = any("BRENK" in f.upper() for f in flags)
        # Skin-permeable estimate: logP 1.5–3.5, MW <= 500
        skin_ok = (1.5 <= logp <= 3.5) and (mw <= 500)
        rows.append({
            "leader": ld["name"], "variant": ld["variant"],
            "MW": round(mw, 1), "logP": round(logp, 2),
            "HBD": hbd, "HBA": hba, "TPSA": round(tpsa, 1),
            "rotb": rotb, "aro_rings": aro_rings, "rings": rings,
            "lipinski_violations": lipinski_violations,
            "veber_pass": veber_pass,
            "pains_flag": pains_flag, "brenk_flag": brenk_flag,
            "skin_permeable_window": skin_ok,
            "subA_count": ld["subA_count"], "best_target": ld["best_target"],
        })
        print(f"  ✅ {ld['name']}: MW={mw:.0f} logP={logp:.1f} Lipinski_viol={lipinski_violations} skin_window={skin_ok}")

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUT / "rule_audit.csv", index=False)
        print(f"  saved {OUT/'rule_audit.csv'} ({len(df)} rows)")
        return df
    return None


def main():
    print("Universal scaffold 5 leaders ADMET + Tanimoto + Rule audit")
    rule_df = rule_audit()
    tani_df = tanimoto_korean()
    admet_df = admet_predict()
    print("\nDone.")
    if rule_df is not None:
        print("\nRule audit summary:")
        print(rule_df[["leader", "MW", "logP", "lipinski_violations",
                       "pains_flag", "brenk_flag", "skin_permeable_window"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
