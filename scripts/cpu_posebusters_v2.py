"""PoseBusters v2: extract ligand SDF + receptor PDB from Boltz-2 CIF and validate."""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
TMP = OUT / "posebusters_tmp"
TMP.mkdir(parents=True, exist_ok=True)


def extract_and_validate(args):
    target, compound, cif_path = args
    try:
        import gemmi
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from posebusters import PoseBusters

        # Parse CIF
        st = gemmi.read_structure(str(cif_path))
        st.setup_entities()

        # Output paths (per-process to avoid race conditions)
        ligand_sdf = TMP / f"{target}__{compound}__lig.sdf"
        receptor_pdb = TMP / f"{target}__{compound}__rec.pdb"

        # Write protein-only PDB (chain A typically)
        protein_st = gemmi.Structure()
        protein_st.cell = st.cell
        protein_st.spacegroup_hm = st.spacegroup_hm
        new_model = gemmi.Model("1")
        ligand_residues = []
        for model in st:
            for chain in model:
                new_chain = gemmi.Chain(chain.name)
                for res in chain:
                    if res.entity_type == gemmi.EntityType.Polymer:
                        new_chain.add_residue(res)
                    elif len(res.name) <= 3 and res.name not in ("HOH", "WAT"):
                        # Probably ligand — keep for SDF extraction
                        ligand_residues.append(res)
                if len(new_chain) > 0:
                    new_model.add_chain(new_chain)
            break
        protein_st.add_model(new_model)
        protein_st.write_pdb(str(receptor_pdb))

        # Convert ligand to SDF via RDKit (read protein-stripped CIF as ligand-only)
        # Easier path: use gemmi to write ligand block as PDB, then RDKit
        if not ligand_residues:
            return {"target": target, "compound": compound,
                    "passed": False, "error": "no ligand found"}

        lig_st = gemmi.Structure()
        lig_st.cell = st.cell
        lig_model = gemmi.Model("1")
        lig_chain = gemmi.Chain("L")
        for r in ligand_residues:
            lig_chain.add_residue(r)
        lig_model.add_chain(lig_chain)
        lig_st.add_model(lig_model)
        lig_pdb = TMP / f"{target}__{compound}__lig.pdb"
        lig_st.write_pdb(str(lig_pdb))

        # RDKit read PDB → write SDF
        mol = Chem.MolFromPDBFile(str(lig_pdb), removeHs=False, sanitize=False)
        if mol is None:
            return {"target": target, "compound": compound,
                    "passed": False, "error": "rdkit pdb→mol failed"}
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            pass
        writer = Chem.SDWriter(str(ligand_sdf))
        writer.write(mol)
        writer.close()

        # PoseBusters
        buster = PoseBusters(config="dock")
        df = buster.bust(mol_pred=[str(ligand_sdf)],
                          mol_cond=str(receptor_pdb))

        n_checks = len(df.columns)
        n_passed = int(df.iloc[0].sum())
        passed = bool(df.iloc[0].all())

        return {
            "target": target,
            "compound": compound,
            "passed": passed,
            "n_checks": n_checks,
            "n_passed": n_passed,
            **{c: bool(df.iloc[0][c]) for c in df.columns},
        }
    except Exception as e:
        return {
            "target": target,
            "compound": compound,
            "passed": False,
            "error": str(e)[:200],
        }


def main():
    print("=" * 72)
    print("PoseBusters v2 — proper ligand/receptor extraction")
    print("=" * 72)

    args_list = []
    for cif in ROOT.glob("pilot/**/boltz_results_*/predictions/**/*.cif"):
        if "affinity" in cif.name.lower():
            continue
        parts = cif.stem.split("__")
        if len(parts) < 2:
            continue
        target = parts[0]
        compound = parts[-1].replace("_model_0", "")
        args_list.append((target, compound, cif))

    args_list = sorted(set(args_list))[:300]
    print(f"PoseBusters tasks: {len(args_list)}")

    with Pool(processes=12) as pool:
        results = pool.map(extract_and_validate, args_list)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "posebusters_validation_v2.csv", index=False)
    print(f"\n✅ posebusters_validation_v2.csv ({len(df)} rows)")

    summary = df.groupby("target")["passed"].agg(
        ["count", "sum", "mean"]).rename(columns={"sum": "n_passed",
                                                    "mean": "pass_rate"})
    summary.to_csv(OUT / "posebusters_summary_v2.csv")
    print("\n[Pass rate per target — v2]")
    print(summary.round(3).to_string())

    overall = df["passed"].mean()
    print(f"\nOverall: {overall:.1%} ({df['passed'].sum()}/{len(df)})")


if __name__ == "__main__":
    sys.exit(main())
