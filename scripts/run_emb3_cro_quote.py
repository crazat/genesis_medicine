"""EMB-3 in vitro CRO 견적 자동 생성.

Validation panel (paper의 in vitro IC50 hook):
  Tier 1 (필수, paper 공개 전):
    - TGF-β1 reporter assay (cell-based)
    - MMP-1 enzymatic FRET
    - hERG patch clamp (Tier 1 safety)
    - Skin irritation (in vitro EpiDerm)

  Tier 2 (paper 강화, IPF cross-disease 정당화):
    - SMAD3 phosphorylation
    - PDGFRB kinase activity
    - Pulmonary fibroblast TGF-β-induced collagen

  Tier 3 (clinical-track, post-paper):
    - Hypertrophic fibroblast model
    - Pulmonary fibroblast IPF cell line
    - 한국 CRO 14-day acute tox

화합물:
  EMB-3 (lead, 합성 필요)
  Embelin (commercial, control)
  Pirfenidone (clinical IPF SoC, positive control)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/scaffold_hop/cro_quote"
OUT.mkdir(parents=True, exist_ok=True)


# 견적 (한국 CRO 2026 평균, KRW)
QUOTE = [
    # Tier 1 — 필수 (paper 공개 전, IC50 정량화)
    {"tier": 1, "assay": "TGF-β1 SMAD2/3 phosphorylation reporter (HEK293)",
     "target": "TGFB1", "type": "cell-based",
     "cost_per_compound_krw": 850_000, "compounds": 3, "weeks": 4,
     "rationale": "EMB-3 affinity 0.749 → IC50 정량 검증. paper Table 4."},
    {"tier": 1, "assay": "MMP-1 enzymatic FRET inhibition",
     "target": "MMP1", "type": "biochemical",
     "cost_per_compound_krw": 450_000, "compounds": 3, "weeks": 3,
     "rationale": "MD 0.79 Å + affinity 0.674 → IC50 검증. paper Table 3."},
    {"tier": 1, "assay": "hERG patch clamp (manual, IonOptix)",
     "target": "hERG", "type": "biophysical",
     "cost_per_compound_krw": 2_500_000, "compounds": 3, "weeks": 6,
     "rationale": "ADMET 예측 0.16 ↔ wet 검증. 외용제·시스템 노출 안전성 핵심."},
    {"tier": 1, "assay": "Skin irritation (in vitro EpiDerm reconstructed skin)",
     "target": "skin", "type": "imaging+biochemical",
     "cost_per_compound_krw": 1_400_000, "compounds": 3, "weeks": 5,
     "rationale": "외용제 OECD TG 439 — Recover 한의원 임상 준비."},
    # Tier 2 — paper 강화 (multi-target + IPF translational)
    {"tier": 2, "assay": "SMAD3 phosphorylation (TGFβ-induced fibroblast)",
     "target": "SMAD3", "type": "cell-based",
     "cost_per_compound_krw": 1_100_000, "compounds": 2, "weeks": 5,
     "rationale": "multi-tier downstream — paper network section 입증."},
    {"tier": 2, "assay": "PDGFRB kinase activity (HTRF)",
     "target": "PDGFRB", "type": "biochemical",
     "cost_per_compound_krw": 750_000, "compounds": 2, "weeks": 4,
     "rationale": "Myofibroblast axis — IPF 적용성 강화."},
    {"tier": 2, "assay": "Pulmonary fibroblast TGFβ-induced collagen (IMR-90)",
     "target": "COL1A1+IPF model", "type": "cell-based",
     "cost_per_compound_krw": 2_400_000, "compounds": 2, "weeks": 8,
     "rationale": "★ IPF cross-disease — paper 핵심 translational hook."},
    # Tier 3 — clinical track (post-paper)
    {"tier": 3, "assay": "Hypertrophic fibroblast keloid model",
     "target": "scar", "type": "cell-based",
     "cost_per_compound_krw": 1_800_000, "compounds": 2, "weeks": 8,
     "rationale": "Recover 한의원 임상 1상 entry."},
    {"tier": 3, "assay": "Human IPF lung fibroblast (BEAS-2B + CCL18)",
     "target": "IPF", "type": "cell-based",
     "cost_per_compound_krw": 3_500_000, "compounds": 2, "weeks": 10,
     "rationale": "IPF 임상 entry 자료 (orphan drug 신청 근거)."},
    {"tier": 3, "assay": "Acute oral tox (rat, OECD TG 423)",
     "target": "systemic_safety", "type": "in vivo",
     "cost_per_compound_krw": 8_000_000, "compounds": 1, "weeks": 6,
     "rationale": "내복약·systemic IPF 적용 시 필수."},
]

# 추가 비용 — 합성/조달
SYNTHESIS = [
    {"item": "EMB-3 합성 (mg scale, 95% pure)", "vendor": "ChemBridge / Korean CRO",
     "cost_krw": 4_500_000, "weeks": 6,
     "rationale": "EMB-3는 신규 — 5-step synthesis 필요"},
    {"item": "Embelin 조달", "vendor": "Sigma-Aldrich (≥98%)",
     "cost_krw": 350_000, "weeks": 1,
     "rationale": "Cat. E0250, 100mg ≈ ₩350k"},
    {"item": "Pirfenidone 조달", "vendor": "Sigma-Aldrich",
     "cost_krw": 200_000, "weeks": 1,
     "rationale": "P2118, 100mg ≈ ₩200k. IPF SoC 양성 대조군"},
]


def main() -> int:
    print("=" * 100)
    print("EMB-3 in vitro CRO 견적 — Recover 한의원 + Genesis_Medicine 협업")
    print("=" * 100)

    df = pd.DataFrame(QUOTE)
    df["total_krw"] = df["cost_per_compound_krw"] * df["compounds"]
    df_synth = pd.DataFrame(SYNTHESIS)

    # Tier별 합계
    print("\n=== Tier별 비용 ===")
    for tier in [1, 2, 3]:
        sub = df[df["tier"] == tier]
        cost = sub["total_krw"].sum()
        weeks = sub["weeks"].max()
        print(f"  Tier {tier}: {len(sub)} assay, "
              f"{int(cost / 10_000):>6,} 만원, "
              f"~{weeks}주")
        for r in sub.itertuples():
            print(f"    • {r.assay[:60]:60s} "
                  f"₩{int(r.total_krw / 10_000):>5,}만 ({r.compounds} cpd × "
                  f"{r.weeks}주)")
    synth_total = df_synth["cost_krw"].sum()
    print(f"\n  합성/조달: ₩{int(synth_total / 10_000):,}만")

    # Total
    grand = df["total_krw"].sum() + synth_total
    print(f"\n=== 총 견적 ===")
    print(f"  Tier 1 (paper 공개 전 필수): "
          f"₩{int(df[df['tier']==1]['total_krw'].sum() / 10_000):,}만")
    print(f"  Tier 1+2 (paper 강화):     "
          f"₩{int(df[df['tier'].isin([1,2])]['total_krw'].sum() / 10_000):,}만")
    print(f"  Tier 1+2+3 (전체):        "
          f"₩{int(df['total_krw'].sum() / 10_000):,}만")
    print(f"  + 합성/조달:               ₩{int(synth_total / 10_000):,}만")
    print(f"  ───────────────────────────────────────")
    print(f"  TOTAL:                    ₩{int(grand / 10_000):,}만 "
          f"(~${int(grand / 1300):,} USD)")
    print(f"  duration: ~10주 (Tier 1 만), ~14주 (Tier 1+2)")

    df.to_csv(OUT / "cro_quote_full.csv", index=False)
    df_synth.to_csv(OUT / "synthesis_quote.csv", index=False)
    pd.DataFrame([{
        "tier_1_krw": int(df[df['tier']==1]['total_krw'].sum()),
        "tier_12_krw": int(df[df['tier'].isin([1,2])]['total_krw'].sum()),
        "tier_123_krw": int(df['total_krw'].sum()),
        "synthesis_krw": int(synth_total),
        "grand_total_krw": int(grand),
        "duration_tier1_weeks": 10,
        "duration_tier12_weeks": 14,
        "recommendation": "Tier 1 (paper 공개 전 IC50 + hERG + skin irritation) 우선 진행",
    }]).to_csv(OUT / "summary.csv", index=False)
    print(f"\n✅ {OUT}/cro_quote_full.csv  +  synthesis_quote.csv  +  summary.csv")

    print("\n=== 권장 ===")
    print("Tier 1 (₩{:,}만) 먼저 진행 — paper IC50 데이터 + 안전성 → 두 번째 paper 게재 전 wet lab 후크 확보."
          .format(int(df[df['tier']==1]['total_krw'].sum() / 10_000)))
    print("Tier 2는 paper 게재 시점 또는 직후. Tier 3는 clinical track 진입 결정 후.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
