"""Murcko + generic scaffold tree analysis — chemical diversity quantification.

For 2336 mol pool:
  - Murcko scaffold (preserves H-count)
  - Generic scaffold (Murcko + atom→C, bond→single)
  - Bemis-Murcko atomic count
  - Scaffold-to-mol mapping
  - Top scaffold representatives
"""
from __future__ import annotations

import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def get_scaffolds(smi):
    try:
        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return None
        murcko = MurckoScaffold.GetScaffoldForMol(m)
        murcko_smi = Chem.MolToSmiles(murcko) if murcko else ""
        generic = MurckoScaffold.MakeScaffoldGeneric(murcko) if murcko else None
        generic_smi = Chem.MolToSmiles(generic) if generic else ""
        return {
            "smiles": smi,
            "murcko": murcko_smi,
            "generic": generic_smi,
            "n_atoms": m.GetNumAtoms(),
            "n_rings": Chem.rdMolDescriptors.CalcNumRings(m),
        }
    except Exception:
        return None


def main():
    print("=" * 72)
    print("Murcko + generic scaffold diversity")
    print("=" * 72)

    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    print(f"Pool: {len(drug)}")

    with Pool(processes=12) as p:
        results = p.map(get_scaffolds, drug["smiles"].tolist())
    valid = [r for r in results if r]
    df = pd.DataFrame(valid)
    df.to_csv(OUT / "scaffold_full_analysis.csv", index=False)
    print(f"Valid: {len(df)}")

    # Murcko diversity
    murcko_counts = Counter(df["murcko"].tolist())
    print(f"\nUnique Murcko scaffolds: {len(murcko_counts)}")
    print(f"Top 15 Murcko scaffolds:")
    for sc, cnt in murcko_counts.most_common(15):
        print(f"  {cnt:4d}× {sc[:60]}")

    # Generic diversity
    generic_counts = Counter(df["generic"].tolist())
    print(f"\nUnique generic scaffolds: {len(generic_counts)}")
    print(f"Top 10 generic scaffolds:")
    for sc, cnt in generic_counts.most_common(10):
        print(f"  {cnt:4d}× {sc[:60]}")

    # Save scaffold counts
    pd.DataFrame(murcko_counts.most_common(50),
                  columns=["scaffold", "count"]).to_csv(
        OUT / "scaffold_murcko_top50.csv", index=False)
    pd.DataFrame(generic_counts.most_common(30),
                  columns=["scaffold", "count"]).to_csv(
        OUT / "scaffold_generic_top30.csv", index=False)

    # Diversity metrics
    n_total = len(df)
    div_murcko = len(murcko_counts) / n_total
    div_generic = len(generic_counts) / n_total
    print(f"\n[Scaffold diversity index]")
    print(f"  Murcko diversity: {div_murcko:.3f} ({len(murcko_counts)}/{n_total})")
    print(f"  Generic diversity: {div_generic:.3f}")
    print(f"  Top-1 Murcko cluster fraction: {murcko_counts.most_common(1)[0][1]/n_total:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
