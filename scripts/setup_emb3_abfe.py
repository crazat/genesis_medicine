"""EMB-3 × MMP-1 ABFE setup (실행 전 준비만).

Boltz-2 binary classifier (0.674)를 정량 ΔG (kcal/mol) → IC50 nM 추정으로 환원.
EMB-3 × MMP-1이 0.79 Å MD ligand stability 보였으므로 ABFE 정량화 paper-tier 데이터.

GPU 추정: 16 windows × 10 ns prod × 3 replicas = 480 ns simulation.
   1484 ns/day (skin_scar v2 측정) 기준 약 7-8시간 GPU.
   eq 5 ns × 16 × 3 = 240 ns 추가 → 총 720 ns ≈ 11-12시간.

본 스크립트는 input 준비 + config 생성. 실행은 사용자 확인 후:
   $ .venv/bin/python -c "from scripts.setup_emb3_abfe import run; run()"
혹은 nohup 백그라운드 launch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "pilot/scaffold_hop"
OUT = SCAFFOLD / "abfe_emb3_mmp1"
OUT.mkdir(parents=True, exist_ok=True)

# Boltz-2 cofold output에서 가져옴
SOURCE_CIF = (SCAFFOLD / "boltz2_validation/output/boltz_results_inputs"
                       / "predictions/mmp1__embelin_emb3"
                       / "mmp1__embelin_emb3_model_0.cif")
EMB3_SMILES = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"


def prepare_inputs() -> dict:
    """receptor + ligand 분리 → ABFE 입력 형식."""
    if not SOURCE_CIF.exists():
        return {"error": f"source CIF 없음: {SOURCE_CIF}",
                "hint": "scripts/run_scaffold_hop_cofold.py 먼저 실행"}

    print(f"[1/3] CIF parsing: {SOURCE_CIF}")
    try:
        import openmm.app as app
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError as e:
        return {"error": f"deps: {e}"}

    cif = app.PDBxFile(str(SOURCE_CIF))
    # ligand atoms: residue name LIG1 (Boltz output convention)
    lig_atoms = [a for a in cif.topology.atoms() if a.residue.name == "LIG1"]
    receptor_atoms = [a for a in cif.topology.atoms()
                       if a.residue.name != "LIG1"]
    print(f"  receptor atoms: {len(receptor_atoms)}")
    print(f"  ligand atoms:   {len(lig_atoms)}")

    # PDB 단백질 분리 저장
    receptor_pdb = OUT / "receptor.pdb"
    # 새 topology 만들기 — ligand 제외
    receptor_modeller = app.Modeller(cif.topology, cif.positions)
    to_delete = [r for r in receptor_modeller.topology.residues()
                  if r.name == "LIG1"]
    receptor_modeller.delete(to_delete)
    with receptor_pdb.open("w") as f:
        app.PDBFile.writeFile(receptor_modeller.topology,
                              receptor_modeller.positions, f)
    print(f"  ✅ receptor PDB: {receptor_pdb}")

    # Ligand SDF 생성 (RDKit으로 SMILES → 3D)
    lig_sdf = OUT / "ligand.sdf"
    mol = Chem.MolFromSmiles(EMB3_SMILES)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
    mol.SetProp("_Name", "EMB-3")
    mol.SetProp("source", "scaffold_hop_lead_2026-04-25")
    Chem.SDWriter(str(lig_sdf)).write(mol)
    print(f"  ✅ ligand SDF: {lig_sdf}")

    return {
        "receptor_pdb": str(receptor_pdb),
        "ligand_sdf": str(lig_sdf),
    }


def make_config(inputs: dict) -> Path:
    """ABFE 실행 config (FEP-SPell-ABFE 형식)."""
    print(f"\n[2/3] ABFE config 생성")
    cfg = {
        "receptor": inputs["receptor_pdb"],
        "ligand": inputs["ligand_sdf"],
        "system_name": "EMB3_MMP1",
        # Production parameters (paper-quality)
        "n_replicas": 3,
        "n_lambda_windows": 16,
        "timestep_fs": 2.0,
        "eq_ns": 5.0,
        "prod_ns": 10.0,
        "seed": 42,
        # Force field
        "protein_ff": "amber/ff14SB.xml",
        "water_model": "tip3p",
        "ligand_ff": "gaff-2.11",
        "charge_method": "am1bcc",
        # MD
        "temperature_K": 310,
        "ionic_strength_M": 0.15,   # physiological
        "device": "cuda:0",
        # Output
        "output_dir": str(OUT),
        # Estimate
        "_estimated_total_ns": 720,
        "_estimated_gpu_hours": 12,
    }
    cfg_path = OUT / "abfe_config.json"
    cfg_path.write_text(json.dumps(cfg, indent=2))
    print(f"  ✅ {cfg_path}")
    return cfg_path


def print_run_command(cfg_path: Path) -> None:
    print(f"\n[3/3] 실행 가이드 (사용자 확인 후)")
    print()
    print(f"  # GPU 가용 (확인) → 백그라운드 launch")
    print(f"  nohup .venv/bin/python -m genesis_medicine.md.abfe_adapter \\")
    print(f"       --config {cfg_path} \\")
    print(f"       --backend fep_spell \\")
    print(f"       > {OUT}/abfe.log 2>&1 &")
    print()
    print(f"  # 진행 모니터")
    print(f"  tail -f {OUT}/abfe.log")
    print()
    print(f"  # 완료 후 결과")
    print(f"  cat {OUT}/abfe_result.json")
    print()
    print(f"  예상 시간: 11-12시간 (RTX 5090, 1484 ns/day 기준)")
    print(f"  예상 결과: ΔG (kcal/mol) + IC50 추정 nM")


def main() -> int:
    print("=== EMB-3 × MMP-1 ABFE setup ===\n")
    inputs = prepare_inputs()
    if "error" in inputs:
        print(f"❌ {inputs['error']}")
        if "hint" in inputs:
            print(f"   {inputs['hint']}")
        return 1
    cfg = make_config(inputs)
    print_run_command(cfg)

    # 한 번에 시작 안함 — 사용자 결정
    print("\n⚠️  실행은 별도 결정 — GPU 12시간 + Boltz-2/MD 기능 일시 차단됨.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
