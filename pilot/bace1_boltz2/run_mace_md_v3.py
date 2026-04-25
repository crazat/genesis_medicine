"""CHEMBL230245-BACE1 complex ML-MM MD (v3, genesis-md conda env).

v3 설계
-------
1. Boltz-2 CIF에서 protein + ligand 분리
2. ligand SMILES → OpenFF Molecule + SystemGenerator로 GAFF-2 파라미터화
3. Modeller.addHydrogens로 수소 보강
4. AMBER ff14SB + GAFF-2 결합 시스템 생성
5. (옵션) MACE-OFF23 overlay on ligand atoms
6. 짧은 gas-phase 100 ps MD

실행:
    conda activate genesis-md
    python pilot/bace1_boltz2/run_mace_md_v3.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def main() -> int:
    base = Path(__file__).parent
    complex_cif = base / "output_affinity/boltz_results_inputs_affinity/predictions/bace1_chembl230245/bace1_chembl230245_model_0.cif"
    assert complex_cif.exists(), f"복합체 CIF 없음: {complex_cif}"

    out_dir = base / "md_chembl230245_v3"
    out_dir.mkdir(parents=True, exist_ok=True)

    # CHEMBL230245 SMILES (pilot YAML에서)
    lig_smiles = "CC(C)S(=O)(=O)N(C)c1cc(C(=O)N[C@@H](Cc2ccccc2)[C@@H](N)CF)cc(OC)c1"

    print("=" * 60)
    print("CHEMBL230245-BACE1 ML-MM MD (v3)")
    print("=" * 60)

    # ------ Step 1: Ligand OpenFF Molecule ------
    print("\n[1/5] Ligand SMILES → OpenFF Molecule")
    from openff.toolkit import Molecule

    try:
        lig = Molecule.from_smiles(lig_smiles)
        lig.generate_conformers(n_conformers=1)
        print(f"  ✅ {lig.n_atoms} atoms (with H), {lig.n_bonds} bonds")
    except Exception as e:
        print(f"  ❌ SMILES 파싱 실패: {e}")
        return 1

    # ------ Step 2: PDBFixer로 terminal cap 추가 후 protein-only 로드 ------
    print("\n[2/5] PDBFixer로 terminal 보강 + ligand 분리")
    import openmm.app as app
    from openmm import unit
    from pdbfixer import PDBFixer

    fixer = PDBFixer(filename=str(complex_cif))
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)   # LIG1 포함 heterogen 모두 제거 (나중에 추가)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    # terminal 문제 해결을 위해 pdbfixer 제거 후 app.ForceField의 ignoreExternalBonds 대신
    # 마지막 PHE에 C-term cap 인식 문제는 atom 누락일 가능성 높음
    print(f"  PDBFixer 후: {fixer.topology.getNumAtoms()} atoms, "
          f"{fixer.topology.getNumResidues()} residues")

    modeller_full = app.Modeller(fixer.topology, fixer.positions)
    print(f"  protein-only: {modeller_full.topology.getNumAtoms()} atoms")

    # ------ Step 3: SystemGenerator (AMBER + GAFF-2) ------
    print("\n[3/5] SystemGenerator — AMBER ff14SB + GAFF-2 for ligand")
    from openmmforcefields.generators import SystemGenerator

    forcefield_kwargs = {"constraints": app.HBonds}
    system_generator = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs=forcefield_kwargs,
    )
    print("  ✅ SystemGenerator 초기화 (ff14SB + GAFF-2.11)")

    # ------ Step 4: ligand를 OpenMM topology로 변환 후 합치기 ------
    print("\n[4/5] Protein + Ligand topology 결합")
    import numpy as np

    # ligand OpenFF Molecule → openmm Topology
    lig_top = lig.to_topology().to_openmm()
    lig_pos = lig.conformers[0].to_openmm()

    # Boltz-2 원본에서 LIG1 위치 추출 (포켓 정렬용)
    _orig = app.PDBxFile(str(complex_cif))
    original_lig_positions = []
    for atom in _orig.topology.atoms():
        if atom.residue.name == "LIG1":
            original_lig_positions.append(_orig.positions[atom.index])
    print(f"  원본 LIG1 heavy atoms: {len(original_lig_positions)}")
    print(f"  OpenFF ligand: {lig.n_atoms} atoms (H 포함)")

    # 원본 heavy-atom 좌표의 centroid로 OpenFF conformer 이동
    if original_lig_positions:
        import numpy as np
        orig_centroid = np.mean(
            [[p.x, p.y, p.z] for p in original_lig_positions], axis=0
        )
        lig_coords = lig.conformers[0].m_as("nanometer")  # (N, 3)
        lig_centroid = lig_coords.mean(axis=0)
        shift = orig_centroid - lig_centroid
        shifted = lig_coords + shift
        from openff.units import unit as off_unit
        lig._conformers = [shifted * off_unit.nanometer]
        lig_pos = lig.conformers[0].to_openmm()
        print(f"  ligand centroid → 원본 포켓 ({orig_centroid.round(2)})")

    # 순서 중요: (a) 단백질에만 먼저 수소 추가, (b) ligand를 그 후에 add.
    # ligand가 먼저 있으면 addHydrogens가 전체를 순회하며 terminal cap 누락을 감지함.
    modeller_full.addHydrogens(system_generator.forcefield, pH=7.4)
    print(f"  protein (+H): {modeller_full.topology.getNumAtoms()} atoms")

    modeller_full.add(lig_top, lig_pos)
    print(f"  최종 complex: {modeller_full.topology.getNumAtoms()} atoms")

    # ------ Step 5: System 생성 + Minimize + 짧은 MD ------
    print("\n[5/5] System 생성 + 최소화 + 100 ps NVT (gas phase)")
    import openmm as mm

    system = system_generator.create_system(modeller_full.topology)

    # (간단화) MACE-OFF23 overlay 생략 — 우선 classical MD로 setup 검증
    # 다음 세션: ml_atoms = [i for i,a in enumerate(modeller_full.topology.atoms()) if a.residue.name in {"UNK","LIG","UNL"}]

    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin,
        1.0 / unit.picosecond,
        1.0 * unit.femtosecond,
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(modeller_full.topology, system, integrator, platform)
    sim.context.setPositions(modeller_full.positions)

    state0 = sim.context.getState(getEnergy=True)
    print(f"  초기 PE: {state0.getPotentialEnergy()}")

    sim.minimizeEnergy(maxIterations=500)
    state1 = sim.context.getState(getEnergy=True)
    print(f"  최소화 후 PE: {state1.getPotentialEnergy()}")

    # 짧은 MD
    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)

    steps_per_frame = 1000  # 1 ps
    total_steps = 100_000    # 100 ps
    sim.reporters.append(app.DCDReporter(str(out_dir / "traj.dcd"), steps_per_frame))
    sim.reporters.append(app.StateDataReporter(
        str(out_dir / "log.csv"),
        steps_per_frame,
        step=True, potentialEnergy=True, kineticEnergy=True, temperature=True,
    ))

    t0 = time.time()
    sim.step(total_steps)
    wall = time.time() - t0
    print(f"\n  ✅ 100 ps MD 완료 in {wall:.1f}s ({total_steps/wall:.0f} steps/s)")

    final_pdb = out_dir / "final.pdb"
    with open(final_pdb, "w") as f:
        app.PDBFile.writeFile(
            sim.topology,
            sim.context.getState(getPositions=True).getPositions(),
            f,
        )
    print(f"  최종 구조: {final_pdb}")
    print(f"\n=== 완료 ===\n  로그: {out_dir / 'log.csv'}\n  트라젝토리: {out_dir / 'traj.dcd'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
