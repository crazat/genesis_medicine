"""Round 4 expanded — 200+ candidates with relaxed filter.

Original v1 was too strict (only 20 valid). v2:
  - MW 150-500 (vs 200-450)
  - logP 0-5 (vs 1-4)
  - More aggressive bioisostere library
  - Larger BRICS recombination depth
"""
from __future__ import annotations

import sys
import random
from itertools import product
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, BRICS, Descriptors, Crippen, QED

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def generate_brics_deep(args):
    seed_smi, n_max = args
    seed = Chem.MolFromSmiles(seed_smi)
    if not seed:
        return []
    fragments = list(BRICS.BRICSDecompose(seed))
    fragments = [f for f in fragments if Chem.MolFromSmiles(f)]
    if len(fragments) < 2:
        return []

    builder = BRICS.BRICSBuild(
        [Chem.MolFromSmiles(f) for f in fragments],
        seeds=[Chem.MolFromSmiles(seed_smi)])
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


def generate_bioisosteres_extensive(seed_smi, n_max=80):
    """Full bioisostere library."""
    pairs = [
        # OH replacements
        ("(O)", "(F)"), ("(O)", "(N)"), ("(O)", "(C#N)"), ("(O)", "(Cl)"),
        ("(O)", "(SC)"), ("(O)", "(C(F)(F)F)"), ("(O)", "(CN)"),
        # Methyl replacements
        ("(C)", "(C(F)(F)F)"), ("(C)", "(C#N)"), ("(C)", "(F)"),
        ("(C)", "(Cl)"),  ("(C)", "(O)"),
        # =O replacements
        ("(=O)", "(=S)"), ("(=O)", "(=NC)"),
        # Ring replacement attempts (parts only)
        ("c1ccccc1", "c1ccncc1"),  # benzene → pyridine
        ("c1ccccc1", "c1ccsc1"),   # benzene → thiophene
        # Chain modifications
        ("CC", "CO"), ("CC", "CN"), ("CCC", "CCO"),
    ]
    out = []
    seen = {seed_smi}
    for old, new in pairs:
        for offset in range(3):
            try:
                mod = seed_smi.replace(old, new, offset + 1)
                if mod != seed_smi and mod not in seen:
                    m = Chem.MolFromSmiles(mod)
                    if m:
                        canon = Chem.MolToSmiles(m)
                        if canon not in seen:
                            seen.add(canon)
                            out.append(canon)
            except Exception:
                continue
            if len(out) >= n_max:
                return out
    return out


def filter_relaxed(args):
    smi = args
    try:
        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        mw = Descriptors.MolWt(m)
        logp = Crippen.MolLogP(m)
        if not (150 <= mw <= 500):
            return None
        if not (0 <= logp <= 5):
            return None
        hbd = Descriptors.NumHDonors(m)
        hba = Descriptors.NumHAcceptors(m)
        tpsa = Descriptors.TPSA(m)
        rotb = Descriptors.NumRotatableBonds(m)
        if hbd > 5 or hba > 10:
            return None
        if rotb > 10 or tpsa > 140:
            return None
        return {
            "smiles": smi,
            "MW": mw,
            "logP": logp,
            "HBD": hbd,
            "HBA": hba,
            "TPSA": tpsa,
            "RotB": rotb,
            "QED": QED.qed(m),
            "logKp": -2.7 + 0.71 * logp - 0.0061 * mw,
        }
    except Exception:
        return None


def main():
    random.seed(42)
    print("=" * 72)
    print("Round 4 EXPANDED (relaxed filter, 200+ target)")
    print("=" * 72)

    seeds = [
        "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",  # r3_6 winner
        "CCCCCC1=C(O)C(=O)C(=O)C(CCC)C1=O",  # r3_5
        "CCCCC1=C(O)C(=O)C(O)=C(C)C1=O",  # r3_14
        "CCCCCCC1=C(O)C(=O)C(C)(C)C(=O)C1=O",  # r3_3
        "CCCCC1=C(O)C(=O)C(O)=C(CC)C1=O",  # additional
        "CCCCCC1=C(O)C(=O)C(=O)C(C)(C)C1=O",  # additional
        "OC1=CC(O)=C(CC(=O)O)C(O)=C1O",  # gallate-like
        "Cc1cc(O)c2c(c1)Oc1cc(O)cc(O)c1C2=O",  # flavone-like
        "Oc1ccc(/C=C/c2cc(O)cc(O)c2)cc1",  # resveratrol
        "OCc1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",  # multi-ranker winner!
    ]

    # Stage 1: BRICS deep
    print("\n[Stage 1: Deep BRICS recombination from 10 seeds]")
    args_list = [(smi, 200) for smi in seeds]
    with Pool(processes=10) as p:
        all_brics = p.map(generate_brics_deep, args_list)
    brics_pool = set()
    for mols in all_brics:
        brics_pool.update(mols)
    print(f"  BRICS pool: {len(brics_pool)} unique")

    # Stage 2: Extensive bioisostere
    print("\n[Stage 2: Extensive bioisostere swap]")
    bio_pool = set()
    for smi in seeds:
        bio_pool.update(generate_bioisosteres_extensive(smi, n_max=100))
    print(f"  Bioisostere pool: {len(bio_pool)} unique")

    # Combine + filter
    full_pool = list(brics_pool | bio_pool)
    print(f"\n[Stage 3: Relaxed drug-likeness filter on {len(full_pool)} mol]")
    with Pool(processes=12) as p:
        results = p.map(filter_relaxed, full_pool)
    filtered = [r for r in results if r]
    print(f"  Drug-like (relaxed): {len(filtered)}")

    if len(filtered) > 0:
        df = pd.DataFrame(filtered)
        df["round4_score"] = (df["QED"] * 0.4
                                 + df["logKp"].clip(-4, 0) / -4 * 0.2
                                 + (df["MW"] < 350).astype(float) * 0.2
                                 + (df["RotB"] < 7).astype(float) * 0.2)
        df.sort_values("round4_score", ascending=False, inplace=True)
        df.drop_duplicates("smiles", inplace=True)
        df.to_csv(OUT / "round4_expanded.csv", index=False)
        print(f"\n✅ round4_expanded.csv ({len(df)} mol)")

        df.head(200).to_csv(OUT / "round4_top200.csv", index=False)
        print(f"✅ round4_top200.csv (top 200)")

        print(f"\n[Round 4 expanded top 10]")
        for _, r in df.head(10).iterrows():
            smi = str(r["smiles"])[:60]
            print(f"  score={r['round4_score']:.3f} QED={r['QED']:.3f} "
                  f"MW={r['MW']:.0f} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
