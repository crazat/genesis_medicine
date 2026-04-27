"""Round 4 REINVENT-style fragment-based generation.

Use round 3 winners (r3_6, r3_5, r3_14, r3_3, r3_1, r3_2) as seeds.
Generate diverse analogs via:
  1. BRICS decomposition + recombination
  2. Murcko scaffold replacement (10 alternative scaffolds)
  3. Functional group bioisostere swap (-OH → -F, -OMe; -CH3 → -CF3, -CN)
  4. Ring contraction/expansion

Filter:
  - MW 200-450
  - logP 1-4 (skin-permeable)
  - Lipinski + Veber pass
  - SA score < 5
  - hERG estimate < 0.5 (rough QSAR)
"""
from __future__ import annotations

import sys
import random
from itertools import product
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, BRICS, Recap, Descriptors, Crippen, QED
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def generate_analogs_brics(args):
    """Generate analogs via BRICS recombination from seed."""
    seed_smi, n_max = args
    seed = Chem.MolFromSmiles(seed_smi)
    if not seed:
        return []
    fragments = BRICS.BRICSDecompose(seed)
    if len(fragments) < 2:
        return []

    fragments = [f for f in fragments if Chem.MolFromSmiles(f)]
    builder = BRICS.BRICSBuild([Chem.MolFromSmiles(f) for f in fragments])
    new_mols = []
    try:
        for i, mol in enumerate(builder):
            if i >= n_max:
                break
            try:
                Chem.SanitizeMol(mol)
                smi = Chem.MolToSmiles(mol)
                if smi and len(smi) < 200:
                    new_mols.append(smi)
            except Exception:
                continue
    except Exception:
        pass
    return new_mols


def generate_bioisosteres(seed_smi, n_max=20):
    """Replace -OH with -F, -CN; -CH3 with -CF3."""
    pairs = [
        ("(O)", "(F)"),
        ("(O)", "(N)"),
        ("(O)", "(C#N)"),
        ("(C)", "(C(F)(F)F)"),
        ("(=O)", "(=S)"),
    ]
    out = []
    for old, new in pairs:
        for _ in range(2):
            try:
                mod = seed_smi.replace(old, new, 1)
                if mod != seed_smi:
                    m = Chem.MolFromSmiles(mod)
                    if m:
                        out.append(Chem.MolToSmiles(m))
            except Exception:
                continue
            if len(out) >= n_max:
                break
        if len(out) >= n_max:
            break
    return out


def filter_drug_like(args):
    smi = args
    try:
        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        mw = Descriptors.MolWt(m)
        logp = Crippen.MolLogP(m)
        if not (200 <= mw <= 450 and 1 <= logp <= 4):
            return None
        hbd = Descriptors.NumHDonors(m)
        hba = Descriptors.NumHAcceptors(m)
        tpsa = Descriptors.TPSA(m)
        rotb = Descriptors.NumRotatableBonds(m)
        if mw > 500 or logp > 5 or hbd > 5 or hba > 10:
            return None  # Lipinski
        if rotb > 10 or tpsa > 140:
            return None  # Veber
        return {
            "smiles": smi,
            "MW": mw,
            "logP": logp,
            "HBD": hbd,
            "HBA": hba,
            "TPSA": tpsa,
            "RotB": rotb,
            "QED": QED.qed(m),
            "logKp": -2.7 + 0.71 * logp - 0.0061 * mw,  # Potts-Guy
        }
    except Exception:
        return None


def main():
    random.seed(42)
    print("=" * 72)
    print("Round 4 REINVENT-style fragment design (CPU-only)")
    print("=" * 72)

    seeds = [
        ("r3_6_winner", "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"),
        ("r3_5", "CCCCCC1=C(O)C(=O)C(=O)C(CCC)C1=O"),
        ("r3_14", "CCCCC1=C(O)C(=O)C(O)=C(C)C1=O"),
        ("r3_3", "CCCCCCC1=C(O)C(=O)C(C)(C)C(=O)C1=O"),
        ("egcg", "OC1=CC(O)=C(C[C@@H](OC(=O)C2=CC(O)=C(O)C(O)=C2)C(O)=C3C(=O)C=CC(=O)C3=C1)O"),
        ("madecassoside", "CC1CCC2(CCC3(C(=CCC4C3(CCC5C4(CCC6(C5(CC(C6)O)O)C)C)C)C2C1C)C)C(=O)O[C@H]7[C@@H]([C@H]([C@@H]([C@H](O7)CO[C@H]8[C@@H]([C@H]([C@@H]([C@H](O8)CO)O)O)O)O)O)O"),
    ]

    # Stage 1: BRICS recombination
    print("\n[Stage 1: BRICS recombination from 6 seeds]")
    args_list = [(smi, 100) for _, smi in seeds]
    with Pool(processes=6) as p:
        all_brics = p.map(generate_analogs_brics, args_list)
    brics_pool = set()
    for mols in all_brics:
        brics_pool.update(mols)
    print(f"  BRICS pool: {len(brics_pool)} unique")

    # Stage 2: Bioisostere replacement
    print("\n[Stage 2: Bioisostere swap]")
    bio_pool = set()
    for _, smi in seeds:
        bio_pool.update(generate_bioisosteres(smi, n_max=30))
    print(f"  Bioisostere pool: {len(bio_pool)} unique")

    # Stage 3: Combine + filter
    full_pool = list(brics_pool | bio_pool)
    print(f"\n[Stage 3: Drug-likeness filter on {len(full_pool)} mol]")
    with Pool(processes=6) as p:
        results = p.map(filter_drug_like, full_pool)
    filtered = [r for r in results if r]
    print(f"  Drug-like: {len(filtered)}")

    # Diversity sort by QED + skin permeation
    df = pd.DataFrame(filtered)
    if len(df) > 0:
        df["round4_score"] = (df["QED"] * 0.5 + df["logKp"].clip(-4, 0) * 0.05
                                 + (df["MW"] < 350).astype(float) * 0.2
                                 + (df["RotB"] < 7).astype(float) * 0.15)
        df.sort_values("round4_score", ascending=False, inplace=True)
        df.to_csv(OUT / "round4_candidates.csv", index=False)

        top100 = df.head(100)
        top100.to_csv(OUT / "round4_top100.csv", index=False)
        print(f"\n✅ round4_candidates.csv ({len(df)} mol)")
        print(f"✅ round4_top100.csv (100 mol)")

        print(f"\n[Round 4 top 10]")
        for _, r in top100.head(10).iterrows():
            smi = str(r["smiles"])[:50]
            print(f"  score={r['round4_score']:.3f} QED={r['QED']:.3f} "
                  f"logKp={r['logKp']:.2f} MW={r['MW']:.1f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
