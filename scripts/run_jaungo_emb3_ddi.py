"""자운고 + EMB-3 강화 처방 DDI 평가.

자운고 (전통 외용 흉터):
  - Shikonin (자초)
  - Acetylshikonin
  - Ferulic acid (당귀)
EMB-3 강화 추가:
  - EMB-3 (1,4-benzoquinone scaffold)
  - Embelin (참고)

복합 처방 시 5-component all pairs (10 pairs) DDI 평가.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/scaffold_hop/jaungo_emb3_ddi"
OUT.mkdir(parents=True, exist_ok=True)


JAUNGO_EMB3_FORMULA = [
    {"name": "Shikonin",
     "smiles": "CC(=CCCC(C)=O)C1=CC2=CC=CC(=C2C(=O)C1=O)O"},
    {"name": "Acetylshikonin",
     "smiles": "CC(=CCC(C(=O)C)C1=CC2=CC=CC(=C2C(=O)C1=O)O)C"},
    {"name": "Ferulic acid",
     "smiles": "COC1=CC(=CC(=C1)O)/C=C/C(=O)O"},
    {"name": "EMB-3",
     "smiles": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"},
    {"name": "Embelin",
     "smiles": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O"},
]


def main() -> int:
    from genesis_medicine.ddi.tcm_ddi import (
        evaluate_prescription, render_ddi_report, classify_compound,
    )

    print("=== 자운고 + EMB-3 강화 처방 DDI 평가 ===\n")

    print("[성분 분류]")
    for c in JAUNGO_EMB3_FORMULA:
        classes = classify_compound(c["smiles"])
        print(f"  {c['name']:18s} → {classes}")

    print(f"\n[10 pair DDI 평가]")
    predictions = evaluate_prescription(JAUNGO_EMB3_FORMULA)
    md = render_ddi_report(predictions, "자운고 + EMB-3 강화")
    out_md = OUT / "ddi_report.md"
    out_md.write_text(md)
    print(f"  ✅ {out_md}")

    print(f"\n=== Pair-wise 결과 ===")
    by_severity = {}
    for p in predictions:
        emo = {"synergy": "🟢", "additive": "🟡", "antagonism": "🟠",
                "duplicate": "⚠️", "neutral": "—"}.get(p.interaction_type, "?")
        sev = p.severity
        by_severity.setdefault(sev, []).append(p)
        print(f"\n  {p.drug_a_name:18s} × {p.drug_b_name:18s}")
        print(f"    {emo} {p.interaction_type} (severity {p.severity}, "
              f"conf {p.confidence:.2f})")
        print(f"    {p.mechanism[:100]}")

    print(f"\n=== 종합 — Recover 한의원 처방 권장 ===")
    high = by_severity.get("high", [])
    moderate = by_severity.get("moderate", [])
    if high:
        print(f"  🔴 HIGH severity: {len(high)} pair — 처방 재구성 필요")
    if moderate:
        print(f"  🟠 MODERATE severity: {len(moderate)} pair — 모니터링 권장")
        for p in moderate:
            print(f"    - {p.drug_a_name} × {p.drug_b_name}: {p.mechanism[:80]}")
    if not high and not moderate:
        print(f"  ✅ 모든 pair LOW severity — 안전한 복합 처방")

    # 권장 농도 비율 (heuristic)
    print(f"\n=== 권장 비율 (heuristic) ===")
    print(f"  Shikonin 25% + Acetylshikonin 15% (자운고 활성)")
    print(f"  Ferulic acid 5% (지지)")
    print(f"  EMB-3 30% (anti-fibrotic 강화)")
    print(f"  Embelin 5% (low-dose, MMP-1 보강)")
    print(f"  Vehicle (sesame oil + beeswax) 20%")
    print(f"\n  ⚠️ 실제 비율은 체질·증상에 따라 한의사 판단")
    return 0


if __name__ == "__main__":
    sys.exit(main())
