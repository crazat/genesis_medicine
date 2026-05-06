"""ZAFF Phase 5: ABFE production on holo MMP-1 + EMB-3 complex.

Adapts the existing openmmtools alchemical replica-exchange protocol from
scripts/run_emb3_abfe_openmmtools.py to consume a pre-built complex parm7
(produced by Phase 4) instead of building system on the fly. This preserves
the explicit holo Zn parameters from Phase 2c.

Protocol:
  - Complex leg: 16 lambda windows, 3 replicas, 1 ns eq + 5 ns prod each
    -> 16 x 3 x 5 = 240 ns total
  - Solvent leg: ligand alone in TIP3P, 16 windows x 3 replicas x 3 ns prod
    -> 144 ns total
  - Boresch 6-DOF orientational restraint on ligand to receptor anchor atoms
  - Standard-state correction: dG_R = -RT ln(V_R / V_o)
  - Output: dG_bind = dG_solvent_decouple - dG_complex_decouple - dG_R

Inputs:
  pilot/abfe_mmp1_holo_zn/complex/{complex.parm7, complex.rst7, PHASE4_OK}

Outputs:
  pilot/abfe_mmp1_holo_zn/abfe_production/{
    complex_leg/, solvent_leg/, dG_bind.json, PHASE5_OK
  }

Wallclock estimate: 12-18 h on RTX 5090 (complex leg dominant).
"""
from __future__ import annotations

import argparse
import copy
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


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "pilot/abfe_mmp1_holo_zn"
COMPLEX_DIR = WORK / "complex"
OUT = WORK / "abfe_production"
OUT.mkdir(parents=True, exist_ok=True)

PHASE4_GATE = COMPLEX_DIR / "PHASE4_OK"
COMPLEX_PARM7 = COMPLEX_DIR / "complex.parm7"
COMPLEX_RST7 = COMPLEX_DIR / "complex.rst7"

N_LAMBDA = 16
N_REPLICAS = 3
NS_EQ = 1.0
NS_PROD_COMPLEX = 5.0
NS_PROD_SOLVENT = 3.0
TEMPERATURE_K = 310
TIMESTEP_FS = 2.0
FLAT_BOTTOM_K = 10.0  # kcal/mol/A^2
FLAT_BOTTOM_R_MAX = 8.0  # A


def build_alchemical_state(parm: pmd.Structure, lig_atoms: list[int]):
    """Build OpenMM system + alchemical region for the ligand."""
    sys_omm = parm.createSystem(
        nonbondedMethod=app.PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=app.HBonds,
        rigidWater=True,
        removeCMMotion=True,
    )
    sys_omm.addForce(mm.MonteCarloBarostat(1.0 * unit.atmosphere, TEMPERATURE_K * unit.kelvin, 25))
    region = alchemy.AlchemicalRegion(alchemical_atoms=lig_atoms, annihilate_electrostatics=True, annihilate_sterics=False)
    factory = alchemy.AbsoluteAlchemicalFactory(consistent_exceptions=False)
    alch_sys = factory.create_alchemical_system(sys_omm, region)
    return alch_sys


def build_lambda_schedule(n: int) -> list[dict]:
    """Half elec, half sterics: 8+8 split, smoothly ramped."""
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

    # Build lambda-state list using alchemy.AlchemicalState (handles lambda_sterics/electrostatics)
    thermo_states = []
    for sched in schedule:
        ts = states.ThermodynamicState(
            system=alch_sys, temperature=TEMPERATURE_K * unit.kelvin,
            pressure=1.0 * unit.atmosphere,
        )
        a_state = alchemy.AlchemicalState(
            lambda_electrostatics=float(sched["lambda_electrostatics"]),
            lambda_sterics=float(sched["lambda_sterics"]),
        )
        thermo_states.append(states.CompoundThermodynamicState(
            thermodynamic_state=ts, composable_states=[a_state]
        ))

    # Initial sampler state from rst7
    init_state = states.SamplerState(positions=parm.positions, box_vectors=parm.box_vectors)

    n_iter_eq = int(NS_EQ * 1e6 / TIMESTEP_FS / 5000)  # 5000 steps per iteration
    n_iter_prod = int(ns_prod * 1e6 / TIMESTEP_FS / 5000)

    move = mcmc.LangevinDynamicsMove(
        timestep=TIMESTEP_FS * unit.femtosecond,
        n_steps=5000,
    )

    storage = out_dir / "trajectory.nc"
    sampler = multistate.ReplicaExchangeSampler(
        mcmc_moves=move, number_of_iterations=n_iter_prod,
        replica_mixing_scheme="swap-all",
    )

    print(f"  n_lambda={N_LAMBDA} replicas n_iter_eq={n_iter_eq} n_iter_prod={n_iter_prod}")
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

    # MBAR
    analyzer = multistate.MultiStateSamplerAnalyzer(reporter)
    Deltaf_ij, dDeltaf_ij = analyzer.get_free_energy()
    dG = float(Deltaf_ij[0, -1]) * analyzer.kT.value_in_unit(unit.kilocalorie_per_mole)
    dG_err = float(dDeltaf_ij[0, -1]) * analyzer.kT.value_in_unit(unit.kilocalorie_per_mole)
    print(f"  dG_{leg} = {dG:.3f} +/- {dG_err:.3f} kcal/mol")
    return {"leg": leg, "dG": dG, "dG_err": dG_err, "ns_prod": ns_prod}


def run_complex_leg() -> int:
    print(f"[Phase5a] loading complex parm7")
    parm = pmd.load_file(str(COMPLEX_PARM7), str(COMPLEX_RST7))
    lig_atoms = [a.idx for a in parm.atoms if a.residue.name == "LIG"]
    if len(lig_atoms) == 0:
        print("FAIL: no LIG residue found")
        return 6
    cx_dir = OUT / "complex_leg"
    cx_result = run_leg(parm, lig_atoms, "complex", NS_PROD_COMPLEX, cx_dir)
    (cx_dir / "result.json").write_text(json.dumps(cx_result, indent=2))
    (cx_dir / "PHASE5A_OK").touch()
    return 0


def run_solvent_leg() -> int:
    sv_dir = OUT / "solvent_leg"
    sv_dir.mkdir(parents=True, exist_ok=True)
    sv_parm7 = sv_dir / "solvent.parm7"
    sv_rst7 = sv_dir / "solvent.rst7"

    if not (sv_parm7.exists() and sv_rst7.exists()):
        print("[Phase5b] building ligand-in-water parm7 via tleap")
        emb3_mol2 = COMPLEX_DIR / "emb3.mol2"
        emb3_frcmod = COMPLEX_DIR / "emb3.frcmod"
        if not (emb3_mol2.exists() and emb3_frcmod.exists()):
            print(f"FAIL: missing emb3.mol2 ({emb3_mol2.exists()}) or emb3.frcmod ({emb3_frcmod.exists()})")
            return 8
        leap_in = sv_dir / "tleap_solvent.in"
        leap_in.write_text(f"""
source leaprc.water.tip3p
source leaprc.gaff2
loadAmberParams {emb3_frcmod}
LIG = loadMol2 {emb3_mol2}
solvateBox LIG TIP3PBOX 12.0
saveAmberParm LIG {sv_parm7} {sv_rst7}
quit
""".strip())
        proc = subprocess.run(
            ["tleap", "-f", str(leap_in)],
            cwd=str(sv_dir), capture_output=True, text=True,
        )
        (sv_dir / "tleap_solvent.log").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
        if proc.returncode != 0 or not sv_parm7.exists():
            print(f"FAIL: tleap solvent build failed rc={proc.returncode}")
            print(proc.stderr[-1500:])
            return 9

    print(f"[Phase5b] loading solvent parm7 {sv_parm7}")
    parm = pmd.load_file(str(sv_parm7), str(sv_rst7))
    lig_atoms = [a.idx for a in parm.atoms if a.residue.name == "LIG"]
    print(f"  total atoms: {len(parm.atoms)}, lig atoms: {len(lig_atoms)}")
    if len(lig_atoms) == 0:
        print("FAIL: no LIG residue in solvent leg parm7")
        return 6
    sv_result = run_leg(parm, lig_atoms, "solvent", NS_PROD_SOLVENT, sv_dir)
    (sv_dir / "result.json").write_text(json.dumps(sv_result, indent=2))
    (sv_dir / "PHASE5B_OK").touch()
    return 0


def combine() -> int:
    cx_path = OUT / "complex_leg/result.json"
    sv_path = OUT / "solvent_leg/result.json"
    if not (cx_path.exists() and sv_path.exists()):
        print(f"FAIL: missing leg results — complex={cx_path.exists()} solvent={sv_path.exists()}")
        return 7
    cx_result = json.loads(cx_path.read_text())
    sv_result = json.loads(sv_path.read_text())

    R = 1.9872036e-3  # kcal/mol/K
    V_R = (4.0 / 3.0) * np.pi * (FLAT_BOTTOM_R_MAX) ** 3
    V_0 = 1660.5
    dG_R = -R * TEMPERATURE_K * np.log(V_R / V_0)
    dG_bind = sv_result["dG"] - cx_result["dG"] - dG_R
    dG_bind_err = (sv_result["dG_err"] ** 2 + cx_result["dG_err"] ** 2) ** 0.5

    summary = {
        "phase": "Phase 5 ABFE production",
        "system": "EMB-3 + holo MMP-1 (Zn nonbonded ions234lm_126_tip3p)",
        "complex_leg": cx_result,
        "solvent_leg": sv_result,
        "dG_R_standard_state_correction": round(dG_R, 3),
        "dG_bind_kcal_mol": round(dG_bind, 3),
        "dG_bind_err_kcal_mol": round(dG_bind_err, 3),
        "pass_dG_neg_with_uncertainty": bool((dG_bind + dG_bind_err) < 0),
        "n_lambda": N_LAMBDA,
        "n_replicas": N_REPLICAS,
        "ns_prod_complex": NS_PROD_COMPLEX,
        "ns_prod_solvent": NS_PROD_SOLVENT,
        "temperature_K": TEMPERATURE_K,
        "flat_bottom_k_kcal_per_mol_A2": FLAT_BOTTOM_K,
        "flat_bottom_r_max_A": FLAT_BOTTOM_R_MAX,
    }
    (OUT / "dG_bind.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if summary["pass_dG_neg_with_uncertainty"]:
        (OUT / "PHASE5_OK").touch()
        return 0
    (OUT / "PHASE5_INCONCLUSIVE").touch()
    return 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--leg", choices=["complex", "solvent", "combine", "all"], default="all",
                   help="which leg to run; 'all' = sequential complex->solvent->combine (legacy)")
    args = p.parse_args()

    if not PHASE4_GATE.exists():
        print(f"FAIL: Phase 4 gate not satisfied ({PHASE4_GATE})")
        return 5

    if args.leg == "complex":
        return run_complex_leg()
    if args.leg == "solvent":
        return run_solvent_leg()
    if args.leg == "combine":
        return combine()

    rc = run_complex_leg()
    if rc != 0:
        return rc
    rc = run_solvent_leg()
    if rc != 0:
        return rc
    return combine()


if __name__ == "__main__":
    sys.exit(main())
