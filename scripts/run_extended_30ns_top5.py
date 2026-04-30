"""Extended 30 ns MD on top 5 sub-Å pairs for paper-tier kinetic validation.

Targets the absolute best 10-ns RMSD pairs:
- R14_5 × MMP1 (0.56), R14_5 × CTGF (0.68): scar vertical
- R12_23 × AR (0.68), R12_23 × SIRT1 (0.68), R12_23 × PTGS2 (0.72)

5 × 30 ns ≈ 5 × 30 min = ~150 min GPU. Output: pilot/md_extended_30ns
"""
from __future__ import annotations

import json, os, sys, time
from pathlib import Path
import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_extended_30ns"
OUT.mkdir(parents=True, exist_ok=True)

R12_23_SMI = "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"
R14_5_SMI = "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"

JOBS = [
    {"name": "mmp1__r14_5_30ns",   "round": "r14", "idx": 5,  "tgt": "mmp1",  "smiles": R14_5_SMI},
    {"name": "ctgf__r14_5_30ns",   "round": "r14", "idx": 5,  "tgt": "ctgf",  "smiles": R14_5_SMI},
    {"name": "ar__r12_23_30ns",    "round": "r12", "idx": 23, "tgt": "ar",    "smiles": R12_23_SMI},
    {"name": "sirt1__r12_23_30ns", "round": "r12", "idx": 23, "tgt": "sirt1", "smiles": R12_23_SMI},
    {"name": "ptgs2__r12_23_30ns", "round": "r12", "idx": 23, "tgt": "ptgs2", "smiles": R12_23_SMI},
]


def cif_path(job):
    return ("pilot/cpu_meaningful/output_{r}_{tgt}/boltz_results_inputs_{r}_{tgt}/"
            "predictions/{r}_{tgt}_{i}/{r}_{tgt}_{i}_model_0.cif").format(
        r=job["round"], tgt=job["tgt"], i=job["idx"])


def run_md(name, cif, smiles, ns=30.0):
    cif_full = ROOT / cif
    if not cif_full.exists():
        return {"name": name, "status": "missing_cif", "cif": cif}

    out_dir = OUT / name
    out_dir.mkdir(exist_ok=True)
    print(f"\n=== {name} (30 ns extended) ===")

    import openmm as mm
    import openmm.app as app
    from openmm import unit
    from openff.toolkit import Molecule
    from openff.units import unit as off_unit
    from openmmforcefields.generators import SystemGenerator
    from pdbfixer import PDBFixer
    import numpy as np

    lig = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
    lig.generate_conformers(n_conformers=1)

    fixer = PDBFixer(filename=str(cif_full))
    fixer.findMissingResidues(); fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues(); fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms(); fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    sg = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig], forcefield_kwargs={"constraints": app.HBonds})

    _orig = app.PDBxFile(str(cif_full))
    lig_orig = [_orig.positions[a.index] for a in _orig.topology.atoms()
                 if a.residue.name == "LIG1"]
    if lig_orig:
        oc = np.mean([[p.x, p.y, p.z] for p in lig_orig], axis=0)
        coords = lig.conformers[0].m_as("nanometer")
        coords += oc - coords.mean(axis=0)
        lig._conformers = [coords * off_unit.nanometer]

    modeller.addHydrogens(sg.forcefield, pH=7.4)
    modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())

    system = sg.create_system(modeller.topology)
    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0 / unit.picosecond, 1.0 * unit.femtosecond)
    sim = app.Simulation(modeller.topology, system, integrator,
                          mm.Platform.getPlatformByName("CUDA"))

    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=1000)
    sim.context.setVelocitiesToTemperature(150 * unit.kelvin)
    sim.step(12500)
    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
    sim.step(12500)
    integrator.setStepSize(2.0 * unit.femtosecond)

    steps_per_frame = 1000  # 1 frame per 2 ps for 30 ns
    total_steps = int(ns * 500_000)
    sim.reporters.append(app.DCDReporter(str(out_dir / "traj.dcd"), steps_per_frame))
    sim.reporters.append(app.StateDataReporter(
        str(out_dir / "log.csv"), steps_per_frame,
        step=True, potentialEnergy=True, temperature=True, speed=True))

    t0 = time.time()
    sim.step(total_steps)
    wall = time.time() - t0

    final_pdb = out_dir / "final.pdb"
    with open(final_pdb, "w") as f:
        app.PDBFile.writeFile(
            sim.topology,
            sim.context.getState(getPositions=True).getPositions(), f)

    import mdtraj as md
    t = md.load(str(out_dir / "traj.dcd"), top=str(final_pdb))
    lig_idx = t.topology.select("resname UNK")
    if len(lig_idx) == 0:
        lig_idx = t.topology.select("not protein")
    rmsd = md.rmsd(t, t, frame=0, atom_indices=lig_idx)
    rmsd_mean = float(rmsd.mean()); rmsd_max = float(rmsd.max())
    rmsd_final = float(rmsd[-1])

    # Last 10 ns mean (more conservative paper-tier)
    n_frames = len(rmsd)
    last_third = rmsd[2 * n_frames // 3:]
    rmsd_last10ns = float(last_third.mean())

    print(f"  ✅ {ns} ns in {wall/60:.1f} min")
    print(f"  RMSD mean(all)={rmsd_mean*10:.2f} max={rmsd_max*10:.2f} final={rmsd_final*10:.2f} mean(last 10ns)={rmsd_last10ns*10:.2f}")
    return {
        "name": name, "status": "ok",
        "wall_min": round(wall / 60, 2),
        "rmsd_mean_A": round(rmsd_mean * 10, 2),
        "rmsd_max_A": round(rmsd_max * 10, 2),
        "rmsd_final_A": round(rmsd_final * 10, 2),
        "rmsd_last10ns_A": round(rmsd_last10ns * 10, 2),
        "ns_simulated": ns}


def main():
    print("Extended 30 ns MD on top 5 sub-Å pairs")
    results = []
    for job in JOBS:
        try:
            r = run_md(job["name"], cif_path(job), job["smiles"], ns=30.0)
        except Exception as e:
            import traceback; traceback.print_exc()
            r = {"name": job["name"], "status": f"error: {str(e)[:200]}"}
        results.append(r)
        with (OUT / "summary.json").open("w") as f:
            json.dump(results, f, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\nFinal extended-time results:")
    if "rmsd_mean_A" in df.columns:
        print(df[["name", "rmsd_mean_A", "rmsd_last10ns_A", "rmsd_max_A", "wall_min"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
