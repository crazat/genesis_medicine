"""ABFE Phase 5 production — MultiStateSampler (no replica exchange).

Drop-in replacement for zaff_phase5_abfe_production_generic.py after the
2026-05-05 smoketest validated that MultiStateSampler completes all iterations
on the same ZAFF + Zn restraint system (whereas ReplicaExchangeSampler with
swap-all deadlocks at first iteration write).

Usage:
  python scripts/zaff_phase5_abfe_production_mss.py --work pilot/abfe_benchmark_chembl/CHEMBL415 --leg all

Expects:
  {work}/complex/{complex.parm7, complex.rst7, lig.mol2, lig.frcmod, PHASE4_OK}

Produces:
  {work}/abfe_production_mss/{complex_leg,solvent_leg,dG_bind.json,PHASE5_OK|INCONCLUSIVE}
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import openmm as mm
import openmm.app as app
from openmm import unit
import parmed as pmd
from openmmtools import alchemy, mcmc, multistate, states


N_LAMBDA = 16
NS_EQ = 1.0
NS_PROD_COMPLEX = 8.0
NS_PROD_SOLVENT = 5.0
TEMPERATURE_K = 310
TIMESTEP_FS = 2.0
FLAT_BOTTOM_K = 10.0
FLAT_BOTTOM_R_MAX = 8.0


def build_alchemical_state(parm: pmd.Structure, lig_atoms: list[int]):
    sys_omm = parm.createSystem(
        nonbondedMethod=app.PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=app.HBonds,
        rigidWater=True,
        removeCMMotion=True,
    )
    sys_omm.addForce(mm.MonteCarloBarostat(1.0 * unit.atmosphere, TEMPERATURE_K * unit.kelvin, 25))
    region = alchemy.AlchemicalRegion(alchemical_atoms=lig_atoms,
                                       annihilate_electrostatics=True, annihilate_sterics=False)
    factory = alchemy.AbsoluteAlchemicalFactory(consistent_exceptions=False)
    return factory.create_alchemical_system(sys_omm, region)


def build_lambda_schedule(n: int) -> list[dict]:
    half = n // 2
    elec = np.linspace(1.0, 0.0, half + 1)[1:]
    ster = np.linspace(1.0, 0.0, half + 1)[1:]
    schedule = []
    for e in elec:
        schedule.append({"lambda_electrostatics": float(e), "lambda_sterics": 1.0})
    for s in ster:
        schedule.append({"lambda_electrostatics": 0.0, "lambda_sterics": float(s)})
    return schedule


def run_leg(parm: pmd.Structure, lig_atoms: list[int], leg: str, ns_prod: float, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {leg} leg ===")
    print(f"  ligand atoms: {len(lig_atoms)}")
    alch_sys = build_alchemical_state(parm, lig_atoms)
    schedule = build_lambda_schedule(N_LAMBDA)

    thermo_states = []
    for sched in schedule:
        ts = states.ThermodynamicState(system=alch_sys, temperature=TEMPERATURE_K * unit.kelvin,
                                        pressure=1.0 * unit.atmosphere)
        a_state = alchemy.AlchemicalState(
            lambda_electrostatics=float(sched["lambda_electrostatics"]),
            lambda_sterics=float(sched["lambda_sterics"]),
        )
        thermo_states.append(states.CompoundThermodynamicState(
            thermodynamic_state=ts, composable_states=[a_state]))

    init_state = states.SamplerState(positions=parm.positions, box_vectors=parm.box_vectors)
    n_iter_eq = max(1, int(NS_EQ * 1e6 / TIMESTEP_FS / 5000))
    n_iter_prod = max(1, int(ns_prod * 1e6 / TIMESTEP_FS / 5000))
    move = mcmc.LangevinDynamicsMove(timestep=TIMESTEP_FS * unit.femtosecond, n_steps=5000)

    storage = out_dir / "trajectory.nc"
    if storage.exists():
        storage.unlink()
    ck = out_dir / "trajectory_checkpoint.nc"
    if ck.exists():
        ck.unlink()

    sampler = multistate.MultiStateSampler(
        mcmc_moves=move, number_of_iterations=n_iter_prod)
    print(f"  n_lambda={N_LAMBDA} n_iter_eq={n_iter_eq} n_iter_prod={n_iter_prod}")
    reporter = multistate.MultiStateReporter(str(storage), checkpoint_interval=10)
    sampler.create(thermo_states, init_state, reporter)

    print(f"  equilibration {NS_EQ} ns ...")
    t0 = time.time()
    sampler.equilibrate(n_iterations=n_iter_eq)
    print(f"    eq done {(time.time()-t0)/60:.1f} min")
    print(f"  production {ns_prod} ns x {N_LAMBDA} windows ...")
    t1 = time.time()
    sampler.run()
    print(f"    prod done {(time.time()-t1)/60:.1f} min")

    analyzer = multistate.MultiStateSamplerAnalyzer(reporter)
    Deltaf_ij, dDeltaf_ij = analyzer.get_free_energy()
    dG = float(Deltaf_ij[0, -1]) * analyzer.kT.value_in_unit(unit.kilocalorie_per_mole)
    dG_err = float(dDeltaf_ij[0, -1]) * analyzer.kT.value_in_unit(unit.kilocalorie_per_mole)
    print(f"  dG_{leg} = {dG:.3f} +/- {dG_err:.3f} kcal/mol")
    return {"leg": leg, "dG": dG, "dG_err": dG_err, "ns_prod": ns_prod}


def run_complex_leg(work: Path, lig_name: str) -> int:
    cx_dir = work / "complex"
    out = work / "abfe_production_mss" / "complex_leg"
    parm = pmd.load_file(str(cx_dir / "complex.parm7"), str(cx_dir / "complex.rst7"))
    lig_atoms = [a.idx for a in parm.atoms if a.residue.name == "LIG"]
    if not lig_atoms:
        print("FAIL: no LIG residue")
        return 6
    result = run_leg(parm, lig_atoms, "complex", NS_PROD_COMPLEX, out)
    (out / "result.json").write_text(json.dumps(result, indent=2))
    (out / "PHASE5A_OK").touch()
    return 0


def run_solvent_leg(work: Path, lig_name: str) -> int:
    sv_dir = work / "abfe_production_mss" / "solvent_leg"
    sv_dir.mkdir(parents=True, exist_ok=True)
    sv_parm7 = sv_dir / "solvent.parm7"
    sv_rst7 = sv_dir / "solvent.rst7"

    if not (sv_parm7.exists() and sv_rst7.exists()):
        cx_dir = work / "complex"
        mol2 = cx_dir / f"{lig_name}.mol2"
        frcmod = cx_dir / f"{lig_name}.frcmod"
        if not (mol2.exists() and frcmod.exists()):
            print(f"FAIL: missing {mol2} or {frcmod}")
            return 8
        leap_in = sv_dir / "tleap_solvent.in"
        leap_in.write_text(
            f"source leaprc.water.tip3p\n"
            f"source leaprc.gaff2\n"
            f"loadAmberParams {frcmod}\n"
            f"LIG = loadMol2 {mol2}\n"
            f"solvateBox LIG TIP3PBOX 12.0\n"
            f"saveAmberParm LIG {sv_parm7} {sv_rst7}\n"
            f"quit\n"
        )
        proc = subprocess.run(["tleap", "-f", str(leap_in)], cwd=str(sv_dir),
                              capture_output=True, text=True)
        (sv_dir / "tleap_solvent.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
        if proc.returncode != 0 or not sv_parm7.exists():
            print(f"FAIL: tleap solvent rc={proc.returncode}")
            return 9

    parm = pmd.load_file(str(sv_parm7), str(sv_rst7))
    lig_atoms = [a.idx for a in parm.atoms if a.residue.name == "LIG"]
    if not lig_atoms:
        return 6
    result = run_leg(parm, lig_atoms, "solvent", NS_PROD_SOLVENT, sv_dir)
    (sv_dir / "result.json").write_text(json.dumps(result, indent=2))
    (sv_dir / "PHASE5B_OK").touch()
    return 0


def combine(work: Path, system_label: str) -> int:
    out = work / "abfe_production_mss"
    cx_path = out / "complex_leg/result.json"
    sv_path = out / "solvent_leg/result.json"
    if not (cx_path.exists() and sv_path.exists()):
        print(f"FAIL: missing leg results")
        return 7
    cx = json.loads(cx_path.read_text())
    sv = json.loads(sv_path.read_text())

    R = 1.9872036e-3
    V_R = (4.0 / 3.0) * np.pi * FLAT_BOTTOM_R_MAX ** 3
    V_0 = 1660.5
    dG_R = -R * TEMPERATURE_K * np.log(V_R / V_0)
    dG_bind = sv["dG"] - cx["dG"] - dG_R
    dG_bind_err = (sv["dG_err"] ** 2 + cx["dG_err"] ** 2) ** 0.5

    summary = {
        "phase": "Phase 5 ABFE production (MultiStateSampler, no replica exchange)",
        "system": system_label,
        "complex_leg": cx,
        "solvent_leg": sv,
        "dG_R_standard_state_correction": round(dG_R, 3),
        "dG_bind_kcal_mol": round(dG_bind, 3),
        "dG_bind_err_kcal_mol": round(dG_bind_err, 3),
        "pass_dG_neg_with_uncertainty": bool((dG_bind + dG_bind_err) < 0),
        "n_lambda": N_LAMBDA,
        "ns_prod_complex": NS_PROD_COMPLEX, "ns_prod_solvent": NS_PROD_SOLVENT,
        "temperature_K": TEMPERATURE_K,
        "flat_bottom_k_kcal_per_mol_A2": FLAT_BOTTOM_K,
        "flat_bottom_r_max_A": FLAT_BOTTOM_R_MAX,
        "sampler": "openmmtools.multistate.MultiStateSampler (no replica exchange)",
    }
    (out / "dG_bind.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if summary["pass_dG_neg_with_uncertainty"]:
        (out / "PHASE5_OK").touch()
        return 0
    (out / "PHASE5_INCONCLUSIVE").touch()
    return 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--work", required=True, help="ABFE work dir")
    p.add_argument("--leg", choices=["complex", "solvent", "combine", "all"], default="all")
    p.add_argument("--lig-name", default="lig", help="ligand mol2/frcmod basename")
    p.add_argument("--system-label", default=None, help="for dG_bind.json metadata")
    args = p.parse_args()

    work = Path(args.work).resolve()
    label = args.system_label or f"{work.name} + holo MMP-1 (ZAFF, MSS)"

    gate = work / "complex" / "PHASE4_OK"
    if not gate.exists():
        print(f"FAIL: Phase 4 gate not satisfied ({gate})")
        return 5

    if args.leg == "complex":
        return run_complex_leg(work, args.lig_name)
    if args.leg == "solvent":
        return run_solvent_leg(work, args.lig_name)
    if args.leg == "combine":
        return combine(work, label)

    rc = run_complex_leg(work, args.lig_name)
    if rc != 0:
        return rc
    rc = run_solvent_leg(work, args.lig_name)
    if rc != 0:
        return rc
    return combine(work, label)


if __name__ == "__main__":
    sys.exit(main())
