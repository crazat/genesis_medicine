"""scaffold-hop top hits → Boltz-2 cofold (TGFB1/MMP1/CTGF).

목적: ADMET-AI로 우선 선별된 변형이 seed의 affinity profile을 유지하는지 검증.
승리 기준: 후보 affinity_probability_binary ≥ seed - 0.05 (5% 이내 동등 또는 상향).

Cached MSA (data/msa/{target}.a3m) 사용 → MSA fetch 없이 GPU 즉시 시작.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = Path.home() / "genesis_medicine" / "data"
MSA_CACHE = DATA / "msa"
SCAFFOLD = ROOT / "pilot/scaffold_hop"
OUT = SCAFFOLD / "boltz2_validation"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    {"key": "TGFB1", "uniprot": "P01137",
     "sequence": "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS"},
    {"key": "MMP1", "uniprot": "P03956",
     "sequence": "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"},
    {"key": "CTGF", "uniprot": "P29279",
     "sequence": "MTAARLALSCAALAALLPGATALPDGCGCGGRAHWGCGAVGEACSAALEIGSTVFASTPTPPSYAAEIRPGLPVDQDPCRLRAVCESFYHPSSALARQLPRAEPGFNVQDRRLILAGCGCGCQNGCSEPLQPYPLSPCSKQCQPGYQCDDSPSCSCQCLPGCASGAQCAQCRPRPESESSCRKQSCSCRQQGSVHCGYAVKDGGRGCYAGCTSDLDQVDFGCCSHKASNFGSCSSPVRDCGYHWGFPPYHQCASNMGYLLDPLDCQCYFNASGAGAQVFFGGADCGFANGCNQGSPLSF"},
]

# baseline (skin_scar v2 결과에서 추출, 2026-04-25)
SEED_BASELINE = {
    "embelin":  {"TGFB1": 0.746, "MMP1": 0.584, "CTGF": 0.732},
    "curcumin": {"TGFB1": 0.568, "MMP1": 0.508, "CTGF": 0.752},
}

TOP_N = 3   # 각 seed 별 상위 3개만 검증


def collect_top_hits() -> list[dict]:
    rows = []
    for seed in ["embelin", "curcumin"]:
        ranked = SCAFFOLD / seed / "outputs/ranked.csv"
        if not ranked.exists():
            print(f"⚠️  {ranked} 없음")
            continue
        df = pd.read_csv(ranked)
        for i, r in df.head(TOP_N).iterrows():
            rows.append({
                "seed": seed,
                "rank": i + 1,
                "name": f"{seed}_emb{i+1}" if seed == "embelin" else f"cur{i+1}",
                "smiles": r["smiles"],
                "score": float(r["score"]),
                "hERG": float(r["hERG"]),
                "skin": float(r["Skin_Reaction"]),
                "logP": float(r["logP"]),
                "MW": float(r["MW"]),
            })
    return rows


def build_yaml(target: dict, comp: dict, out_dir: Path, msa_path: Path) -> Path:
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": target["sequence"],
                         "msa": str(msa_path.absolute())}},
            {"ligand": {"id": "B", "smiles": comp["smiles"]}},
        ],
        "properties": [{"affinity": {"binder": "B"}}],
    }
    p = out_dir / f"{target['key'].lower()}__{comp['name']}.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def main() -> int:
    hits = collect_top_hits()
    if not hits:
        print("❌ scaffold_hop top hits 없음 — analyze_scaffold_hop.py 먼저 실행")
        return 1
    print(f"=== 검증 대상: {len(hits)} 변형 × {len(TARGETS)} 타겟 = "
          f"{len(hits) * len(TARGETS)} cofold ===\n")
    for h in hits:
        print(f"  [{h['name']}] score={h['score']:.3f} hERG={h['hERG']:.2f} "
              f"skin={h['skin']:.2f} | {h['smiles']}")

    # MSA 확인
    msa_paths = {}
    for tgt in TARGETS:
        p = MSA_CACHE / f"{tgt['key'].lower()}.a3m"
        if not p.exists():
            print(f"\n❌ MSA 캐시 없음: {p}")
            return 2
        msa_paths[tgt["key"]] = p
    print(f"\n✅ MSA 캐시 3개 모두 확보: {[str(p) for p in msa_paths.values()]}")

    # Input YAML 생성
    inputs_dir = OUT / "inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = OUT / "output"
    out_dir.mkdir(exist_ok=True)
    n_yaml = 0
    for tgt in TARGETS:
        for h in hits:
            build_yaml(tgt, h, inputs_dir, msa_paths[tgt["key"]])
            n_yaml += 1
    print(f"\n✅ {n_yaml} YAML → {inputs_dir}")

    # Boltz-2 실행
    boltz = str(Path(sys.executable).parent / "boltz")
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
    print(f"\n=== Boltz-2 실행 ({n_yaml} 항목) ===")
    print(f"$ {' '.join(cmd[:5])} …")
    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    wall = time.time() - t0
    print(f"\n✅ 완료 in {wall/60:.1f}분 (exit={rc})")

    # 결과 수집
    rows = []
    for aff in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        target_key, comp_name = stem.split("__", 1)
        rows.append({
            "target": target_key.upper(),
            "compound": comp_name,
            "seed": "embelin" if comp_name.startswith("embelin_") else "curcumin",
            "affinity_pred_value": d.get("affinity_pred_value"),
            "affinity_probability_binary": d.get("affinity_probability_binary"),
        })
    res = pd.DataFrame(rows)

    # baseline 비교
    res["seed_baseline"] = res.apply(
        lambda r: SEED_BASELINE[r["seed"]].get(r["target"], None), axis=1)
    res["delta"] = (res["affinity_probability_binary"]
                    - res["seed_baseline"])
    res["passes"] = res["delta"] >= -0.05  # 5% 이내 또는 상향

    pivot = res.pivot_table(index="compound", columns="target",
                            values="affinity_probability_binary",
                            aggfunc="first")
    pivot["mean"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("mean", ascending=False)
    pivot.to_csv(OUT / "validation_consensus.csv")
    res.to_csv(OUT / "validation_full.csv", index=False)

    print("\n=== Affinity per target (binary prob, 1.0 = strong binder) ===")
    print(pivot.to_string(float_format=lambda v: f"{v:.3f}"
                          if pd.notna(v) else "—"))

    print("\n=== Seed baseline 대비 ===")
    for seed in ["embelin", "curcumin"]:
        sub = res[res["seed"] == seed]
        n_pass = sub["passes"].sum()
        n_total = len(sub)
        print(f"  {seed}: {n_pass}/{n_total} cofold passes "
              f"(Δ ≥ -0.05 vs seed)")
        for _, r in sub.iterrows():
            sym = "✅" if r["passes"] else "⚠️"
            print(f"    {sym} {r['compound']:25s} × {r['target']:6s} "
                  f"= {r['affinity_probability_binary']:.3f}  "
                  f"(seed {r['seed_baseline']:.3f}, Δ {r['delta']:+.3f})")

    print(f"\n✅ {OUT}/validation_full.csv  +  validation_consensus.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
