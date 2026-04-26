"""EMB-3 SC permeation MD setup (실행은 별도, GPU 할당 시).

ABFE 진행 중에는 setup만 — 실제 simulation은 ABFE 끝난 후.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/scaffold_hop/sc_permeation"
OUT.mkdir(parents=True, exist_ok=True)


COMPOUNDS = {
    "EMB-3":         "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
    "Embelin":       "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
    "Asiaticoside":  "C[C@@H]1CC[C@@]2(CC[C@@]3(C(=CC[C@H]4[C@]3(C[C@H]([C@@H]5[C@@]4(C[C@H]([C@@H]([C@@]5(C)CO)O)O)C)O)C)[C@@H]2[C@H]1C)C)C(=O)O",
    "EGCG":          "C1[C@H]([C@H](OC2=CC(=CC(=C21)O)O)C3=CC(=C(C(=C3)O)O)O)OC(=O)C4=CC(=C(C(=C4)O)O)O",
    "Curcumin":      "COC1=C(C=CC(=C1)/C=C/C(=O)CC(=O)/C=C/C2=CC(=C(C=C2)O)OC)O",
}


def main() -> int:
    from genesis_medicine.md.stratum_corneum import (
        StratumCorneumConfig, build_sc_system, simulate_permeation,
        estimate_log_kp_from_md,
    )

    print("=== EMB-3 SC permeation MD setup ===\n")

    cfg = StratumCorneumConfig(
        n_ceramide=16, n_ffa=16, n_chol=16,
        ratio=(1.0, 1.0, 1.0),
        box_x=6.0, box_y=6.0, box_z=12.0,
        n_replicas=8,    # 줄여서 시간 절감
        eq_ns=20.0,      # 50 → 20 (RTX 5090에서 적당)
        pull_ns=50.0,    # 100 → 50
    )

    sys_dir = OUT / "sc_system"
    sys_info = build_sc_system(cfg, sys_dir)
    print(f"  ✅ SC system 빌드 인스트럭션 → {sys_info['instructions']}")
    print(f"     예상 atoms: {sys_info['n_atoms_estimated']}")
    print(f"     예상 GPU 시간: {cfg.n_replicas * cfg.pull_ns / 800:.1f}h × {len(COMPOUNDS)} 화합물")

    print(f"\n=== Permeation MD 후보 ({len(COMPOUNDS)}) ===")
    sc_pdb = sys_dir / "system.pdb"   # CHARMM-GUI 빌드 후 생성될 경로
    for name, smiles in COMPOUNDS.items():
        comp_dir = OUT / name.replace(" ", "_")
        result = simulate_permeation(sc_pdb, smiles, cfg, comp_dir)
        print(f"  {name:15s} stub 생성 → {comp_dir}/permeation_log.json")

    # 예상 log Kp 비교 (logkp_predicted from ADMET head + Diamond-Katz)
    print(f"\n=== ΔG barrier → log Kp 변환 (Diamond-Katz) ===")
    print(f"{'화합물':12s}  {'ΔG (kcal)':>10s}  {'log Kp (cm/h)':>12s}")
    for name, smiles in COMPOUNDS.items():
        # 가정: ΔG barrier 6-15 kcal/mol (천연물 통상)
        for dg in [6.0, 10.0, 15.0]:
            kp = estimate_log_kp_from_md(dg)
            if dg == 10.0:
                print(f"  {name:12s}  {dg:>10.1f}  {kp:>12.2f}")

    print(f"\n=== 다음 단계 ===")
    print(f"  1. CHARMM-GUI Membrane Builder (https://charmm-gui.org)")
    print(f"     - CER NS + FFA + Cholesterol 1:1:1 × 16 each leaflet")
    print(f"     - 결과 PDB → {sys_dir}/charmmgui_inputs/")
    print(f"  2. ABFE 끝난 후 (06:30 KST 이후) simulate_permeation() 실행")
    print(f"  3. log Kp_MD 측정 → ADMET-AI logkp_predicted 검증")
    return 0


if __name__ == "__main__":
    sys.exit(main())
