"""Track 3 — PAINS audit + Korean herbal mapping for 6 leaders + R14 pool.

Output:
- pilot/cpu_meaningful/track3_pains_audit.json
- pilot/cpu_meaningful/track3_herbal_match.csv
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from multiprocessing import Pool
from rdkit import Chem
from rdkit.Chem import AllChem, FilterCatalog, DataStructs
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

LEADERS = {
    "R11_0":  "OCc1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",
    "R12_4":  "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
    "R12_11": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1",
    "R12_23": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1",
    "R14_5":  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
    "R13_13": "C=CC(C)(C)c1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",
}


def fp_array(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    arr = np.zeros(2048, dtype=np.float32)
    DataStructs.ConvertToNumpyArray(
        AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048), arr)
    return arr


def pains_check(name_smi):
    name, smi = name_smi
    m = Chem.MolFromSmiles(smi)
    catalog_params = FilterCatalog.FilterCatalogParams()
    for fc in [FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A,
               FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B,
               FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C,
               FilterCatalog.FilterCatalogParams.FilterCatalogs.BRENK,
               FilterCatalog.FilterCatalogParams.FilterCatalogs.NIH]:
        catalog_params.AddCatalog(fc)
    cat = FilterCatalog.FilterCatalog(catalog_params)
    matches = cat.GetMatches(m)
    return {
        "name": name,
        "smiles": smi,
        "n_pains_alerts": len(matches),
        "alerts": [m.GetDescription() for m in matches[:5]],
        "passes_pains_filter": len(matches) == 0,
    }


def main():
    print("=" * 60)
    print("Track 3 — PAINS + Korean herbal mapping")
    print("=" * 60)
    items = list(LEADERS.items())

    print("\n[Step 1] PAINS audit on 6 leaders + R14 candidates")
    with Pool(8) as p:
        leader_pains = p.map(pains_check, items)

    # R14 candidates
    r14_pool = pd.read_csv(OUT / "bayesian_v9_round13_candidates.csv").head(50)
    r14_items = [(f"R14cand_{i}", r["smiles"]) for i, r in r14_pool.iterrows()]
    with Pool(8) as p:
        r14_pains = p.map(pains_check, r14_items)

    pains_total = leader_pains + r14_pains
    n_clean = sum(1 for r in pains_total if r["passes_pains_filter"])
    print(f"  6 leaders + 50 R14 candidates: {n_clean}/{len(pains_total)} PAINS-free")

    pains_path = OUT / "track3_pains_audit.json"
    pains_path.write_text(json.dumps(pains_total, indent=2))
    print(f"  ✅ {pains_path}")

    # Korean herbal mapping
    print("\n[Step 2] Korean herbal mapping (Tanimoto FP similarity)")
    herb_csv = ROOT / "data/skin_compounds_curated.csv"
    if not herb_csv.exists():
        print(f"  ⚠️ {herb_csv} not found — try alternate locations")
        for cand in ["data/herbal_master.csv", "data/herb_compounds.csv",
                     "pilot/cpu_meaningful/integrated_top_candidates_per_target.csv"]:
            if (ROOT / cand).exists():
                herb_csv = ROOT / cand
                print(f"  using {herb_csv}")
                break

    if herb_csv.exists():
        herb = pd.read_csv(herb_csv)
        smi_col = next((c for c in herb.columns if c.lower() in ("smiles", "smi")), None)
        if smi_col:
            herb = herb.dropna(subset=[smi_col]).drop_duplicates(smi_col).reset_index(drop=True)
            with Pool(8) as p:
                herb_fps = p.map(fp_array, herb[smi_col].tolist())
            valid = [(i, f) for i, f in enumerate(herb_fps) if f is not None]
            herb_arr = np.array([f for _, f in valid])
            herb_smis = [herb[smi_col].iloc[i] for i, _ in valid]

            rows = []
            for name, smi in items:
                fp = fp_array(smi)
                if fp is None:
                    continue
                # Cosine similarity (proxy for Tanimoto when binary)
                sims = (herb_arr @ fp) / (
                    np.linalg.norm(herb_arr, axis=1) * np.linalg.norm(fp) + 1e-9)
                top5 = np.argsort(-sims)[:5]
                for rank, i in enumerate(top5, 1):
                    rows.append({
                        "leader": name,
                        "leader_smiles": smi,
                        "rank": rank,
                        "herb_compound_smiles": herb_smis[i],
                        "tanimoto_proxy": round(float(sims[i]), 3),
                    })
            herb_match_df = pd.DataFrame(rows)
            out_path = OUT / "track3_herbal_match.csv"
            herb_match_df.to_csv(out_path, index=False)
            print(f"  ✅ {out_path} ({len(rows)} matches)")
            print(f"\n[Top herbal match per leader]")
            for name in [k for k, _ in items]:
                top = herb_match_df[herb_match_df.leader == name].iloc[0]
                print(f"  {name}: top={top['tanimoto_proxy']:.3f} → {top['herb_compound_smiles'][:50]}")
        else:
            print(f"  ⚠️ no SMILES column in {herb_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
