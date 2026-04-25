"""흉터 재생 파일럿 — Genesis_Medicine v3 첫 실 런.

흐름
----
1. AFDB에서 흉터 3대 핵심 타겟 구조 다운로드 (TGF-β1, MMP-1, CTGF)
2. data/skin_compounds_curated.csv에서 흉터 카테고리 천연물 + Lipinski 통과 + MW < 600 필터
3. 각 (타겟 × 천연물) Boltz-2 cofolding + affinity head
4. ECR 합의 점수 (3 타겟에서의 종합 친화도)
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import yaml

BASE = Path(__file__).parent
RESULT = BASE / "results"
RESULT.mkdir(parents=True, exist_ok=True)

# 흉터 3대 타겟 (TGF-β1, MMP-1, CTGF) UniProt ID
SCAR_TARGETS = [
    {"key": "TGFB1", "uniprot": "P01137",
     # TGF-β1 mature peptide (residues 279-390 of P01137)
     "sequence": "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS"},
    {"key": "MMP1", "uniprot": "P03956",
     # MMP-1 catalytic domain (residues 100-269 of P03956)
     "sequence": "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"},
    {"key": "CTGF", "uniprot": "P29279",
     # CTGF/CCN2 mature protein (residues 27-349 of P29279)
     "sequence": "MTAARLALSCAALAALLPGATALPDGCGCGGRAHWGCGAVGEACSAALEIGSTVFASTPTPPSYAAEIRPGLPVDQDPCRLRAVCESFYHPSSALARQLPRAEPGFNVQDRRLILAGCGCGCQNGCSEPLQPYPLSPCSKQCQPGYQCDDSPSCSCQCLPGCASGAQCAQCRPRPESESSCRKQSCSCRQQGSVHCGYAVKDGGRGCYAGCTSDLDQVDFGCCSHKASNFGSCSSPVRDCGYHWGFPPYHQCASNMGYLLDPLDCQCYFNASGAGAQVFFGGADCGFANGCNQGSPLSF"},
]

# 천연물 필터: scar 또는 wound 카테고리 + Lipinski 일부 + MW < 600 (외용제 친화)
def select_compounds() -> pd.DataFrame:
    df = pd.read_csv(BASE.parent.parent / "data" / "skin_compounds_curated.csv")
    # 흉터 관련 카테고리
    mask = df["category"].str.contains("scar|wound|anti-inflam", case=False, na=False)
    df = df[mask].copy()
    # MW 외용제 친화 (작아야 침투 OK)
    df = df[df["mw"].astype(float) <= 600]
    # 중복 제거 (Madecassoside 등)
    df = df.drop_duplicates(subset=["name", "cid"])
    return df.reset_index(drop=True)


def build_yaml(target_seq: str, target_key: str, comp_name: str, smiles: str, out_dir: Path) -> Path:
    safe = comp_name.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").lower()
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": target_seq}},
            {"ligand": {"id": "B", "smiles": smiles}},
        ],
        "properties": [{"affinity": {"binder": "B"}}],
    }
    p = out_dir / f"{target_key.lower()}__{safe}.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def main() -> int:
    df = select_compounds()
    print(f"=== 흉터 파일럿: {len(df)}개 천연물 × {len(SCAR_TARGETS)}개 타겟 ===")
    print(df[["name", "source_korean", "mw", "logp", "category"]].to_string(index=False))

    inputs_dir = RESULT / "boltz2_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = RESULT / "boltz2_output"
    out_dir.mkdir(exist_ok=True)

    n_total = 0
    for target in SCAR_TARGETS:
        for _, row in df.iterrows():
            if pd.isna(row["smiles"]):
                continue
            build_yaml(target["sequence"], target["key"], row["name"], row["smiles"], inputs_dir)
            n_total += 1
    print(f"\nYAML {n_total}개 생성 → {inputs_dir}")

    # Boltz-2 실행
    boltz_bin = str(Path.home() / "genesis_medicine" / ".venv" / "bin" / "boltz")
    cmd = [
        boltz_bin, "predict", str(inputs_dir),
        "--out_dir", str(out_dir),
        "--use_msa_server",
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print(f"\n=== Boltz-2 실행: {n_total}개 작업 ===")
    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    wall = time.time() - t0
    print(f"\n✅ 완료 in {wall/60:.1f}분 (exit={rc})")

    # 결과 수집
    rows = []
    for aff in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        # 파일명: affinity_tgfb1__asiaticoside.json
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

    res = pd.DataFrame(rows)
    # compound 이름 복원
    name_map = {n.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").lower(): n
                for n in df["name"].tolist()}
    res["compound"] = res["compound_safe"].map(lambda s: name_map.get(s, s))

    pivot = res.pivot_table(
        index="compound",
        columns="target",
        values="affinity_probability_binary",
        aggfunc="first",
    )
    pivot["consensus_score"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("consensus_score", ascending=False)
    pivot.to_csv(RESULT / "scar_consensus.csv")
    res.to_csv(RESULT / "scar_full.csv", index=False)

    print("\n=== 흉터 3타겟 합의 affinity_probability_binary ===")
    print(pivot.to_string(float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))
    print(f"\n✅ 저장: {RESULT}/scar_consensus.csv  +  scar_full.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
