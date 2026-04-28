"""CMS-19 MD extended — SREBP1 retry + 4 추가 target + EMB-3 baseline.

GPU saturate batch: 9 MD jobs × 10 ns ~= 70 min RTX 5090.
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_cms19_extended"
OUT.mkdir(parents=True, exist_ok=True)

CMS19_SMI = "COc1ccc(O)c(C=Cc2cc(O)c(O)c(O)c2)c1"
EMB3_SMI = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"

JOBS = [
    # SREBP1 retry — extended minimization
    {"name": "srebp1__cms19_retry",
     "cif": "pilot/cpu_meaningful/output_r9_srebp1/boltz_results_inputs_r9_srebp1/predictions/r9_srebp1_19/r9_srebp1_19_model_0.cif",
     "smiles": CMS19_SMI, "min_iters": 5000, "ns": 5.0},
    # CMS-19 × 4 추가 target (R7+R8+R9 affinity 상위)
    {"name": "mmp1__cms19",
     "cif": "pilot/cpu_meaningful/output_r9_mmp1/boltz_results_inputs_r9_mmp1/predictions/r9_mmp1_19/r9_mmp1_19_model_0.cif",
     "smiles": CMS19_SMI, "min_iters": 1000, "ns": 10.0},
    {"name": "mitf__cms19",
     "cif": "pilot/cpu_meaningful/output_r9_mitf/boltz_results_inputs_r9_mitf/predictions/r9_mitf_19/r9_mitf_19_model_0.cif",
     "smiles": CMS19_SMI, "min_iters": 1000, "ns": 10.0},
    {"name": "tyr__cms19",
     "cif": "pilot/cpu_meaningful/output_r9_tyr/boltz_results_inputs_r9_tyr/predictions/r9_tyr_19/r9_tyr_19_model_0.cif",
     "smiles": CMS19_SMI, "min_iters": 1000, "ns": 10.0},
    {"name": "tyrp1__cms19",
     "cif": "pilot/cpu_meaningful/output_r9_tyrp1/boltz_results_inputs_r9_tyrp1/predictions/r9_tyrp1_19/r9_tyrp1_19_model_0.cif",
     "smiles": CMS19_SMI, "min_iters": 1000, "ns": 10.0},
]


def run_md(name: str, cif: str, smiles: str, ns: float = 10.0,
            min_iters: int = 1000) -> dict:
    cif_path = ROOT / cif
    if not cif_path.exists():
        return {"name": name, "status": "missing_cif", "cif": cif}

    out_dir = OUT / name
    out_dir.mkdir(exist_ok=True)
    print(f"\n=== {name} (min={min_iters}, ns={ns}) ===")

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
            310 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtosecond,
        )
        try:
            platform = mm.Platform.getPlatformByName("CUDA")
            sim = app.Simulation(modeller.topology, system, integrator, platform)
        except Exception:
            sim = app.Simulation(modeller.topology, system, integrator)

        sim.context.setPositions(modeller.positions)
        sim.minimizeEnergy(maxIterations=min_iters)
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
            app.PDBFile.writeFile(sim.topology,
                                  sim.context.getState(getPositions=True).getPositions(), f)

        try:
            import mdtraj as md
            t = md.load(str(out_dir / "traj.dcd"), top=str(final_pdb))
            lig_idx = t.topology.select("resname UNK and element != H")
            if len(lig_idx) == 0:
                lig_idx = t.topology.select("(not protein) and element != H")
            rmsd = md.rmsd(t, t, frame=0, atom_indices=lig_idx)
            return {"name": name, "status": "ok",
                    "wall_min": round(wall / 60, 2),
                    "rmsd_mean_A": round(float(rmsd.mean()) * 10, 2),
                    "rmsd_max_A": round(float(rmsd.max()) * 10, 2),
                    "rmsd_final_A": round(float(rmsd[-1]) * 10, 2),
                    "ns_simulated": ns}
        except Exception as e:
            return {"name": name, "wall_min": round(wall / 60, 2),
                    "status": f"rmsd_err: {str(e)[:100]}"}
    except Exception as e:
        return {"name": name, "status": f"runtime: {str(e)[:200]}"}


def main():
    print("=" * 72)
    print("CMS-19 MD extended — SREBP1 retry + 4 추가 target")
    print("=" * 72)
    results = []
    for job in JOBS:
        r = run_md(job["name"], job["cif"], job["smiles"],
                    ns=job.get("ns", 10.0),
                    min_iters=job.get("min_iters", 1000))
        results.append(r)
        print(f"[result] {r}")
        with (OUT / "summary.json").open("w") as f:
            json.dump(results, f, indent=2)
    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    paper_tier = sum(1 for r in results
                       if r.get("rmsd_mean_A", 999) < 2.0)
    print(f"\nPaper-tier: {paper_tier}/{len(results)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
