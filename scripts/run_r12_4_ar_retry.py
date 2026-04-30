"""R12_4 × AR retry with extended minimization + slower initial integration.

Original ar__r12_4 NaN'd at minimizeEnergy=300 + 2 fs timestep. Fix:
- 2000 minimization iterations
- 1 fs timestep first 50 ps (equilibration), then 2 fs production
- Re-center ligand after embed if pose drift
"""
from __future__ import annotations

import json, os, sys, time
from pathlib import Path

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r12_4_full14"
OUT.mkdir(parents=True, exist_ok=True)

R12_4_SMI = "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"
NAME = "ar__r12_4"
CIF = "pilot/cpu_meaningful/output_r12_ar/boltz_results_inputs_r12_ar/predictions/r12_ar_4/r12_ar_4_model_0.cif"


def run():
    cif_path = ROOT / CIF
    out_dir = OUT / NAME
    out_dir.mkdir(exist_ok=True)
    print(f"=== {NAME} (retry, extended min) ===")

    import openmm as mm
    import openmm.app as app
    from openmm import unit
    from openff.toolkit import Molecule
    from openff.units import unit as off_unit
    from openmmforcefields.generators import SystemGenerator
    from pdbfixer import PDBFixer
    import numpy as np

    lig = Molecule.from_smiles(R12_4_SMI, allow_undefined_stereo=True)
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

    # Slower 1 fs timestep for stable equilibration
    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0 / unit.picosecond, 1.0 * unit.femtosecond)
    try:
        sim = app.Simulation(modeller.topology, system, integrator,
                              mm.Platform.getPlatformByName("CUDA"))
        print("  CUDA")
    except Exception:
        sim = app.Simulation(modeller.topology, system, integrator)

    sim.context.setPositions(modeller.positions)

    # Extended minimization (2000 vs 300 default)
    print("  Extended minimization 2000 iter...")
    sim.minimizeEnergy(maxIterations=2000)

    # Slow heating: 0 → 310 K over 50 ps at 1 fs
    print("  Slow heating 50 ps @ 1 fs...")
    sim.context.setVelocitiesToTemperature(0 * unit.kelvin)
    n_heat_steps = int(50_000 / 1)  # 50 ps at 1 fs = 50000 steps
    sim.step(n_heat_steps // 2)
    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
    sim.step(n_heat_steps // 2)

    # Production at 2 fs (10 ns)
    print("  Production 10 ns @ 2 fs...")
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
    rmsd_final = float(rmsd[-1])

    print(f"\n  ✅ 10 ns + 50 ps heat in {wall/60:.1f} min")
    print(f"  RMSD mean={rmsd_mean*10:.2f} max={rmsd_max*10:.2f} final={rmsd_final*10:.2f}")

    result = {
        "name": NAME, "status": "ok",
        "wall_min": round(wall / 60, 2),
        "rmsd_mean_A": round(rmsd_mean * 10, 2),
        "rmsd_max_A": round(rmsd_max * 10, 2),
        "rmsd_final_A": round(rmsd_final * 10, 2),
        "ns_simulated": 10.0,
        "retry_protocol": "min2000_heat50ps_1fs"}
    (out_dir / "retry_result.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    try:
        r = run()
        print(f"\n{json.dumps(r, indent=2)}")
        sys.exit(0)
    except Exception as e:
        import traceback; traceback.print_exc()
        sys.exit(1)
