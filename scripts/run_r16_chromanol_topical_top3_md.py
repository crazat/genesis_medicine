"""R16 chromanol topical analog top-3 Boltz-2 pairs: 10 ns MD validation.

Input:
  pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv

Output:
  pilot/md_r16_chromanol_topical_top3_10ns/summary.json
  pilot/md_r16_chromanol_topical_top3_10ns/summary.csv
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd


_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r16_chromanol_topical_top3_10ns"
OUT.mkdir(parents=True, exist_ok=True)
COFOLD_CSV = ROOT / "pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv"
RESULT_ROOT = (
    ROOT
    / "pilot/cpu_meaningful/output_r16_chromanol_topical"
    / "boltz_results_inputs_r16_chromanol_topical"
    / "predictions"
)


def clean_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def build_jobs() -> list[dict[str, object]]:
    df = pd.read_csv(COFOLD_CSV)
    top = df.sort_values("rank_by_affinity_probability").head(3)
    jobs = []
    for _, row in top.iterrows():
        job_id = str(row["job_id"])
        analog_id = str(row["analog_id"])
        target = str(row["target"]).lower()
        cif = RESULT_ROOT / job_id / f"{job_id}_model_0.cif"
        jobs.append(
            {
                "name": f"{job_id}__{clean_name(analog_id)}__10ns",
                "job_id": job_id,
                "analog_id": analog_id,
                "target": target,
                "cif": str(cif.relative_to(ROOT)),
                "smiles": str(row["smiles"]),
                "topical_followup_score": row.get("topical_followup_score"),
                "logP": row.get("logP"),
                "QED": row.get("QED"),
                "gap_eV": row.get("gap_eV"),
                "affinity_probability_binary": row.get("affinity_probability_binary"),
                "affinity_pred_value": row.get("affinity_pred_value"),
            }
        )
    return jobs


def run_md(job: dict[str, object], ns: float = 10.0) -> dict[str, object]:
    name = str(job["name"])
    cif_full = ROOT / str(job["cif"])
    if not cif_full.exists():
        return {"name": name, "status": "missing_cif", "cif": job["cif"]}

    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {name} ({ns:.0f} ns R16 topical chromanol MD) ===")
    print(f"  CIF: {job['cif']}")
    print(f"  affinity_probability_binary: {job.get('affinity_probability_binary')}")

    import numpy as np
    import openmm as mm
    import openmm.app as app
    from openff.toolkit import Molecule
    from openff.units import unit as off_unit
    from openmm import unit
    from openmmforcefields.generators import SystemGenerator
    from pdbfixer import PDBFixer

    lig = Molecule.from_smiles(str(job["smiles"]), allow_undefined_stereo=True)
    lig.generate_conformers(n_conformers=1)

    fixer = PDBFixer(filename=str(cif_full))
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    sg = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds},
    )

    original = app.PDBxFile(str(cif_full))
    lig_orig = [
        original.positions[atom.index]
        for atom in original.topology.atoms()
        if atom.residue.name == "LIG1"
    ]
    if lig_orig:
        original_centroid = np.mean([[p.x, p.y, p.z] for p in lig_orig], axis=0)
        coords = lig.conformers[0].m_as("nanometer")
        coords += original_centroid - coords.mean(axis=0)
        lig._conformers = [coords * off_unit.nanometer]

    modeller.addHydrogens(sg.forcefield, pH=7.4)
    modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())

    system = sg.create_system(modeller.topology)
    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin,
        1.0 / unit.picosecond,
        1.0 * unit.femtosecond,
    )
    sim = app.Simulation(
        modeller.topology,
        system,
        integrator,
        mm.Platform.getPlatformByName("CUDA"),
    )

    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=1000)
    sim.context.setVelocitiesToTemperature(150 * unit.kelvin)
    sim.step(12500)
    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
    sim.step(12500)
    integrator.setStepSize(2.0 * unit.femtosecond)

    steps_per_frame = 1000
    total_steps = int(ns * 500_000)
    sim.reporters.append(app.DCDReporter(str(out_dir / "traj.dcd"), steps_per_frame))
    sim.reporters.append(
        app.StateDataReporter(
            str(out_dir / "log.csv"),
            steps_per_frame,
            step=True,
            potentialEnergy=True,
            temperature=True,
            speed=True,
        )
    )

    t0 = time.time()
    sim.step(total_steps)
    wall = time.time() - t0

    final_pdb = out_dir / "final.pdb"
    with final_pdb.open("w") as fh:
        app.PDBFile.writeFile(
            sim.topology,
            sim.context.getState(getPositions=True).getPositions(),
            fh,
        )

    import mdtraj as md

    traj = md.load(str(out_dir / "traj.dcd"), top=str(final_pdb))
    lig_idx = traj.topology.select("resname UNK and element != H")
    if len(lig_idx) == 0:
        lig_idx = traj.topology.select("(not protein) and element != H")
    rmsd = md.rmsd(traj, traj, frame=0, atom_indices=lig_idx)
    n_frames = len(rmsd)
    last_third = rmsd[2 * n_frames // 3:]

    result = {
        "name": name,
        "job_id": job["job_id"],
        "analog_id": job["analog_id"],
        "target": job["target"],
        "status": "ok",
        "smiles": job["smiles"],
        "topical_followup_score": job.get("topical_followup_score"),
        "logP": job.get("logP"),
        "QED": job.get("QED"),
        "gap_eV": job.get("gap_eV"),
        "affinity_probability_binary": job.get("affinity_probability_binary"),
        "affinity_pred_value": job.get("affinity_pred_value"),
        "wall_min": round(wall / 60, 2),
        "rmsd_mean_A": round(float(rmsd.mean()) * 10, 2),
        "rmsd_max_A": round(float(rmsd.max()) * 10, 2),
        "rmsd_final_A": round(float(rmsd[-1]) * 10, 2),
        "rmsd_last_third_A": round(float(last_third.mean()) * 10, 2),
        "ns_simulated": ns,
    }
    print(
        f"  ok: mean={result['rmsd_mean_A']} A, "
        f"last-third={result['rmsd_last_third_A']} A, "
        f"max={result['rmsd_max_A']} A, wall={result['wall_min']} min"
    )
    return result


def main() -> int:
    jobs = build_jobs()
    print("R16 topical chromanol analog top-3 10 ns MD")
    print(pd.DataFrame(jobs)[["job_id", "analog_id", "target", "affinity_probability_binary", "cif"]].to_string(index=False))

    results: list[dict[str, object]] = []
    for job in jobs:
        try:
            result = run_md(job, ns=10.0)
        except Exception as exc:
            import traceback

            traceback.print_exc()
            result = {
                "name": job["name"],
                "job_id": job["job_id"],
                "analog_id": job["analog_id"],
                "target": job["target"],
                "status": f"error:{str(exc)[:200]}",
            }
        results.append(result)
        (OUT / "summary.json").write_text(json.dumps(results, indent=2))

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\nFinal R16 topical chromanol top-3 MD summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
