"""흉터 파일럿 → ADMET 게이트 + manuscript 자동 생성.

흐름:
1. Boltz-2 결과 (scar_consensus.csv, scar_full.csv) 로드
2. ADMET-AI v2 — 49개 화합물 41 endpoints
3. 통합 결정 테이블 (consensus × ADMET)
4. manuscript_writer로 paper draft 자동
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).parent
RES = PILOT / "results_v2"


def main() -> int:
    # 1. Boltz-2 결과 로드
    cons = pd.read_csv(RES / "scar_consensus.csv", index_col=0)
    full = pd.read_csv(RES / "scar_full.csv")
    print(f"=== Boltz-2 결과: {len(cons)} 화합물 × 3 타겟 ===")

    # 2. 화합물 메타 + SMILES
    compounds = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    used = compounds[compounds["name"].isin(cons.index)].copy()
    print(f"   매칭 화합물 메타: {len(used)}")

    # 3. ADMET-AI v2
    print("\n=== ADMET-AI v2 ===")
    from admet_ai import ADMETModel
    model = ADMETModel(num_workers=2)
    smi_list = used["smiles"].dropna().tolist()
    name_to_smi = dict(zip(used["name"], used["smiles"]))
    smi_to_name = {v: k for k, v in name_to_smi.items()}
    preds = model.predict(smiles=smi_list)
    if isinstance(preds, pd.DataFrame):
        preds.insert(0, "compound", [smi_to_name.get(s, "?") for s in preds.index])
        admet_df = preds.reset_index(drop=True)
    else:
        admet_df = pd.DataFrame(preds)
    admet_df.to_csv(RES / "scar_admet.csv", index=False)
    print(f"   ✅ {len(admet_df)}/{len(smi_list)} 통과")

    # 4. 통합 결정 테이블
    rows = []
    for compound, row in cons.iterrows():
        a = admet_df[admet_df["compound"] == compound]
        if len(a) == 0:
            continue
        a = a.iloc[0]
        herg = float(a.get("hERG", 1.0))
        dili = float(a.get("DILI", 1.0))
        qed = float(a.get("QED", 0.0))
        bbb = float(a.get("BBB_Martins", 0.0))
        ames = float(a.get("AMES", 1.0))
        logp = float(a.get("logP", 0.0))
        mw = float(a.get("molecular_weight", 0.0))
        # 경피 외용제 적합 — BBB 대신 logP 1.5-3.5 + MW < 500
        topical_friendly = (1.5 <= logp <= 3.5) and (mw <= 500)

        cons_score = float(row.get("consensus_score", 0))
        # 외용제 종합 점수: cofolding + 안전 + 합성·물성
        topical_score = (
            cons_score
            * (1 - herg)
            * (1 - dili)
            * (1 - ames)
            * qed
            * (1.0 if topical_friendly else 0.6)
        )
        rows.append({
            "compound": compound,
            "consensus_affinity": round(cons_score, 3),
            "TGFB1": round(row.get("TGFB1", float("nan")), 3),
            "MMP1": round(row.get("MMP1", float("nan")), 3),
            "CTGF": round(row.get("CTGF", float("nan")), 3),
            "QED": round(qed, 3),
            "logP": round(logp, 2),
            "MW": round(mw, 1),
            "hERG": round(herg, 3),
            "DILI": round(dili, 3),
            "AMES": round(ames, 3),
            "BBB": round(bbb, 3),
            "topical_friendly": topical_friendly,
            "topical_score": round(topical_score, 4),
        })

    out = pd.DataFrame(rows).sort_values("topical_score", ascending=False)
    out_csv = RES / "scar_full_report.csv"
    out.to_csv(out_csv, index=False)
    print("\n" + "=" * 110)
    print("흉터 재생 — Boltz-2 affinity × ADMET × 외용제 적합도 통합 결정 테이블 (Top 20)")
    print("=" * 110)
    show_cols = ["compound", "consensus_affinity", "QED", "logP", "MW",
                 "hERG", "DILI", "topical_friendly", "topical_score"]
    print(out[show_cols].head(20).to_string(index=False))
    print(f"\n✅ 저장: {out_csv}")

    # 5. Manuscript 자동 생성
    print("\n=== Manuscript 자동 생성 ===")
    from genesis_medicine.reporting import StudyContext, build_manuscript

    # consensus 형태 그대로 사용 (column = target)
    ctx = StudyContext(
        name="skin_scar_v2",
        title=("Multi-target structure-based screening of Korean herbal natural "
               "products against TGF-β1, MMP-1, and CTGF for skin scar regeneration"),
        short_title="Korean herb scar SBVS",
        disease="Skin scar (hypertrophic, atrophic, keloid)",
        description=(
            "본 연구는 한국 한방 처방(자운고·자운고 변형·당귀음자·황련해독탕 등)의 "
            "핵심 천연물 49종에 대해 흉터 3대 분자 타겟(TGF-β1, MMP-1, CTGF)에 "
            "Boltz-2 공동접힘 + 친화도 head를 적용하고, ADMET-AI v2로 약물성 게이트를 "
            "통과한 후보를 도출한다."
        ),
        results_dir=RES,
        consensus_csv=RES / "scar_consensus.csv",
        full_csv=RES / "scar_full.csv",
        compounds_csv=ROOT / "data/skin_compounds_curated.csv",
        targets=[
            {"key": "TGFB1", "uniprot": "P01137", "display": "TGF-β1",
             "mode": "antagonist"},
            {"key": "MMP1", "uniprot": "P03956", "display": "MMP-1 (collagenase)",
             "mode": "inhibitor"},
            {"key": "CTGF", "uniprot": "P29279", "display": "CTGF / CCN2",
             "mode": "antagonist"},
        ],
        components_used=[
            "boltz2", "admet_ai", "rdkit", "openmm",
            "alphafold_db", "pubchem", "coconut_2", "lotus", "npass_3",
            "mmseqs2", "colabfold_code",
        ],
        output_dir=RES / "manuscript",
        seed=42,
        license_profile="commercial",
        authors=[
            {"name": "Recover Clinic Computational Team",
             "affiliation": "Recover Clinic, Gangnam, Seoul, Korea",
             "orcid": ""},
        ],
        correspondence_email="research@recover-clinic.kr",
        funding="Self-funded R&D by Recover Clinic.",
        conflicts="The authors declare no conflicts of interest.",
    )
    result = build_manuscript(ctx)
    print(f"✅ {result.manuscript_md}")
    print(f"   word_count: {result.word_count}")
    print(f"   figures   : {len(result.figures)} files")
    print(f"   tables    : {len(result.tables)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
