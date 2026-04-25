"""TGF-β1 latent form cryptic pocket 검증 (B 개정판).

활성형 mature TGF-β1 (residues 279-390, 113 AA) vs 전장 P01137 (390 AA, LAP 포함).
EMB-3 + EGCG + Embelin이 LAP/integrin binding region (cryptic pocket)에 결합한다면
"first allosteric anti-fibrotic" claim 가능.

핵심 비교:
  mature TGFB1 affinity vs full-length affinity per compound
  → full > mature: cryptic pocket binding
  → full < mature: 활성형 결합 (예상)
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
OUT = ROOT / "pilot/scaffold_hop/tgfb1_latent"
OUT.mkdir(parents=True, exist_ok=True)

COMPOUNDS = {
    "embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
    "emb3":    "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
    "egcg":    "C1[C@H]([C@H](OC2=CC(=CC(=C21)O)O)C3=CC(=C(C(=C3)O)O)O)OC(=O)C4=CC(=C(C(=C4)O)O)O",
}

# mature 활성형 baseline (skin_scar v2에서 측정됨)
MATURE_BASELINE = {
    "embelin": 0.746,
    "emb3":    0.710,   # scaffold_hop boltz2_validation
    "egcg":    0.617,   # cross_disease/long_form.csv (scar)
}


def fetch_uniprot_seq(acc: str) -> str:
    cache = MSA_CACHE / f"{acc}.fasta"
    if cache.exists():
        text = cache.read_text()
    else:
        r = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta",
                          timeout=30)
        r.raise_for_status()
        text = r.text
        cache.write_text(text)
    return "".join(line for line in text.splitlines() if not line.startswith(">"))


def fetch_msa_via_boltz(seq: str, key: str) -> Path:
    cache_path = MSA_CACHE / f"{key}.a3m"
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return cache_path

    print(f"  ⏳ {key}: MSA 호출 (full-length, ColabFold)…", flush=True)
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
    boltz = str(ROOT / ".venv" / "bin" / "boltz")
    cmd = [
        boltz, "predict", str(yaml_path.parent),
        "--out_dir", str(out_dir),
        "--use_msa_server",
        "--sampling_steps", "5", "--diffusion_samples", "1",
        "--recycling_steps", "1", "--devices", "1",
    ]
    subprocess.run(cmd, check=False, capture_output=True, timeout=900)
    cands = list(out_dir.rglob("*_unpaired_tmp_env/uniref.a3m"))
    if not cands:
        raise RuntimeError(f"{key} MSA fetch 실패")
    src = cands[0]
    cleaned = src.read_bytes().replace(b"\x00", b"")
    cache_path.write_bytes(cleaned)
    n = sum(1 for ln in cache_path.read_text(errors="ignore").splitlines()
            if ln.startswith(">"))
    print(f"  ✅ {key}: {n} seqs → {cache_path}")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return cache_path


def main() -> int:
    print("=== TGF-β1 latent (full-length) cryptic pocket 검증 ===\n")

    print("[1/3] 전장 TGFB1 (P01137) 시퀀스 + MSA")
    full_seq = fetch_uniprot_seq("P01137")
    print(f"  full-length: {len(full_seq)} AA (LAP residues 30-278 + mature 279-390)")
    if len(full_seq) > 600:
        print(f"  ⚠️  전장 {len(full_seq)} AA > 600 → Boltz-2 권장 한계 초과, 잘라냄")
        # LAP+mature: residues 1-390 → keep first 600 if shorter, else first 600
        full_seq = full_seq[:600]
    msa_path = fetch_msa_via_boltz(full_seq, "tgfb1_full")

    # 2. Input YAML 생성 — full-length × 3 화합물
    print("\n[2/3] full-length cofold input 생성")
    inputs_dir = OUT / "inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = OUT / "output"
    out_dir.mkdir(exist_ok=True)
    for comp, smi in COMPOUNDS.items():
        payload = {
            "version": 1,
            "sequences": [
                {"protein": {"id": "A", "sequence": full_seq,
                             "msa": str(msa_path.absolute())}},
                {"ligand": {"id": "B", "smiles": smi}},
            ],
            "properties": [{"affinity": {"binder": "B"}}],
        }
        p = inputs_dir / f"tgfb1full__{comp}.yaml"
        p.write_text(yaml.safe_dump(payload, sort_keys=False))
    print(f"  ✅ {len(COMPOUNDS)} YAML")

    # 3. Boltz-2 cofold
    print(f"\n[3/3] Boltz-2 cofolding (full-length)")
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

    # 4. mature vs full-length 비교
    rows = []
    for aff in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        _, comp = stem.split("__", 1)
        full_aff = d.get("affinity_probability_binary")
        mature = MATURE_BASELINE.get(comp, None)
        rows.append({
            "compound": comp,
            "tgfb1_mature_aff": mature,
            "tgfb1_full_aff": full_aff,
            "delta": (full_aff - mature) if (full_aff is not None and mature
                                              is not None) else None,
            "interpretation": (
                "🚀 cryptic pocket (full > mature, allosteric 가능성)"
                if full_aff and mature and (full_aff - mature) > 0.05 else
                ("⚠️ cryptic 약함" if full_aff and mature and abs(full_aff - mature) <= 0.05 else
                 "활성형 결합 (canonical)")
            ),
        })
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "latent_vs_mature.csv", index=False)

    print("\n=== mature vs full-length TGF-β1 affinity ===")
    print(res.to_string(index=False, float_format=lambda v: f"{v:.3f}"
                        if pd.notna(v) else "—"))

    n_cryptic = sum(1 for r in rows if r["delta"] and r["delta"] > 0.05)
    print(f"\n  cryptic pocket signal: {n_cryptic}/{len(rows)} 화합물에서 발견")
    if n_cryptic >= 2:
        print("  🎯 BIG DISCOVERY 시그널 — 추가 MD 검증 권장")
    return 0


if __name__ == "__main__":
    sys.exit(main())
