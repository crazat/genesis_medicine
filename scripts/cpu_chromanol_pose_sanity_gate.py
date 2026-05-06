"""Pose sanity gate for current R15/R16 chromanol Boltz-2 cofold outputs.

Purpose:
  - Add a PoseBusters/RDKit/OpenMM validation layer before manuscript claims.
  - Validate current chromanol cofold poses without launching GPU work.

Inputs:
  - pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv
  - pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv

Outputs:
  - pilot/cpu_meaningful/chromanol_pose_sanity_gate.csv
  - pilot/cpu_meaningful/chromanol_pose_sanity_gate_summary.json
  - pilot/cpu_meaningful/chromanol_pose_sanity_gate_summary.md

This script intentionally does not import TensorFlow/ADMET-AI and does not use
multiprocessing.Pool.
"""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
from openmm.app import Modeller, PDBFile, PDBxFile
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

AA = {
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "CYS",
    "GLN",
    "GLU",
    "GLY",
    "HIS",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except Exception:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def load_jobs() -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []

    r15_path = OUT / "r15_chromanol_cofold_14targets.csv"
    if r15_path.exists():
        r15 = pd.read_csv(r15_path)
        for _, row in r15.iterrows():
            prediction_dir = ROOT / str(row["prediction_dir"])
            job_id = prediction_dir.name
            jobs.append(
                {
                    "source": "r15_chromanol",
                    "job_id": job_id,
                    "target": str(row["target"]).lower(),
                    "compound": str(row.get("compound", "R15_chromanol")),
                    "smiles": str(row["smiles"]),
                    "affinity_probability_binary": safe_float(row.get("affinity_probability_binary")),
                    "confidence_score": safe_float(row.get("confidence_score")),
                    "complex_plddt": safe_float(row.get("complex_plddt")),
                    "cif": prediction_dir / f"{job_id}_model_0.cif",
                }
            )

    r16_path = OUT / "r16_chromanol_topical_cofold.csv"
    if r16_path.exists():
        r16 = pd.read_csv(r16_path)
        for _, row in r16.iterrows():
            prediction_dir = ROOT / str(row["prediction_dir"])
            job_id = str(row["job_id"])
            jobs.append(
                {
                    "source": "r16_chromanol_topical",
                    "job_id": job_id,
                    "target": str(row["target"]).lower(),
                    "compound": str(row.get("analog_id", job_id)),
                    "smiles": str(row["smiles"]),
                    "affinity_probability_binary": safe_float(row.get("affinity_probability_binary")),
                    "confidence_score": safe_float(row.get("confidence_score")),
                    "complex_plddt": safe_float(row.get("complex_plddt")),
                    "cif": prediction_dir / f"{job_id}_model_0.cif",
                    "logP": safe_float(row.get("logP")),
                    "QED": safe_float(row.get("QED")),
                    "gap_eV": safe_float(row.get("gap_eV")),
                }
            )

    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for job in jobs:
        key = (str(job["source"]), str(job["job_id"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)
    return deduped


def split_cif(cif_path: Path, workdir: Path) -> tuple[Path, Chem.Mol, int, int]:
    pdbx = PDBxFile(str(cif_path))
    lig_atoms = []
    prot_atoms = []
    for atom in pdbx.topology.atoms():
        if atom.residue.name == "LIG1":
            lig_atoms.append(atom)
        elif atom.residue.name in AA:
            prot_atoms.append(atom)

    if not lig_atoms:
        raise ValueError("no LIG1 atoms found")
    if not prot_atoms:
        raise ValueError("no protein atoms found")

    prot_path = workdir / "protein.pdb"
    prot_mod = Modeller(pdbx.topology, pdbx.positions)
    prot_mod.delete([atom for atom in prot_mod.topology.atoms() if atom not in prot_atoms])
    with prot_path.open("w") as handle:
        PDBFile.writeFile(prot_mod.topology, prot_mod.positions, handle)

    lig_path = workdir / "ligand.pdb"
    lig_mod = Modeller(pdbx.topology, pdbx.positions)
    lig_mod.delete([atom for atom in lig_mod.topology.atoms() if atom not in lig_atoms])
    with lig_path.open("w") as handle:
        PDBFile.writeFile(lig_mod.topology, lig_mod.positions, handle)

    lig_mol = Chem.MolFromPDBFile(str(lig_path), sanitize=False, removeHs=False)
    if lig_mol is None:
        raise ValueError("RDKit failed to read ligand PDB")

    return prot_path, lig_mol, len(prot_atoms), len(lig_atoms)


def run_posebusters(lig_mol: Chem.Mol, prot_path: Path) -> tuple[dict[str, bool], int, int, bool]:
    from posebusters import PoseBusters

    buster = PoseBusters(config="dock")
    report = buster.bust(mol_pred=lig_mol, mol_cond=str(prot_path), full_report=False)
    row = report.iloc[0]
    checks = {str(col): bool(row[col]) for col in report.columns}
    n_pass = sum(1 for value in checks.values() if value)
    n_total = len(checks)
    return checks, n_pass, n_total, n_pass == n_total


def classify_gate(status: str, checks: dict[str, bool], n_pass: int, n_total: int) -> tuple[str, str]:
    if status != "ok":
        return "fail", status
    failed = [key for key, value in checks.items() if not value]
    if not failed:
        return "pass", "all PoseBusters dock checks pass"

    pass_rate = n_pass / n_total if n_total else 0.0
    chemistry_prefixes = (
        "mol_pred_loaded",
        "mol_cond_loaded",
        "sanitization",
        "inchi_convertible",
        "all_atoms_connected",
        "no_radicals",
        "bond_lengths",
        "bond_angles",
        "internal_steric_clash",
    )
    has_chemistry_failure = any(key.startswith(chemistry_prefixes) for key in failed)
    if pass_rate >= 0.90 and not has_chemistry_failure:
        return "review", "raw cofold pose has protein-distance/overlap caveat; MD/minimized pose can still be usable"
    if pass_rate >= 0.90:
        return "review", "minor ligand-geometry caveat; inspect before manuscript claim"
    return "fail", "multiple pose sanity failures"


def validate_one(job: dict[str, Any]) -> dict[str, Any]:
    base = {
        "source": job["source"],
        "job_id": job["job_id"],
        "target": job["target"],
        "compound": job["compound"],
        "smiles": job["smiles"],
        "affinity_probability_binary": job.get("affinity_probability_binary"),
        "confidence_score": job.get("confidence_score"),
        "complex_plddt": job.get("complex_plddt"),
        "logP": job.get("logP"),
        "QED": job.get("QED"),
        "gap_eV": job.get("gap_eV"),
        "cif": rel(Path(job["cif"])),
    }
    cif_path = Path(job["cif"])
    if not cif_path.exists():
        return {**base, "status": "missing_cif", "pose_sanity_pass": False}

    template = Chem.MolFromSmiles(str(job["smiles"]))
    if template is None:
        return {**base, "status": "invalid_smiles", "pose_sanity_pass": False}

    with tempfile.TemporaryDirectory(prefix="chromanol_pose_gate_") as tmp:
        tmp_path = Path(tmp)
        try:
            prot_path, lig_mol, protein_atoms, ligand_atoms = split_cif(cif_path, tmp_path)
            typed_lig = AllChem.AssignBondOrdersFromTemplate(template, lig_mol)
            checks, n_pass, n_total, full_pass = run_posebusters(typed_lig, prot_path)
        except Exception as exc:
            return {
                **base,
                "status": f"error:{str(exc)[:160]}",
                "pose_sanity_pass": False,
                "n_posebusters_pass": 0,
                "n_posebusters_total": 0,
            }

    gate_status, gate_reason = classify_gate("ok", checks, n_pass, n_total)
    failed_checks = ";".join(key for key, value in checks.items() if not value)
    return {
        **base,
        "status": "ok",
        "pose_sanity_pass": full_pass,
        "gate_status": gate_status,
        "gate_reason": gate_reason,
        "failed_checks": failed_checks,
        "n_posebusters_pass": n_pass,
        "n_posebusters_total": n_total,
        "posebusters_pass_rate": round(n_pass / n_total, 4) if n_total else 0.0,
        "protein_atoms": protein_atoms,
        "ligand_atoms": ligand_atoms,
        **{f"pb_{key}": value for key, value in checks.items()},
    }


def write_summary(df: pd.DataFrame) -> None:
    ok = df[df["status"].eq("ok")].copy()
    full_pass = ok[ok["pose_sanity_pass"].eq(True)]
    gate_counts = (
        ok["gate_status"].value_counts().to_dict()
        if "gate_status" in ok.columns and len(ok)
        else {}
    )
    summary = {
        "rows": int(len(df)),
        "ok_rows": int(len(ok)),
        "full_pass_rows": int(len(full_pass)),
        "full_pass_rate": float(len(full_pass) / len(ok)) if len(ok) else 0.0,
        "gate_counts": {str(key): int(value) for key, value in gate_counts.items()},
        "by_source": {},
        "by_target": {},
    }
    if len(ok):
        for source, sub in ok.groupby("source"):
            summary["by_source"][source] = {
                "ok_rows": int(len(sub)),
                "full_pass_rows": int(sub["pose_sanity_pass"].sum()),
                "full_pass_rate": float(sub["pose_sanity_pass"].mean()),
                "gate_pass_rows": int(sub["gate_status"].eq("pass").sum()),
                "gate_review_rows": int(sub["gate_status"].eq("review").sum()),
                "gate_fail_rows": int(sub["gate_status"].eq("fail").sum()),
                "mean_posebusters_pass_rate": float(sub["posebusters_pass_rate"].mean()),
            }
        for target, sub in ok.groupby("target"):
            summary["by_target"][target] = {
                "ok_rows": int(len(sub)),
                "full_pass_rows": int(sub["pose_sanity_pass"].sum()),
                "full_pass_rate": float(sub["pose_sanity_pass"].mean()),
                "gate_pass_rows": int(sub["gate_status"].eq("pass").sum()),
                "gate_review_rows": int(sub["gate_status"].eq("review").sum()),
                "gate_fail_rows": int(sub["gate_status"].eq("fail").sum()),
                "mean_posebusters_pass_rate": float(sub["posebusters_pass_rate"].mean()),
            }

    (OUT / "chromanol_pose_sanity_gate_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Chromanol Pose Sanity Gate",
        "",
        "- scope: R15 chromanol 14-target cofold + R16 topical chromanol 18-pair cofold",
        "- method: OpenMM PDBxFile CIF split, RDKit SMILES template bond-order assignment, PoseBusters `dock` checks",
        "- caveat: this is a physical pose sanity gate, not wet-lab evidence and not a binding free-energy calculation.",
        "",
        "## Overall",
        "",
        f"- rows: `{summary['rows']}`",
        f"- ok_rows: `{summary['ok_rows']}`",
        f"- full_pass_rows: `{summary['full_pass_rows']}`",
        f"- full_pass_rate: `{summary['full_pass_rate']:.3f}`",
        f"- gate_counts: `{summary['gate_counts']}`",
        "",
        "## By Source",
        "",
        "| Source | ok rows | pass | review | fail | full-pass rate | mean check pass-rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for source, row in summary["by_source"].items():
        lines.append(
            "| {source} | {ok_rows} | {gate_pass_rows} | {gate_review_rows} | {gate_fail_rows} | {full_pass_rate:.3f} | {mean_posebusters_pass_rate:.3f} |".format(
                source=source,
                **row,
            )
        )

    lines.extend(
        [
            "",
            "## By Target",
            "",
            "| Target | ok rows | pass | review | fail | full-pass rate | mean check pass-rate |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for target, row in sorted(summary["by_target"].items()):
        lines.append(
            "| {target} | {ok_rows} | {gate_pass_rows} | {gate_review_rows} | {gate_fail_rows} | {full_pass_rate:.3f} | {mean_posebusters_pass_rate:.3f} |".format(
                target=target,
                **row,
            )
        )

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `pilot/cpu_meaningful/chromanol_pose_sanity_gate.csv`",
            "- `pilot/cpu_meaningful/chromanol_pose_sanity_gate_summary.json`",
        ]
    )
    (OUT / "chromanol_pose_sanity_gate_summary.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    jobs = load_jobs()
    print(f"Chromanol pose sanity gate jobs: {len(jobs)}")
    rows = []
    for idx, job in enumerate(jobs, start=1):
        print(f"[{idx:02d}/{len(jobs):02d}] {job['source']} {job['job_id']} {job['target']} {job['compound']}")
        rows.append(validate_one(job))
    df = pd.DataFrame(rows)
    out_csv = OUT / "chromanol_pose_sanity_gate.csv"
    df.to_csv(out_csv, index=False)
    write_summary(df)
    ok = df[df["status"].eq("ok")]
    full_pass = int(ok["pose_sanity_pass"].sum()) if len(ok) else 0
    print(f"Saved {rel(out_csv)}")
    print(f"OK {len(ok)}/{len(df)}; full pass {full_pass}/{len(ok)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
