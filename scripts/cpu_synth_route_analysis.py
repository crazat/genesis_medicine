"""Synthesizability + retrosynthetic route depth estimation.

Per top 50 candidate:
  - SA score (already computed)
  - RingCount + Stereocenter count
  - Estimated synthesis steps (heuristic from atom complexity)
  - Available starting material commercial estimate (Murcko + ring count)
  - Retrosynthetic accessibility class (E_easy / M_medium / H_hard)
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

import rdkit
SA_PATH = Path(rdkit.__file__).parent / "Contrib" / "SA_Score"
sys.path.insert(0, str(SA_PATH))
import sascorer


def analyze_synth(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        n_rings = Descriptors.RingCount(m)
        n_stereo = rdMolDescriptors.CalcNumAtomStereoCenters(m)
        n_arom = Descriptors.NumAromaticRings(m)
        n_heavy = Descriptors.HeavyAtomCount(m)
        sa = sascorer.calculateScore(m)
        scaffold = MurckoScaffold.GetScaffoldForMol(m)
        scaffold_smi = Chem.MolToSmiles(scaffold) if scaffold else ""

        # Heuristic synthesis steps
        est_steps = 1 + n_rings + n_stereo + (n_arom // 2)

        # Class
        if sa < 3.5 and n_stereo < 3 and est_steps < 6:
            cls = "E_easy"
        elif sa < 4.5 and est_steps < 9:
            cls = "M_medium"
        else:
            cls = "H_hard"

        return {
            "smiles": smi,
            "scaffold": scaffold_smi,
            "n_rings": n_rings,
            "n_stereo": n_stereo,
            "n_aromatic": n_arom,
            "n_heavy_atoms": n_heavy,
            "sa_score": sa,
            "est_synth_steps": est_steps,
            "synth_class": cls,
        }
    except Exception:
        return None


def main():
    print("=" * 72)
    print("Synthesizability + retrosynthetic route analysis")
    print("=" * 72)

    # Load top 50 candidates from pareto + multi-ranker leaders + r3 winners
    sources = [
        ("pareto_top50.csv", 50),
        ("multi_ranker_leaders.csv", 20),
        ("round4_top100.csv", 100),
    ]
    all_smis = set()
    for fn, lim in sources:
        path = OUT / fn
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "smiles" in df.columns:
            all_smis.update(df["smiles"].head(lim).dropna().tolist())

    print(f"Total unique mol to analyze: {len(all_smis)}")

    with Pool(processes=6) as p:
        results = p.map(analyze_synth, list(all_smis))
    valid = [r for r in results if r]
    df = pd.DataFrame(valid)
    df.sort_values("sa_score", inplace=True)
    df.to_csv(OUT / "synth_route_analysis.csv", index=False)

    print(f"\n✅ synth_route_analysis.csv ({len(df)} mol)")

    # Class distribution
    print(f"\n[Synthesis class distribution]")
    cls_counts = df["synth_class"].value_counts()
    for cls, n in cls_counts.items():
        print(f"  {cls}: {n}")

    # Top 10 by easiest synthesis
    easy = df[df["synth_class"] == "E_easy"].head(10)
    print(f"\n[Top 10 easiest synthesis (SA < 3.5, < 6 steps)]")
    for _, r in easy.iterrows():
        smi = str(r["smiles"])[:50]
        print(f"  SA={r['sa_score']:.2f} steps={r['est_synth_steps']} | {smi}")

    # SA distribution
    print(f"\n[SA score distribution]")
    print(f"  Mean: {df['sa_score'].mean():.2f}")
    print(f"  Min: {df['sa_score'].min():.2f}")
    print(f"  Max: {df['sa_score'].max():.2f}")
    print(f"  < 3.5 (drug-like easy): {(df['sa_score'] < 3.5).sum()}")
    print(f"  >= 5 (synth challenge): {(df['sa_score'] >= 5).sum()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
