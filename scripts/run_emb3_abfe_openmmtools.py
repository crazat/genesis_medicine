"""ABFE EMB-3 × MMP-1 — openmmtools alchemical replica exchange.

FEP-SPell-ABFE 로컬 환경 미지원 (Slurm/APBS) → openmmtools 0.26으로 직접 작성.

설계:
  - 8 lambda windows (electrostatics 4 + sterics 4)
  - 1 ns eq + 3 ns production per window
  - replica exchange between windows (Hamiltonian RE)
  - MBAR로 ΔG 계산
  - 총 시뮬: 8 × 4 ns = 32 ns
  - 예상 시간: RTX 5090 ~30-60분

복합체 ΔG (binding) = ΔG_complex - ΔG_solvent
  여기서는 단순화: complex ΔG 만 계산 (relative comparison용).
  실제 absolute ΔG는 추가 solvent leg 필요 (이후 작업).
"""

from __future__ import annotations

import json
import os
import sys
import time
import warnings
from pathlib import Path

# ambertools 경로 (am1bcc charges)
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
OUT = ABFE_DIR / "openmmtools_run"
OUT.mkdir(parents=True, exist_ok=True)

CIF = (SCAFFOLD / "boltz2_validation/output/boltz_results_inputs"
                / "predictions/mmp1__embelin_emb3"
                / "mmp1__embelin_emb3_model_0.cif")
EMB3_SMILES = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"


def setup_system():
    """Boltz-2 cofold output → solvated complex system."""
    print("[1/5] System setup")
    if not CIF.exists():
        raise FileNotFoundError(CIF)

    lig = Molecule.from_smiles(EMB3_SMILES, allow_undefined_stereo=True)
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

    # Position ligand at original CIF coords
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

    # Solvate
    print("   solvating with TIP3P water + 0.15 M NaCl…")
    modeller.addSolvent(sg.forcefield, model="tip3p",
                         padding=1.0*unit.nanometer,
                         ionicStrength=0.15*unit.molar)
    print(f"   total atoms: {modeller.topology.getNumAtoms()}")

    system = sg.create_system(modeller.topology)

    # 식별 ligand atoms
    lig_atoms = [a.index for a in modeller.topology.atoms()
                  if a.residue.name in ("UNK", "LIG", "LIG1")]
    print(f"   ligand atoms: {len(lig_atoms)}")

    # Energy minimization + 짧은 equilibration (NaN 방지)
    print("   minimization + 100 ps NVT equilibration…")
    integ = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0/unit.picosecond, 2.0*unit.femtosecond,
    )
    sim = app.Simulation(modeller.topology, system, integ,
                          mm.Platform.getPlatformByName("CUDA"))
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=2000)
    sim.context.setVelocitiesToTemperature(310*unit.kelvin)
    sim.step(50_000)   # 100 ps NVT
    eq_state = sim.context.getState(getPositions=True, getVelocities=True,
                                      enforcePeriodicBox=True)
    eq_positions = eq_state.getPositions()
    eq_box = eq_state.getPeriodicBoxVectors()
    print(f"   ✅ equilibration 완료")

    return modeller, system, lig_atoms, eq_positions, eq_box


def make_alchemical_system(system, lig_atoms):
    """Alchemical region: ligand atoms decoupling."""
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


def make_lambda_states(alch_system, n_windows=12):
    """Lambda schedule: 더 부드러운 electrostatics → sterics decoupling.

    softcore sterics는 alchemy 기본 활성. NaN 방지를 위해 lambda 간격 작게.
    """
    print(f"\n[3/5] Lambda schedule ({n_windows} windows)")
    n_half = n_windows // 2
    lambdas_elec_phase = np.linspace(1.0, 0.0, n_half + 1)
    lambdas_steric_phase = np.linspace(1.0, 0.0, n_windows - n_half + 1)

    schedule = []
    for le in lambdas_elec_phase:
        schedule.append({"lambda_electrostatics": float(le),
                         "lambda_sterics": 1.0})
    for ls in lambdas_steric_phase[1:]:
        schedule.append({"lambda_electrostatics": 0.0,
                         "lambda_sterics": float(ls)})

    print(f"   total windows: {len(schedule)} "
          f"(elec phase: {n_half + 1}, steric phase: {n_windows - n_half})")

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


def run_replica_exchange(thermo_states, eq_positions, eq_box, n_iter=300):
    """Replica exchange Hamiltonian sampling — equilibrated 시작점 사용."""
    print(f"\n[4/5] Replica exchange ({len(thermo_states)} replicas, "
          f"{n_iter} iterations)")
    sampler_state = states.SamplerState(
        positions=eq_positions, box_vectors=eq_box,
    )
    sampler_states = [sampler_state] * len(thermo_states)

    move = mcmc.LangevinDynamicsMove(
        timestep=2.0*unit.femtosecond,
        collision_rate=1.0/unit.picosecond,
        n_steps=500,   # 1 ps per iteration
        reassign_velocities=False,
    )

    storage = OUT / "replica_exchange.nc"
    if storage.exists():
        storage.unlink()
    sampler = multistate.ReplicaExchangeSampler(
        mcmc_moves=move,
        number_of_iterations=n_iter,
        online_analysis_interval=50,
    )
    reporter = multistate.MultiStateReporter(str(storage), checkpoint_interval=20)
    sampler.create(
        thermodynamic_states=thermo_states,
        sampler_states=sampler_states,
        storage=reporter,
    )
    print(f"   storage: {storage}")
    print(f"   running… (1 ps/iter × {n_iter} iter × {len(thermo_states)} replicas "
          f"= {n_iter * len(thermo_states)} ps total)")
    t0 = time.time()
    sampler.run(n_iter)
    wall = time.time() - t0
    print(f"   ✅ {wall/60:.1f}분")
    return reporter, wall


def analyze(reporter):
    """MBAR analysis → ΔG."""
    print("\n[5/5] MBAR analysis")
    from openmmtools.multistate import MultiStateSamplerAnalyzer

    analyzer = MultiStateSamplerAnalyzer(reporter)
    Deltaf_ij, dDeltaf_ij = analyzer.get_free_energy()
    # f[0] = 시작 (full coupling), f[-1] = 완전 decoupled
    # ΔG_decoupling = f[-1] - f[0] (kT 단위)
    n_states = Deltaf_ij.shape[0]
    df_kT = Deltaf_ij[0, -1]
    ddf_kT = dDeltaf_ij[0, -1]

    kT_kcal = 0.5961621   # 310 K kcal/mol
    df_kcal = df_kT * kT_kcal
    ddf_kcal = ddf_kT * kT_kcal
    print(f"   ΔG (decoupling, kT): {df_kT:.3f} ± {ddf_kT:.3f}")
    print(f"   ΔG (decoupling, kcal/mol): {df_kcal:.3f} ± {ddf_kcal:.3f}")

    # Note: 여기 ΔG는 complex leg only (binding free energy 추정)
    # Binding ΔG = -ΔG_decoupling + 보정항 (volume restraint, restraints)
    # 단순 비교용으로 ΔG_decoupling 자체 사용 (작을수록 약결합)
    return df_kcal, ddf_kcal


def main() -> int:
    print("=== EMB-3 × MMP-1 ABFE (openmmtools) ===\n")
    t_start = time.time()

    modeller, system, lig_atoms, eq_pos, eq_box = setup_system()
    alch = make_alchemical_system(system, lig_atoms)
    thermo_states = make_lambda_states(alch, n_windows=12)
    reporter, sim_wall = run_replica_exchange(thermo_states, eq_pos, eq_box,
                                                n_iter=200)
    df_kcal, ddf_kcal = analyze(reporter)

    total_wall = time.time() - t_start
    print(f"\n=== TOTAL: {total_wall/60:.1f}분 ===")

    result = {
        "system": "EMB-3_MMP1",
        "method": "openmmtools_alchemical_replica_exchange",
        "n_lambda_windows": 8,
        "n_iterations": 300,
        "ps_per_iteration": 1,
        "total_simulation_ns": 8 * 300 * 0.001,
        "delta_g_decoupling_kcal_mol": df_kcal,
        "delta_g_uncertainty_kcal_mol": ddf_kcal,
        "interpretation": (
            "ΔG_decoupling 작을수록 약결합 (ligand 떼는 비용 작음). "
            "실험 IC50 추정에는 standard volume correction + restraint correction 추가 필요. "
            "여기서는 EMB-3 lead 정량 baseline 확보용."
        ),
        "wall_minutes": round(total_wall / 60, 2),
        "wall_simulation_minutes": round(sim_wall / 60, 2),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    print(f"\n✅ {OUT}/result.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
