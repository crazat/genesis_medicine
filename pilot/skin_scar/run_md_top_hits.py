"""흉터 Top hit (Embelin/EGCG/Curcumin) × 3 타겟 = 9 MD 10ns 검증.

기존 v3 MD 스크립트 (CHEMBL230245용) 참고하여 generic 화. 각 hit-target에 대해
- PDBFixer로 protein 보강
- OpenFF로 ligand parameterize
- AMBER ff14SB + GAFF-2.11
- 10 ns gas-phase MD
- ligand RMSD vs frame 0
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).parent
BOLTZ_OUT = PILOT / "results_v2/boltz2_output/boltz_results_boltz2_inputs/predictions"
OUT = PILOT / "md_top_hits"
OUT.mkdir(parents=True, exist_ok=True)

# Top hits + SMILES (skin_compounds_curated.csv에서 추출)
TARGETS = ["tgfb1", "mmp1", "ctgf"]
COMPOUNDS = {
    "embelin": "CCCCCCCCCCCC1=CC(=O)C(=C(C1=O)O)O",
    "egcg":    "C1[C@H]([C@H](OC2=CC(=CC(=C21)O)O)C3=CC(=C(C(=C3)O)O)O)OC(=O)C4=CC(=C(C(=C4)O)O)O",
    "curcumin": "COC1=C(C=CC(=C1)/C=C/C(=O)CC(=O)/C=C/C2=CC(=C(C=C2)O)OC)O",
}


def run_md_for(target: str, compound: str, smiles: str, ns: float = 10.0) -> dict:
    """단일 (target, compound) MD 10ns."""
    cif = BOLTZ_OUT / f"{target}__{compound}" / f"{target}__{compound}_model_0.cif"
    if not cif.exists():
        return {"target": target, "compound": compound, "status": "missing_cif"}

    out_dir = OUT / f"{target}__{compound}"
    out_dir.mkdir(exist_ok=True)
    print(f"\n=== {target} × {compound} ===")
    print(f"  CIF: {cif}")

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
        return {"target": target, "compound": compound, "status": f"import error: {e}"}

    # Ligand
    lig = Molecule.from_smiles(smiles)
    lig.generate_conformers(n_conformers=1)

    # Protein 보강
    fixer = PDBFixer(filename=str(cif))
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    # SystemGenerator
    sg = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds},
    )

    # Centroid 정렬
    _orig = app.PDBxFile(str(cif))
    lig_orig = [_orig.positions[a.index] for a in _orig.topology.atoms()
                if a.residue.name == "LIG1"]
    if lig_orig:
        oc = np.mean([[p.x, p.y, p.z] for p in lig_orig], axis=0)
        coords = lig.conformers[0].m_as("nanometer")
        coords += oc - coords.mean(axis=0)
        lig._conformers = [coords * off_unit.nanometer]

    # Combine
    modeller.addHydrogens(sg.forcefield, pH=7.4)
    modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())

    system = sg.create_system(modeller.topology)
    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0/unit.picosecond, 2.0*unit.femtosecond,
    )
    sim = app.Simulation(modeller.topology, system, integrator,
                         mm.Platform.getPlatformByName("CUDA"))
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=300)
    sim.context.setVelocitiesToTemperature(310*unit.kelvin)

    steps_per_frame = 500           # 1 ps
    total_steps = int(ns * 500_000)
    sim.reporters.append(app.DCDReporter(str(out_dir/"traj.dcd"), steps_per_frame))
    sim.reporters.append(app.StateDataReporter(
        str(out_dir/"log.csv"), steps_per_frame,
        step=True, potentialEnergy=True, kineticEnergy=True, temperature=True, speed=True,
    ))

    t0 = time.time()
    sim.step(total_steps)
    wall = time.time() - t0

    final_pdb = out_dir / "final.pdb"
    with open(final_pdb, "w") as f:
        app.PDBFile.writeFile(sim.topology,
                              sim.context.getState(getPositions=True).getPositions(),
                              f)

    # RMSD
    try:
        import mdtraj as md
        t = md.load(str(out_dir/"traj.dcd"), top=str(final_pdb))
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

    print(f"  ✅ {ns} ns in {wall/60:.1f}분, RMSD mean={rmsd_mean*10:.2f} Å, "
          f"max={rmsd_max*10:.2f} Å")

    return {
        "target": target, "compound": compound,
        "status": "ok",
        "wall_min": round(wall/60, 2),
        "rmsd_mean_A": round(rmsd_mean*10, 2),
        "rmsd_max_A": round(rmsd_max*10, 2),
        "rmsd_final_A": round(rmsd_final*10, 2),
    }


def main() -> int:
    results = []
    for compound, smiles in COMPOUNDS.items():
        for target in TARGETS:
            r = run_md_for(target, compound, smiles, ns=10.0)
            results.append(r)
            with (OUT / "summary.json").open("w") as f:
                json.dump(results, f, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\n" + "=" * 70)
    print("MD 10ns Top hits 검증 — 종합")
    print("=" * 70)
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
