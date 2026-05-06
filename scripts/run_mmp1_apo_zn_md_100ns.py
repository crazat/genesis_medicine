"""
Apo-Zn MMP-1 100 ns NPT MD as control for #08 abfe_methodology paper.

Continues from `pilot/abfe_mmp1_holo_zn/sanity_md/final.pdb` (last frame of 5 ns
sanity MD) using the same parm7. Output trajectory feeds into:
  - Zn-coordination geometry drift over 100 ns (HID111-Zn, HID121-Zn, HIE201-Zn, GLU219-Zn)
  - C-alpha RMSD vs starting frame
  - Comparison with EMB-3/embelin complex leg trajectories to attribute conformational
    differences to the ligand vs intrinsic dynamics.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import openmm as mm
import openmm.app as app
import openmm.unit as u

ROOT = Path("/home/crazat/genesis_medicine")
PARM = ROOT / "pilot/abfe_mmp1_holo_zn/mmp1_holo.parm7"
START_PDB = ROOT / "pilot/abfe_mmp1_holo_zn/sanity_md/final.pdb"
OUT_DIR = ROOT / "pilot/mmp1_apo_zn_md_100ns"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NS_TOTAL = 100.0
DT_FS = 2.0
TEMP_K = 310.0
PRESSURE_BAR = 1.0
REPORT_PS = 100.0  # 1000 frames over 100 ns

steps_total = int(NS_TOTAL * 1e6 / DT_FS)  # 100 ns / 2 fs = 50,000,000 steps
steps_per_report = int(REPORT_PS * 1000 / DT_FS)  # 100 ps / 2 fs = 50,000 steps


def main() -> int:
    start = time.time()
    print(f"[apo-Zn MD] loading parm: {PARM}")
    print(f"[apo-Zn MD] starting frame: {START_PDB}")

    parm = app.AmberPrmtopFile(str(PARM))
    pdb = app.PDBFile(str(START_PDB))

    system = parm.createSystem(
        nonbondedMethod=app.PME,
        nonbondedCutoff=10.0 * u.angstrom,
        constraints=app.HBonds,
        rigidWater=True,
        removeCMMotion=True,
        hydrogenMass=1.5 * u.amu,
    )
    system.addForce(mm.MonteCarloBarostat(PRESSURE_BAR * u.bar, TEMP_K * u.kelvin, 25))

    integrator = mm.LangevinMiddleIntegrator(
        TEMP_K * u.kelvin, 1.0 / u.picosecond, DT_FS * u.femtosecond
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    properties = {"Precision": "mixed"}

    sim = app.Simulation(parm.topology, system, integrator, platform, properties)
    sim.context.setPositions(pdb.positions)
    if pdb.topology.getPeriodicBoxVectors() is not None:
        sim.context.setPeriodicBoxVectors(*pdb.topology.getPeriodicBoxVectors())

    print(f"[apo-Zn MD] system: {system.getNumParticles()} particles, dt={DT_FS}fs, T={TEMP_K}K")
    print(f"[apo-Zn MD] steps_total={steps_total:,}  report_every={steps_per_report:,}")

    # Brief minimization to relax the loaded frame
    print("[apo-Zn MD] minimizing 200 steps")
    sim.minimizeEnergy(maxIterations=200)

    sim.context.setVelocitiesToTemperature(TEMP_K * u.kelvin)

    sim.reporters.append(
        app.DCDReporter(str(OUT_DIR / "traj.dcd"), steps_per_report)
    )
    sim.reporters.append(
        app.StateDataReporter(
            str(OUT_DIR / "log.csv"),
            steps_per_report,
            time=True,
            potentialEnergy=True,
            kineticEnergy=True,
            temperature=True,
            volume=True,
            density=True,
            speed=True,
        )
    )
    sim.reporters.append(
        app.StateDataReporter(
            sys.stdout,
            steps_per_report * 10,  # less verbose stdout
            step=True,
            time=True,
            temperature=True,
            speed=True,
        )
    )

    print("[apo-Zn MD] starting 100 ns NPT")
    sim.step(steps_total)

    # Save final state
    state = sim.context.getState(getPositions=True, enforcePeriodicBox=True)
    with open(OUT_DIR / "final.pdb", "w") as f:
        app.PDBFile.writeFile(parm.topology, state.getPositions(), f, keepIds=True)

    wall = (time.time() - start) / 60.0

    summary = {
        "phase": "apo-Zn MMP-1 100 ns NPT control MD",
        "purpose": "Control trajectory for #08 paper — Zn coordination dynamics without ligand",
        "ns_simulated": NS_TOTAL,
        "n_atoms": system.getNumParticles(),
        "dt_fs": DT_FS,
        "temperature_K": TEMP_K,
        "pressure_bar": PRESSURE_BAR,
        "report_ps": REPORT_PS,
        "wallclock_minutes": round(wall, 2),
        "starting_frame_from": str(START_PDB.relative_to(ROOT)),
        "outputs": {
            "traj": "pilot/mmp1_apo_zn_md_100ns/traj.dcd",
            "log": "pilot/mmp1_apo_zn_md_100ns/log.csv",
            "final": "pilot/mmp1_apo_zn_md_100ns/final.pdb",
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUT_DIR / "APO_MD_OK").touch()
    print(f"[apo-Zn MD] DONE wall={wall:.1f} min, final.pdb + APO_MD_OK written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
