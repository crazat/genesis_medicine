"""기미·색소 파일럿 v1 — TYR/TYRP1/DCT 핵심 3타겟 + MSA 사전 캐시.

전략
----
- 멜라닌 합성 enzyme 3종 (small-molecule docking 가능)
- MITF (TF) + MC1R (GPCR)는 별도 (이번 파일럿에서는 제외 — 동일 docking 적용 어려움)
- pigment / hyperpigmentation / multi 카테고리 천연물

흉터 v2와 동일 프로토콜 (MSA 사전 캐시 → ~30분 예상).
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

BASE = Path(__file__).parent
DATA = Path.home() / "genesis_medicine" / "data"
MSA_CACHE = DATA / "msa"
MSA_CACHE.mkdir(parents=True, exist_ok=True)
RESULT = BASE / "results_v1"
RESULT.mkdir(parents=True, exist_ok=True)

# 색소 핵심 타겟 (small-molecule docking 가능)
PIGMENT_TARGETS = [
    {"key": "TYR",   "uniprot": "P14679", "display": "Tyrosinase"},
    {"key": "TYRP1", "uniprot": "P17643", "display": "TRP-1"},
    {"key": "DCT",   "uniprot": "P40126", "display": "TRP-2 (DCT)"},
]


def fetch_uniprot_seq(acc: str) -> str:
    cache = MSA_CACHE / f"{acc}.fasta"
    if cache.exists():
        text = cache.read_text()
    else:
        r = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", timeout=20)
        r.raise_for_status()
        text = r.text
        cache.write_text(text)
    return "".join(line for line in text.splitlines() if not line.startswith(">"))


def get_msa_or_fetch(target: dict, sample_smiles: str = "CCO") -> Path:
    """타겟별 MSA 캐시. 없으면 1회 ColabFold 호출."""
    key = target["key"].lower()
    cache_path = MSA_CACHE / f"{key}.a3m"
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return cache_path

    # MSA가 없으면 ColabFold로 1번만 받음
    print(f"  ⏳ {target['key']}: MSA 없음 — ColabFold 1회 호출 (단일 화합물로)")
    tmp_dir = RESULT / "msa_bootstrap" / key
    tmp_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = tmp_dir / "input" / "bootstrap.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": target["sequence"]}},
            {"ligand": {"id": "B", "smiles": sample_smiles}},
        ],
    }
    yaml_path.write_text(yaml.safe_dump(payload, sort_keys=False))
    out_dir = tmp_dir / "output"
    out_dir.mkdir(exist_ok=True)

    # MSA만 받기 — 짧은 sampling으로 빠르게 끝남
    boltz_bin = str(Path.home() / "genesis_medicine" / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(yaml_path.parent),
        "--out_dir", str(out_dir),
        "--use_msa_server",
        "--sampling_steps", "5", "--diffusion_samples", "1",
        "--recycling_steps", "1", "--devices", "1",
    ]
    subprocess.run(cmd, check=False, capture_output=True, timeout=900)

    # 생성된 a3m 찾기
    a3m_candidates = list(out_dir.rglob("*_unpaired_tmp_env/uniref.a3m"))
    if not a3m_candidates:
        raise RuntimeError(f"{target['key']}: ColabFold 호출 후 a3m 못 찾음")
    src = a3m_candidates[0]
    cleaned = src.read_bytes().replace(b"\x00", b"")
    cache_path.write_bytes(cleaned)
    n = sum(1 for line in cache_path.read_text(errors="ignore").splitlines() if line.startswith(">"))
    print(f"  ✅ {target['key']}: {n} seqs → {cache_path}")
    return cache_path


def select_compounds() -> pd.DataFrame:
    df = pd.read_csv(DATA / "skin_compounds_curated.csv")
    mask = df["category"].str.contains("pigment|hyperpigment|melanin|multi", case=False, na=False)
    df = df[mask & (df["mw"].astype(float) <= 600)].drop_duplicates(subset=["name", "cid"])
    return df.reset_index(drop=True)


def build_yaml(target: dict, comp_name: str, smiles: str, out_dir: Path,
               msa_path: Path) -> Path:
    safe = comp_name.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").lower()
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {
                "id": "A", "sequence": target["sequence"],
                "msa": str(msa_path.absolute()),
            }},
            {"ligand": {"id": "B", "smiles": smiles}},
        ],
        "properties": [{"affinity": {"binder": "B"}}],
    }
    p = out_dir / f"{target['key'].lower()}__{safe}.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def main() -> int:
    print("=" * 70)
    print("기미·색소 파일럿 v1 — TYR/TYRP1/DCT")
    print("=" * 70)

    # 1. 타겟 시퀀스
    print("\n[1/5] 타겟 시퀀스 확보 (UniProt)")
    for t in PIGMENT_TARGETS:
        t["sequence"] = fetch_uniprot_seq(t["uniprot"])
        print(f"   {t['key']} ({t['uniprot']}): {len(t['sequence'])} aa")

    # 2. MSA 캐시 (없으면 1회씩만 ColabFold)
    print("\n[2/5] MSA 캐시 확보")
    msa_paths = {}
    for t in PIGMENT_TARGETS:
        msa_paths[t["key"]] = get_msa_or_fetch(t)

    # 3. 천연물 선택
    print("\n[3/5] 천연물 선택")
    df = select_compounds()
    print(f"   {len(df)}개 (pigment / hyperpigment / multi, MW ≤ 600)")
    print(df[["name", "source_korean", "mw", "category"]].head(10).to_string(index=False))

    # 4. Input YAML
    print("\n[4/5] Input YAML 생성")
    inputs_dir = RESULT / "boltz2_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = RESULT / "boltz2_output"
    out_dir.mkdir(exist_ok=True)
    n_total = 0
    for t in PIGMENT_TARGETS:
        for _, row in df.iterrows():
            if pd.isna(row["smiles"]):
                continue
            build_yaml(t, row["name"], row["smiles"], inputs_dir, msa_paths[t["key"]])
            n_total += 1
    print(f"   {n_total} YAMLs ({len(df)} × {len(PIGMENT_TARGETS)} 타겟)")

    # 5. Boltz-2 cofolding
    print(f"\n[5/5] Boltz-2 cofolding ({n_total}개)")
    boltz_bin = str(Path.home() / "genesis_medicine" / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(inputs_dir),
        "--out_dir", str(out_dir),
        "--sampling_steps", "25", "--diffusion_samples", "1",
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

    # 결과 수집
    rows = []
    for aff in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        target_key, comp_safe = stem.split("__", 1)
        pv = d.get("affinity_pred_value")
        rows.append({
            "target": target_key.upper(),
            "compound_safe": comp_safe,
            "affinity_pred_value": pv,
            "affinity_probability_binary": d.get("affinity_probability_binary"),
            "pIC50_approx": 6.0 - float(pv) if pv is not None else None,
        })

    if not rows:
        print("❌ 결과 없음")
        return 2

    res = pd.DataFrame(rows)
    name_map = {n.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").lower(): n
                for n in df["name"].tolist()}
    res["compound"] = res["compound_safe"].map(lambda s: name_map.get(s, s))

    pivot = res.pivot_table(
        index="compound", columns="target",
        values="affinity_probability_binary", aggfunc="first",
    )
    pivot["consensus_score"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("consensus_score", ascending=False)
    pivot.to_csv(RESULT / "pigment_consensus.csv")
    res.to_csv(RESULT / "pigment_full.csv", index=False)

    print("\n=== Top 15 (consensus) ===")
    print(pivot.head(15).to_string(float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))
    print(f"\n✅ {RESULT}/pigment_consensus.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
