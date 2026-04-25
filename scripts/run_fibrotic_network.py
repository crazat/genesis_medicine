"""Anti-fibrotic network multi-target 검증.

목적: EMB-3가 단일 TGF-β1 inhibitor가 아니라 fibrotic master-switch network 전반
조절자인지 검증 (paper "system-level rewiring" 메시지).

타겟 9개:
  Network anti-fibrotic (binding 원함):
    TGFB1 · MMP1 · CTGF (이전 결과 활용)
    LOX (collagen crosslinking)
    SMAD3 (TGF-β1 downstream master)
    PDGFRB (myofibroblast activation)
    JUN (AP-1 fibrotic transcription) — 이전 photoaging 캐시 재사용

  Selectivity test (binding NOT 원함):
    FGF2 (pro-regenerative)
    VEGFA (pro-angiogenic)

화합물:
  Embelin (seed)
  EMB-3 (scaffold-hop lead)
  EGCG (universal compound — 비교)
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
DATA = ROOT / "data"
MSA_CACHE = DATA / "msa"
OUT = ROOT / "pilot/scaffold_hop/network_validation"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    # 이미 보유 (skin_scar v2에서)
    {"key": "TGFB1", "uniprot": "P01137", "role": "anti_fibrotic", "core": True},
    {"key": "MMP1",  "uniprot": "P03956", "role": "anti_fibrotic", "core": True},
    {"key": "CTGF",  "uniprot": "P29279", "role": "anti_fibrotic", "core": True},
    {"key": "JUN",   "uniprot": "P05412", "role": "anti_fibrotic", "core": False},
    # 새 fetch
    {"key": "LOX",   "uniprot": "P28300", "role": "anti_fibrotic", "core": False},
    {"key": "SMAD3", "uniprot": "P84022", "role": "anti_fibrotic", "core": False},
    {"key": "PDGFRB","uniprot": "P09619", "role": "anti_fibrotic", "core": False},
    # selectivity test (pro-regenerative — NOT bind 원함)
    {"key": "FGF2",  "uniprot": "P09038", "role": "pro_regen",     "core": False},
    {"key": "VEGFA", "uniprot": "P15692", "role": "pro_regen",     "core": False},
]

COMPOUNDS = {
    "embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
    "emb3":    "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
    "egcg":    "C1[C@H]([C@H](OC2=CC(=CC(=C21)O)O)C3=CC(=C(C(=C3)O)O)O)OC(=O)C4=CC(=C(C(=C4)O)O)O",
}


def fetch_uniprot_seq(acc: str) -> str:
    cache = MSA_CACHE / f"{acc}.fasta"
    if cache.exists():
        text = cache.read_text()
    else:
        print(f"  fetch UniProt {acc}…", flush=True)
        r = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta",
                          timeout=30)
        r.raise_for_status()
        text = r.text
        cache.write_text(text)
    return "".join(line for line in text.splitlines() if not line.startswith(">"))


def get_or_fetch_msa(target: dict) -> Path:
    key = target["key"].lower()
    p = MSA_CACHE / f"{key}.a3m"
    if p.exists() and p.stat().st_size > 1000:
        return p

    print(f"  ⏳ {target['key']} ({target['uniprot']}): MSA 없음 — "
          f"ColabFold 호출", flush=True)
    seq = fetch_uniprot_seq(target["uniprot"])
    if len(seq) > 600:
        seq = seq[:600]   # Boltz-2 권장 길이 제한 (large protein 자르기)
    tmp_dir = OUT / "msa_bootstrap" / key
    yaml_path = tmp_dir / "input" / "bootstrap.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": seq}},
            {"ligand": {"id": "B", "smiles": "CCO"}},
        ],
    }
    yaml_path.write_text(yaml.safe_dump(payload, sort_keys=False))
    out_dir = tmp_dir / "output"
    out_dir.mkdir(exist_ok=True)
    boltz_bin = str(ROOT / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(yaml_path.parent),
        "--out_dir", str(out_dir),
        "--use_msa_server",
        "--sampling_steps", "5", "--diffusion_samples", "1",
        "--recycling_steps", "1", "--devices", "1",
    ]
    subprocess.run(cmd, check=False, capture_output=True, timeout=900)
    cands = list(out_dir.rglob("*_unpaired_tmp_env/uniref.a3m"))
    if not cands:
        raise RuntimeError(f"{target['key']} MSA fetch 실패")
    src = cands[0]
    cleaned = src.read_bytes().replace(b"\x00", b"")
    p.write_bytes(cleaned)
    n = sum(1 for ln in p.read_text(errors="ignore").splitlines()
            if ln.startswith(">"))
    print(f"  ✅ {target['key']}: {n} seqs cached → {p}")
    # 임시 정리
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return p


def build_yaml(target: dict, comp_name: str, smiles: str, seq: str,
               out_dir: Path, msa_path: Path) -> Path:
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": seq,
                         "msa": str(msa_path.absolute())}},
            {"ligand": {"id": "B", "smiles": smiles}},
        ],
        "properties": [{"affinity": {"binder": "B"}}],
    }
    p = out_dir / f"{target['key'].lower()}__{comp_name}.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def main() -> int:
    print(f"=== Anti-fibrotic network 검증: {len(TARGETS)} 타겟 × "
          f"{len(COMPOUNDS)} 화합물 = {len(TARGETS) * len(COMPOUNDS)} cofold ===\n")

    # 1. MSA 확보
    print("[1/3] MSA 확보…")
    target_seqs = {}
    target_msa = {}
    for tgt in TARGETS:
        target_seqs[tgt["key"]] = fetch_uniprot_seq(tgt["uniprot"])
        if len(target_seqs[tgt["key"]]) > 600:
            target_seqs[tgt["key"]] = target_seqs[tgt["key"]][:600]
        target_msa[tgt["key"]] = get_or_fetch_msa(tgt)

    # 2. YAML 생성
    print("\n[2/3] Input YAML 생성")
    inputs_dir = OUT / "inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = OUT / "output"
    out_dir.mkdir(exist_ok=True)
    n = 0
    for tgt in TARGETS:
        for comp, smi in COMPOUNDS.items():
            build_yaml(tgt, comp, smi, target_seqs[tgt["key"]],
                       inputs_dir, target_msa[tgt["key"]])
            n += 1
    print(f"   {n} YAML → {inputs_dir}")

    # 3. Boltz-2 실행
    print(f"\n[3/3] Boltz-2 cofolding ({n} 항목)")
    boltz = str(ROOT / ".venv" / "bin" / "boltz")
    cmd = [
        boltz, "predict", str(inputs_dir),
        "--out_dir", str(out_dir),
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    wall = time.time() - t0
    print(f"\n✅ {wall/60:.1f}분 (exit={rc})")

    # 4. 결과 종합
    rows = []
    for aff in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        target_key, comp = stem.split("__", 1)
        rows.append({
            "target": target_key.upper(),
            "compound": comp,
            "affinity_pred_value": d.get("affinity_pred_value"),
            "affinity_probability_binary": d.get("affinity_probability_binary"),
        })
    res = pd.DataFrame(rows)

    # role별 분류
    role_map = {t["key"]: t["role"] for t in TARGETS}
    res["role"] = res["target"].map(role_map)

    pivot = res.pivot_table(index="compound", columns="target",
                            values="affinity_probability_binary",
                            aggfunc="first")
    pivot.to_csv(OUT / "network_consensus.csv")
    res.to_csv(OUT / "network_full.csv", index=False)

    # 분석
    print("\n=== Network affinity per compound (binary prob) ===")
    print(pivot.to_string(float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))

    print("\n=== Anti-fibrotic vs Pro-regen 차원 ===")
    summary_rows = []
    for comp in COMPOUNDS:
        anti = res[(res["compound"] == comp) & (res["role"] == "anti_fibrotic")]
        pro = res[(res["compound"] == comp) & (res["role"] == "pro_regen")]
        anti_mean = anti["affinity_probability_binary"].mean()
        pro_mean = pro["affinity_probability_binary"].mean()
        n_strong = (anti["affinity_probability_binary"] >= 0.5).sum()
        n_targets = len(anti)
        # network coverage = strong binding 비율
        network_coverage = n_strong / n_targets if n_targets else 0
        # selectivity = anti - pro (높을수록 좋음)
        selectivity = anti_mean - pro_mean
        # dual-action score
        dual_score = network_coverage * (1 - max(0, pro_mean - 0.4))
        summary_rows.append({
            "compound": comp,
            "anti_fibrotic_mean": round(anti_mean, 3),
            "pro_regen_mean": round(pro_mean, 3),
            "network_coverage": round(network_coverage, 2),
            "selectivity": round(selectivity, 3),
            "dual_score": round(dual_score, 3),
        })
        print(f"  {comp:10s} anti-fibrotic mean={anti_mean:.3f} ({n_strong}/{n_targets} ≥0.5) | "
              f"pro-regen mean={pro_mean:.3f} | "
              f"selectivity={selectivity:+.3f} | "
              f"dual_score={dual_score:.3f}")

    pd.DataFrame(summary_rows).to_csv(OUT / "summary.csv", index=False)
    print(f"\n✅ {OUT}/network_full.csv  +  network_consensus.csv  +  summary.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
