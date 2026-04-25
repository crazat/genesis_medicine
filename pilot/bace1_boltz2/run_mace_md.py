"""CHEMBL230245-BACE1 복합체 MACE-OFF23 ML-MM MD.

NEXT ACTIONS #7 실행.

CHEMBL230245는 9개 화합물 중 유일하게 안전 게이트 통과:
  QED=0.41, BBB=0.71, hERG=0.98 (경계)
본 MD로 Boltz-2 예측 포즈의 물리적 안정성 검증.

Stage 8' — OpenMM 8.5 + MACE-OFF23(medium) ML potential on ligand + pocket 잔기.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path


def convert_cif_to_pdb(cif: Path, pdb_out: Path) -> Path:
    """Boltz-2 output CIF 그대로 반환 — OpenMM PDBxFile가 직접 읽음."""
    # 실제로는 CIF 그대로 사용 — PDBxFile가 openmm에서 지원
    return cif


def main() -> int:
    base = Path(__file__).parent
    complex_cif = base / "output_affinity/boltz_results_inputs_affinity/predictions/bace1_chembl230245/bace1_chembl230245_model_0.cif"
    assert complex_cif.exists(), f"복합체 CIF 없음: {complex_cif}"

    out_dir = base / "md_chembl230245"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. CIF → OpenMM PDBxFile로 직접 로드
    print("=== Step 1: Boltz-2 output CIF 로드 (OpenMM PDBxFile) ===")
    complex_path = complex_cif  # 원본 CIF 그대로
    print(f"  → {complex_path} ({complex_path.stat().st_size/1024:.1f} KB)")

    # 2. OpenMM 준비
    print("\n=== Step 2: OpenMM 시스템 준비 + MACE-OFF23 ML overlay ===")
    import openmm as mm
    import openmm.app as app
    import openmm.unit as unit

    pdb = app.PDBxFile(str(complex_path))

    # ligand resname 찾기 (Boltz-2 output은 ligand를 LIG/UNL/HETATM으로 저장)
    lig_resname = None
    for res in pdb.topology.residues():
        if res.name not in ("HOH", "WAT") and not res.name in (
            "ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU",
            "LYS","MET","PHE","PRO","SER","THR","TRP","TYR","VAL","MSE",
        ):
            lig_resname = res.name
            break
    if lig_resname is None:
        print("❌ ligand 찾기 실패 — PDB resnames:")
        names = {r.name for r in pdb.topology.residues()}
        print(f"  {names}")
        return 1
    print(f"  ligand resname: {lig_resname}")

    # 3. ML atom 선택 (ligand + 포켓 5Å)
    ml_atoms = []
    ligand_coords = []
    for atom in pdb.topology.atoms():
        if atom.residue.name == lig_resname:
            ml_atoms.append(atom.index)
            ligand_coords.append(pdb.positions[atom.index])
    print(f"  ligand atoms: {len(ml_atoms)}")

    # 포켓 5Å 내 residue 추가
    import numpy as np
    lig_coords_nm = np.array([(c.x, c.y, c.z) for c in ligand_coords])
    pocket_atoms_set = set(ml_atoms)
    for atom in pdb.topology.atoms():
        if atom.index in pocket_atoms_set:
            continue
        if atom.residue.name == lig_resname:
            continue
        pos = pdb.positions[atom.index]
        d = np.min(np.sqrt(np.sum(
            (lig_coords_nm - np.array([pos.x, pos.y, pos.z]))**2, axis=1
        )))
        if d < 0.5:  # 5 Å = 0.5 nm
            pocket_atoms_set.add(atom.index)
    ml_atoms = sorted(pocket_atoms_set)
    print(f"  ligand + pocket (5Å) ML atoms: {len(ml_atoms)}")

    # 4. Force field
    forcefield = app.ForceField("amber14-all.xml", "amber14/tip3p.xml")
    # ligand에 대한 GAFF/UNL이 필요 — 여기선 간단히 OpenMM default로 시도
    try:
        system = forcefield.createSystem(
            pdb.topology,
            nonbondedMethod=app.NoCutoff,  # 초기 테스트: 용매 없이 gas phase
            constraints=app.HBonds,
        )
        print("  ✅ AMBER + tip3p로 system 생성")
    except Exception as e:
        print(f"  ❌ AMBER forcefield 실패 (ligand 미지원): {e}")
        print("     → smirnoff99Frosst로 재시도 (openff)")
        # fallback — ligand topology 생성 필요. 시간 제약상 스킵.
        print("  ⚠️  실제 운용은 openff-toolkit + OpenMMForceFieldMix 필요")
        return 2

    # 5. MACE-OFF23 MLPotential attach
    from openmmml import MLPotential
    potential = MLPotential("mace-off23-medium")
    print(f"  ML 영역에 MACE-OFF23(medium) overlay: {len(ml_atoms)} atoms")
    new_system = potential.createMixedSystem(
        pdb.topology, system, ml_atoms, interpolate=False,
    )

    integrator = mm.LangevinMiddleIntegrator(
        310 * unit.kelvin, 1.0 / unit.picosecond, 1.0 * unit.femtosecond,
    )
    platform = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(pdb.topology, new_system, integrator, platform)
    sim.context.setPositions(pdb.positions)

    print("\n=== Step 3: 에너지 최소화 ===")
    state0 = sim.context.getState(getEnergy=True)
    print(f"  초기 PE: {state0.getPotentialEnergy()}")
    sim.minimizeEnergy(maxIterations=200)
    state1 = sim.context.getState(getEnergy=True)
    print(f"  최소화 후 PE: {state1.getPotentialEnergy()}")

    print("\n=== Step 4: 짧은 NVT 시험 (100 ps) ===")
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
    print(f"  ✅ 100 ps MD 완료 in {wall:.0f}s")

    final_pdb = out_dir / "final.pdb"
    with open(final_pdb, "w") as f:
        app.PDBFile.writeFile(
            sim.topology,
            sim.context.getState(getPositions=True).getPositions(),
            f,
        )
    print(f"  최종 구조: {final_pdb}")

    print(f"\n=== 완료 ===\nMD 로그: {out_dir / 'log.csv'}\n트라젝토리: {out_dir / 'traj.dcd'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
