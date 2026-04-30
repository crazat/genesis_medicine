"""R13_13 × SIRT1 fill-in MD — completes R13_13 14/14 universal coverage."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r13_13_full14"
OUT.mkdir(parents=True, exist_ok=True)

R13_13_SMI = "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1"
NAME = "sirt1__r13_13"
CIF = "pilot/cpu_meaningful/output_r13_sirt1/boltz_results_inputs_r13_sirt1/predictions/r13_sirt1_13/r13_sirt1_13_model_0.cif"


def main():
    cif_path = ROOT / CIF
    if not cif_path.exists():
        print(f"missing CIF: {CIF}")
        return 1

    out_dir = OUT / NAME
    out_dir.mkdir(exist_ok=True)
    print(f"=== {NAME} ===")

    import openmm as mm
    import openmm.app as app
    from openmm import unit
    from openff.toolkit import Molecule
    from openff.units import unit as off_unit
    from openmmforcefields.generators import SystemGenerator
    from pdbfixer import PDBFixer
    import numpy as np
    import pandas as pd

    lig = Molecule.from_smiles(R13_13_SMI, allow_undefined_stereo=True)
    lig.generate_conformers(n_conformers=1)

    fixer = PDBFixer(filename=str(cif_path))
    fixer.findMissingResidues(); fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues(); fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms(); fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    sg = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig], forcefield_kwargs={"constraints": app.HBonds})

    _orig = app.PDBxFile(str(cif_path))
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

    steps_per_frame = 500
    total_steps = int(10.0 * 500_000)
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

    print(f"  ✅ 10 ns in {wall/60:.1f} min, RMSD mean={rmsd_mean*10:.2f} max={rmsd_max*10:.2f}")
    result = {
        "name": NAME, "status": "ok",
        "wall_min": round(wall / 60, 2),
        "rmsd_mean_A": round(rmsd_mean * 10, 2),
        "rmsd_max_A": round(rmsd_max * 10, 2),
        "ns_simulated": 10.0}
    (out_dir / "result.json").write_text(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
