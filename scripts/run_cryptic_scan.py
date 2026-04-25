"""흉터 3타겟 cryptic pocket 스캔 (Fpocket).

PocketMiner는 TF 2.1 레거시 의존이 깊어 우회. Fpocket (Le Guilloux 2009, 검증된 도구)으로
TGFB1/MMP1/CTGF 모든 pocket 자동 식별 + canonical 대비 alternative site 분석.

목적:
  - canonical active site (TGFBR-binding interface 등) 외에 결합 가능 pocket 발굴
  - EMB-3가 canonical에 결합하지만, 다른 천연물이 cryptic site에 결합할 가능성 탐색
  - "first allosteric anti-fibrotic" 가설 일부 보강 (B 가설 음성 결과 후속)

Boltz-2 예측 구조 (network_validation 결과)에서 ligand 제거 후 fpocket 실행.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NETWORK = ROOT / "pilot/scaffold_hop/network_validation/output/boltz_results_inputs/predictions"
OUT = ROOT / "pilot/scaffold_hop/cryptic_scan"
OUT.mkdir(parents=True, exist_ok=True)

FPOCKET = "/home/crazat/miniforge3/envs/genesis-md/bin/fpocket"

TARGETS = [
    {"key": "TGFB1", "subdir": "tgfb1__embelin", "canonical_site": "TGFBR binding"},
    {"key": "MMP1",  "subdir": "mmp1__embelin",  "canonical_site": "Zn-binding HEXXHXXGXXH"},
    {"key": "CTGF",  "subdir": "ctgf__embelin",  "canonical_site": "IGFBP/VWC domain"},
]


def cif_to_pdb_no_ligand(cif_path: Path, pdb_out: Path) -> bool:
    """CIF → PDB, ligand (LIG1) 제거."""
    try:
        from openmm.app import PDBxFile, PDBFile, Modeller
    except ImportError:
        # fallback: openmm not in current python — call genesis-md python
        cmd = [
            "/home/crazat/miniforge3/envs/genesis-md/bin/python",
            "-c",
            f"""
from openmm.app import PDBxFile, PDBFile, Modeller
cif = PDBxFile('{cif_path}')
mod = Modeller(cif.topology, cif.positions)
to_del = [r for r in mod.topology.residues() if r.name == 'LIG1']
mod.delete(to_del)
with open('{pdb_out}', 'w') as f:
    PDBFile.writeFile(mod.topology, mod.positions, f)
""",
        ]
        return subprocess.run(cmd).returncode == 0
    cif = PDBxFile(str(cif_path))
    mod = Modeller(cif.topology, cif.positions)
    to_del = [r for r in mod.topology.residues() if r.name == "LIG1"]
    mod.delete(to_del)
    with open(pdb_out, "w") as f:
        PDBFile.writeFile(mod.topology, mod.positions, f)
    return True


def parse_fpocket_output(out_dir: Path) -> list[dict]:
    """fpocket 결과 디렉토리 파싱 → pocket 리스트."""
    info_file = out_dir / f"{out_dir.parent.name}_info.txt"
    if not info_file.exists():
        # fpocket 명명 규칙 다를 수 있음
        info_files = list(out_dir.glob("*_info.txt"))
        if info_files:
            info_file = info_files[0]
        else:
            return []
    text = info_file.read_text()
    pockets = []
    cur = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Pocket"):
            if cur:
                pockets.append(cur)
            num = line.split()[1].rstrip(":")
            cur = {"pocket_n": int(num)}
        elif cur and ":" in line:
            k, _, v = line.partition(":")
            try:
                cur[k.strip().replace(" ", "_").lower()] = float(v.strip())
            except ValueError:
                cur[k.strip().replace(" ", "_").lower()] = v.strip()
    if cur:
        pockets.append(cur)
    return pockets


def main() -> int:
    print("=== 흉터 3타겟 cryptic pocket 스캔 (Fpocket) ===\n")

    if not Path(FPOCKET).exists():
        print(f"❌ fpocket 미설치: {FPOCKET}", file=sys.stderr)
        return 1

    summary = []
    for tgt in TARGETS:
        print(f"\n[{tgt['key']}] (canonical: {tgt['canonical_site']})")
        cif = NETWORK / tgt["subdir"] / f"{tgt['subdir']}_model_0.cif"
        if not cif.exists():
            print(f"  ⚠️  CIF 없음: {cif}")
            continue

        # 1. Convert CIF → PDB (no ligand)
        work = OUT / tgt["key"]
        work.mkdir(exist_ok=True)
        pdb = work / f"{tgt['key']}_apo.pdb"
        print(f"  CIF → PDB (ligand 제거): {pdb}")
        ok = cif_to_pdb_no_ligand(cif, pdb)
        if not ok:
            print(f"  ❌ PDB 생성 실패")
            continue

        # 2. Run fpocket
        # fpocket creates {pdb_basename}_out/
        print(f"  fpocket 실행…")
        # fpocket이 입력 PDB와 같은 위치에 출력
        rc = subprocess.run([FPOCKET, "-f", str(pdb)],
                              cwd=work, capture_output=True, text=True).returncode
        if rc != 0:
            print(f"  ❌ fpocket exit={rc}")
            continue

        out_dir = work / f"{tgt['key']}_apo_out"
        if not out_dir.exists():
            print(f"  ⚠️  output dir 없음: {out_dir}")
            continue

        # 3. Parse results
        pockets = parse_fpocket_output(out_dir)
        n_pockets = len(pockets)
        print(f"  ✅ {n_pockets} pockets 식별")

        # Top 5 출력
        for p in pockets[:5]:
            score = p.get("score", p.get("druggability_score", 0))
            vol = p.get("volume", 0)
            n_res = p.get("number_of_alpha_spheres",
                           p.get("number_of_neighbor_residues", 0))
            print(f"    Pocket {p['pocket_n']:2d}: score={score}, "
                  f"vol={vol}, n_alpha={n_res}")

        summary.append({
            "target": tgt["key"],
            "canonical_site": tgt["canonical_site"],
            "n_pockets": n_pockets,
            "top_pocket_score": (pockets[0].get("score",
                                                  pockets[0].get("druggability_score", 0))
                                  if pockets else 0),
            "second_pocket_score": (pockets[1].get("score",
                                                    pockets[1].get("druggability_score", 0))
                                    if len(pockets) > 1 else 0),
            "n_high_scoring": sum(1 for p in pockets
                                    if (p.get("score",
                                              p.get("druggability_score", 0)) or 0) > 0.5),
        })

        # JSON dump pockets
        (work / "pockets.json").write_text(json.dumps(pockets, indent=2,
                                                        default=str))

    # Summary table
    if summary:
        df = pd.DataFrame(summary)
        df.to_csv(OUT / "summary.csv", index=False)
        print(f"\n=== 종합 ===")
        print(df.to_string(index=False))

    print(f"\n=== 해석 ===")
    print("- top pocket = canonical active site일 가능성 높음")
    print("- second pocket score > 0.5 + 다른 위치 = cryptic candidate")
    print("- pocket > 5개 + 분산 = allosteric option 풍부")

    print(f"\n✅ {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
