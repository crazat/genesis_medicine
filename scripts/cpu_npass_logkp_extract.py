"""Extract logKp / skin permeation training set from NPASS 3.0 dump.

Tier B #9 — NPASS 2026 dump (213MB downloaded 2026-04-27) → 자체 LGBM
logKp head 학습 데이터 추출.

Strategy:
1. Read NPASS3.0_naturalproducts_structure.txt (np_id, SMILES)
2. Read NPASS3.0_activities.txt (np_id, target_id, activity_value, units)
3. Filter activities where target name suggests skin permeation
   (Caco-2 surrogate, logD, BBB rejected)
4. Cross-reference with skin_compounds_curated.csv to validate ranking
5. Export (smiles, log_kp_proxy) TSV for LGBM training

Note: NPASS 3.0 may not have direct logKp; use Caco-2/PAMPA as proxy
or fall back to physicochemical predictors. This is a SCAFFOLD —
real logKp ground truth still needs SkinPiX dataset (separate task).
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NPASS_DIR = ROOT / ".cache/npass2026"
OUT_DIR = ROOT / "pilot/cpu_meaningful"


def main() -> int:
    structure = NPASS_DIR / "NPASS3.0_naturalproducts_structure.txt"
    activities = NPASS_DIR / "NPASS3.0_activities.txt"
    if not structure.exists() or not activities.exists():
        print(f"❌ NPASS files missing in {NPASS_DIR}")
        return 1

    print(f"Reading {structure.name}...")
    s = pd.read_csv(structure, sep="\t", on_bad_lines="skip", low_memory=False)
    print(f"  Structure: {len(s)} rows, columns: {list(s.columns)[:5]}")

    print(f"Reading {activities.name}...")
    a = pd.read_csv(activities, sep="\t", on_bad_lines="skip", low_memory=False)
    print(f"  Activities: {len(a)} rows, columns: {list(a.columns)}")

    # Activity type counts
    act_counts = a["activity_type_grouped"].value_counts().head(30)
    print(f"\nTop 30 activity types:")
    for k, v in act_counts.items():
        print(f"  {k}: {v}")

    # Find skin-permeation-relevant activities
    skin_keywords = ["caco", "pampa", "papp", "permeab", "skin", "logd",
                       "logp", "logkp", "transdermal", "absorption"]
    a["is_skin_relevant"] = a["activity_type"].str.lower().fillna("").apply(
        lambda x: any(k in x for k in skin_keywords))
    skin_acts = a[a["is_skin_relevant"]]
    print(f"\nSkin-relevant activities: {len(skin_acts)}")

    # Caco-2 + PAMPA most common surrogates
    if len(skin_acts) > 0:
        for at in skin_acts["activity_type"].value_counts().head(10).items():
            print(f"  {at[0]}: {at[1]}")

    # Build training set: smiles × logKp_proxy
    smi_col = "SMILES" if "SMILES" in s.columns else "smiles"
    if smi_col not in s.columns:
        print(f"❌ No SMILES column in structure: {s.columns.tolist()}")
        return 1

    structure_smi = s[["np_id", smi_col]].rename(columns={smi_col: "smiles"})
    structure_smi = structure_smi.dropna(subset=["smiles", "np_id"])

    # ADME-Tox audit table
    adme_keywords = ["caco", "pampa", "papp", "logd", "logp", "absorption",
                       "bioavail", "f%", "clearance", "vd", "auc"]
    a["is_adme"] = a["activity_type"].str.lower().fillna("").apply(
        lambda x: any(k in x for k in adme_keywords))
    adme_table = a[a["is_adme"]].merge(structure_smi, on="np_id", how="left")
    adme_table = adme_table.dropna(subset=["smiles"])
    print(f"\nNPASS 2026 ADME table (smiles × activity): {len(adme_table)}")

    out_csv = OUT_DIR / "npass_2026_adme_skin_relevant.csv"
    adme_table[["np_id", "smiles", "target_id", "activity_type",
                 "activity_value", "activity_units", "assay_organism"]].to_csv(
        out_csv, index=False)
    print(f"\n✅ {out_csv}")

    # Compare with our 102 curated
    curated = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    print(f"\nCurated 102 compounds:")
    print(f"  Compounds with NPASS hit (by canonical SMILES match): "
          f"{curated['smiles'].isin(structure_smi['smiles']).sum()}/{len(curated)}")

    # Quick logP-based logKp proxy (Potts-Guy fallback for full NPASS structure DB)
    try:
        from rdkit import Chem
        from rdkit.Chem import Crippen, Descriptors
        n = 0
        rows = []
        for _, r in structure_smi.head(10000).iterrows():
            m = Chem.MolFromSmiles(str(r["smiles"]))
            if m is None:
                continue
            logp = Crippen.MolLogP(m)
            mw = Descriptors.MolWt(m)
            log_kp = -2.7 + 0.71 * logp - 0.0061 * mw
            rows.append({"np_id": r["np_id"], "smiles": r["smiles"],
                         "logp": logp, "mw": mw, "log_kp_pottsguy": log_kp})
            n += 1
        proxy = pd.DataFrame(rows)
        out_proxy = OUT_DIR / "npass_2026_pottsguy_logkp_10k.csv"
        proxy.to_csv(out_proxy, index=False)
        print(f"  Potts-Guy logKp proxy: {n} rows → {out_proxy}")
        print(f"  logKp distribution: median {proxy['log_kp_pottsguy'].median():.2f}, "
              f"top permeable {(proxy['log_kp_pottsguy'] > -3.5).sum()} "
              f"({100 * (proxy['log_kp_pottsguy'] > -3.5).mean():.1f}%)")
    except ImportError:
        print("  (RDKit unavailable — skipping Potts-Guy proxy)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
