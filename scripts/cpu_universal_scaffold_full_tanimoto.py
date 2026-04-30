"""Full Tanimoto similarity scan: 5 universal scaffold leaders vs ALL natural-product DBs.

Sources scanned:
- data/skin_compounds_curated.csv (102 Korean herbal)
- pilot/cpu_meaningful/all_boltz2_affinity_consolidated*.csv (R5+ cofold pool)
- pilot/cpu_meaningful/bayesian_v10_round14_candidates.csv (R14 pool)
- pilot/cpu_meaningful/r15_brics_candidates.csv (if exists)

Output: pilot/universal_scaffold_admet/full_tanimoto_top30.csv (top 30 per leader)
"""
from __future__ import annotations
import sys
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/universal_scaffold_admet"
OUT.mkdir(parents=True, exist_ok=True)

LEADERS = [
    ("R12_4",  "OCC1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R12_11", "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"),
    ("R12_23", "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R14_5",  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"),
    ("R13_13", "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1"),
]

SOURCES = [
    ("korean_herbal", "data/skin_compounds_curated.csv", "smiles"),
    ("r5_cofold", "pilot/cpu_meaningful/all_boltz2_affinity_consolidated_r5.csv", "smiles"),
    ("r14_candidates", "pilot/cpu_meaningful/bayesian_v10_round14_candidates.csv", "smiles"),
    ("r15_brics", "pilot/cpu_meaningful/r15_brics_candidates.csv", "derivative_smiles"),
]


def main():
    from rdkit import Chem
    from rdkit.Chem import AllChem, DataStructs

    pool = []
    for src, csv_rel, smi_col in SOURCES:
        p = ROOT / csv_rel
        if not p.exists():
            print(f"  ⚠️  missing {csv_rel}")
            continue
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"  ❌ {csv_rel}: {e}")
            continue
        if smi_col not in df.columns:
            for c in df.columns:
                if "smile" in c.lower():
                    smi_col = c; break
            else:
                print(f"  ⚠️  no smiles in {csv_rel}")
                continue
        for idx, row in df.iterrows():
            s = row.get(smi_col)
            if pd.notna(s) and isinstance(s, str):
                pool.append({"src": src, "smiles": s, "row_idx": idx,
                              "name": row.get("name") or row.get("herb_name") or row.get("source") or "?"})
        print(f"  ✅ {src}: {len(df)} loaded")

    print(f"\nTotal pool: {len(pool)} compounds")

    # Compute fingerprints
    print("Computing fingerprints...")
    pool_fps = []
    valid_pool = []
    for item in pool:
        m = Chem.MolFromSmiles(item["smiles"])
        if m is None:
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
        pool_fps.append(fp)
        valid_pool.append(item)
    print(f"  {len(valid_pool)} valid molecules with fingerprints")

    # For each leader, compute Tanimoto vs pool, keep top 30
    rows = []
    for name, smi in LEADERS:
        m = Chem.MolFromSmiles(smi)
        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
        sims = []
        for i, pfp in enumerate(pool_fps):
            t = DataStructs.TanimotoSimilarity(fp, pfp)
            sims.append((i, t))
        sims.sort(key=lambda x: -x[1])
        for rank, (idx, t) in enumerate(sims[:30], 1):
            item = valid_pool[idx]
            rows.append({
                "leader": name, "rank": rank, "tanimoto": round(t, 3),
                "src": item["src"], "match_smiles": item["smiles"],
                "match_name": item["name"], "row_idx": item["row_idx"],
            })
        print(f"  ✅ {name}: top-1={sims[0][1]:.3f} ({valid_pool[sims[0][0]]['src']}: {valid_pool[sims[0][0]]['name']})")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "full_tanimoto_top30.csv", index=False)
    print(f"\nSaved {OUT/'full_tanimoto_top30.csv'} ({len(df)} rows)")
    print("\nTop-1 per leader (combined sources):")
    top1 = df[df['rank'] == 1][['leader', 'tanimoto', 'src', 'match_name']]
    print(top1.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
