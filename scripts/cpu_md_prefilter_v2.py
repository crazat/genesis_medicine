"""MD prefilter v2 — uses OpenMMForceFields GAFF (already in venv) instead of
openff sage. Heavy CPU 100 ps simulation per top integrated candidate.
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def md_one(args):
    idx, target, compound, smi = args
    try:
        import openmm
        import openmm.app as app
        import openmm.unit as unit
        from openmmforcefields.generators import GAFFTemplateGenerator
        from openff.toolkit import Molecule
        from rdkit import Chem, RDLogger
        from rdkit.Chem import AllChem
        RDLogger.DisableLog("rdApp.*")

        m = Chem.MolFromSmiles(smi)
        if m is None:
            return {"idx": idx, "target": target, "compound": compound,
                    "passed": False, "error": "parse"}
        m = Chem.AddHs(m)
        cid = AllChem.EmbedMolecule(m, randomSeed=42)
        if cid < 0:
            return {"idx": idx, "target": target, "compound": compound,
                    "passed": False, "error": "embed"}
        AllChem.MMFFOptimizeMolecule(m, maxIters=500)

        # Write to PDB
        import io
        from openff.toolkit import Molecule as OFFMolecule
        # Build via openff (this approach uses GAFF via openmmforcefields)
        ofmol = OFFMolecule.from_rdkit(m)
        ofmol.assign_partial_charges("am1bcc")

        # Topology + system via GAFF
        gaff = GAFFTemplateGenerator(molecules=[ofmol])
        ff = app.ForceField()
        ff.registerTemplateGenerator(gaff.generator)

        ofmol_topology = ofmol.to_topology().to_openmm()
        ofmol_positions = ofmol.conformers[0].to_openmm()

        system = ff.createSystem(ofmol_topology, nonbondedMethod=app.NoCutoff,
                                   constraints=app.HBonds)

        integrator = openmm.LangevinMiddleIntegrator(
            300 * unit.kelvin, 1.0 / unit.picosecond,
            2.0 * unit.femtosecond)
        platform = openmm.Platform.getPlatformByName("CPU")
        sim = app.Simulation(ofmol_topology, system, integrator, platform)
        sim.context.setPositions(ofmol_positions)
        sim.minimizeEnergy(maxIterations=200)

        e0 = sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilocalorie_per_mole)
        p0 = sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)

        sim.context.setVelocitiesToTemperature(300 * unit.kelvin)
        sim.step(50000)    # 100 ps

        pf = sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        ef = sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilocalorie_per_mole)

        rmsd = float(np.sqrt(((pf - p0) ** 2).sum(axis=1).mean()) * 10)

        return {
            "idx": idx,
            "target": target,
            "compound": compound,
            "smi": smi,
            "rmsd_A": rmsd,
            "initial_energy_kcal": float(e0),
            "final_energy_kcal": float(ef),
            "delta_E_kcal": float(ef - e0),
            "passed": rmsd < 5.0 and not np.isnan(ef),
        }
    except Exception as e:
        return {"idx": idx, "target": target, "compound": compound,
                "passed": False, "error": str(e)[:160]}


def main():
    print("=" * 72)
    print("MD prefilter v2 — GAFF + OpenMM 100 ps per molecule (Pool 8)")
    print("=" * 72)

    df = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    df = df.dropna(subset=["smiles"])
    args_list = []
    for tgt, sub in df.groupby("target"):
        for i, (_, r) in enumerate(sub.head(5).iterrows()):
            args_list.append((i, tgt, r["compound"], r["smiles"]))
    print(f"MD simulations: {len(args_list)}")

    t0 = time.time()
    with Pool(processes=8) as pool:
        results = pool.map(md_one, args_list)
    print(f"\nWall time: {(time.time() - t0) / 60:.1f} min")

    res_df = pd.DataFrame(results)
    res_df.to_csv(OUT / "md_prefilter_v2_results.csv", index=False)
    print(f"\n✅ md_prefilter_v2_results.csv ({len(res_df)} rows)")

    if "passed" in res_df.columns:
        n_pass = res_df["passed"].sum()
        print(f"  Pose-stable: {n_pass}/{len(res_df)}")
    if "rmsd_A" in res_df.columns:
        valid = res_df["rmsd_A"].dropna()
        if len(valid) > 0:
            print(f"  RMSD: {valid.min():.2f}-{valid.max():.2f} Å, "
                  f"mean {valid.mean():.2f}")
    if "error" in res_df.columns:
        n_err = res_df["error"].notna().sum()
        if n_err > 0:
            print(f"  Errors: {n_err}, first: {res_df['error'].dropna().iloc[0][:120]}")


if __name__ == "__main__":
    sys.exit(main())
