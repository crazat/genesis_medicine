"""한방 처방 → 성분 → 다중 피부질환 네트워크 분석.

각 처방(자운고, 옥용산, 당귀음자, 황련해독탕 등)의 핵심 성분이
어떤 피부질환에 분자 수준 효능을 가지는지 자동 매핑.

처방의 "한 약방문이 여러 증상" 효능을 분자 수준에서 정당화.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot" / "herbal_prescriptions"
OUT.mkdir(parents=True, exist_ok=True)


# 핵심 한약 처방 → 핵심 성분 (compound name as in skin_compounds_curated.csv)
PRESCRIPTIONS = {
    "자운고 (Jaungo, 紫雲膏)": {
        "indication_traditional": "외용 흉터·창상·화상",
        "key_compounds": ["Shikonin", "Acetylshikonin", "Ferulic acid"],
    },
    "옥용산 (Ok-yong-san, 玉容散)": {
        "indication_traditional": "미백·기미 외용",
        "key_compounds": ["Kojic acid", "Arbutin", "Glabridin", "Liquiritin"],
    },
    "당귀음자 (Danggui-eumja, 當歸飮子)": {
        "indication_traditional": "혈허성 피부 소양·만성 건조",
        "key_compounds": ["Ferulic acid", "Paeoniflorin"],
    },
    "온청음 (On-cheong-eum, 溫淸飮)": {
        "indication_traditional": "혈허열·아토피·소양",
        "key_compounds": ["Paeoniflorin", "Berberine", "Baicalin"],
    },
    "황련해독탕 (Hwang-ryeon-hae-dok-tang, 黃連解毒湯)": {
        "indication_traditional": "급성 염증 여드름·열독 피부",
        "key_compounds": ["Berberine", "Baicalein", "Baicalin"],
    },
    "방풍통성산 (Bang-poong-tong-seong-san, 防風通聖散)": {
        "indication_traditional": "발열성 여드름·체질 개선",
        "key_compounds": ["Baicalin", "Rhein"],
    },
    "사물탕 (Sa-mul-tang, 四物湯)": {
        "indication_traditional": "혈허·콜라겐·안티에이징",
        "key_compounds": ["Paeoniflorin", "Ferulic acid"],
    },
    "활혈거어탕 (活血祛瘀湯)": {
        "indication_traditional": "비후성 흉터·켈로이드",
        "key_compounds": ["Paeoniflorin", "Ferulic acid"],
    },
    "센텔라 외용 (Madecassol)": {
        "indication_traditional": "흉터 (clinical)",
        "key_compounds": ["Asiaticoside", "Madecassoside", "Asiatic acid", "Madecassic acid"],
    },
    "녹차 외용 (Polyphenon E)": {
        "indication_traditional": "광노화·항산화",
        "key_compounds": ["EGCG"],
    },
}


def main() -> int:
    print("=" * 90)
    print("한방 처방 → 성분 → 다중 피부질환 네트워크")
    print("=" * 90)

    # cross-disease 매트릭스 로드
    matrix = pd.read_csv(
        ROOT / "pilot/cross_disease/matrix_affinity.csv",
        index_col=0,
    )

    diseases = ["scar", "pigment", "alopecia", "acne", "photoaging"]

    rows = []
    for rx_name, info in PRESCRIPTIONS.items():
        components = info["key_compounds"]
        # 각 질환별 처방 종합 점수 = 성분들의 평균 affinity (해당 질환에서)
        scores: dict[str, float] = {}
        component_data: dict[str, dict[str, float]] = {}
        for d in diseases:
            if d not in matrix.columns:
                continue
            vals = []
            for c in components:
                if c in matrix.index and not pd.isna(matrix.loc[c, d]):
                    v = float(matrix.loc[c, d])
                    vals.append(v)
                    component_data.setdefault(c, {})[d] = round(v, 3)
            scores[d] = round(sum(vals) / len(vals), 3) if vals else float("nan")

        # 가장 강한 질환
        valid = {d: s for d, s in scores.items() if not pd.isna(s)}
        best_d = max(valid, key=valid.get) if valid else "—"
        best_s = valid.get(best_d, float("nan"))

        rows.append({
            "prescription": rx_name,
            "indication_traditional": info["indication_traditional"],
            "n_components_evaluated": len(component_data),
            **{f"score_{d}": scores.get(d, float("nan")) for d in diseases},
            "best_disease_predicted": best_d,
            "best_score": best_s,
        })

        # 처방별 디테일 출력
        print(f"\n## {rx_name}")
        print(f"   전통 적응증: {info['indication_traditional']}")
        print(f"   성분 ({len(component_data)}/{len(components)} 평가됨):")
        for c, vals in component_data.items():
            top_d = max(vals, key=vals.get)
            print(f"     {c:25s}  {top_d}={vals[top_d]:.3f}  | "
                  f"others=({', '.join(f'{d}={v:.2f}' for d, v in vals.items() if d != top_d)})")
        print(f"   분자 수준 예측 1순위 적응증: {best_d} (score {best_s:.3f})")
        # 전통 vs 예측 일치도
        trad = info["indication_traditional"].lower()
        d_keywords = {
            "scar":       ["scar", "흉터", "창상", "화상", "키로이드", "켈로이드"],
            "pigment":    ["미백", "기미", "색소"],
            "alopecia":   ["탈모", "alopecia", "hair"],
            "acne":       ["여드름", "acne", "염증"],
            "photoaging": ["광노화", "안티에이징", "photoaging", "wrinkle"],
        }
        match = any(kw in trad for kw in d_keywords.get(best_d, []))
        if match:
            print(f"   ✅ 전통 적응증과 분자수준 예측 일치!")
        else:
            print(f"   ⚠️  전통 적응증({trad}) vs 예측({best_d}) — 차이 분석 필요")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "prescription_disease_scores.csv", index=False)

    # 처방별 disease score 요약 표
    print("\n" + "=" * 90)
    print("처방 × 질환 매트릭스 (분자수준 종합 score)")
    print("=" * 90)
    show = df[["prescription", "indication_traditional",
               "score_scar", "score_pigment", "score_alopecia",
               "score_acne", "score_photoaging", "best_disease_predicted"]]
    print(show.to_string(index=False, float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"))

    print(f"\n✅ 저장: {OUT}/prescription_disease_scores.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
