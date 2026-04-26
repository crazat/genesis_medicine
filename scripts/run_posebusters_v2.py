"""PoseBusters validation v2 — proper CIF handling via OpenMM PDBxFile + SMILES template.

Fix for v1 'unreadable' bug: RDKit cannot read CIF directly. v2 uses:
    1. OpenMM PDBxFile to parse CIF (protein + ligand)
    2. Modeller to split protein vs ligand atoms
    3. PDB block writes for both
    4. AssignBondOrdersFromTemplate to recover ligand bond orders from SMILES
    5. PoseBusters bust(mol_pred=lig, mol_cond=protein.pdb)

SMILES sourced from:
    - pilot/scaffold_hop_round*/reinvent_inputs/round_N_top.csv
    - pilot/screen/<disease>/library_compounds.csv
    - data/sar_panel_phase2.csv
    - data/skin_compounds_curated.csv
    - pilot/chai1_ensemble/* (hard-coded in script)

Output: pilot/posebusters/posebusters_results_v2.csv with per-pose pass/fail
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
from openmm.app import PDBFile, PDBxFile, Modeller
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/posebusters"
OUT.mkdir(parents=True, exist_ok=True)

AA = {"ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS",
      "MET","PHE","PRO","SER","THR","TRP","TYR","VAL"}
NON_LIG = AA | {"HOH","WAT","NA","CL","K","MG","CA","ZN"}

# Hard-coded SMILES for Chai-1 ensemble pairs
CHAI1_SMILES = {
    "EMB-3":   "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
    "Oxyresveratrol": "Oc1ccc(/C=C/c2cc(O)c(O)cc2O)cc1",
    "Baicalein": "Oc1cc2oc(-c3ccccc3)cc(=O)c2c(O)c1O",
    "Emodin": "Cc1cc(O)c2C(=O)c3cc(O)cc(O)c3C(=O)c2c1",
}


def load_smiles_index() -> dict:
    """Build a {compound_name: smiles} dict from all known sources."""
    idx = dict(CHAI1_SMILES)

    # Disease screen libraries
    for d in ["pigmentation","alopecia","acne","photoaging"]:
        p = ROOT / f"data/screen_libraries/{d}_compounds.csv"
        if p.exists():
            df = pd.read_csv(p)
            if {"compound","smiles"}.issubset(df.columns):
                for _, r in df.iterrows():
                    idx[str(r["compound"]).strip()] = str(r["smiles"]).strip()

    # SAR panel
    p = ROOT / "data/sar_panel_phase2.csv"
    if p.exists():
        df = pd.read_csv(p)
        if {"compound","smiles"}.issubset(df.columns):
            for _, r in df.iterrows():
                idx[str(r["compound"]).strip()] = str(r["smiles"]).strip()

    # Skin compounds curated
    p = ROOT / "data/skin_compounds_curated.csv"
    if p.exists():
        df = pd.read_csv(p)
        if {"compound","smiles"}.issubset(df.columns):
            for _, r in df.iterrows():
                idx[str(r["compound"]).strip()] = str(r["smiles"]).strip()

    # Scaffold-hop round outputs (REINVENT-generated)
    for round_n in [1, 2, 3]:
        for csv in (ROOT / f"pilot/scaffold_hop_round{round_n}").rglob("*.csv"):
            try:
                df = pd.read_csv(csv)
                if {"compound","smiles"}.issubset(df.columns):
                    for _, r in df.iterrows():
                        idx[str(r["compound"]).strip()] = str(r["smiles"]).strip()
                elif "smiles" in df.columns:
                    for i, r in df.iterrows():
                        idx[f"r{round_n}_{i}"] = str(r["smiles"]).strip()
            except Exception:
                continue
    return idx


def cif_to_protein_lig(cif_path: Path) -> tuple[str | None, Chem.Mol | None]:
    """Read CIF, return (protein_pdb_path, ligand_mol_no_bonds)."""
    try:
        pdbx = PDBxFile(str(cif_path))
    except Exception as e:
        return None, None

    lig_atoms = []
    prot_atoms = []
    for atom in pdbx.topology.atoms():
        if atom.residue.name not in NON_LIG:
            lig_atoms.append(atom)
        elif atom.residue.name in AA:
            prot_atoms.append(atom)

    if not lig_atoms or not prot_atoms:
        return None, None

    # Write protein PDB
    with tempfile.NamedTemporaryFile("w", suffix=".pdb", delete=False) as tf:
        prot_pdb_path = Path(tf.name)
    mod_p = Modeller(pdbx.topology, pdbx.positions)
    mod_p.delete([a for a in mod_p.topology.atoms() if a not in prot_atoms])
    with open(prot_pdb_path, "w") as f:
        PDBFile.writeFile(mod_p.topology, mod_p.positions, f)

    # Write ligand PDB
    with tempfile.NamedTemporaryFile("w", suffix=".pdb", delete=False) as tf:
        lig_pdb_path = Path(tf.name)
    mod_l = Modeller(pdbx.topology, pdbx.positions)
    mod_l.delete([a for a in mod_l.topology.atoms() if a not in lig_atoms])
    with open(lig_pdb_path, "w") as f:
        PDBFile.writeFile(mod_l.topology, mod_l.positions, f)

    lig_mol = Chem.MolFromPDBFile(str(lig_pdb_path), sanitize=False, removeHs=False)
    lig_pdb_path.unlink(missing_ok=True)
    return str(prot_pdb_path), lig_mol


def run_one(cif_path: Path, target: str, compound: str, smiles_idx: dict) -> dict:
    smi = smiles_idx.get(compound)
    if not smi:
        return {"cif": str(cif_path), "target": target, "compound": compound,
                "status": "no_smiles_in_index", "n_pass": 0, "n_total": 0}

    prot_pdb, lig_mol = cif_to_protein_lig(cif_path)
    if prot_pdb is None or lig_mol is None:
        return {"cif": str(cif_path), "target": target, "compound": compound,
                "status": "cif_parse_failed", "n_pass": 0, "n_total": 0}

    template = Chem.MolFromSmiles(smi)
    if template is None:
        Path(prot_pdb).unlink(missing_ok=True)
        return {"cif": str(cif_path), "target": target, "compound": compound,
                "status": "smiles_invalid", "n_pass": 0, "n_total": 0}

    try:
        lig_typed = AllChem.AssignBondOrdersFromTemplate(template, lig_mol)
    except Exception as e:
        Path(prot_pdb).unlink(missing_ok=True)
        return {"cif": str(cif_path), "target": target, "compound": compound,
                "status": f"bond_assign_failed: {str(e)[:50]}", "n_pass": 0, "n_total": 0}

    try:
        from posebusters import PoseBusters
        pb = PoseBusters(config="dock")
        report = pb.bust(mol_pred=lig_typed, mol_cond=str(prot_pdb))
        # Boolean check columns (skip mol_pred_loaded etc.)
        check_cols = [c for c in report.columns
                       if c not in {"mol_pred_loaded","mol_cond_loaded"}]
        check_results = {c: bool(report[c].iloc[0]) for c in check_cols}
        n_pass = sum(check_results.values())
        n_total = len(check_results)
        return {"cif": str(cif_path), "target": target, "compound": compound,
                "status": "ok",
                "n_pass": n_pass, "n_total": n_total,
                **{f"pb_{c}": v for c, v in check_results.items()}}
    except Exception as e:
        return {"cif": str(cif_path), "target": target, "compound": compound,
                "status": f"posebusters_error: {str(e)[:60]}", "n_pass": 0, "n_total": 0}
    finally:
        Path(prot_pdb).unlink(missing_ok=True)


def discover_jobs() -> list[dict]:
    jobs = []

    # Boltz-2 outputs
    for src in [
        ROOT / "pilot/scaffold_hop/boltz_output",
        ROOT / "pilot/scaffold_hop_round2/boltz_output",
        ROOT / "pilot/scaffold_hop_round3/boltz_output",
        ROOT / "pilot/screen/pigmentation/boltz_output",
        ROOT / "pilot/screen/alopecia/boltz_output",
        ROOT / "pilot/screen/acne/boltz_output",
        ROOT / "pilot/screen/photoaging/boltz_output",
    ]:
        if not src.exists():
            continue
        for cif in src.rglob("*_model_0.cif"):
            stem = cif.stem.replace("_model_0", "")
            try:
                target_part, comp_part = stem.split("__", 1)
            except ValueError:
                continue
            jobs.append({"cif": cif, "target": target_part, "compound": comp_part})

    # Chai-1 ensemble
    chai_root = ROOT / "pilot/chai1_ensemble/chai1_runs"
    if chai_root.exists():
        for run in chai_root.iterdir():
            if not run.is_dir():
                continue
            try:
                target_part, comp_part = run.name.replace("_chai1", "").split("__", 1)
            except ValueError:
                continue
            for cif in run.glob("pred.model_idx_*.cif"):
                jobs.append({"cif": cif, "target": target_part, "compound": comp_part})

    return jobs


def main():
    print("=" * 72)
    print("PoseBusters v2 — OpenMM-based CIF parsing + SMILES template")
    print("=" * 72)
    smiles_idx = load_smiles_index()
    print(f"  SMILES index: {len(smiles_idx)} compounds")

    jobs = discover_jobs()
    print(f"  jobs: {len(jobs)}")

    rows = []
    for i, j in enumerate(jobs, 1):
        if i % 10 == 0:
            print(f"  [{i}/{len(jobs)}] {j['target']:8s} × {j['compound']:30s}")
        result = run_one(j["cif"], j["target"], j["compound"], smiles_idx)
        rows.append(result)

    df = pd.DataFrame(rows)
    out_csv = OUT / "posebusters_results_v2.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n✅ {out_csv}")

    # Summary
    ok = df[df["status"] == "ok"]
    print(f"\n=== SUMMARY ===")
    print(f"  total      : {len(df)}")
    print(f"  parsed OK  : {len(ok)}")
    print(f"  failed     : {len(df) - len(ok)}")
    if len(ok):
        full_pass = ok[ok["n_pass"] == ok["n_total"]]
        print(f"  full-pass  : {len(full_pass)}/{len(ok)} ({100*len(full_pass)/len(ok):.1f}%)")
        mean_pass = (ok["n_pass"] / ok["n_total"]).mean()
        print(f"  mean pass-rate: {mean_pass:.3f} ({mean_pass*ok['n_total'].iloc[0]:.1f}/{ok['n_total'].iloc[0]})")

    summary_path = OUT / "posebusters_v2_summary.json"
    summary_path.write_text(json.dumps({
        "n_total": len(df),
        "n_ok": len(ok),
        "n_full_pass": int(len(full_pass)) if len(ok) else 0,
        "mean_pass_rate": float((ok["n_pass"] / ok["n_total"]).mean()) if len(ok) else 0,
    }, indent=2))
    print(f"✅ {summary_path}")


if __name__ == "__main__":
    sys.exit(main())
