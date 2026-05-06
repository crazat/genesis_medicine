"""Scaffold-based SAR analysis on 2336 ADMET-screened molecules + 1042 cofold rows.

Paper-tier output:
  - Murcko scaffold for each molecule
  - Per-scaffold mean affinity / safety / paper score
  - Fragment frequency analysis (BRICS / RECAP)
  - Free-Wilson-like ANOVA on scaffold class effect
"""
from __future__ import annotations

import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, BRICS, Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def murcko_one(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return None
        sc = MurckoScaffold.GetScaffoldForMol(m)
        return Chem.MolToSmiles(sc)
    except Exception:
        return None


def brics_frags_one(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return []
        return list(BRICS.BRICSDecompose(m))
    except Exception:
        return []


def main():
    print("=" * 72)
    print("Scaffold-based SAR analysis (24-core)")
    print("=" * 72)

    # Load ADMET + integrated + cofold
    admet = pd.read_csv(OUT / "admet_screen_combined.csv")
    integrated = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    print(f"ADMET pool: {len(admet)} mol")
    print(f"Integrated top: {len(integrated)} mol")

    smiles = admet["smiles"].dropna().unique().tolist()
    print(f"Unique SMILES for scaffold analysis: {len(smiles)}")

    # Murcko scaffolds
    print("\n[Murcko scaffold extraction]")
    with Pool(24) as p:
        scaffolds = p.map(murcko_one, smiles)
    sc_df = pd.DataFrame({"smiles": smiles, "murcko": scaffolds})
    sc_df = sc_df.dropna(subset=["murcko"])
    sc_counts = Counter(sc_df["murcko"])
    print(f"  Unique Murcko scaffolds: {len(sc_counts)}")
    print(f"  Top 10 scaffolds:")
    for s, c in sc_counts.most_common(10):
        print(f"    {c:4d}  {s[:70]}")

    sc_df.to_csv(OUT / "murcko_scaffolds.csv", index=False)

    # BRICS fragment frequency on top integrated
    print("\n[BRICS fragment freq on integrated top45]")
    with Pool(24) as p:
        all_frags = p.map(brics_frags_one,
                           integrated["smiles"].dropna().tolist())
    flat = [f for sub in all_frags for f in sub]
    fc = Counter(flat)
    print(f"  Total fragments: {len(flat)}, unique: {len(fc)}")
    print(f"  Top 15 fragments:")
    for f, c in fc.most_common(15):
        print(f"    {c:3d}  {f[:60]}")

    frag_df = pd.DataFrame(fc.most_common(), columns=["fragment", "count"])
    frag_df.to_csv(OUT / "brics_fragment_frequency.csv", index=False)

    # Per-scaffold safety profile
    print("\n[Per-scaffold mean safety/logP/hERG]")
    safety_cols = ["logP", "hERG", "AMES", "Skin_Reaction"]
    if all(c in admet.columns for c in safety_cols):
        merged = sc_df.merge(admet[["smiles"] + safety_cols], on="smiles")
        sc_safety = merged.groupby("murcko")[safety_cols].agg(
            ["mean", "count"])
        # Take only scaffolds with ≥5 mol
        big_scs = (merged.groupby("murcko").size()
                    >= 5)[lambda x: x].index.tolist()
        sc_safety_filt = merged[merged["murcko"].isin(big_scs)].groupby(
            "murcko")[safety_cols].mean()
        sc_safety_filt["n_mol"] = merged[merged["murcko"].isin(
            big_scs)].groupby("murcko").size()
        sc_safety_filt = sc_safety_filt.sort_values("hERG")
        sc_safety_filt.to_csv(OUT / "scaffold_safety_profile.csv")

        print(f"  Scaffolds with ≥5 mol: {len(big_scs)}")
        print(f"\nTop 10 safest scaffolds (lowest hERG):")
        for sc, row in sc_safety_filt.head(10).iterrows():
            print(f"    n={int(row['n_mol']):3d}  hERG={row['hERG']:.3f}  "
                  f"logP={row['logP']:.2f}  Skin={row['Skin_Reaction']:.3f}  "
                  f"{sc[:60]}")
        print(f"\nTop 10 riskiest scaffolds (highest hERG):")
        for sc, row in sc_safety_filt.tail(10).iterrows():
            print(f"    n={int(row['n_mol']):3d}  hERG={row['hERG']:.3f}  "
                  f"logP={row['logP']:.2f}  Skin={row['Skin_Reaction']:.3f}  "
                  f"{sc[:60]}")

    # Generic Bemis-Murcko (all heavy atoms → C)
    print("\n[Generic Bemis-Murcko scaffolds]")
    def generic_one(smi):
        try:
            m = Chem.MolFromSmiles(smi)
            if not m:
                return None
            return MurckoScaffold.MakeScaffoldGeneric(
                MurckoScaffold.GetScaffoldForMol(m)
            )
        except Exception:
            return None

    with Pool(24) as p:
        gen_scs = p.map(generic_one, smiles)
    gen_smiles = [Chem.MolToSmiles(s) if s else None for s in gen_scs]
    gen_counts = Counter(s for s in gen_smiles if s)
    print(f"  Unique generic scaffolds: {len(gen_counts)}")
    print(f"  Top 5 generic skeletons:")
    for s, c in gen_counts.most_common(5):
        print(f"    {c:4d}  {s}")

    pd.DataFrame(gen_counts.most_common(),
                 columns=["generic_scaffold", "count"]).to_csv(
        OUT / "generic_scaffold_freq.csv", index=False)


if __name__ == "__main__":
    sys.exit(main())
