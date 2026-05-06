"""ZAFF Phase 3: 5 ns NPT sanity MD on holo MMP-1 with non-bonded Zn.

Validates that the non-bonded Zn (ions234lm_126_tip3p) plus position-restraint
on Zn + 3 His-NE2 atoms preserves catalytic coordination geometry during
equilibration. Pass criterion: all 3 Zn-NE2 distances within 0.5 A of starting
mean during the last 1 ns.

Inputs:
  pilot/abfe_mmp1_holo_zn/mmp1_holo.parm7
  pilot/abfe_mmp1_holo_zn/mmp1_holo.rst7
  pilot/abfe_mmp1_holo_zn/zn_coord_atoms.json

Outputs:
  pilot/abfe_mmp1_holo_zn/sanity_md/{traj.dcd, final.pdb, log.csv, summary.json}

Wallclock: 1.5-2 h on RTX 5090.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import parmed as pmd
import openmm as mm
import openmm.app as app
from openmm import unit


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "pilot/abfe_mmp1_holo_zn_embelin"
OUT = WORK / "holo_md_100ns"
OUT.mkdir(parents=True, exist_ok=True)

PARM7 = WORK / "mmp1_holo.parm7"
RST7 = WORK / "mmp1_holo.rst7"
COORD_JSON = WORK / "zn_coord_atoms.json"

# Sanity MD timing
NS_EQ = 0.2          # 200 ps NVT + 200 ps NPT equilibration
NS_PROD = 100.0      # 100 ns NPT production (embelin holo + Zn — paper #A H3 dynamics)
TIMESTEP_FS = 2.0
TEMPERATURE_K = 310
RESTRAINT_K = 10.0   # kcal/mol/A^2 on Zn + His-NE2 atoms


def main() -> int:
    print(f"[Phase3] loading {PARM7.name}")
    parm = pmd.load_file(str(PARM7), str(RST7))
    coord_info = json.loads(COORD_JSON.read_text())
    zn_idx = coord_info["zn_atom_idx"]
    coord_idxs = [c["atom_idx"] for c in coord_info["coord_atoms"]]
    restraint_idxs = [zn_idx] + coord_idxs
    print(f"  total atoms: {len(parm.atoms)}")
    print(f"  Zn idx {zn_idx}; coord-shell idxs {coord_idxs}")

    print("[Phase3] building OpenMM system")
    system = parm.createSystem(
        nonbondedMethod=app.PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=app.HBonds,
        rigidWater=True,
        removeCMMotion=True,
    )
    # Add MonteCarloBarostat for NPT
    system.addForce(mm.MonteCarloBarostat(1.0 * unit.atmosphere, TEMPERATURE_K * unit.kelvin, 25))

    # Position restraint on Zn + 3 His-NE2 (cartesian harmonic)
    k_force = RESTRAINT_K * unit.kilocalorie_per_mole / unit.angstrom**2
    restraint = mm.CustomExternalForce("0.5*k_pos*((x-x0)^2 + (y-y0)^2 + (z-z0)^2)")
    restraint.addPerParticleParameter("k_pos")
    restraint.addPerParticleParameter("x0")
    restraint.addPerParticleParameter("y0")
    restraint.addPerParticleParameter("z0")
    coords_nm = parm.coordinates / 10.0  # parmed Angstrom -> nm
    for i in restraint_idxs:
        x0, y0, z0 = coords_nm[i]
        restraint.addParticle(int(i), [k_force.value_in_unit(unit.kilojoule_per_mole / unit.nanometer**2),
                                       float(x0), float(y0), float(z0)])
    system.addForce(restraint)
    print(f"  position restraint on {len(restraint_idxs)} atoms (Zn + 3 His-NE2), k={RESTRAINT_K} kcal/mol/A^2")

    integrator = mm.LangevinMiddleIntegrator(
        TEMPERATURE_K * unit.kelvin,
        1.0 / unit.picosecond,
        TIMESTEP_FS * unit.femtosecond,
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(parm.topology, system, integrator, platform)
    sim.context.setPositions(parm.positions)

    print("[Phase3] minimization")
    t0 = time.time()
    sim.minimizeEnergy(maxIterations=2000)
    print(f"  done in {time.time()-t0:.1f}s")

    print(f"[Phase3] equilibration: {NS_EQ*2:.1f} ns total ({NS_EQ} NVT + {NS_EQ} NPT)")
    sim.context.setVelocitiesToTemperature(TEMPERATURE_K * unit.kelvin)
    n_eq_steps = int(NS_EQ * 1e6 / TIMESTEP_FS)  # 1 ns = 500_000 steps at 2 fs
    sim.step(n_eq_steps)  # NVT-like (without barostat fully scaled — still includes barostat)

    # Reporters for production
    dcd = OUT / "traj.dcd"
    log_csv = OUT / "log.csv"
    sim.reporters.append(app.DCDReporter(str(dcd), 50_000))     # 100 ps stride
    sim.reporters.append(app.StateDataReporter(
        str(log_csv), 50_000, time=True, potentialEnergy=True,
        kineticEnergy=True, temperature=True, volume=True, density=True
    ))

    print(f"[Phase3] production: {NS_PROD} ns NPT")
    n_prod_steps = int(NS_PROD * 1e6 / TIMESTEP_FS)
    t0 = time.time()
    sim.step(n_prod_steps)
    wallclock_s = time.time() - t0
    print(f"  production done in {wallclock_s/60:.1f} min")

    # Final state
    final_state = sim.context.getState(getPositions=True, enforcePeriodicBox=True)
    with (OUT / "final.pdb").open("w") as fh:
        app.PDBFile.writeFile(sim.topology, final_state.getPositions(), fh)

    # Analyze Zn coordination distances over trajectory
    print("[Phase3] analyzing Zn-NE2 distances")
    import mdtraj as md
    t = md.load(str(dcd), top=str(OUT / "final.pdb"))
    pairs = [[zn_idx, c] for c in coord_idxs]
    distances_nm = md.compute_distances(t, pairs)  # frames x pairs
    distances_A = distances_nm * 10.0
    last_third = int(len(t) * 2 / 3)
    last_means = distances_A[last_third:].mean(axis=0)
    starting = distances_A[0]
    drift = last_means - starting
    pass_each = np.abs(drift) < 0.5
    overall_pass = bool(np.all(pass_each))

    summary = {
        "phase": "Phase 3 sanity MD",
        "wallclock_minutes": round(wallclock_s / 60, 1),
        "ns_simulated": NS_PROD,
        "n_atoms": len(parm.atoms),
        "zn_atom_idx": zn_idx,
        "coord_atoms": coord_info["coord_atoms"],
        "starting_distances_A": [round(float(x), 3) for x in starting],
        "last_third_mean_distances_A": [round(float(x), 3) for x in last_means],
        "drift_A": [round(float(x), 3) for x in drift],
        "drift_within_0.5A": [bool(x) for x in pass_each],
        "pass": overall_pass,
        "pass_criterion": "all 3 Zn-NE2 distances drift < 0.5 A in last third",
        "outputs": {
            "trajectory": str(dcd.relative_to(ROOT)),
            "final_pdb": str((OUT / "final.pdb").relative_to(ROOT)),
            "log_csv": str(log_csv.relative_to(ROOT)),
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

    if overall_pass:
        (OUT / "PHASE3_PASS").touch()
        return 0
    (OUT / "PHASE3_FAIL").touch()
    return 1


if __name__ == "__main__":
    sys.exit(main())
