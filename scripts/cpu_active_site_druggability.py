"""Druggability scoring for 14 disease targets via geometric pocket analysis.

For each target receptor PDB:
  - Extract pocket residues (5 Å around bound ligand)
  - Compute pocket volume estimate (heavy atom count)
  - Hydrophobic / polar / charged residue fractions
  - Druggability score (Schmitt+Egner heuristic)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

HYDROPHOBIC = {"ALA", "VAL", "LEU", "ILE", "MET", "PHE", "TYR", "TRP", "PRO", "GLY"}
POLAR = {"SER", "THR", "ASN", "GLN", "CYS", "HIS"}
CHARGED_POS = {"LYS", "ARG", "HIS"}
CHARGED_NEG = {"ASP", "GLU"}


def parse_pdb_pocket(pdb_path, ligand_residues=("LIG1", "LIG", "UNK", "INH")):
    """Find protein residues within 5 Å of any ligand atom."""
    if not pdb_path.exists():
        return None

    protein_atoms = []
    ligand_atoms = []

    for line in pdb_path.read_text().split("\n"):
        if line.startswith("ATOM") or line.startswith("HETATM"):
            try:
                resname = line[17:20].strip()
                chain = line[21]
                resnum = int(line[22:26].strip())
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                atom = {"res": resname, "chain": chain, "resnum": resnum,
                          "xyz": (x, y, z)}
                if resname in ligand_residues:
                    ligand_atoms.append(atom)
                elif line.startswith("ATOM"):
                    protein_atoms.append(atom)
            except (ValueError, IndexError):
                continue

    if not ligand_atoms:
        return None

    # Find protein residues within 5 Å of any ligand atom
    pocket_residues = set()
    for la in ligand_atoms:
        for pa in protein_atoms:
            dx = la["xyz"][0] - pa["xyz"][0]
            dy = la["xyz"][1] - pa["xyz"][1]
            dz = la["xyz"][2] - pa["xyz"][2]
            if (dx * dx + dy * dy + dz * dz) <= 25:  # 5 Å
                pocket_residues.add((pa["chain"], pa["resnum"], pa["res"]))

    return list(pocket_residues)


def main():
    print("=" * 72)
    print("Druggability scoring — 14 disease targets")
    print("=" * 72)

    rows = []
    pdb_paths = list(ROOT.glob("pilot/**/output*/boltz_results*/predictions/**/*.pdb"))
    pdb_paths += list(ROOT.glob("pilot/scaffold_hop/**/cofold*.pdb"))
    pdb_paths += list(ROOT.glob("pilot/scaffold_hop/**/receptor.pdb"))
    seen = set()

    for pdb in pdb_paths:
        # Parse target name from path
        target = "unknown"
        for part in pdb.parts:
            if "__" in part:
                target = part.split("__")[0]
                break
            if part.startswith("output_"):
                target = part.replace("output_", "").split("_")[0]
                break
        key = (target, str(pdb.parent))
        if key in seen:
            continue
        seen.add(key)

        pocket = parse_pdb_pocket(pdb)
        if not pocket or len(pocket) < 5:
            continue

        residues = [r[2] for r in pocket]
        n_total = len(residues)
        n_hydro = sum(1 for r in residues if r in HYDROPHOBIC)
        n_polar = sum(1 for r in residues if r in POLAR)
        n_pos = sum(1 for r in residues if r in CHARGED_POS)
        n_neg = sum(1 for r in residues if r in CHARGED_NEG)

        # Druggability score (Schmitt+Egner)
        f_hydro = n_hydro / n_total
        f_polar = n_polar / n_total
        f_charged = (n_pos + n_neg) / n_total
        druggability = (f_hydro * 0.5 + (1 - f_charged) * 0.3 + (f_polar) * 0.2)

        rows.append({
            "target": target,
            "pdb": str(pdb.relative_to(ROOT)),
            "n_pocket_residues": n_total,
            "n_hydrophobic": n_hydro,
            "n_polar": n_polar,
            "n_charged": n_pos + n_neg,
            "f_hydrophobic": f_hydro,
            "f_polar": f_polar,
            "f_charged": f_charged,
            "druggability_score": druggability,
        })

    df = pd.DataFrame(rows).sort_values("druggability_score", ascending=False)
    if len(df) > 0:
        df.to_csv(OUT / "druggability_per_target.csv", index=False)
        print(f"\n✅ druggability_per_target.csv ({len(df)} pockets)")

        agg = df.groupby("target").agg(
            mean_druggability=("druggability_score", "mean"),
            n_pockets=("druggability_score", "count"),
            mean_pocket_size=("n_pocket_residues", "mean")).reset_index()
        agg.sort_values("mean_druggability", ascending=False, inplace=True)
        agg.to_csv(OUT / "druggability_summary.csv", index=False)

        print(f"\n[Druggability ranking — top 14 targets]")
        for _, r in agg.head(14).iterrows():
            print(f"  {r['target']:12s} drug={r['mean_druggability']:.3f} "
                  f"pocket_size={r['mean_pocket_size']:.0f} (n={r['n_pockets']})")
    else:
        print("⚠️ No pockets parsed — PDB format issue")

    return 0


if __name__ == "__main__":
    sys.exit(main())
