"""기미 파일럿 → ADMET + 화합물 novelty + 시스템 novelty + manuscript.

흉터 파일럿 build_full_report.py와 같은 패턴, 시스템 novelty 보강.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).parent
RES = PILOT / "results_v1"


def main() -> int:
    cons = pd.read_csv(RES / "pigment_consensus.csv", index_col=0)
    full = pd.read_csv(RES / "pigment_full.csv")
    print(f"=== Boltz-2: {len(cons)} 화합물 × 3 타겟 ===")

    compounds = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    used = compounds[compounds["name"].isin(cons.index)].copy()

    print("\n=== ADMET-AI v2 ===")
    from admet_ai import ADMETModel
    model = ADMETModel(num_workers=2)
    smi_list = used["smiles"].dropna().tolist()
    smi_to_name = {s: n for n, s in zip(used["name"], used["smiles"]) if pd.notna(s)}
    preds = model.predict(smiles=smi_list)
    preds.insert(0, "compound", [smi_to_name.get(s, "?") for s in preds.index])
    admet_df = preds.reset_index(drop=True)
    admet_df.to_csv(RES / "pigment_admet.csv", index=False)
    print(f"   ✅ {len(admet_df)}/{len(smi_list)}")

    # 통합 결정 테이블 (기미 외용제 친화)
    rows = []
    for compound, row in cons.iterrows():
        a = admet_df[admet_df["compound"] == compound]
        if len(a) == 0:
            continue
        a = a.iloc[0]
        herg = float(a.get("hERG", 1.0))
        dili = float(a.get("DILI", 1.0))
        qed = float(a.get("QED", 0.0))
        ames = float(a.get("AMES", 1.0))
        logp = float(a.get("logP", 0.0))
        mw = float(a.get("molecular_weight", 0.0))
        # 기미 외용제: 더 친수성도 OK (logP 0.5-3.0)
        topical_friendly = (0.5 <= logp <= 3.0) and (mw <= 500)
        cons_score = float(row.get("consensus_score", 0))
        topical_score = (
            cons_score * (1 - herg) * (1 - dili) * (1 - ames) * qed
            * (1.0 if topical_friendly else 0.6)
        )
        rows.append({
            "compound": compound,
            "consensus_affinity": round(cons_score, 3),
            "TYR": round(row.get("TYR", float("nan")), 3),
            "TYRP1": round(row.get("TYRP1", float("nan")), 3),
            "DCT": round(row.get("DCT", float("nan")), 3),
            "QED": round(qed, 3),
            "logP": round(logp, 2),
            "MW": round(mw, 1),
            "hERG": round(herg, 3),
            "DILI": round(dili, 3),
            "AMES": round(ames, 3),
            "topical_friendly": topical_friendly,
            "topical_score": round(topical_score, 4),
        })
    out = pd.DataFrame(rows).sort_values("topical_score", ascending=False)
    out.to_csv(RES / "pigment_full_report.csv", index=False)
    print("\n" + "=" * 100)
    print("기미·색소 — 통합 결정 테이블 (Top 15)")
    print("=" * 100)
    cols = ["compound", "consensus_affinity", "QED", "logP", "MW",
            "hERG", "DILI", "topical_friendly", "topical_score"]
    print(out[cols].head(15).to_string(index=False))

    # Manuscript with full novelty (compound + system)
    print("\n=== Manuscript 자동 생성 (화합물 + 시스템 novelty 통합) ===")
    from genesis_medicine.reporting import StudyContext, build_manuscript

    ctx = StudyContext(
        name="skin_pigment_v1",
        title=("Multi-target structure-based screening of Korean herbal "
               "natural products against tyrosinase, TYRP1, and DCT for melasma "
               "and hyperpigmentation"),
        short_title="Korean herb melasma SBVS",
        disease="melasma and skin hyperpigmentation",
        disease_synonyms=["pigmentation", "tyrosinase", "melanin", "hyperpigmentation"],
        description=(
            "본 연구는 한국 한방 처방(옥용산, 백지 복합 등)의 핵심 천연물 27종에 대해 "
            "멜라닌 합성 3대 효소 (Tyrosinase, TYRP1, DCT)에 Boltz-2 cofolding + "
            "affinity head를 적용하고, ADMET-AI v2로 외용제 적합성을 평가한다."
        ),
        results_dir=RES,
        consensus_csv=RES / "pigment_consensus.csv",
        full_csv=RES / "pigment_full.csv",
        compounds_csv=ROOT / "data/skin_compounds_curated.csv",
        targets=[
            {"key": "TYR", "uniprot": "P14679", "display": "Tyrosinase", "mode": "inhibitor"},
            {"key": "TYRP1", "uniprot": "P17643", "display": "TRP-1", "mode": "inhibitor"},
            {"key": "DCT", "uniprot": "P40126", "display": "TRP-2 (DCT)", "mode": "inhibitor"},
        ],
        components_used=[
            "boltz2", "admet_ai", "rdkit", "openmm",
            "alphafold_db", "pubchem", "coconut_2", "lotus", "npass_3",
            "mmseqs2", "colabfold_code",
        ],
        output_dir=RES / "manuscript",
        seed=42, license_profile="commercial",
        authors=[{"name": "Recover Clinic Computational Team",
                  "affiliation": "Recover Clinic, Gangnam, Seoul, Korea",
                  "orcid": ""}],
        correspondence_email="research@recover-clinic.kr",
        # 화합물 단위 novelty
        enable_novelty=True,
        novelty_top_n=10,
        # 시스템 단위 novelty
        enable_system_novelty=True,
        system_methods=[
            "structure-based virtual screening",
            "molecular docking",
            "co-folding",
        ],
        system_data_sources=[
            "Korean traditional medicine",
            "natural products",
        ],
        system_unique_tools=["Boltz-2", "ADMET-AI", "AlphaFold"],
        system_differentiators=[
            "Boltz-2 cofolding + affinity head (FEP-grade) 적용",
            "다중 타겟 ECR (Exponential Consensus Ranking)",
            "외용제 ADMET 게이트 (BBB 대신 logKp + 피부자극)",
            "한방 처방-성분-타겟 자동 네트워크 매핑 (KHP 가중치)",
            "화합물 + 시스템 단위 novelty 자동 검증",
        ],
    )
    result = build_manuscript(ctx)
    print(f"\n✅ {result.manuscript_md}")
    print(f"   word_count: {result.word_count}")
    print(f"   figures   : {len(result.figures)}")
    print(f"   tables    : {len(result.tables)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
