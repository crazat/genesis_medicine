"""MD pose-prefilter — 10 ns OpenMM stability test before ABFE attempt.

Round 9 mitigation #4: only attempt ABFE on cofold poses that pass 10 ns MD
without RMSD > 5 Å. Catches NaN-prone systems before consuming 8 GPU-h.

Usage:
    python scripts/md_pose_prefilter.py \
        --receptor pilot/.../receptor.pdb \
        --ligand-smiles "..." \
        --ligand-template-pdb pilot/.../cofold_template.pdb \
        --ligand-template-resname LIG1 \
        --out pilot/md_prefilter/<name>/ \
        --ns 10.0 \
        --rmsd-threshold-A 5.0

Output: stability_summary.json with PASS/FAIL + RMSD trajectory.

Strategy: re-uses run_abfe_corrected.py setup_complex() to build the system,
then runs plain NPT MD (no alchemical), measures ligand RMSD vs initial pose.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receptor", required=True, type=Path)
    parser.add_argument("--ligand-smiles", required=True, type=str)
    parser.add_argument("--ligand-template-pdb", type=Path)
    parser.add_argument("--ligand-template-resname", type=str, default="")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--ns", type=float, default=10.0)
    parser.add_argument("--rmsd-threshold-A", type=float, default=5.0)
    parser.add_argument("--device", type=str, default="cuda:0")
    args = parser.parse_args()

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    print(f"[prefilter] {args.receptor.name} × {args.ligand_smiles[:40]}…")
    print(f"  ns={args.ns}, RMSD threshold={args.rmsd_threshold_A} Å")

    # Build system using run_abfe_corrected setup
    from run_abfe_corrected import setup_complex
    setup = setup_complex(
        receptor_pdb=args.receptor,
        ligand_smiles=args.ligand_smiles,
        ligand_template_pdb=args.ligand_template_pdb,
        ligand_template_resname=args.ligand_template_resname,
    )

    # Run plain NPT MD (no alchemical)
    from openmm import LangevinMiddleIntegrator
    from openmm.app import Simulation, StateDataReporter
    from openmm import unit, Platform
    import io

    integrator = LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtoseconds
    )
    platform = Platform.getPlatformByName("CUDA")
    sim = Simulation(setup["modeller"].topology, setup["system"],
                      integrator, platform)
    sim.context.setPositions(setup["eq_positions"])
    # Round 9 fix: box vectors REQUIRED for PME/PBC; absent → NaN at step 0
    if "eq_box" in setup:
        sim.context.setPeriodicBoxVectors(*setup["eq_box"])
    else:
        bv = setup["system"].getDefaultPeriodicBoxVectors()
        sim.context.setPeriodicBoxVectors(*bv)

    n_steps = int(args.ns * 1000 / 0.002)    # 2 fs timestep, ns → steps
    save_every = n_steps // 100    # 100 frames
    print(f"  total steps: {n_steps}, frames: 100")

    # Track ligand RMSD
    lig_idx = setup["lig_atoms"]
    initial_pos = np.array(setup["eq_positions"].value_in_unit(unit.nanometer))
    initial_lig = initial_pos[lig_idx]
    initial_lig_centered = initial_lig - initial_lig.mean(axis=0)

    rmsd_traj = []
    start = time.time()
    nan_at = None
    for i in range(0, n_steps, save_every):
        try:
            sim.step(save_every)
            state = sim.context.getState(getPositions=True, enforcePeriodicBox=True)
            pos = np.array(state.getPositions(asNumpy=True).value_in_unit(unit.nanometer))
            lig = pos[lig_idx]
            lig_centered = lig - lig.mean(axis=0)
            # Simple Cartesian RMSD on ligand heavy atoms (no superposition)
            rmsd_nm = float(np.sqrt(np.mean((lig_centered - initial_lig_centered) ** 2)))
            rmsd_traj.append({"step": i + save_every,
                                "ns": (i + save_every) * 0.002 / 1000,
                                "rmsd_A": rmsd_nm * 10})
        except Exception as e:
            nan_at = {"step": i, "error": str(e)[:200]}
            print(f"  ⚠️ MD failed at step {i}: {e}")
            break

    wall = (time.time() - start) / 60
    max_rmsd = max((r["rmsd_A"] for r in rmsd_traj), default=999.0)
    passed = nan_at is None and max_rmsd < args.rmsd_threshold_A

    summary = {
        "receptor": str(args.receptor),
        "ligand_smiles": args.ligand_smiles,
        "ns": args.ns,
        "rmsd_threshold_A": args.rmsd_threshold_A,
        "n_steps": n_steps,
        "n_frames_saved": len(rmsd_traj),
        "max_rmsd_A": max_rmsd,
        "mean_rmsd_A": float(np.mean([r["rmsd_A"] for r in rmsd_traj])) if rmsd_traj else None,
        "wall_minutes": wall,
        "nan_at": nan_at,
        "passed": passed,
        "trajectory": rmsd_traj,
    }
    out_json = out / "stability_summary.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(f"\n  max RMSD: {max_rmsd:.2f} Å")
    print(f"  PASS: {passed}")
    print(f"  ✅ {out_json}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
