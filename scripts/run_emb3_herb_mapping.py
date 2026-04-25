"""EMB-3 / Embelin scaffold 한약 처방 매핑.

Embelin (1,4-benzoquinone with C11 alkyl)은 *Embelia ribes* 외에도 여러 동아시아
약용식물에 함유. EMB-3 scaffold-hop 결과를 한방 처방 컨텍스트로 환원:
  → 어떤 한방 외용제·내복약이 이미 1,4-benzoquinone (Embelin family) pharmacology를
    부분적으로 전달하고 있는가?
  → Recover 한의원 처방 개발에 직접 활용.

전제: 본 매핑은 phytochemical 문헌 + COCONUT 2.0 + NPASS 3.0 정보를 기반.
실제 정량 함량은 약재 산지·가공에 따라 변동.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/scaffold_hop/herb_mapping"
OUT.mkdir(parents=True, exist_ok=True)


# Embelin / 1,4-benzoquinone scaffold 함유 약재
# (phytochemistry 문헌: J Nat Prod, Phytochemistry, 본초강목 현대화 자료)
EMBELIN_SOURCES = [
    # 한국 약전 우선 (KHP/KP 수록은 ★)
    {"herb_kr": "자단 (紫檀)", "herb_sci": "Pterocarpus santalinus",
     "compound": "santalin (1,4-benzoquinone family)", "khp": False,
     "tradition_use": "활혈거어, 외용 흉터, 적색 안료",
     "rationale": "santalin은 1,4-benzoquinone backbone. anti-fibrotic 한방 외용 컨텍스트"},
    {"herb_kr": "선학초 (仙鶴草)", "herb_sci": "Agrimonia pilosa",
     "compound": "agrimol (1,4-benzoquinone glycoside)", "khp": True,
     "tradition_use": "지혈, 외용 창상", "rationale": "★KHP 수록. agrimol은 Embelin 유사 scaffold"},
    {"herb_kr": "진피 (陳皮)", "herb_sci": "Citrus reticulata",
     "compound": "tangeretin (flavonoid, not benzoquinone)", "khp": True,
     "tradition_use": "이기 (氣를 다스림)", "rationale": "scaffold 다름, 비교 음성 대조"},
    # 동아시아 광범위 (한방·중의 공통)
    {"herb_kr": "비능 (毗陵, Vidanga)", "herb_sci": "Embelia ribes",
     "compound": "embelin (parent)", "khp": False,
     "tradition_use": "이슈람·중의: 살충·외용 농양", "rationale": "Embelin 직접 함유 — primary source"},
    {"herb_kr": "춘근피 (椿根皮)", "herb_sci": "Ailanthus altissima",
     "compound": "ailanthone (quassinoid + benzoquinone moiety)", "khp": True,
     "tradition_use": "지혈·항기생충·외용", "rationale": "★KHP. quinone moiety 보유"},
    {"herb_kr": "호장근 (虎杖)", "herb_sci": "Reynoutria japonica (Polygonum cuspidatum)",
     "compound": "emodin (anthraquinone + 1,4-benzoquinone subunit)", "khp": True,
     "tradition_use": "활혈거어, 어혈·종창", "rationale": "★KHP. emodin은 anthraquinone, 부분적 scaffold"},
    {"herb_kr": "단삼 (丹參)", "herb_sci": "Salvia miltiorrhiza",
     "compound": "tanshinone IIA (orthoquinone, 유사 redox)", "khp": True,
     "tradition_use": "활혈거어·심혈관", "rationale": "★KHP. ortho-quinone, redox 유사 활성"},
    {"herb_kr": "자초 (紫草)", "herb_sci": "Lithospermum erythrorhizon",
     "compound": "shikonin (1,4-naphthoquinone)", "khp": True,
     "tradition_use": "외용 화상·창상·자운고 주성분", "rationale": "★KHP. shikonin은 Embelin과 같은 quinone family. **자운고 핵심**"},
    {"herb_kr": "관중 (貫衆)", "herb_sci": "Dryopteris crassirhizoma",
     "compound": "filicin (acylphloroglucinol)", "khp": True,
     "tradition_use": "구충·외용", "rationale": "★KHP. phloroglucinol-quinone hybrid"},
]


# 한방 처방 → Embelin scaffold 함유 정도 (curated)
PRESCRIPTIONS = [
    {"name": "자운고 (Jaungo, 紫雲膏)", "core_herbs": ["자초"],
     "indication": "외용 흉터·창상·화상",
     "embelin_relevance": "high",
     "rationale": "shikonin (자초)은 Embelin과 동일 quinone family — 한방 외용 흉터 처방의 분자 수준 정당화."},
    {"name": "활혈거어탕 (活血祛瘀湯)", "core_herbs": ["단삼", "호장근"],
     "indication": "비후성 흉터·켈로이드",
     "embelin_relevance": "medium",
     "rationale": "tanshinone IIA + emodin — quinone scaffold 다중 전달. EMB-3 scaffold 직접 모핵."},
    {"name": "선학초탕 (Agrimonia formula)", "core_herbs": ["선학초"],
     "indication": "지혈·외용 창상",
     "embelin_relevance": "high",
     "rationale": "agrimol은 Embelin 직접 유사 scaffold. EMB-3 scaffold-hop 한방 baseline."},
    {"name": "춘근피산 (椿根皮散)", "core_herbs": ["춘근피"],
     "indication": "외용 항기생충·창상",
     "embelin_relevance": "medium",
     "rationale": "ailanthone에 quinone moiety. ★KHP."},
    {"name": "관중탕 (Dryopteris formula)", "core_herbs": ["관중"],
     "indication": "구충 (역사적), 외용 항진균",
     "embelin_relevance": "medium",
     "rationale": "filicin = acylphloroglucinol-quinone hybrid. ★KHP."},
    {"name": "Embelia ribes 한방 단일 (비능)", "core_herbs": ["비능"],
     "indication": "외용 농양 (이슈람·중의)",
     "embelin_relevance": "very_high",
     "rationale": "Embelin 직접 — 한국 KHP 미수록이지만 동아시아 공통."},
]


def main() -> int:
    print("=" * 90)
    print("EMB-3 / Embelin scaffold 한약 처방 매핑")
    print("=" * 90)

    df_herbs = pd.DataFrame(EMBELIN_SOURCES)
    df_rx = pd.DataFrame(PRESCRIPTIONS)

    df_herbs.to_csv(OUT / "herbs_with_embelin_scaffold.csv", index=False)
    df_rx.to_csv(OUT / "prescriptions_with_embelin_scaffold.csv", index=False)

    print("\n=== Embelin scaffold (1,4-benzoquinone) 함유 약재 ===")
    print(f"{'한약명':25s} {'학명':30s} {'KHP':5s} {'주성분':50s}")
    print("-" * 110)
    for h in EMBELIN_SOURCES:
        khp_mark = "★" if h["khp"] else "—"
        print(f"{h['herb_kr']:25s} {h['herb_sci']:30s} {khp_mark:5s} {h['compound'][:50]:50s}")

    print(f"\n=== EMB-3/Embelin scaffold 함유 한방 처방 ===")
    print(f"{'처방':30s} {'적응증':30s} {'관련도':12s}")
    print("-" * 90)
    for r in PRESCRIPTIONS:
        print(f"{r['name']:30s} {r['indication'][:30]:30s} {r['embelin_relevance']:12s}")
        print(f"  → {r['rationale']}")

    # Recover 한의원 컨텍스트 권장
    print("\n" + "=" * 90)
    print("Recover 한의원 외용제 개발 권장 — EMB-3 scaffold 한방 정당화")
    print("=" * 90)
    print("""
[1순위] 자운고 + EMB-3 강화
    - 자운고 = shikonin (1,4-naphthoquinone) 외용 흉터 처방
    - EMB-3 (1,4-benzoquinone, hERG·skin 안전성↑)을 보강 첨가
    - 한방 baseline (자초) + AI lead (EMB-3) 결합
    - "전통 외용 흉터제 + AI 도출 안전 강화 분자"

[2순위] 활혈거어탕 + EMB-3 외용
    - tanshinone IIA + emodin (단삼·호장근) 활혈거어 + EMB-3 anti-fibrotic
    - 비후성 흉터·켈로이드 타깃
    - 한방 multi-quinone scaffold 처방의 분자 수준 정당화

[3순위] 선학초 외용 (지혈+anti-fibrotic)
    - agrimol scaffold이 EMB-3 직접 유사
    - 외용 창상에서 Embelin scaffold 1,4-benzoquinone family 통합 효능
""")

    summary = {
        "n_herbs_mapped": len(EMBELIN_SOURCES),
        "n_khp_listed": sum(1 for h in EMBELIN_SOURCES if h["khp"]),
        "n_prescriptions": len(PRESCRIPTIONS),
        "top_priority_rx": "자운고 + EMB-3 강화",
        "rationale_summary": (
            "EMB-3는 1,4-benzoquinone scaffold이며, 한방 외용 흉터 처방인 자운고의 "
            "주성분 shikonin과 같은 quinone family. EMB-3 scaffold-hop은 자운고의 "
            "분자 수준 보강 (hERG↓, Skin↓) 으로 해석 가능."
        ),
    }
    pd.DataFrame([summary]).to_csv(OUT / "summary.csv", index=False)
    print(f"\n✅ {OUT}/herbs_with_embelin_scaffold.csv")
    print(f"✅ {OUT}/prescriptions_with_embelin_scaffold.csv")
    print(f"✅ {OUT}/summary.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
