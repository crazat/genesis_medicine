"""
Generic warmup preprocessor for any ABFE Phase 5 work directory.

Usage:
  python scripts/zaff_phase5_warmup_generic.py --work pilot/abfe_benchmark_chembl/CHEMBL415 --leg all

Same logic as zaff_phase5_warmup_embelin.py but parameterized:
  - WORK_DIR is CLI arg
  - Expects {WORK_DIR}/complex/{complex.parm7, complex.rst7}
  - For solvent leg, builds {WORK_DIR}/abfe_production/solvent_leg/solvent.parm7/.rst7
    from {WORK_DIR}/complex/lig.mol2 + lig.frcmod (or {LIGNAME}.mol2 if --lig-name set)

Steps per leg:
  1. Load parm7 + rst7
  2. Minimize 10000 iters
  3. Heat 0K -> 310K over 100 ps (NVT-like with barostat)
  4. NPT 100 ps with restraints
  5. NPT 100 ps unrestrained
  6. Save warmed rst7 (original backed up to .rst7.preminim)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

import openmm as mm
import openmm.app as app
import openmm.unit as u
import parmed as pmd

CONDA_BIN = "/home/crazat/miniforge3/envs/genesis-md/bin"


def build_solvent_parm7(work_dir: Path, lig_name: str) -> tuple[Path, Path]:
    """Build solvent.parm7 from lig.mol2 + lig.frcmod via tleap (mirrors embelin solvent leg)."""
    sv_dir = work_dir / "abfe_production" / "solvent_leg"
    sv_dir.mkdir(parents=True, exist_ok=True)
    parm = sv_dir / "solvent.parm7"
    rst = sv_dir / "solvent.rst7"
    if parm.exists() and rst.exists():
        return parm, rst

    mol2 = work_dir / "complex" / f"{lig_name}.mol2"
    frcmod = work_dir / "complex" / f"{lig_name}.frcmod"
    if not mol2.exists() or not frcmod.exists():
        print(f"FAIL: missing {mol2} or {frcmod}")
        return None, None

    # Copy mol2/frcmod to solvent dir for tleap convenience
    shutil.copy2(mol2, sv_dir / mol2.name)
    shutil.copy2(frcmod, sv_dir / frcmod.name)

    leap_in = sv_dir / "tleap_solvent.in"
    leap_in.write_text(
        f"source leaprc.water.tip3p\n"
        f"source leaprc.gaff2\n"
        f"loadAmberParams {frcmod.name}\n"
        f"LIG = loadMol2 {mol2.name}\n"
        f"solvateBox LIG TIP3PBOX 12.0\n"
        f"saveAmberParm LIG solvent.parm7 solvent.rst7\n"
        f"quit\n"
    )
    proc = subprocess.run([f"{CONDA_BIN}/tleap", "-f", "tleap_solvent.in"],
                          cwd=str(sv_dir), capture_output=True, text=True)
    (sv_dir / "tleap_solvent.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    if proc.returncode != 0 or not parm.exists():
        return None, None
    return parm, rst


def warmup(work_dir: Path, leg: str, lig_name: str = "lig") -> int:
    if leg == "complex":
        parm_path = work_dir / "complex/complex.parm7"
        rst_path = work_dir / "complex/complex.rst7"
    elif leg == "solvent":
        # Build solvent parm7 if needed
        parm_path, rst_path = build_solvent_parm7(work_dir, lig_name)
        if parm_path is None:
            print(f"[warmup-{leg}] FAIL: could not build solvent.parm7")
            return 1
    else:
        raise SystemExit(f"unknown leg {leg}")

    if not parm_path.exists() or not rst_path.exists():
        print(f"FAIL: missing {parm_path} or {rst_path}")
        return 1

    backup = rst_path.with_suffix(".rst7.preminim")
    if not backup.exists():
        shutil.copy2(rst_path, backup)
        print(f"[warmup-{leg}] backed up {rst_path.name} -> {backup.name}")

    print(f"[warmup-{leg}] loading {parm_path}")
    parm = pmd.load_file(str(parm_path), str(rst_path))
    n_atoms = len(parm.atoms)
    print(f"[warmup-{leg}] system: {n_atoms} atoms")

    system = parm.createSystem(
        nonbondedMethod=app.PME,
        nonbondedCutoff=10.0 * u.angstrom,
        constraints=app.HBonds,
        rigidWater=True,
        removeCMMotion=True,
    )

    if leg == "complex":
        # Restraint protein heavy atoms
        restrain_atoms = []
        for atom in parm.atoms:
            r = atom.residue.name
            if r in ("WAT", "HOH", "Na+", "Cl-", "LIG"):
                continue
            if atom.element == 1:
                continue
            restrain_atoms.append(atom.idx)
        print(f"[warmup-{leg}] restraining {len(restrain_atoms)} protein heavy atoms")
        force = mm.CustomExternalForce("0.5*k*((x-x0)^2 + (y-y0)^2 + (z-z0)^2)")
        force.addGlobalParameter("k", 10.0 * u.kilocalorie_per_mole / u.angstrom**2)
        for axis in ("x0", "y0", "z0"):
            force.addPerParticleParameter(axis)
        positions = parm.positions
        for i in restrain_atoms:
            p = positions[i].value_in_unit(u.nanometer)
            force.addParticle(i, [p[0], p[1], p[2]])
        system.addForce(force)
        has_restraint = True
    else:
        has_restraint = False

    system.addForce(mm.MonteCarloBarostat(1.0 * u.atmosphere, 310 * u.kelvin, 25))

    integrator = mm.LangevinMiddleIntegrator(
        310 * u.kelvin, 1.0 / u.picosecond, 1.0 * u.femtosecond
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(parm.topology, system, integrator, platform, {"Precision": "mixed"})
    sim.context.setPositions(parm.positions)
    if parm.box_vectors is not None:
        sim.context.setPeriodicBoxVectors(*parm.box_vectors)

    print(f"[warmup-{leg}] minimizing 10000 iters")
    t0 = time.time()
    sim.minimizeEnergy(maxIterations=10000, tolerance=10.0 * u.kilojoule_per_mole / u.nanometer)
    print(f"  PE: {sim.context.getState(getEnergy=True).getPotentialEnergy()}  ({(time.time()-t0)/60:.1f} min)")

    print(f"[warmup-{leg}] heating 0K -> 310K over 100 ps")
    t0 = time.time()
    sim.context.setVelocitiesToTemperature(10 * u.kelvin)
    for stg in range(10):
        T = 10 + (310 - 10) * (stg + 1) / 10
        integrator.setTemperature(T * u.kelvin)
        sim.step(10000)
    print(f"  done {(time.time()-t0)/60:.1f} min")

    integrator.setStepSize(2.0 * u.femtosecond)
    print(f"[warmup-{leg}] NPT 100 ps with restraints")
    t0 = time.time()
    sim.step(50000)
    print(f"  done {(time.time()-t0)/60:.1f} min")

    if has_restraint:
        sim.context.setParameter("k", 0.0)
        print(f"[warmup-{leg}] NPT 100 ps unrestrained")
        t0 = time.time()
        sim.step(50000)
        print(f"  done {(time.time()-t0)/60:.1f} min")

    final_state = sim.context.getState(getPositions=True, getVelocities=True, enforcePeriodicBox=True)
    parm.positions = final_state.getPositions()
    parm.box_vectors = final_state.getPeriodicBoxVectors()
    parm.save(str(rst_path), overwrite=True)
    print(f"[warmup-{leg}] wrote warmed rst7 -> {rst_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="ABFE work dir (e.g. pilot/abfe_benchmark_chembl/CHEMBL415)")
    ap.add_argument("--leg", choices=["complex", "solvent", "all"], default="all")
    ap.add_argument("--lig-name", default="lig", help="ligand mol2/frcmod basename (default: lig)")
    args = ap.parse_args()
    work = Path(args.work).resolve()
    if not work.exists():
        print(f"FAIL: {work} does not exist")
        return 1
    if args.leg == "all":
        rc = warmup(work, "complex", args.lig_name)
        if rc != 0:
            return rc
        return warmup(work, "solvent", args.lig_name)
    return warmup(work, args.leg, args.lig_name)


if __name__ == "__main__":
    sys.exit(main())
