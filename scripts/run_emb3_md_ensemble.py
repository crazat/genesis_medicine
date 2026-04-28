"""EMB-3 MD ensemble — 7 targets × 10 ns each (head-to-head with CMS-19)."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_emb3_baseline"
OUT.mkdir(parents=True, exist_ok=True)

EMB3_SMI = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"

# Cofold cif paths
PREDICT_DIR = OUT / "boltz_output/boltz_results_boltz_inputs/predictions"

JOBS = [
    {"name": f"{t}__emb3",
     "cif": str(PREDICT_DIR / f"{t}__emb3" / f"{t}__emb3_model_0.cif"),
     "smiles": EMB3_SMI}
    for t in ["tgfb1", "mmp1", "ctgf", "srd5a1", "mitf", "tyr", "tyrp1"]
]


def run_md(name: str, cif: str, smiles: str, ns: float = 10.0) -> dict:
    cif_path = Path(cif)
    if not cif_path.exists():
        return {"name": name, "status": "missing_cif", "cif": cif}
    out_dir = OUT / "md" / name
    out_dir.mkdir(parents=True, exist_ok=True)
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
        return {"name": name, "status": f"import: {e}"}
    try:
        lig = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
        lig.generate_conformers(n_conformers=1)
    except Exception as e:
        return {"name": name, "status": f"ligand: {e}"}
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
            platform = mm.Platform.getPlatformByName("CUDA")
            sim = app.Simulation(modeller.topology, system, integrator, platform)
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
            return {"name": name, "status": f"rmsd: {e}",
                    "wall_min": round(wall / 60, 2)}
    except Exception as e:
        return {"name": name, "status": f"runtime: {str(e)[:200]}"}


def main():
    print("=" * 72)
    print("EMB-3 MD baseline ensemble — 7 × 10 ns (head-to-head with CMS-19)")
    print("=" * 72)
    results = []
    for job in JOBS:
        r = run_md(job["name"], job["cif"], job["smiles"], ns=10.0)
        results.append(r)
        print(f"[result] {r}")
        with (OUT / "md_summary.json").open("w") as f:
            json.dump(results, f, indent=2)
    df = pd.DataFrame(results)
    df.to_csv(OUT / "md_summary.csv", index=False)
    paper_tier = sum(1 for r in results if r.get("rmsd_mean_A", 999) < 2.0)
    print(f"\nPaper-tier: {paper_tier}/{len(results)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
