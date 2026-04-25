"""ABFE Embelin × MMP-1 — paper-tier (EMB-3와 병렬 실행).

EMB-3 ABFE와 동시 실행하여 같은 wall 시간에 두 결과 확보.
EMB-3 vs Embelin ΔΔG → paper의 핵심 정량 비교.

Spec은 run_emb3_abfe_full.py와 동일 (16 windows × 500 iter × 10 ps = 85 ns).
출력은 별도 디렉토리 (abfe_emb3_mmp1/openmmtools_full_embelin/).
"""

from __future__ import annotations

import json
import os
import sys
import time
import warnings
from pathlib import Path

ENV_BIN = "/home/crazat/miniforge3/envs/genesis-md/bin"
if ENV_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{ENV_BIN}:{os.environ.get('PATH', '')}"

warnings.filterwarnings("ignore")

import numpy as np
import openmm as mm
import openmm.app as app
from openmm import unit
from openmmtools import alchemy, mcmc, multistate, states
from openff.toolkit import Molecule
from openff.units import unit as off_unit
from openmmforcefields.generators import SystemGenerator
from pdbfixer import PDBFixer

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "pilot/scaffold_hop"
ABFE_DIR = SCAFFOLD / "abfe_emb3_mmp1"
OUT = ABFE_DIR / "openmmtools_full_embelin"
OUT.mkdir(parents=True, exist_ok=True)

# Embelin baseline → MMP-1 cofold (network_validation에서)
CIF = (SCAFFOLD / "network_validation/output/boltz_results_inputs"
                / "predictions/mmp1__embelin"
                / "mmp1__embelin_model_0.cif")
EMBELIN_SMILES = "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O"

# Same as full EMB-3 spec
N_LAMBDA_WINDOWS = 16
N_ITERATIONS = 500
STEPS_PER_ITERATION = 5000
EQ_NS = 0.5
PADDING_NM = 1.2


def setup_system():
    print("[1/5] System setup (Embelin)")
    if not CIF.exists():
        raise FileNotFoundError(CIF)

    lig = Molecule.from_smiles(EMBELIN_SMILES, allow_undefined_stereo=True)
    lig.generate_conformers(n_conformers=1)

    fixer = PDBFixer(filename=str(CIF))
    fixer.findMissingResidues(); fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues(); fixer.removeHeterogens(False)
    fixer.findMissingAtoms(); fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    sg = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds, "rigidWater": True,
                            "removeCMMotion": True},
        periodic_forcefield_kwargs={"nonbondedMethod": app.PME,
                                     "nonbondedCutoff": 1.0*unit.nanometer},
    )

    _orig = app.PDBxFile(str(CIF))
    lig_orig = [_orig.positions[a.index] for a in _orig.topology.atoms()
                 if a.residue.name == "LIG1"]
    if lig_orig:
        oc = np.mean([[p.x, p.y, p.z] for p in lig_orig], axis=0)
        coords = lig.conformers[0].m_as("nanometer")
        coords += oc - coords.mean(axis=0)
        lig._conformers = [coords * off_unit.nanometer]

    modeller.addHydrogens(sg.forcefield, pH=7.4)
    modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())

    print(f"   solvating with TIP3P + 0.15 M NaCl, padding {PADDING_NM} nm…")
    modeller.addSolvent(sg.forcefield, model="tip3p",
                         padding=PADDING_NM*unit.nanometer,
                         ionicStrength=0.15*unit.molar)
    print(f"   total atoms: {modeller.topology.getNumAtoms()}")

    system = sg.create_system(modeller.topology)
    lig_atoms = [a.index for a in modeller.topology.atoms()
                  if a.residue.name in ("UNK", "LIG", "LIG1")]
    print(f"   ligand atoms: {len(lig_atoms)}")

    print(f"   minimization + {EQ_NS*1000:.0f} ps NPT eq…")
    integ = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0/unit.picosecond, 2.0*unit.femtosecond,
    )
    sim = app.Simulation(modeller.topology, system, integ,
                          mm.Platform.getPlatformByName("CUDA"))
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=5000)
    sim.context.setVelocitiesToTemperature(310*unit.kelvin)
    sim.step(int(EQ_NS * 500_000))
    eq_state = sim.context.getState(getPositions=True, getVelocities=True,
                                      enforcePeriodicBox=True)
    print(f"   ✅ eq 완료")
    return modeller, system, lig_atoms, eq_state.getPositions(), \
        eq_state.getPeriodicBoxVectors()


def make_alchemical_system(system, lig_atoms):
    print("\n[2/5] Alchemical factory")
    factory = alchemy.AbsoluteAlchemicalFactory(
        consistent_exceptions=False,
        switch_width=1.0*unit.angstrom,
        alchemical_pme_treatment="exact",
    )
    region = alchemy.AlchemicalRegion(alchemical_atoms=lig_atoms)
    alch_system = factory.create_alchemical_system(system, region)
    print(f"   alchemical atoms: {len(lig_atoms)}")
    return alch_system


def make_lambda_states(alch_system, n_windows=N_LAMBDA_WINDOWS):
    print(f"\n[3/5] Lambda schedule ({n_windows} windows)")
    n_elec = n_windows // 2 + 1
    n_steric = n_windows - n_elec + 1
    lambdas_elec = np.linspace(1.0, 0.0, n_elec)
    lambdas_steric = np.linspace(1.0, 0.0, n_steric)

    schedule = []
    for le in lambdas_elec:
        schedule.append({"lambda_electrostatics": float(le),
                         "lambda_sterics": 1.0})
    for ls in lambdas_steric[1:]:
        schedule.append({"lambda_electrostatics": 0.0,
                         "lambda_sterics": float(ls)})

    print(f"   total: {len(schedule)} (elec: {n_elec}, steric: {n_steric})")

    thermo_states = []
    for s in schedule:
        ts = states.ThermodynamicState(system=alch_system,
                                        temperature=310*unit.kelvin,
                                        pressure=1*unit.atmosphere)
        css = states.CompoundThermodynamicState(
            thermodynamic_state=ts,
            composable_states=[alchemy.AlchemicalState.from_system(alch_system)]
        )
        css.lambda_electrostatics = s["lambda_electrostatics"]
        css.lambda_sterics = s["lambda_sterics"]
        thermo_states.append(css)
    return thermo_states


def run_replica_exchange(thermo_states, eq_pos, eq_box):
    print(f"\n[4/5] Replica exchange "
          f"({len(thermo_states)} replicas × {N_ITERATIONS} iter "
          f"× {STEPS_PER_ITERATION*0.002:.0f} ps/iter)")

    sampler_state = states.SamplerState(positions=eq_pos, box_vectors=eq_box)
    sampler_states = [sampler_state] * len(thermo_states)

    move = mcmc.LangevinDynamicsMove(
        timestep=2.0*unit.femtosecond,
        collision_rate=1.0/unit.picosecond,
        n_steps=STEPS_PER_ITERATION,
        reassign_velocities=False,
    )

    storage = OUT / "replica_exchange.nc"
    if storage.exists():
        storage.unlink()
    sampler = multistate.ReplicaExchangeSampler(
        mcmc_moves=move,
        number_of_iterations=N_ITERATIONS,
        online_analysis_interval=20,
    )
    reporter = multistate.MultiStateReporter(str(storage),
                                              checkpoint_interval=20)
    sampler.create(
        thermodynamic_states=thermo_states,
        sampler_states=sampler_states,
        storage=reporter,
    )
    print(f"   storage: {storage}")
    t0 = time.time()
    sampler.run(N_ITERATIONS)
    wall = time.time() - t0
    print(f"   ✅ {wall/3600:.2f}시간")
    return reporter, wall


def analyze(reporter):
    print("\n[5/5] MBAR analysis")
    from openmmtools.multistate import MultiStateSamplerAnalyzer

    analyzer = MultiStateSamplerAnalyzer(reporter)
    Deltaf_ij, dDeltaf_ij = analyzer.get_free_energy()
    df_kT = Deltaf_ij[0, -1]
    ddf_kT = dDeltaf_ij[0, -1]

    kT_kcal = 0.5961621
    df_kcal = df_kT * kT_kcal
    ddf_kcal = ddf_kT * kT_kcal

    print(f"   ΔG_decoupling: {df_kT:.3f} ± {ddf_kT:.3f} kT")
    print(f"   ΔG_decoupling: {df_kcal:.3f} ± {ddf_kcal:.3f} kcal/mol")
    return df_kcal, ddf_kcal


def main() -> int:
    print("=== Embelin × MMP-1 ABFE FULL (EMB-3 병렬) ===\n")
    t_start = time.time()

    modeller, system, lig_atoms, eq_pos, eq_box = setup_system()
    alch = make_alchemical_system(system, lig_atoms)
    thermo_states = make_lambda_states(alch)
    reporter, sim_wall = run_replica_exchange(thermo_states, eq_pos, eq_box)
    df_kcal, ddf_kcal = analyze(reporter)

    total_wall = time.time() - t_start
    print(f"\n=== TOTAL: {total_wall/3600:.2f}시간 ===")

    result = {
        "system": "Embelin_MMP1",
        "smiles": EMBELIN_SMILES,
        "method": "openmmtools_alchemical_replica_exchange_full",
        "n_lambda_windows": N_LAMBDA_WINDOWS,
        "n_iterations": N_ITERATIONS,
        "ps_per_iteration": STEPS_PER_ITERATION * 0.002,
        "total_simulation_ns": (N_LAMBDA_WINDOWS * N_ITERATIONS *
                                  STEPS_PER_ITERATION * 0.002 / 1000),
        "padding_nm": PADDING_NM,
        "eq_ns": EQ_NS,
        "delta_g_decoupling_kcal_mol": df_kcal,
        "delta_g_uncertainty_kcal_mol": ddf_kcal,
        "wall_hours": round(total_wall / 3600, 2),
        "wall_simulation_hours": round(sim_wall / 3600, 2),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    print(f"\n✅ {OUT}/result.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
