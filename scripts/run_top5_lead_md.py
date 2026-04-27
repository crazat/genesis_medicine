"""Top-5 selective lead MD ensemble — paper-tier validation.

After ABFE pivot 2026-04-27. Replaces failed ABFE 12h with 5 × 10ns MD
on R4 integration top-5 selective leads identified from 1877 cofold rows.

Targets:
  1. r3_6 × TGFB1 (round 3 winner, mean 0.65, zinc-free)
  2. β-sitosterol × AR (sel_idx 0.563, alopecia top hit)
  3. shikonin × CTGF (자근 직접, sel_idx 0.247, scar top hit)
  4. chlorogenic_acid × SIRT1 (sel_idx 0.293, photoaging hit)
  5. azelaic_acid × TYRP1 (existing acne drug repositioning, pigment)

Sequential 10 ns × 5 = ~2.5 hr GPU. Returns RMSD/RMSF time series.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/scaffold_hop/md_top5_leads"
OUT.mkdir(parents=True, exist_ok=True)


JOBS = [
    {
        "name": "tgfb1__r3_6",
        "cif": "pilot/scaffold_hop_round3/boltz_output/boltz_results_boltz_inputs/predictions/tgfb1__r3_6/tgfb1__r3_6_model_0.cif",
        "smiles": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
    },
    {
        "name": "ar__beta-sitosterol",
        "cif": "pilot/skin_alopecia/results_v1/boltz2_output/boltz_results_boltz2_inputs/predictions/ar__beta-sitosterol/ar__beta-sitosterol_model_0.cif",
        "smiles": "CC[C@@H](CC[C@@H](C)[C@H]1CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2CC=C4[C@@]3(CC[C@@H](C4)O)C)C)C(C)C",
    },
    {
        "name": "ctgf__shikonin",
        "cif": "pilot/skin_scar/results_v2/boltz2_output/boltz_results_boltz2_inputs/predictions/ctgf__shikonin/ctgf__shikonin_model_0.cif",
        "smiles": "CC(=CCC(C1=CC(=O)c2c(O)ccc(O)c2C1=O)O)C",
    },
    {
        "name": "sirt1__chlorogenic_acid",
        "cif": "pilot/skin_photoaging/results_v1/boltz2_output/boltz_results_boltz2_inputs/predictions/sirt1__chlorogenic_acid/sirt1__chlorogenic_acid_model_0.cif",
        "smiles": "O=C(O)[C@H]1C[C@H](OC(=O)/C=C/c2ccc(O)c(O)c2)[C@@H](O)[C@@H](O)C1",
    },
    {
        "name": "tyrp1__azelaic_acid",
        "cif": "pilot/skin_pigment/results_v1/boltz2_output/boltz_results_boltz2_inputs/predictions/tyrp1__azelaic_acid/tyrp1__azelaic_acid_model_0.cif",
        "smiles": "OC(=O)CCCCCCCC(=O)O",
    },
]


def run_md(name: str, cif: str, smiles: str, ns: float = 10.0) -> dict:
    cif_path = ROOT / cif
    if not cif_path.exists():
        return {"name": name, "status": "missing_cif", "cif": cif}

    out_dir = OUT / name
    out_dir.mkdir(exist_ok=True)
    print(f"\n{'=' * 70}")
    print(f"=== {name} ===")
    print(f"  CIF: {cif}")
    print(f"  SMILES: {smiles}")

    try:
        import openmm as mm
        import openmm.app as app
        from openmm import unit
        from openff.toolkit import Molecule
        from openff.units import unit as off_unit
        from openmmforcefields.generators import SystemGenerator
        from pdbfixer import PDBFixer
        import numpy as np
    except ImportError as e:
        return {"name": name, "status": f"import error: {e}"}

    try:
        lig = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
        lig.generate_conformers(n_conformers=1)
    except Exception as e:
        return {"name": name, "status": f"ligand init: {e}"}

    try:
        fixer = PDBFixer(filename=str(cif_path))
        fixer.findMissingResidues()
        fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues()
        fixer.removeHeterogens(keepWater=False)
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()
        modeller = app.Modeller(fixer.topology, fixer.positions)

        sg = SystemGenerator(
            forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
            small_molecule_forcefield="gaff-2.11",
            molecules=[lig],
            forcefield_kwargs={"constraints": app.HBonds},
        )

        # Place ligand at original cofold position
        _orig = app.PDBxFile(str(cif_path))
        lig_orig = [_orig.positions[a.index] for a in _orig.topology.atoms()
                     if a.residue.name == "LIG1"]
        if lig_orig:
            oc = np.mean([[p.x, p.y, p.z] for p in lig_orig], axis=0)
            coords = lig.conformers[0].m_as("nanometer")
            coords += oc - coords.mean(axis=0)
            lig._conformers = [coords * off_unit.nanometer]

        modeller.addHydrogens(sg.forcefield, pH=7.4)
        modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())

        system = sg.create_system(modeller.topology)
        integrator = mm.LangevinMiddleIntegrator(
            310 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtosecond,
        )
        try:
            platform = mm.Platform.getPlatformByName("CUDA")
            sim = app.Simulation(modeller.topology, system, integrator, platform)
            print("  Using CUDA platform")
        except Exception:
            sim = app.Simulation(modeller.topology, system, integrator)
            print("  Using fallback platform (CPU)")

        sim.context.setPositions(modeller.positions)
        sim.minimizeEnergy(maxIterations=300)
        sim.context.setVelocitiesToTemperature(310 * unit.kelvin)

        steps_per_frame = 500
        total_steps = int(ns * 500_000)
        sim.reporters.append(app.DCDReporter(str(out_dir / "traj.dcd"), steps_per_frame))
        sim.reporters.append(app.StateDataReporter(
            str(out_dir / "log.csv"), steps_per_frame,
            step=True, potentialEnergy=True, temperature=True, speed=True,
        ))

        t0 = time.time()
        sim.step(total_steps)
        wall = time.time() - t0

        final_pdb = out_dir / "final.pdb"
        with open(final_pdb, "w") as f:
            app.PDBFile.writeFile(
                sim.topology,
                sim.context.getState(getPositions=True).getPositions(),
                f)

        # RMSD
        try:
            import mdtraj as md
            t = md.load(str(out_dir / "traj.dcd"), top=str(final_pdb))
            lig_idx = t.topology.select("resname UNK and element != H")
            if len(lig_idx) == 0:
                lig_idx = t.topology.select("(not protein) and element != H")
            rmsd = md.rmsd(t, t, frame=0, atom_indices=lig_idx)
            rmsd_mean = float(rmsd.mean())
            rmsd_max = float(rmsd.max())
            rmsd_final = float(rmsd[-1])
        except Exception as e:
            rmsd_mean = rmsd_max = rmsd_final = float("nan")
            print(f"  RMSD calc failed: {e}")

        print(f"  ✅ {ns} ns in {wall/60:.1f} min, "
              f"RMSD mean={rmsd_mean*10:.2f} Å, max={rmsd_max*10:.2f} Å, "
              f"final={rmsd_final*10:.2f} Å")

        return {
            "name": name,
            "status": "ok",
            "wall_min": round(wall / 60, 2),
            "rmsd_mean_A": round(rmsd_mean * 10, 2),
            "rmsd_max_A": round(rmsd_max * 10, 2),
            "rmsd_final_A": round(rmsd_final * 10, 2),
            "ns_simulated": ns,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"name": name, "status": f"runtime error: {str(e)[:200]}"}


def main():
    print("=" * 72)
    print("Top-5 selective lead MD ensemble (10 ns × 5 = ~2.5h GPU)")
    print("=" * 72)

    results = []
    for job in JOBS:
        r = run_md(job["name"], job["cif"], job["smiles"], ns=10.0)
        results.append(r)
        with (OUT / "summary.json").open("w") as f:
            json.dump(results, f, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)

    print("\n" + "=" * 70)
    print("Top-5 Lead MD ensemble — final summary")
    print("=" * 70)
    if "rmsd_mean_A" in df.columns:
        print(df[["name", "status", "rmsd_mean_A", "rmsd_max_A", "wall_min"]].to_string(index=False))
    else:
        print(df.to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
