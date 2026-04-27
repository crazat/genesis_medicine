"""PoseBusters v3 — fix LIG1 4-char filter + chain-B ligand extraction.

v2 bug: `len(res.name) <= 3` excluded Boltz-2's "LIG1" (4 chars). 0/300 pass.
v3 fix: explicit AA/NA whitelist + chain B ligand extraction.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
TMP = OUT / "posebusters_tmp_v3"
TMP.mkdir(parents=True, exist_ok=True)

AA_RES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
    "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
    "MSE", "SEC", "PYL", "HOH", "WAT", "DA", "DC", "DG", "DT", "DU",
    "A", "C", "G", "T", "U",
}


def extract_and_validate(args):
    target, compound, cif_path = args
    try:
        import gemmi
        from rdkit import Chem
        from posebusters import PoseBusters

        st = gemmi.read_structure(str(cif_path))
        st.setup_entities()

        receptor_pdb = TMP / f"{target}__{compound}__rec.pdb"
        lig_pdb = TMP / f"{target}__{compound}__lig.pdb"
        ligand_sdf = TMP / f"{target}__{compound}__lig.sdf"

        # Build protein-only structure (chain A or whatever chain has only AA residues)
        protein_st = gemmi.Structure()
        protein_st.cell = st.cell
        protein_st.spacegroup_hm = st.spacegroup_hm
        new_model = gemmi.Model("1")
        ligand_residues = []

        for model in st:
            for chain in model:
                aa_count = sum(1 for r in chain if r.name in AA_RES)
                lig_count = sum(1 for r in chain if r.name not in AA_RES)
                if aa_count >= lig_count:
                    new_chain = gemmi.Chain(chain.name)
                    for res in chain:
                        if res.name in AA_RES:
                            new_chain.add_residue(res)
                    if len(new_chain) > 0:
                        new_model.add_chain(new_chain)
                else:
                    for res in chain:
                        if res.name not in AA_RES:
                            ligand_residues.append(res)
            break
        protein_st.add_model(new_model)
        protein_st.write_pdb(str(receptor_pdb))

        if not ligand_residues:
            return {"target": target, "compound": compound,
                    "passed": False, "error": "no ligand chain found"}

        lig_st = gemmi.Structure()
        lig_st.cell = st.cell
        lig_model = gemmi.Model("1")
        lig_chain = gemmi.Chain("L")
        for r in ligand_residues:
            lig_chain.add_residue(r)
        lig_model.add_chain(lig_chain)
        lig_st.add_model(lig_model)
        lig_st.write_pdb(str(lig_pdb))

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

        buster = PoseBusters(config="dock")
        df = buster.bust(mol_pred=[str(ligand_sdf)],
                          mol_cond=str(receptor_pdb))

        n_checks = len([c for c in df.columns
                         if df[c].dtype == bool])
        bool_cols = [c for c in df.columns if df[c].dtype == bool]
        n_passed = int(sum(df.iloc[0][c] for c in bool_cols))
        passed = bool(all(df.iloc[0][c] for c in bool_cols))

        out = {"target": target, "compound": compound,
                "passed": passed, "n_checks": n_checks, "n_passed": n_passed}
        for c in bool_cols:
            out[c] = bool(df.iloc[0][c])
        return out
    except Exception as e:
        return {"target": target, "compound": compound,
                "passed": False, "error": str(e)[:200]}


def main():
    print("=" * 72)
    print("PoseBusters v3 — fixed LIG1 filter + chain-based extraction")
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
    df.to_csv(OUT / "posebusters_validation_v3.csv", index=False)
    print(f"\n✅ posebusters_validation_v3.csv ({len(df)} rows)")

    if "passed" in df.columns:
        summary = df.groupby("target")["passed"].agg(
            ["count", "sum", "mean"]).rename(columns={"sum": "n_passed",
                                                        "mean": "pass_rate"})
        summary.to_csv(OUT / "posebusters_summary_v3.csv")
        print("\n[Pass rate per target — v3]")
        print(summary.round(3).to_string())

        overall = df["passed"].mean()
        print(f"\nOverall: {overall:.1%} ({df['passed'].sum()}/{len(df)})")

        # Error mode breakdown
        if "error" in df.columns:
            err = df["error"].fillna("OK").value_counts().head(10)
            print("\n[Error mode breakdown]")
            print(err.to_string())


if __name__ == "__main__":
    sys.exit(main())
