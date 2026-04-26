"""신규 4 anti-fibrotic 타겟 (LPA1/αvβ6/YAP1/TAZ) + 우리 기존 5개 통합.

EMB-3가 fibrosis network 4-tier mechanotransduction 다차원 조절자인지 검증:

  Tier 1 (수용체):     LPA1 (LPAR1, Q92633), αvβ6 (ITGAV+ITGB6 P26010+P18564)
  Tier 2 (signaling):  TGF-β1 → Smad3 (이미 검증)
  Tier 3 (mechanotrans): YAP1 (P46937), TAZ/WWTR1 (Q9GZV5) — integrin·FAK·ROCK
                        와 양성 피드백
  Tier 4 (effector):   CTGF (이미), MMP1 (이미)
  Tier 5 (myofib 활성): PDGFRB (이미)

스크립트는 UniProt seq + MSA fetch + Boltz-2 cofold YAML 생성. ABFE 끝난 후
(12:00 KST) 실제 cofold 실행 → 4 신규 × 3 화합물 = 12 cofold (~5분 GPU).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = Path.home() / "genesis_medicine" / "data"
MSA_CACHE = DATA / "msa"
OUT = ROOT / "pilot/scaffold_hop/mechanotransduction"
OUT.mkdir(parents=True, exist_ok=True)


# 신규 anti-fibrotic 타겟 — 2024-2026 임상 진입
NEW_TARGETS = [
    {"key": "LPAR1", "uniprot": "Q92633", "tier": 1,
     "rationale": ("LPA1 receptor — Admilparant (BMS 986278) Phase 2 IPF FVC 효능. "
                    "G-protein coupled receptor, lung fibroblast 활성"),
     "max_len": 600},
    {"key": "ITGB6", "uniprot": "P18564", "tier": 1,
     "rationale": ("Integrin β6 subunit (αvβ6 형성). Nat Comm 2023 RFdiffusion "
                    "miniprotein picomolar binder, bleomycin lung 효능"),
     "max_len": 600},
    {"key": "YAP1", "uniprot": "P46937", "tier": 3,
     "rationale": ("YAP — mechanotransduction master, integrin·FAK·ROCK "
                    "양성 피드백, fibroblast 활성 perpetuate"),
     "max_len": 400},
    {"key": "WWTR1", "uniprot": "Q9GZV5", "tier": 3,
     "rationale": ("TAZ (transcriptional coactivator) — YAP1 paralog, "
                    "myofibroblast 분화 핵심"),
     "max_len": 400},
]

COMPOUNDS = {
    "embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
    "emb3":    "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
    "egcg":    "C1[C@H]([C@H](OC2=CC(=CC(=C21)O)O)C3=CC(=C(C(=C3)O)O)O)OC(=O)C4=CC(=C(C(=C4)O)O)O",
}


def fetch_uniprot_seq(acc: str) -> str:
    cache = MSA_CACHE / f"{acc}.fasta"
    if cache.exists():
        return "".join(line for line in cache.read_text().splitlines()
                        if not line.startswith(">"))
    print(f"  fetch UniProt {acc}…", flush=True)
    r = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", timeout=30)
    r.raise_for_status()
    cache.write_text(r.text)
    return "".join(line for line in r.text.splitlines() if not line.startswith(">"))


def get_or_fetch_msa(target: dict) -> Path:
    key = target["key"].lower()
    p = MSA_CACHE / f"{key}.a3m"
    if p.exists() and p.stat().st_size > 1000:
        return p

    print(f"  ⏳ {target['key']} ({target['uniprot']}): MSA 호출 (ColabFold)…",
          flush=True)
    seq = fetch_uniprot_seq(target["uniprot"])
    if len(seq) > target["max_len"]:
        print(f"     truncating {len(seq)} → {target['max_len']}")
        seq = seq[:target["max_len"]]
    tmp = OUT / "msa_bootstrap" / key
    yaml_path = tmp / "input" / "bootstrap.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": seq}},
            {"ligand": {"id": "B", "smiles": "CCO"}},
        ],
    }
    yaml_path.write_text(yaml.safe_dump(payload, sort_keys=False))
    out_dir = tmp / "output"
    out_dir.mkdir(exist_ok=True)
    boltz = str(ROOT / ".venv/bin/boltz")
    cmd = [boltz, "predict", str(yaml_path.parent), "--out_dir", str(out_dir),
           "--use_msa_server", "--sampling_steps", "5",
           "--diffusion_samples", "1", "--recycling_steps", "1",
           "--devices", "1"]
    subprocess.run(cmd, check=False, capture_output=True, timeout=900)
    cands = list(out_dir.rglob("*_unpaired_tmp_env/uniref.a3m"))
    if not cands:
        raise RuntimeError(f"{target['key']} MSA fetch 실패")
    cleaned = cands[0].read_bytes().replace(b"\x00", b"")
    p.write_bytes(cleaned)
    n = sum(1 for ln in p.read_text(errors="ignore").splitlines()
            if ln.startswith(">"))
    print(f"  ✅ {target['key']}: {n} seqs → {p}")
    shutil.rmtree(tmp, ignore_errors=True)
    return p


def build_cofold_yamls():
    """신규 4 타겟 × 3 화합물 = 12 cofold YAML 생성."""
    inputs_dir = OUT / "inputs"
    inputs_dir.mkdir(exist_ok=True)
    n = 0
    for tgt in NEW_TARGETS:
        seq = fetch_uniprot_seq(tgt["uniprot"])
        if len(seq) > tgt["max_len"]:
            seq = seq[:tgt["max_len"]]
        msa = MSA_CACHE / f"{tgt['key'].lower()}.a3m"
        for comp, smi in COMPOUNDS.items():
            payload = {
                "version": 1,
                "sequences": [
                    {"protein": {"id": "A", "sequence": seq,
                                  "msa": str(msa.absolute())}},
                    {"ligand": {"id": "B", "smiles": smi}},
                ],
                "properties": [{"affinity": {"binder": "B"}}],
            }
            p = inputs_dir / f"{tgt['key'].lower()}__{comp}.yaml"
            p.write_text(yaml.safe_dump(payload, sort_keys=False))
            n += 1
    return n, inputs_dir


def main() -> int:
    print("=== 신규 4 mechanotransduction 타겟 cofold prep ===\n")

    # 1. UniProt seq fetch
    print("[1/3] UniProt sequences")
    for t in NEW_TARGETS:
        seq = fetch_uniprot_seq(t["uniprot"])
        print(f"  {t['key']:6s} ({t['uniprot']}) tier {t['tier']}: {len(seq)} AA")
        print(f"           {t['rationale']}")

    # 2. MSA fetch (ColabFold via Boltz-2)
    print(f"\n[2/3] MSA fetch (ColabFold, ~3-5분/타겟)")
    if "--skip-msa" in sys.argv:
        print(f"  --skip-msa 옵션 — MSA fetch 생략")
    else:
        for t in NEW_TARGETS:
            msa_path = MSA_CACHE / f"{t['key'].lower()}.a3m"
            if msa_path.exists() and msa_path.stat().st_size > 1000:
                print(f"  {t['key']:6s}: 캐시됨 (skip)")
                continue
            try:
                get_or_fetch_msa(t)
            except Exception as e:
                print(f"  ⚠️  {t['key']}: {e}")

    # 3. Cofold YAML 생성
    print(f"\n[3/3] Cofold YAML 생성 ({len(NEW_TARGETS)} × {len(COMPOUNDS)} = "
          f"{len(NEW_TARGETS) * len(COMPOUNDS)})")
    n, inputs_dir = build_cofold_yamls()
    print(f"  ✅ {n} YAML → {inputs_dir}")

    # 4. 실행 가이드
    print(f"\n=== 다음 단계 (ABFE 끝난 후, 12:00 KST 이후) ===")
    print(f"\n  .venv/bin/boltz predict {inputs_dir} \\")
    print(f"      --out_dir {OUT}/output \\")
    print(f"      --sampling_steps 25 --diffusion_samples 1 \\")
    print(f"      --recycling_steps 3 --sampling_steps_affinity 200 \\")
    print(f"      --diffusion_samples_affinity 5 --affinity_mw_correction \\")
    print(f"      --devices 1")
    print(f"\n  예상 시간: ~3-5분 GPU (12 cofold × ~25s)")
    print(f"\n  결과 분석: scripts/run_mechanotransduction_analysis.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
