"""흉터 파일럿 v2 — MSA 사전 캐시 재사용 (이전 38개 a3m 활용).

이전 v1이 ColabFold rate-limit으로 매우 느려서 v2는:
1. 이미 받은 a3m을 영구 캐시 (data/msa/{target}.a3m)
2. 49 화합물 × 3 타겟 = 147 input YAML 모두 msa 경로 명시
3. --use_msa_server 빼고 실행 → MSA fetch 없이 바로 GPU 추론
4. 예상 시간: ~30-40분 (이전 1.5시간 대비)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import yaml

BASE = Path(__file__).parent
DATA = Path.home() / "genesis_medicine" / "data"
MSA_CACHE = DATA / "msa"
MSA_CACHE.mkdir(parents=True, exist_ok=True)
RESULT = BASE / "results_v2"
RESULT.mkdir(parents=True, exist_ok=True)

# v1에서 받은 MSA 활용
V1_MSA_DIR = BASE / "results" / "boltz2_output" / "boltz_results_boltz2_inputs" / "msa"

# v1 코드와 동일한 시퀀스
SCAR_TARGETS = [
    {"key": "TGFB1", "uniprot": "P01137",
     "sequence": "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS",
     "msa_donor": "tgfb1__asiatic_acid_unpaired_tmp_env"},
    {"key": "MMP1", "uniprot": "P03956",
     "sequence": "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG",
     "msa_donor": "mmp1__curcumin_unpaired_tmp_env"},
    {"key": "CTGF", "uniprot": "P29279",
     "sequence": "MTAARLALSCAALAALLPGATALPDGCGCGGRAHWGCGAVGEACSAALEIGSTVFASTPTPPSYAAEIRPGLPVDQDPCRLRAVCESFYHPSSALARQLPRAEPGFNVQDRRLILAGCGCGCQNGCSEPLQPYPLSPCSKQCQPGYQCDDSPSCSCQCLPGCASGAQCAQCRPRPESESSCRKQSCSCRQQGSVHCGYAVKDGGRGCYAGCTSDLDQVDFGCCSHKASNFGSCSSPVRDCGYHWGFPPYHQCASNMGYLLDPLDCQCYFNASGAGAQVFFGGADCGFANGCNQGSPLSF",
     "msa_donor": "ctgf__schizandrin_a_unpaired_tmp_env"},
]


def select_compounds() -> pd.DataFrame:
    df = pd.read_csv(DATA / "skin_compounds_curated.csv")
    mask = df["category"].str.contains("scar|wound|anti-inflam", case=False, na=False)
    df = df[mask & (df["mw"].astype(float) <= 600)].drop_duplicates(subset=["name", "cid"])
    return df.reset_index(drop=True)


def cache_msas() -> dict[str, Path]:
    """v1 결과에서 각 타겟별 a3m을 영구 캐시."""
    cache = {}
    for tgt in SCAR_TARGETS:
        donor = V1_MSA_DIR / tgt["msa_donor"]
        # uniref.a3m + bfd a3m을 합치기 (cat) — Boltz가 합쳐진 형태도 받음
        # 하지만 query line이 중복되면 안 되므로 가장 간단한 건 uniref.a3m 단독 사용
        src = donor / "uniref.a3m"
        if not src.exists():
            print(f"  ⚠️  {tgt['key']}: {src} 없음 — 다른 후보 시도")
            for alt in V1_MSA_DIR.glob(f"{tgt['key'].lower()}__*_unpaired_tmp_env"):
                cand = alt / "uniref.a3m"
                if cand.exists():
                    src = cand
                    break
        if not src.exists():
            print(f"  ❌ {tgt['key']}: MSA 못 찾음")
            continue
        dst = MSA_CACHE / f"{tgt['key'].lower()}.a3m"
        # null byte 제거 후 저장 (Boltz YAML 파서가 \x00을 거부)
        cleaned = src.read_bytes().replace(b"\x00", b"")
        dst.write_bytes(cleaned)
        n_seqs = sum(1 for line in dst.read_text(errors="ignore").splitlines() if line.startswith(">"))
        print(f"  ✅ {tgt['key']}: {n_seqs} seqs cached → {dst}")
        cache[tgt["key"]] = dst
    return cache


def build_yaml(target: dict, comp_name: str, smiles: str, out_dir: Path,
               msa_path: Path) -> Path:
    safe = comp_name.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").lower()
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {
                "id": "A",
                "sequence": target["sequence"],
                "msa": str(msa_path.absolute()),  # ← 핵심: 사전 캐시된 a3m
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
    print("흉터 파일럿 v2 — MSA 사전 캐시 + GPU 즉시 시작")
    print("=" * 70)

    # 1. MSA 캐시
    print("\n[1/4] MSA 캐시 확보...")
    msa_paths = cache_msas()
    if len(msa_paths) != 3:
        print(f"❌ 3개 타겟 MSA 모두 필요 ({len(msa_paths)}/3)")
        return 1

    # 2. 천연물 선택
    print("\n[2/4] 천연물 선택...")
    df = select_compounds()
    print(f"   {len(df)}개 화합물 (scar/wound/anti-inflam, MW ≤ 600)")

    # 3. Input YAML 생성
    print("\n[3/4] Input YAML 생성 (msa 경로 명시)...")
    inputs_dir = RESULT / "boltz2_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = RESULT / "boltz2_output"
    out_dir.mkdir(exist_ok=True)

    n_total = 0
    for target in SCAR_TARGETS:
        for _, row in df.iterrows():
            if pd.isna(row["smiles"]):
                continue
            build_yaml(target, row["name"], row["smiles"], inputs_dir,
                       msa_paths[target["key"]])
            n_total += 1
    print(f"   {n_total}개 YAML 생성 → {inputs_dir}")

    # 4. Boltz-2 실행 (use_msa_server 없음 — 캐시 MSA 사용)
    print("\n[4/4] Boltz-2 cofolding (MSA 미리 받음 → GPU 즉시 시작)...")
    boltz_bin = str(Path.home() / "genesis_medicine" / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(inputs_dir),
        "--out_dir", str(out_dir),
        # NO --use_msa_server — yaml에 msa 경로가 있으므로
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print(f"   cmd: {' '.join(cmd[:6])} ...")

    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    wall = time.time() - t0
    print(f"\n✅ 완료 in {wall/60:.1f}분 (exit={rc})")

    # 5. 결과 수집
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
        print("\n❌ 결과 0개 — 모든 input이 실패했음 (a3m 또는 YAML 파싱 문제)")
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
    pivot.to_csv(RESULT / "scar_consensus.csv")
    res.to_csv(RESULT / "scar_full.csv", index=False)

    print("\n=== 흉터 3타겟 합의 (top 15) ===")
    print(pivot.head(15).to_string(float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))
    print(f"\n✅ {RESULT}/scar_consensus.csv  +  scar_full.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
