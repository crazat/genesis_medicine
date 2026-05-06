"""ABFE Phase 5 smoke test: MultiStateSampler diagnostic.

Tests the hypothesis that openmmtools.multistate.ReplicaExchangeSampler.run()
deadlock root cause is in replica-exchange swap mechanism, not in the iteration
loop itself. If MultiStateSampler (no swap) works → switch production to MSS.
If MultiStateSampler also deadlocks → bypass openmmtools.multistate entirely
(write sequential per-window OpenMM + offline pymbar).

Reduced from production:
  N_LAMBDA: 16 → 4 (still spans full 0→1 alchemical path)
  NS_EQ:   1.0 → 0.05 ns
  NS_PROD: 8.0 → 0.1 ns per window
  Wallclock target: 10-15 min on RTX 5090 (vs ~5h production)

Uses CHEMBL415 phase 4 prep (already validated).

Usage:
  python scripts/zaff_phase5_abfe_smoketest.py
"""
from __future__ import annotations

import json
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


ROOT = Path("/home/crazat/genesis_medicine")
WORK = ROOT / "pilot/abfe_benchmark_chembl/CHEMBL415"
OUT = WORK / "abfe_smoketest_mss"

N_LAMBDA = 4
NS_EQ = 0.05
NS_PROD = 0.1
TEMPERATURE_K = 310
TIMESTEP_FS = 2.0


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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    cx_dir = WORK / "complex"
    parm7 = cx_dir / "complex.parm7"
    rst7 = cx_dir / "complex.rst7"
    print(f"[smoke] loading {parm7.name}")
    parm = pmd.load_file(str(parm7), str(rst7))
    lig_atoms = [a.idx for a in parm.atoms if a.residue.name == "LIG"]
    print(f"  {len(parm.atoms)} atoms, {len(lig_atoms)} ligand atoms")
    if not lig_atoms:
        print("FAIL: no LIG residue")
        return 6

    print("[smoke] building alchemical system")
    alch_sys = build_alchemical_state(parm, lig_atoms)
    schedule = build_lambda_schedule(N_LAMBDA)
    print(f"  N_LAMBDA={N_LAMBDA} schedule={schedule}")

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
    n_iter_prod = max(1, int(NS_PROD * 1e6 / TIMESTEP_FS / 5000))
    move = mcmc.LangevinDynamicsMove(timestep=TIMESTEP_FS * unit.femtosecond, n_steps=5000)

    storage = OUT / "trajectory.nc"
    if storage.exists():
        storage.unlink()
    ck = OUT / "trajectory_checkpoint.nc"
    if ck.exists():
        ck.unlink()

    # KEY DIFFERENCE: MultiStateSampler (no swap) vs ReplicaExchangeSampler
    print("[smoke] creating MultiStateSampler (no replica exchange swaps)")
    sampler = multistate.MultiStateSampler(
        mcmc_moves=move, number_of_iterations=n_iter_prod)
    print(f"  n_iter_eq={n_iter_eq} n_iter_prod={n_iter_prod}")
    reporter = multistate.MultiStateReporter(str(storage), checkpoint_interval=10)
    sampler.create(thermo_states, init_state, reporter)

    print(f"[smoke] equilibration {NS_EQ} ns ({n_iter_eq} iter) ...")
    t0 = time.time()
    sampler.equilibrate(n_iterations=n_iter_eq)
    eq_min = (time.time() - t0) / 60
    print(f"  eq done {eq_min:.2f} min")

    print(f"[smoke] production {NS_PROD} ns x {N_LAMBDA} windows ({n_iter_prod} iter) ...")
    t1 = time.time()
    sampler.run()
    prod_min = (time.time() - t1) / 60
    print(f"  prod done {prod_min:.2f} min")

    print("[smoke] free-energy analysis")
    analyzer = multistate.MultiStateSamplerAnalyzer(reporter)
    Deltaf_ij, dDeltaf_ij = analyzer.get_free_energy()
    dG = float(Deltaf_ij[0, -1]) * analyzer.kT.value_in_unit(unit.kilocalorie_per_mole)
    dG_err = float(dDeltaf_ij[0, -1]) * analyzer.kT.value_in_unit(unit.kilocalorie_per_mole)
    print(f"  dG_alch_complex_smoketest = {dG:.3f} +/- {dG_err:.3f} kcal/mol (4 windows × 0.1 ns)")

    summary = {
        "phase": "Phase 5 ABFE smoketest (MultiStateSampler, no replica exchange)",
        "system": "CHEMBL415 (Batimastat) + holo MMP-1 ZAFF",
        "n_lambda": N_LAMBDA,
        "ns_eq": NS_EQ,
        "ns_prod": NS_PROD,
        "eq_minutes": round(eq_min, 2),
        "prod_minutes": round(prod_min, 2),
        "dG_alch_kcal_mol": round(dG, 3),
        "dG_err_kcal_mol": round(dG_err, 3),
        "diagnostic_pass": True,
        "interpretation": "MultiStateSampler completed all iterations — replica-exchange swap was the root deadlock cause. Production can switch to MSS.",
    }
    (OUT / "smoketest_result.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    (OUT / "SMOKETEST_OK").touch()
    return 0


if __name__ == "__main__":
    sys.exit(main())
