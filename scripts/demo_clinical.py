"""흉터 + 기미 IRB 프로토콜 + CRO 견적 시연 생성."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clinical_outputs"
OUT.mkdir(exist_ok=True)


def main() -> int:
    from genesis_medicine.clinical import (ClinicalContext,
                                            generate_irb_protocol,
                                            generate_consent_form_korean,
                                            generate_consent_form_english,
                                            estimate_total_cost)
    from genesis_medicine.clinical.cro_quote import render_quote_markdown

    # ---- 흉터 IRB ----
    scar = ClinicalContext(
        title="센텔라 + 자운고 외용 vs 표준치료 비교 임상시험 (atrophic scar, RCT)",
        pi_name="Recover 한의원 PI",
        pi_affiliation="Recover 한의원",
        sponsor="Recover Clinic R&D",
        sponsor_address="서울 강남구 (TBD, 2026-08 오픈)",
        disease="여드름 흉터 / 위축성 흉터 (atrophic acne scar)",
        intervention="센텔라 외용 + 새살침 (자초 추출물 함유)",
        n_subjects=40,
        duration_weeks=12,
        primary_outcome="AI 안면 분석 흉터 깊이/면적 변화율 (12주 vs baseline)",
        in_silico_evidence=(
            "Genesis_Medicine v3 흉터 파일럿 (49 화합물 × TGF-β1/MMP-1/CTGF 3타겟): "
            "센텔라(Asiaticoside, Madecassoside, Asiatic acid)는 ADMET 안전 게이트 통과, "
            "자초의 Acetylshikonin·Shikonin은 affinity probability 0.62-0.73으로 top-5 결합. "
            "TGF-β1 + MMP-1 + CTGF 3-타겟 ECR 합의 점수 0.65 (자운고 평균)."
        ),
        has_acupuncture=True, has_constitutional_rx=False,
    )
    (OUT / "scar_irb_protocol.md").write_text(generate_irb_protocol(scar), encoding="utf-8")
    (OUT / "scar_consent_kr.md").write_text(generate_consent_form_korean(scar), encoding="utf-8")
    (OUT / "scar_consent_en.md").write_text(generate_consent_form_english(scar), encoding="utf-8")
    print(f"✅ 흉터 IRB + 동의서 (한글/영문) → {OUT}/scar_*.md")

    # ---- 기미 IRB ----
    pigment = ClinicalContext(
        title="옥용산 유래 천연물 (kojic acid + arbutin + glabridin) 외용 vs 4% hydroquinone 비교 (멜라스마)",
        pi_name="Recover 한의원 PI",
        pi_affiliation="Recover 한의원",
        sponsor="Recover Clinic R&D",
        sponsor_address="서울 강남구 (TBD, 2026-08 오픈)",
        disease="안면 멜라스마 (melasma)",
        intervention="옥용산 유래 천연물 복합 외용 크림 (kojic + arbutin + glabridin)",
        n_subjects=30,
        duration_weeks=12,
        primary_outcome="MASI score (Melasma Area and Severity Index) + AI 색소 정량 변화",
        secondary_outcomes=[
            "환자 만족도 VAS",
            "이상반응",
            "VISIA 색소 점수",
        ],
        in_silico_evidence=(
            "Genesis_Medicine v3 기미 파일럿 (27 화합물 × TYR/TYRP1/DCT 3타겟): "
            "Ellagic acid 0.673 / Resveratrol 0.633 / Apigenin 0.630 등 강한 결합. "
            "Azelaic acid (FDA 승인 미백 1차)을 시스템이 정확히 1순위로 도출하여 인프라 검증. "
            "**System novelty 1.00 (blue ocean)**: '한방 + Boltz-2 + 멜라닌 효소' 첫 시도."
        ),
        has_acupuncture=False, has_constitutional_rx=False,
    )
    (OUT / "pigment_irb_protocol.md").write_text(generate_irb_protocol(pigment), encoding="utf-8")
    (OUT / "pigment_consent_kr.md").write_text(generate_consent_form_korean(pigment), encoding="utf-8")
    print(f"✅ 기미 IRB → {OUT}/pigment_*.md")

    # ---- CRO 견적 (4 질환) ----
    print("\n" + "=" * 80)
    print("In vitro CRO 견적 (Top 5 hit, standard tier)")
    print("=" * 80)

    total_all = 0
    for disease in ["scar", "pigment", "alopecia", "acne", "photoaging"]:
        est = estimate_total_cost(disease, n_top_hits=5, tier="standard")
        md = render_quote_markdown(est)
        path = OUT / f"cro_quote_{disease}.md"
        path.write_text(md, encoding="utf-8")
        print(f"  {disease:12s}: {est['total_krw']:>15,d} KRW "
              f"(~${est['total_usd_approx']:,.0f}, {est['n_assays']} assays, "
              f"{est['longest_assay_weeks']}주)")
        total_all += est["total_krw"]

    print(f"\n  5질환 통합:    {total_all:>15,d} KRW (~${total_all/1350:,.0f})")
    print(f"\n✅ {OUT}/cro_quote_*.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
