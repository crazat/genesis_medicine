"""
Warmup preprocessor for embelin ABFE Phase 5.

The original Phase 5 script feeds tleap-built rst7 directly into alchemical
equilibration with no minimization. This works for small ligands like EMB-3
(C6 hexyl) but fails for embelin (C12 undecyl) because the long alkyl tail
clashes with protein. Equilibration NaN's at iteration 0.

This script:
  1. Loads complex.parm7 + complex.rst7
  2. Builds a non-alchemical OpenMM system (full lambda=1 interactions)
  3. Minimizes 10000 steps to relax steric clashes
  4. Heats 0K -> 310K over 100 ps NVT with protein heavy-atom restraints (10 kcal/mol/A^2)
  5. Equilibrates 100 ps NPT with restraints, then 100 ps NPT unrestrained
  6. Writes the warmed-up state back as complex.rst7 (original backed up to complex.rst7.preminim)

After this completes, the existing Phase 5 script can be re-run unchanged.

Usage:
  python scripts/zaff_phase5_warmup_embelin.py --leg complex
  python scripts/zaff_phase5_warmup_embelin.py --leg solvent
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

import openmm as mm
import openmm.app as app
import openmm.unit as u
import parmed as pmd

ROOT = Path("/home/crazat/genesis_medicine")
WORK = ROOT / "pilot/abfe_mmp1_holo_zn_embelin"


def warmup(leg: str) -> int:
    if leg == "complex":
        parm_path = WORK / "complex/complex.parm7"
        rst_path = WORK / "complex/complex.rst7"
    elif leg == "solvent":
        parm_path = WORK / "abfe_production/solvent_leg/solvent.parm7"
        rst_path = WORK / "abfe_production/solvent_leg/solvent.rst7"
    else:
        raise SystemExit(f"unknown leg {leg}")

    if not parm_path.exists() or not rst_path.exists():
        print(f"FAIL: missing {parm_path} or {rst_path}")
        return 1

    backup = rst_path.with_suffix(".rst7.preminim")
    if not backup.exists():
        shutil.copy2(rst_path, backup)
        print(f"[warmup-{leg}] backed up {rst_path.name} -> {backup.name}")

    print(f"[warmup-{leg}] loading parmed structure")
    parm = pmd.load_file(str(parm_path), str(rst_path))
    n_atoms = len(parm.atoms)
    print(f"[warmup-{leg}] system: {n_atoms} atoms, box={parm.box}")

    # Build non-alchemical OpenMM system (full interactions)
    system = parm.createSystem(
        nonbondedMethod=app.PME,
        nonbondedCutoff=10.0 * u.angstrom,
        constraints=app.HBonds,
        rigidWater=True,
        removeCMMotion=True,
    )

    # Add positional restraints on protein heavy atoms (not ligand, not water, not ions)
    # Identify by residue type. Ligand residue is 'LIG' from antechamber/tleap.
    if leg == "complex":
        restrain_atoms = []
        for atom in parm.atoms:
            r = atom.residue.name
            if r in ("WAT", "HOH", "Na+", "Cl-", "LIG"):
                continue
            if atom.element == 1:  # H
                continue
            restrain_atoms.append(atom.idx)
        print(f"[warmup-{leg}] restraining {len(restrain_atoms)} protein heavy atoms (k=10 kcal/mol/A^2)")
        force = mm.CustomExternalForce("0.5*k*((x-x0)^2 + (y-y0)^2 + (z-z0)^2)")
        force.addGlobalParameter("k", 10.0 * u.kilocalorie_per_mole / u.angstrom**2)
        force.addPerParticleParameter("x0")
        force.addPerParticleParameter("y0")
        force.addPerParticleParameter("z0")
        positions = parm.positions
        for i in restrain_atoms:
            p = positions[i].value_in_unit(u.nanometer)
            force.addParticle(i, [p[0], p[1], p[2]])
        restraint_idx = system.addForce(force)
    else:
        restraint_idx = None

    system.addForce(mm.MonteCarloBarostat(1.0 * u.atmosphere, 310 * u.kelvin, 25))

    integrator = mm.LangevinMiddleIntegrator(
        310 * u.kelvin, 1.0 / u.picosecond, 1.0 * u.femtosecond  # gentler 1fs timestep for warmup
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    properties = {"Precision": "mixed"}

    sim = app.Simulation(parm.topology, system, integrator, platform, properties)
    sim.context.setPositions(parm.positions)
    if parm.box_vectors is not None:
        sim.context.setPeriodicBoxVectors(*parm.box_vectors)

    print(f"[warmup-{leg}] minimizing up to 10000 iterations (tol=10 kJ/mol/nm)")
    t0 = time.time()
    sim.minimizeEnergy(maxIterations=10000, tolerance=10.0 * u.kilojoule_per_mole / u.nanometer)
    print(f"[warmup-{leg}]   minimization done {(time.time()-t0)/60:.1f} min")

    state = sim.context.getState(getEnergy=True)
    print(f"[warmup-{leg}]   PE after min: {state.getPotentialEnergy()}")

    # Heat 0K -> 310K over 100 ps in 10 stages (NVT-like; barostat already on but T ramps)
    print(f"[warmup-{leg}] heating 0K -> 310K over 100 ps")
    t0 = time.time()
    sim.context.setVelocitiesToTemperature(10 * u.kelvin)
    n_heat_stages = 10
    steps_per_stage = 10000  # 10 ps per stage at 1fs
    for stg in range(n_heat_stages):
        T = 10 + (310 - 10) * (stg + 1) / n_heat_stages
        integrator.setTemperature(T * u.kelvin)
        sim.step(steps_per_stage)
    print(f"[warmup-{leg}]   heat done {(time.time()-t0)/60:.1f} min")

    # NPT equilibration with restraints, 100 ps at 2 fs
    integrator.setStepSize(2.0 * u.femtosecond)
    print(f"[warmup-{leg}] NPT 100 ps with restraints")
    t0 = time.time()
    sim.step(50000)  # 100 ps at 2 fs
    print(f"[warmup-{leg}]   restrained NPT done {(time.time()-t0)/60:.1f} min")

    # Release restraints and run another 100 ps free NPT
    if restraint_idx is not None:
        # Setting k=0 effectively disables the restraint
        sim.context.setParameter("k", 0.0)
        print(f"[warmup-{leg}] NPT 100 ps unrestrained")
        t0 = time.time()
        sim.step(50000)
        print(f"[warmup-{leg}]   free NPT done {(time.time()-t0)/60:.1f} min")

    # Save final state back to rst7 via parmed
    final_state = sim.context.getState(getPositions=True, getVelocities=True, enforcePeriodicBox=True)
    parm.positions = final_state.getPositions()
    parm.box_vectors = final_state.getPeriodicBoxVectors()
    parm.save(str(rst_path), overwrite=True)
    print(f"[warmup-{leg}] wrote warmed rst7 -> {rst_path}")

    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=["complex", "solvent", "all"], default="complex")
    args = ap.parse_args()
    if args.leg == "all":
        rc = warmup("complex")
        if rc != 0:
            return rc
        return warmup("solvent")
    return warmup(args.leg)


if __name__ == "__main__":
    sys.exit(main())
