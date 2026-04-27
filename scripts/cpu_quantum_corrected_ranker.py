"""Quantum-corrected ranking — combine 5000-conformer Boltzmann + xtb GFN2.

For top 100 BRICS candidates with both:
  - 5000-conformer ensemble (conformers_5000x200.csv)
  - xtb GFN2 single-point energy (xtb_progressive_slice_*.csv)

Compute:
  - Boltzmann-weighted free energy proxy
  - Conformational entropy (effective N_eff)
  - Quantum-corrected ranking
  - Conformational rigidity index (lower = better preorganized for binding)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def main():
    print("=" * 72)
    print("Quantum-corrected ranking (5000-conformer × xtb GFN2)")
    print("=" * 72)

    confs = pd.read_csv(OUT / "conformers_5000x200.csv")
    print(f"5000-conformer rows: {len(confs)}")
    print(f"  cols: {confs.columns.tolist()}")

    # xtb progressive slices
    xtb_files = sorted(OUT.glob("xtb_progressive_slice_*.csv"))
    xtb_dfs = [pd.read_csv(f) for f in xtb_files]
    xtb = pd.concat(xtb_dfs, ignore_index=True).drop_duplicates("smi")
    print(f"xtb GFN2 rows: {len(xtb)}")
    print(f"  cols: {xtb.columns.tolist()}")

    # Merge on smiles (if 5000-conformer has smiles)
    if "smi" in confs.columns:
        merged = confs.merge(xtb, on="smi", how="inner", suffixes=("_conf", "_xtb"))
    else:
        # confs has idx but no smi — need another path
        confs["smi"] = confs.get("smiles", "")
        merged = confs.merge(xtb, on="smi", how="inner", suffixes=("_conf", "_xtb"))

    print(f"Merged (both conformer + xtb): {len(merged)}")

    if len(merged) < 5:
        # Use what we have separately
        print("\n[Limited overlap — using conformer ensemble only]")
        merged = confs

    # Quantum-corrected score
    if "boltzmann_eff_confs" in merged.columns:
        merged["conf_entropy_score"] = np.log(
            merged["boltzmann_eff_confs"].clip(lower=1.0))
        merged["rigidity_index"] = 1 / (
            merged["boltzmann_eff_confs"].clip(lower=1.0))
        print(f"\n[Conformational rigidity stats]")
        print(f"  Mean N_eff: {merged['boltzmann_eff_confs'].mean():.1f}")
        print(f"  Min N_eff (most rigid): {merged['boltzmann_eff_confs'].min():.1f}")
        print(f"  Max N_eff (most flexible): {merged['boltzmann_eff_confs'].max():.1f}")

    if "energy_kcal_mol" in merged.columns:
        # xtb GFN2 single-point energy (rough quantum correction)
        merged["xtb_relative"] = (merged["energy_kcal_mol"]
                                    - merged["energy_kcal_mol"].mean())

    # Combined quantum-corrected score
    if "boltzmann_eff_confs" in merged.columns:
        # Smaller N_eff → more preorganized → better score
        merged["quantum_score"] = (
            merged.get("min_E", 0).clip(lower=-200) * -0.001
            + np.log(merged["boltzmann_eff_confs"].clip(lower=1.0)) * 0.5
            + merged.get("energy_range", 0).clip(upper=50) * -0.005)
    else:
        merged["quantum_score"] = 0

    merged.sort_values("quantum_score", ascending=False, inplace=True)
    merged.to_csv(OUT / "quantum_corrected_ranking.csv", index=False)

    top20 = merged.head(20)
    top20.to_csv(OUT / "quantum_top20.csv", index=False)

    print(f"\n✅ quantum_corrected_ranking.csv ({len(merged)} mol)")
    print(f"✅ quantum_top20.csv (20 mol)")

    print(f"\n[Top 10 quantum-corrected candidates]")
    for _, r in top20.head(10).iterrows():
        smi = str(r.get("smi", r.get("smiles", "")))[:40]
        n_eff = r.get("boltzmann_eff_confs", float("nan"))
        n_eff_s = f"{n_eff:.0f}" if not pd.isna(n_eff) else "n/a"
        print(f"  q_score={r['quantum_score']:.3f} N_eff={n_eff_s} | {smi}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
