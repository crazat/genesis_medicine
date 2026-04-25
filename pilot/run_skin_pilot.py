"""Generic skin pilot runner.

탈모/여드름/광노화/(흉터/기미는 별도 디렉터리에 있지만 호환) 4-5개 질환을
하나의 스크립트로 일괄 실행.

흐름
----
1. CLI: --disease alopecia | acne | photoaging
2. UniProt에서 타겟 시퀀스 자동 fetch
3. MSA 캐시 (없으면 ColabFold 1회 호출)
4. compound 카테고리 매칭 → 자동 필터
5. Boltz-2 cofolding (147 quad / cofolding 단계)
6. ADMET-AI v2 + 외용제 종합점수
7. manuscript with 양 단위 novelty 자동 생성
"""

from __future__ import annotations

import argparse
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
MSA_CACHE.mkdir(parents=True, exist_ok=True)


# ---------- 질환별 프리셋 ----------

PRESETS = {
    "alopecia": {
        "title": ("Multi-target structure-based screening of Korean herbal natural "
                  "products against 5α-reductase 2, androgen receptor, and Wnt/β-catenin "
                  "for androgenetic alopecia"),
        "short_title": "Korean herb AGA SBVS",
        "disease": "androgenetic alopecia",
        "disease_synonyms": ["alopecia", "hair loss", "balding", "AGA"],
        "compound_categories": ["alopecia", "hair", "anti-inflam", "multi"],
        "topical_logp": (1.5, 4.5),     # 두피·모낭 침투
        "targets": [
            {"key": "SRD5A2",  "uniprot": "P31213", "display": "5α-reductase type 2",
             "mode": "inhibitor"},
            {"key": "AR",       "uniprot": "P10275", "display": "Androgen receptor",
             "mode": "antagonist"},
            {"key": "CTNNB1",   "uniprot": "P35222", "display": "β-catenin",
             "mode": "stabilizer_preserve"},
        ],
        "differentiators": [
            "Boltz-2 cofolding + affinity head (FEP-grade)",
            "다중 타겟 ECR (5αR + AR + Wnt)",
            "두피·모낭 침투 logP 1.5-4.5 게이트",
            "한방 처방 (하수오·측백·인삼) 분자 메커니즘 매핑",
        ],
    },
    "acne": {
        "title": ("Multi-target structure-based screening of Korean herbal natural "
                  "products against androgen receptor, NLRP3 inflammasome, and TLR2 for "
                  "acne vulgaris"),
        "short_title": "Korean herb acne SBVS",
        "disease": "acne vulgaris",
        "disease_synonyms": ["acne", "pimple", "comedone", "Cutibacterium acnes"],
        "compound_categories": ["acne", "anti-inflam", "antibact", "multi"],
        "topical_logp": (1.0, 4.0),
        "targets": [
            {"key": "AR",       "uniprot": "P10275", "display": "Androgen receptor",
             "mode": "antagonist"},
            {"key": "SRD5A2",   "uniprot": "P31213", "display": "5α-reductase type 2",
             "mode": "inhibitor"},
            {"key": "PTGS2",    "uniprot": "P35354", "display": "COX-2",
             "mode": "selective_inhibitor"},
        ],
        "differentiators": [
            "4축 (피지·각화·C. acnes·염증) 동시 평가 지향",
            "Boltz-2 + ADMET 외용제 게이트",
            "황련해독탕·방풍통성산 분자 메커니즘",
        ],
    },
    "photoaging": {
        "title": ("Multi-target structure-based screening of Korean herbal natural "
                  "products against MMP-1, SIRT1, and AP-1 for skin photoaging"),
        "short_title": "Korean herb photoaging SBVS",
        "disease": "photoaging",
        "disease_synonyms": ["skin aging", "wrinkle", "UV damage", "anti-aging"],
        "compound_categories": ["photoaging", "anti-inflam", "multi"],
        "topical_logp": (1.5, 5.0),
        "targets": [
            {"key": "MMP1",  "uniprot": "P03956", "display": "MMP-1",
             "mode": "inhibitor"},
            {"key": "SIRT1", "uniprot": "Q96EB6", "display": "SIRT1",
             "mode": "allosteric_activator"},
            {"key": "JUN",   "uniprot": "P05412", "display": "c-Jun (AP-1)",
             "mode": "suppressor"},
        ],
        "differentiators": [
            "MMP-1 inhibitor + SIRT1 activator 이중작용 우선",
            "Boltz-2 + ADMET-AI 외용 안티에이징 적합도",
            "사물탕·옥용산 분자 정량",
        ],
    },
}


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


def get_or_fetch_msa(target: dict, work_dir: Path) -> Path:
    key = target["key"].lower()
    cache_path = MSA_CACHE / f"{key}.a3m"
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return cache_path

    print(f"  ⏳ {target['key']}: MSA 없음 — ColabFold 1회 호출")
    tmp_dir = work_dir / "msa_bootstrap" / key
    yaml_path = tmp_dir / "input" / "bootstrap.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": target["sequence"]}},
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
    a3m_candidates = list(out_dir.rglob("*_unpaired_tmp_env/uniref.a3m"))
    if not a3m_candidates:
        raise RuntimeError(f"{target['key']} MSA 못 받음")
    src = a3m_candidates[0]
    cleaned = src.read_bytes().replace(b"\x00", b"")
    cache_path.write_bytes(cleaned)
    n = sum(1 for line in cache_path.read_text(errors="ignore").splitlines() if line.startswith(">"))
    print(f"  ✅ {target['key']}: {n} seqs → {cache_path}")
    return cache_path


def select_compounds(categories: list[str]) -> pd.DataFrame:
    df = pd.read_csv(DATA / "skin_compounds_curated.csv")
    pat = "|".join(categories)
    mask = df["category"].str.contains(pat, case=False, na=False)
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


def run_pipeline(disease_key: str) -> int:
    if disease_key not in PRESETS:
        print(f"❌ 알 수 없는 질환: {disease_key}. 가능: {list(PRESETS)}")
        return 1
    cfg = PRESETS[disease_key]

    pilot_dir = ROOT / "pilot" / f"skin_{disease_key}"
    pilot_dir.mkdir(parents=True, exist_ok=True)
    res = pilot_dir / "results_v1"
    res.mkdir(exist_ok=True)

    print("=" * 70)
    print(f"피부 파일럿 — {disease_key} ({cfg['title'][:60]}…)")
    print("=" * 70)

    # 1. 타겟 sequence
    print(f"\n[1/6] 타겟 시퀀스 ({len(cfg['targets'])}개)")
    for t in cfg["targets"]:
        t["sequence"] = fetch_uniprot_seq(t["uniprot"])
        print(f"   {t['key']} ({t['uniprot']}): {len(t['sequence'])} aa")

    # 2. MSA 캐시
    print(f"\n[2/6] MSA 캐시")
    msa_paths = {}
    for t in cfg["targets"]:
        msa_paths[t["key"]] = get_or_fetch_msa(t, res)

    # 3. 화합물 선택
    print(f"\n[3/6] 천연물 선택 (카테고리: {cfg['compound_categories']})")
    df_comp = select_compounds(cfg["compound_categories"])
    print(f"   {len(df_comp)} 화합물")

    # 4. YAML 생성
    print(f"\n[4/6] Input YAML")
    inputs_dir = res / "boltz2_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = res / "boltz2_output"
    out_dir.mkdir(exist_ok=True)
    n_total = 0
    for t in cfg["targets"]:
        for _, row in df_comp.iterrows():
            if pd.isna(row["smiles"]):
                continue
            build_yaml(t, row["name"], row["smiles"], inputs_dir, msa_paths[t["key"]])
            n_total += 1
    print(f"   {n_total} runs")

    # 5. Boltz-2 cofolding
    print(f"\n[5/6] Boltz-2 cofolding...")
    boltz_bin = str(ROOT / ".venv" / "bin" / "boltz")
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
    subprocess.run(cmd)
    print(f"   ✅ {(time.time()-t0)/60:.1f}분")

    # 6. 결과 수집
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
        print("❌ 결과 없음"); return 2

    res_df = pd.DataFrame(rows)
    name_map = {n.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").lower(): n
                for n in df_comp["name"].tolist()}
    res_df["compound"] = res_df["compound_safe"].map(lambda s: name_map.get(s, s))
    pivot = res_df.pivot_table(index="compound", columns="target",
                               values="affinity_probability_binary", aggfunc="first")
    pivot["consensus_score"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("consensus_score", ascending=False)
    pivot.to_csv(res / f"{disease_key}_consensus.csv")
    res_df.to_csv(res / f"{disease_key}_full.csv", index=False)

    # 7. ADMET + manuscript (with novelty)
    print(f"\n[6/6] ADMET-AI + manuscript (with 양 단위 novelty)")
    from admet_ai import ADMETModel
    model = ADMETModel(num_workers=2)
    used = df_comp[df_comp["name"].isin(pivot.index)].copy()
    smi_to_name = {s: n for n, s in zip(used["name"], used["smiles"]) if pd.notna(s)}
    preds = model.predict(smiles=used["smiles"].dropna().tolist())
    preds.insert(0, "compound", [smi_to_name.get(s, "?") for s in preds.index])
    preds.reset_index(drop=True).to_csv(res / f"{disease_key}_admet.csv", index=False)

    logp_lo, logp_hi = cfg["topical_logp"]
    rows2 = []
    for compound, row in pivot.iterrows():
        a = preds[preds["compound"] == compound]
        if len(a) == 0:
            continue
        a = a.iloc[0]
        herg, dili = float(a.get("hERG", 1.0)), float(a.get("DILI", 1.0))
        qed, ames = float(a.get("QED", 0.0)), float(a.get("AMES", 1.0))
        logp, mw = float(a.get("logP", 0.0)), float(a.get("molecular_weight", 0.0))
        topical = (logp_lo <= logp <= logp_hi) and (mw <= 500)
        cs = float(row.get("consensus_score", 0))
        score = cs * (1 - herg) * (1 - dili) * (1 - ames) * qed * (1.0 if topical else 0.6)
        rows2.append({
            "compound": compound, "consensus_affinity": round(cs, 3),
            **{f"{t['key']}": round(row.get(t['key'], float('nan')), 3) for t in cfg["targets"]},
            "QED": round(qed, 3), "logP": round(logp, 2), "MW": round(mw, 1),
            "hERG": round(herg, 3), "DILI": round(dili, 3),
            "topical_friendly": topical, "topical_score": round(score, 4),
        })
    full_report = pd.DataFrame(rows2).sort_values("topical_score", ascending=False)
    full_report.to_csv(res / f"{disease_key}_full_report.csv", index=False)
    print(f"   Top 5 외용제: {full_report.head(5)['compound'].tolist()}")

    # Manuscript
    from genesis_medicine.reporting import StudyContext, build_manuscript
    ctx = StudyContext(
        name=f"skin_{disease_key}_v1",
        title=cfg["title"],
        short_title=cfg["short_title"],
        disease=cfg["disease"],
        disease_synonyms=cfg["disease_synonyms"],
        description=(f"본 연구는 한국 한방 처방 천연물에 대해 {cfg['disease']} 핵심 "
                     f"분자 타겟 {len(cfg['targets'])}개에 Boltz-2 cofolding + "
                     f"affinity head를 적용한다."),
        results_dir=res,
        consensus_csv=res / f"{disease_key}_consensus.csv",
        full_csv=res / f"{disease_key}_full.csv",
        compounds_csv=DATA / "skin_compounds_curated.csv",
        targets=[{"key": t["key"], "uniprot": t["uniprot"],
                  "display": t["display"], "mode": t["mode"]}
                 for t in cfg["targets"]],
        components_used=[
            "boltz2", "admet_ai", "rdkit", "openmm",
            "alphafold_db", "pubchem", "coconut_2", "lotus", "npass_3",
            "mmseqs2", "colabfold_code",
        ],
        output_dir=res / "manuscript",
        seed=42, license_profile="commercial",
        authors=[{"name": "Recover Clinic Computational Team",
                  "affiliation": "Recover Clinic, Gangnam, Seoul, Korea",
                  "orcid": ""}],
        correspondence_email="research@recover-clinic.kr",
        enable_novelty=True, novelty_top_n=10,
        enable_system_novelty=True,
        system_methods=["structure-based virtual screening", "molecular docking", "co-folding"],
        system_data_sources=["Korean traditional medicine", "natural products"],
        system_unique_tools=["Boltz-2", "ADMET-AI", "AlphaFold"],
        system_differentiators=cfg["differentiators"],
    )
    result = build_manuscript(ctx)
    print(f"\n✅ {result.manuscript_md}\n   words={result.word_count}, "
          f"figs={len(result.figures)}, tables={len(result.tables)}")

    # PDF 변환
    sh = ROOT / "scripts" / "manuscript_to_pdf.sh"
    rel = (res / "manuscript").relative_to(ROOT)
    subprocess.run(["bash", str(sh), str(rel), "phytomedicine"],
                   capture_output=True)
    print(f"   ✅ PDF/DOCX/HTML 변환 완료")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--disease", required=True, choices=list(PRESETS.keys()))
    args = p.parse_args()
    return run_pipeline(args.disease)


if __name__ == "__main__":
    sys.exit(main())
