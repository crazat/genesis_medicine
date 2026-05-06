"""4 PAINS-free leaders × additional MD ensembles for primary CRO target validation.

R12_4   (hydroxymethyl) × CTGF + AR + LOX + SREBP1
R12_11  (methoxy) × MMP1 + SIRT1 + MITF + SREBP1
R12_23  (methyl ester) × MITF + AR + DCT
R14_5   (methoxy variant 2) × TGFB1 + AR + SIRT1 + SRD5A1

Sequential 10 ns × 15 = ~120 min GPU. Output: pilot/md_pains_free_4leaders
"""
from __future__ import annotations

import json, os, sys, time
from pathlib import Path
import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_pains_free_4leaders"
OUT.mkdir(parents=True, exist_ok=True)


JOBS = [
    # R12_4 hydroxymethyl variant (PAINS-free, primary CRO target)
    {"name": "ctgf__r12_4",   "round": "r12", "idx": 4, "tgt": "ctgf",
     "smiles": "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    {"name": "ar__r12_4",     "round": "r12", "idx": 4, "tgt": "ar",
     "smiles": "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    {"name": "lox__r12_4",    "round": "r12", "idx": 4, "tgt": "lox",
     "smiles": "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    {"name": "srebp1__r12_4", "round": "r12", "idx": 4, "tgt": "srebp1",
     "smiles": "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    # R12_11 methoxy variant (3-cycle re-discovered, primary CRO target)
    {"name": "mmp1__r12_11",   "round": "r12", "idx": 11, "tgt": "mmp1",
     "smiles": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"},
    {"name": "sirt1__r12_11",  "round": "r12", "idx": 11, "tgt": "sirt1",
     "smiles": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"},
    {"name": "mitf__r12_11",   "round": "r12", "idx": 11, "tgt": "mitf",
     "smiles": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"},
    {"name": "srebp1__r12_11", "round": "r12", "idx": 11, "tgt": "srebp1",
     "smiles": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"},
    # R12_23 methyl ester (TYR-selective lead, additional confirmation)
    {"name": "mitf__r12_23",   "round": "r12", "idx": 23, "tgt": "mitf",
     "smiles": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"},
    {"name": "ar__r12_23",     "round": "r12", "idx": 23, "tgt": "ar",
     "smiles": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"},
    {"name": "dct__r12_23",    "round": "r12", "idx": 23, "tgt": "dct",
     "smiles": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"},
    # R14_5 methoxy variant 2 (highest Korean herbal alignment, primary CRO target)
    {"name": "tgfb1__r14_5",   "round": "r14", "idx": 5, "tgt": "tgfb1",
     "smiles": "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    {"name": "ar__r14_5",      "round": "r14", "idx": 5, "tgt": "ar",
     "smiles": "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    {"name": "sirt1__r14_5",   "round": "r14", "idx": 5, "tgt": "sirt1",
     "smiles": "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
    {"name": "srd5a1__r14_5",  "round": "r14", "idx": 5, "tgt": "srd5a1",
     "smiles": "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"},
]


def cif_path(job):
    return ("pilot/cpu_meaningful/output_{r}_{tgt}/boltz_results_inputs_{r}_{tgt}/"
            "predictions/{r}_{tgt}_{i}/{r}_{tgt}_{i}_model_0.cif").format(
        r=job["round"], tgt=job["tgt"], i=job["idx"])


def run_md(name, cif, smiles, ns=10.0):
    cif_path = ROOT / cif
    if not cif_path.exists():
        return {"name": name, "status": "missing_cif", "cif": cif}

    out_dir = OUT / name
    out_dir.mkdir(exist_ok=True)
    print(f"\n{'=' * 70}\n=== {name} ===\n  SMILES: {smiles}")

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
            310 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtosecond)
        try:
            sim = app.Simulation(modeller.topology, system, integrator,
                                  mm.Platform.getPlatformByName("CUDA"))
            print("  CUDA")
        except Exception:
            sim = app.Simulation(modeller.topology, system, integrator)

        sim.context.setPositions(modeller.positions)
        sim.minimizeEnergy(maxIterations=300)
        sim.context.setVelocitiesToTemperature(310 * unit.kelvin)

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
            rmsd_mean = float(rmsd.mean())
            rmsd_max = float(rmsd.max())
            rmsd_final = float(rmsd[-1])
        except Exception as e:
            rmsd_mean = rmsd_max = rmsd_final = float("nan")

        print(f"  ✅ {ns} ns in {wall/60:.1f} min, RMSD mean={rmsd_mean*10:.2f} Å, "
              f"max={rmsd_max*10:.2f} Å")

        return {
            "name": name, "status": "ok",
            "wall_min": round(wall / 60, 2),
            "rmsd_mean_A": round(rmsd_mean * 10, 2),
            "rmsd_max_A": round(rmsd_max * 10, 2),
            "rmsd_final_A": round(rmsd_final * 10, 2),
            "ns_simulated": ns,
        }

    except Exception as e:
        import traceback; traceback.print_exc()
        return {"name": name, "status": f"runtime error: {str(e)[:200]}"}


def main():
    print("=" * 72)
    print("4 PAINS-free leaders × 15 protein targets MD ensemble (CRO target validation)")
    print("=" * 72)

    results = []
    for job in JOBS:
        r = run_md(job["name"], cif_path(job), job["smiles"], ns=10.0)
        results.append(r)
        with (OUT / "summary.json").open("w") as f:
            json.dump(results, f, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)

    print("\n" + "=" * 70)
    print("4 PAINS-free leaders MD ensemble — final summary")
    print("=" * 70)
    if "rmsd_mean_A" in df.columns:
        print(df[["name", "status", "rmsd_mean_A", "rmsd_max_A", "wall_min"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
