"""R13_13 × 10 missing skin targets MD — 5th leader (prenyl variant, PAINS-flagged).

Already done (4): TGFB1, AR, SIRT1, SREBP1 (md_r14_5_r13_13)
Missing (10): MMP1, CTGF, MITF, LOX, TYR, TYRP1, DCT, SRD5A1, SRD5A2, PTGS2

Output: pilot/md_r13_13_full14
"""
from __future__ import annotations

import json, os, sys, time
from pathlib import Path
import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r13_13_full14"
OUT.mkdir(parents=True, exist_ok=True)

# R13_13 SMILES — confirm by checking actual round 13 cofold inputs
R13_13_SMI_FALLBACK = "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1"  # Prenyl R11_0 variant

JOBS = [
    {"name": "mmp1__r13_13",   "tgt": "mmp1"},
    {"name": "ctgf__r13_13",   "tgt": "ctgf"},
    {"name": "mitf__r13_13",   "tgt": "mitf"},
    {"name": "lox__r13_13",    "tgt": "lox"},
    {"name": "tyr__r13_13",    "tgt": "tyr"},
    {"name": "tyrp1__r13_13",  "tgt": "tyrp1"},
    {"name": "dct__r13_13",    "tgt": "dct"},
    {"name": "srd5a1__r13_13", "tgt": "srd5a1"},
    {"name": "srd5a2__r13_13", "tgt": "srd5a2"},
    {"name": "ptgs2__r13_13",  "tgt": "ptgs2"},
]


def get_smiles_for_target(tgt):
    """Read SMILES from round-13 candidates CSV if available."""
    candidates_csv = ROOT / "pilot/cpu_meaningful/bayesian_v9_round13_candidates.csv"
    if candidates_csv.exists():
        try:
            df = pd.read_csv(candidates_csv)
            row13 = df.iloc[13] if len(df) > 13 else None
            if row13 is not None and "smiles" in df.columns:
                return row13["smiles"]
        except Exception:
            pass
    return R13_13_SMI_FALLBACK


def run_md(name, cif, smiles, ns=10.0):
    cif_path = ROOT / cif
    if not cif_path.exists():
        return {"name": name, "status": "missing_cif", "cif": cif}

    out_dir = OUT / name
    out_dir.mkdir(exist_ok=True)
    print(f"\n=== {name} ===")

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
        fixer.findMissingResidues(); fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues(); fixer.removeHeterogens(keepWater=False)
        fixer.findMissingAtoms(); fixer.addMissingAtoms()
        modeller = app.Modeller(fixer.topology, fixer.positions)

        sg = SystemGenerator(
            forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
            small_molecule_forcefield="gaff-2.11",
            molecules=[lig], forcefield_kwargs={"constraints": app.HBonds})

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
            310 * unit.kelvin, 1.0 / unit.picosecond, 1.0 * unit.femtosecond)
        try:
            sim = app.Simulation(modeller.topology, system, integrator,
                                  mm.Platform.getPlatformByName("CUDA"))
        except Exception:
            sim = app.Simulation(modeller.topology, system, integrator)

        sim.context.setPositions(modeller.positions)
        sim.minimizeEnergy(maxIterations=1000)
        sim.context.setVelocitiesToTemperature(150 * unit.kelvin)
        sim.step(12500)
        sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
        sim.step(12500)
        integrator.setStepSize(2.0 * unit.femtosecond)

        steps_per_frame = 500
        total_steps = int(ns * 500_000)
        sim.reporters.append(app.DCDReporter(str(out_dir / "traj.dcd"), steps_per_frame))
        sim.reporters.append(app.StateDataReporter(
            str(out_dir / "log.csv"), steps_per_frame,
            step=True, potentialEnergy=True, temperature=True, speed=True))

        t0 = time.time()
        sim.step(total_steps)
        wall = time.time() - t0

        final_pdb = out_dir / "final.pdb"
        with open(final_pdb, "w") as f:
            app.PDBFile.writeFile(
                sim.topology,
                sim.context.getState(getPositions=True).getPositions(), f)

        try:
            import mdtraj as md
            t = md.load(str(out_dir / "traj.dcd"), top=str(final_pdb))
            lig_idx = t.topology.select("resname UNK")
            if len(lig_idx) == 0:
                lig_idx = t.topology.select("not protein")
            rmsd = md.rmsd(t, t, frame=0, atom_indices=lig_idx)
            rmsd_mean = float(rmsd.mean()); rmsd_max = float(rmsd.max())
            rmsd_final = float(rmsd[-1])
        except Exception:
            rmsd_mean = rmsd_max = rmsd_final = float("nan")

        print(f"  ✅ {ns} ns in {wall/60:.1f} min, RMSD mean={rmsd_mean*10:.2f} max={rmsd_max*10:.2f}")
        return {
            "name": name, "status": "ok",
            "wall_min": round(wall / 60, 2),
            "rmsd_mean_A": round(rmsd_mean * 10, 2),
            "rmsd_max_A": round(rmsd_max * 10, 2),
            "rmsd_final_A": round(rmsd_final * 10, 2),
            "ns_simulated": ns}

    except Exception as e:
        import traceback; traceback.print_exc()
        return {"name": name, "status": f"runtime error: {str(e)[:200]}"}


def main():
    smi = R13_13_SMI_FALLBACK
    print(f"R13_13 SMILES: {smi}")
    print("R13_13 (prenyl variant, PAINS-flagged) × 10 missing skin targets")
    results = []
    for job in JOBS:
        cif = (f"pilot/cpu_meaningful/output_r13_{job['tgt']}/boltz_results_inputs_r13_{job['tgt']}/"
               f"predictions/r13_{job['tgt']}_13/r13_{job['tgt']}_13_model_0.cif")
        r = run_md(job["name"], cif, smi, ns=10.0)
        results.append(r)
        with (OUT / "summary.json").open("w") as f:
            json.dump(results, f, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\n" + df[["name", "status", "rmsd_mean_A", "rmsd_max_A", "wall_min"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
