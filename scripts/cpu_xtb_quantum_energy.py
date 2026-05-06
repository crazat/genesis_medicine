"""GFN2-xTB quantum single-point energies on top integrated candidates +
ChEMBL extended + Korean herbals.

Paper-tier output: semi-empirical QM-grade energies for top hits — beyond
classical FF (MMFF), captures electronic effects on conformer stability.
Heavy CPU work via Pool(24).
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def xtb_one(args):
    idx, smi = args
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import AllChem
        from xtb.interface import Calculator, Param
        from xtb.libxtb import VERBOSITY_MUTED
        RDLogger.DisableLog("rdApp.*")

        m = Chem.MolFromSmiles(smi)
        if m is None:
            return {"idx": idx, "smi": smi, "error": "parse"}
        m = Chem.AddHs(m)
        cid = AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True)
        if cid < 0:
            return {"idx": idx, "smi": smi, "error": "embed"}
        try:
            AllChem.MMFFOptimizeMolecule(m, maxIters=500)
        except Exception:
            pass

        # Extract atomic numbers + coords
        atoms = np.array([a.GetAtomicNum() for a in m.GetAtoms()])
        conf = m.GetConformer()
        xyz = np.array([[conf.GetAtomPosition(i).x,
                          conf.GetAtomPosition(i).y,
                          conf.GetAtomPosition(i).z]
                          for i in range(m.GetNumAtoms())])
        # Convert Å → Bohr (xtb uses Bohr)
        xyz_bohr = xyz * 1.8897259886

        calc = Calculator(Param.GFN2xTB, atoms, xyz_bohr)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        return {
            "idx": idx,
            "smi": smi,
            "energy_eh": float(res.get_energy()),    # Hartree
            "n_atoms": int(m.GetNumAtoms()),
            "homo_lumo_gap_eh": None,    # could extract from orbital energies
        }
    except Exception as e:
        return {"idx": idx, "smi": smi, "error": str(e)[:100]}


def main():
    print("=" * 72)
    print("GFN2-xTB quantum single-point energies (24-core)")
    print("=" * 72)

    # Inputs: top integrated 45 + Korean herbals 102
    integ = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    herbal = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")

    smi_list = []
    for _, r in integ.dropna(subset=["smiles"]).iterrows():
        smi_list.append(("integ_" + str(r["compound"]), r["smiles"]))
    for _, r in herbal.dropna(subset=["smiles"]).iterrows():
        smi_list.append(("herbal_" + str(r["name"]), r["smiles"]))

    # Dedupe by smiles
    seen = set()
    args_list = []
    for tag, s in smi_list:
        if s not in seen:
            seen.add(s)
            args_list.append((tag, s))
    print(f"Unique mol for xTB: {len(args_list)}")

    with Pool(processes=24) as pool:
        results = pool.map(xtb_one, args_list)

    df = pd.DataFrame(results)
    if "energy_eh" not in df.columns:
        df["energy_eh"] = np.nan
    df_full = df.copy()
    df_full.to_csv(OUT / "xtb_quantum_all.csv", index=False)
    df = df[df["energy_eh"].notna()]
    df["energy_kcal_per_mol"] = df["energy_eh"] * 627.5095
    df["energy_per_atom_kcal"] = df["energy_kcal_per_mol"] / df["n_atoms"]

    df.to_csv(OUT / "xtb_quantum_energies.csv", index=False)
    print(f"\n✅ xtb_quantum_energies.csv ({len(df)} successful)")
    print(f"  range: {df['energy_kcal_per_mol'].min():.0f} to "
          f"{df['energy_kcal_per_mol'].max():.0f} kcal/mol")
    print(f"  mean atoms: {df['n_atoms'].mean():.1f}")
    print(f"  energy/atom range: {df['energy_per_atom_kcal'].min():.1f} to "
          f"{df['energy_per_atom_kcal'].max():.1f} kcal/mol/atom")


if __name__ == "__main__":
    sys.exit(main())
