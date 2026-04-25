"""BACE1 9개 ligand Boltz-2 affinity head 재실행.

NEXT ACTIONS #3 실행 — affinity_mw_correction + sampling_steps_affinity=200
+ diffusion_samples_affinity=5.

기존 input YAML에 properties 블록 자동 주입.
가속 커널 (cuequivariance 0.10) + boltz-blackwell 활성화.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml


def inject_affinity_properties(input_dir: Path, output_dir: Path) -> list[Path]:
    """기존 YAML에 properties 블록 추가. ligand id를 binder로."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    skip = {"CHEMBL250295"}  # RDKit 파싱 실패 (큰 매크로사이클)
    for path in sorted(input_dir.glob("bace1_*.yaml")):
        name = path.stem.replace("bace1_", "").upper()
        if name in skip:
            print(f"  skip {name} (known RDKit fail)")
            continue
        d = yaml.safe_load(path.read_text())
        # ligand id 찾기 (보통 'B' 또는 'L0')
        lig_id = None
        for entry in d.get("sequences", []):
            if "ligand" in entry:
                lig_id = entry["ligand"].get("id")
                break
        if lig_id is None:
            print(f"  skip {name} (no ligand id)")
            continue
        d["properties"] = [{"affinity": {"binder": lig_id}}]
        target = output_dir / path.name
        target.write_text(yaml.safe_dump(d, sort_keys=False))
        out_paths.append(target)
    return out_paths


def main() -> int:
    base = Path(__file__).parent
    input_dir = base / "inputs"
    affinity_dir = base / "inputs_affinity"
    out_dir = base / "output_affinity"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. YAML에 properties 블록 주입
    print("=== Step 1: YAML properties 블록 주입 ===")
    paths = inject_affinity_properties(input_dir, affinity_dir)
    print(f"  → {len(paths)} YAML 준비")

    # 2. Boltz-2 affinity 추론
    print("\n=== Step 2: Boltz-2 affinity head 실런 ===")
    print("  sampling_steps_affinity=200, diffusion_samples_affinity=5")
    print("  affinity_mw_correction=true, no_kernels=false (cuequivariance v0.10)")

    import os
    boltz_bin = os.environ.get("BOLTZ_BIN") or str(Path(sys.executable).parent / "boltz")
    cmd = [
        boltz_bin, "predict", str(affinity_dir),
        "--out_dir", str(out_dir),
        "--use_msa_server",              # research 프로파일 (BACE1 파일럿이므로 OK)
        "--sampling_steps", "25",
        "--diffusion_samples", "1",       # 구조는 기존 검증됨 — 빠르게
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print(f"  cmd: {' '.join(cmd)}\n")
    t0 = time.time()
    try:
        subprocess.run(cmd, check=True, timeout=7200)
    except subprocess.CalledProcessError as e:
        print(f"Boltz 실패: {e}")
        return 1
    except subprocess.TimeoutExpired:
        print("Boltz 타임아웃")
        return 1
    wall = time.time() - t0
    print(f"\n✅ Boltz affinity 완료 in {wall:.0f}s")

    # 3. 결과 수집
    print("\n=== Step 3: 결과 요약 ===")
    summary = []
    for aff_json in sorted(out_dir.rglob("affinity*.json")):
        d = json.loads(aff_json.read_text())
        chembl = aff_json.parent.parent.name.split("bace1_")[-1].upper() if "bace1_" in str(aff_json) else aff_json.parent.name
        summary.append({
            "chembl_id": chembl,
            "affinity_pred_value": d.get("affinity_pred_value"),
            "affinity_probability_binary": d.get("affinity_probability_binary"),
        })

    print(f"\n  {'chembl_id':<16s} {'pred_value':>12s} {'prob_binary':>12s}")
    for s in summary:
        pv = s["affinity_pred_value"]
        pb = s["affinity_probability_binary"]
        print(f"  {s['chembl_id']:<16s} "
              f"{pv:>12.4f}" if pv is not None else f"  {s['chembl_id']:<16s} {'None':>12s}",
              end="")
        print(f" {pb:>12.4f}" if pb is not None else f" {'None':>12s}")

    out_csv = base / "affinity_results.csv"
    import csv
    with out_csv.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=["chembl_id", "affinity_pred_value", "affinity_probability_binary"])
        writer.writeheader()
        writer.writerows(summary)
    print(f"\n✅ 저장: {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
