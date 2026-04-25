"""CHEMBL230245-BACE1 정식 10 ns MD + RMSD 분석.

100 ps 파일럿에서 안정 확인 (-30,600 kJ/mol). 이제 10 ns로 본격 안정성 검증.

결과물:
- traj.dcd (10,000 frames, 1 ps 간격)
- log.csv (PE/KE/T)
- rmsd.csv (ligand heavy atom RMSD vs frame 0)
- final.pdb
"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def main() -> int:
    base = Path(__file__).parent
    complex_cif = base / "output_affinity/boltz_results_inputs_affinity/predictions/bace1_chembl230245/bace1_chembl230245_model_0.cif"

    out_dir = base / "md_chembl230245_10ns"
    out_dir.mkdir(parents=True, exist_ok=True)

    lig_smiles = "CC(C)S(=O)(=O)N(C)c1cc(C(=O)N[C@@H](Cc2ccccc2)[C@@H](N)CF)cc(OC)c1"

    print("=" * 60)
    print("CHEMBL230245-BACE1 정식 10 ns MD")
    print("=" * 60)

    from openff.toolkit import Molecule
    import openmm as mm
    import openmm.app as app
    from openmm import unit
    from openmmforcefields.generators import SystemGenerator
    from pdbfixer import PDBFixer
    import numpy as np

    # 1. Ligand
    lig = Molecule.from_smiles(lig_smiles)
    lig.generate_conformers(n_conformers=1)

    # 2. Protein
    fixer = PDBFixer(filename=str(complex_cif))
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    # 3. SystemGenerator
    system_generator = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds},
    )

    # 4. Ligand centroid → 원본 포켓
    _orig = app.PDBxFile(str(complex_cif))
    lig_orig_pos = [_orig.positions[a.index] for a in _orig.topology.atoms()
                    if a.residue.name == "LIG1"]
    if lig_orig_pos:
        orig_centroid = np.mean([[p.x, p.y, p.z] for p in lig_orig_pos], axis=0)
        from openff.units import unit as off_unit
        coords = lig.conformers[0].m_as("nanometer")
        coords += orig_centroid - coords.mean(axis=0)
        lig._conformers = [coords * off_unit.nanometer]

    # 5. Combine
    modeller.addHydrogens(system_generator.forcefield, pH=7.4)
    modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())
    print(f"[setup] 최종 complex: {modeller.topology.getNumAtoms()} atoms")

    # 6. System + Integrator
    system = system_generator.create_system(modeller.topology)
    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtosecond,
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(modeller.topology, system, integrator, platform)
    sim.context.setPositions(modeller.positions)

    print("[minimize] 에너지 최소화 (500 steps)...")
    sim.minimizeEnergy(maxIterations=500)
    state_min = sim.context.getState(getEnergy=True)
    print(f"  PE = {state_min.getPotentialEnergy()}")

    # 7. Production MD — 10 ns = 5_000_000 steps @ 2 fs
    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
    steps_per_frame = 500   # 1 ps per frame
    total_steps = 5_000_000  # 10 ns

    sim.reporters.append(app.DCDReporter(str(out_dir / "traj.dcd"), steps_per_frame))
    sim.reporters.append(app.StateDataReporter(
        str(out_dir / "log.csv"),
        steps_per_frame,
        step=True, potentialEnergy=True, kineticEnergy=True, temperature=True,
        speed=True,
    ))

    print(f"[production] 10 ns MD ({total_steps:,} steps)...")
    t0 = time.time()
    sim.step(total_steps)
    wall = time.time() - t0
    print(f"  ✅ {wall/60:.1f} min ({total_steps/wall:.0f} steps/s = {total_steps*2e-6/wall*86400:.1f} ns/day)")

    final_pdb = out_dir / "final.pdb"
    with open(final_pdb, "w") as f:
        app.PDBFile.writeFile(
            sim.topology,
            sim.context.getState(getPositions=True).getPositions(),
            f,
        )

    # 8. RMSD 분석
    print("\n[analysis] ligand RMSD vs frame 0")
    try:
        import mdtraj as md
        t = md.load(str(out_dir / "traj.dcd"), top=str(final_pdb))
        # ligand heavy atoms (UNK or LIG resname)
        lig_indices = t.topology.select("resname UNK and element != H")
        if len(lig_indices) == 0:
            lig_indices = t.topology.select("(not protein) and element != H")
        print(f"  ligand heavy atoms: {len(lig_indices)}")
        rmsd = md.rmsd(t, t, frame=0, atom_indices=lig_indices)
        import pandas as pd
        pd.DataFrame({"frame": range(len(rmsd)), "rmsd_nm": rmsd}).to_csv(
            out_dir / "rmsd.csv", index=False,
        )
        print(f"  RMSD: mean={rmsd.mean():.3f} nm, max={rmsd.max():.3f} nm, final={rmsd[-1]:.3f} nm")
        print(f"  → {out_dir / 'rmsd.csv'}")
    except Exception as e:
        print(f"  RMSD 계산 실패: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
