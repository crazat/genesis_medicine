"""5개 피부 파일럿 cross-disease 통합 분석.

핵심 질문
----------
1. 어떤 화합물이 5개 질환 중 다수에 강한가? (multi-purpose herbal)
2. 각 질환에 unique한 화합물? (specialty)
3. 한약 처방의 다중 성분이 다중 질환에 시너지를 보이는가?
4. 외용제 친화도 + 다중 질환 = 종합 가치 도출

출력
----
- compound × disease 매트릭스 (consensus_affinity)
- compound × disease (topical_score) 매트릭스
- multi_purpose_top.csv: 평균 affinity 높은 universal 후보
- per_disease_unique.csv: 다른 질환에서는 약한데 한 질환에서만 강한 화합물
- herbs_synergy.csv: 같은 약초의 여러 성분이 같은 질환에 동시 강한 경우
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PILOTS = {
    "scar":       "skin_scar/results_v2",
    "pigment":    "skin_pigment/results_v1",
    "alopecia":   "skin_alopecia/results_v1",
    "acne":       "skin_acne/results_v1",
    "photoaging": "skin_photoaging/results_v1",
}

OUT = ROOT / "pilot" / "cross_disease"
OUT.mkdir(parents=True, exist_ok=True)


def load_pilot(disease: str, sub: str) -> pd.DataFrame:
    """consensus + topical_score 통합 로드."""
    res_dir = ROOT / "pilot" / sub
    cons = pd.read_csv(res_dir / f"{disease}_consensus.csv", index_col=0)
    cons["disease"] = disease
    cons["compound"] = cons.index
    # topical_score
    rep = res_dir / f"{disease}_full_report.csv"
    if rep.exists():
        rep_df = pd.read_csv(rep)
        cons["topical_score"] = cons["compound"].map(
            dict(zip(rep_df["compound"], rep_df["topical_score"]))
        )
    return cons[["compound", "disease", "consensus_score", "topical_score"]]


def main() -> int:
    print("=" * 90)
    print("Cross-disease 통합 분석 (5 pilots, Genesis_Medicine v3)")
    print("=" * 90)

    # 1. 전체 long-form 통합
    frames = []
    for disease, sub in PILOTS.items():
        try:
            df = load_pilot(disease, sub)
            frames.append(df)
            print(f"  {disease}: {len(df)} 화합물")
        except Exception as e:
            print(f"  ⚠️ {disease}: {e}")
    long_df = pd.concat(frames, ignore_index=True)
    long_df.to_csv(OUT / "long_form.csv", index=False)
    print(f"\n  long_form.csv: {len(long_df)} 행 (compound × disease)")

    # 2. compound × disease 매트릭스 (consensus_affinity)
    aff_pivot = long_df.pivot_table(
        index="compound", columns="disease",
        values="consensus_score", aggfunc="first",
    )
    aff_pivot["mean_affinity"] = aff_pivot.mean(axis=1)
    aff_pivot["std_affinity"]  = aff_pivot.iloc[:, :-1].std(axis=1)
    aff_pivot["n_diseases"]    = aff_pivot.iloc[:, :-2].notna().sum(axis=1)
    aff_pivot = aff_pivot.sort_values("mean_affinity", ascending=False)
    aff_pivot.to_csv(OUT / "matrix_affinity.csv")

    top_pivot = long_df.pivot_table(
        index="compound", columns="disease",
        values="topical_score", aggfunc="first",
    )
    top_pivot["mean_topical"] = top_pivot.mean(axis=1)
    top_pivot.to_csv(OUT / "matrix_topical.csv")

    # 3. Multi-purpose top (n_diseases ≥ 4 + mean ≥ 0.5)
    multi_pp = aff_pivot[
        (aff_pivot["n_diseases"] >= 4) & (aff_pivot["mean_affinity"] >= 0.4)
    ].head(20)
    multi_pp.to_csv(OUT / "multi_purpose_top.csv")

    print("\n" + "=" * 90)
    print("🌟 Multi-purpose herbal compounds (4-5개 질환 동시 강함)")
    print("=" * 90)
    cols_show = list(PILOTS.keys()) + ["mean_affinity", "n_diseases"]
    cols_show = [c for c in cols_show if c in multi_pp.columns]
    print(multi_pp[cols_show].head(15).to_string(
        float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "—"
    ))

    # 4. Per-disease unique (한 질환에서만 강한 specialty 화합물)
    unique_per = []
    for d in PILOTS:
        if d not in aff_pivot.columns:
            continue
        sub = aff_pivot[aff_pivot[d].notna()].copy()
        # 다른 질환 평균
        other_cols = [c for c in PILOTS if c != d and c in aff_pivot.columns]
        sub["other_mean"] = sub[other_cols].mean(axis=1)
        sub["specialty"] = sub[d] - sub["other_mean"]
        spec = sub[(sub[d] >= 0.5) & (sub["specialty"] >= 0.1)].sort_values(
            "specialty", ascending=False
        ).head(5)
        for compound, row in spec.iterrows():
            unique_per.append({
                "disease": d,
                "compound": compound,
                "this_disease_aff": round(row[d], 3),
                "other_avg_aff": round(row["other_mean"], 3) if pd.notna(row["other_mean"]) else "-",
                "specialty_score": round(row["specialty"], 3),
            })
    unique_df = pd.DataFrame(unique_per)
    unique_df.to_csv(OUT / "per_disease_unique.csv", index=False)
    print("\n" + "=" * 90)
    print("🎯 Per-disease specialty 화합물 (해당 질환만 특이적으로 강함)")
    print("=" * 90)
    print(unique_df.to_string(index=False))

    # 5. 한약(약초) 시너지 분석
    print("\n" + "=" * 90)
    print("🌿 한약초 시너지 (같은 약초 → 다중 성분 → 다중 질환)")
    print("=" * 90)
    compounds_meta = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    # compound → source_korean / source_botanical
    src_map = dict(zip(compounds_meta["name"], compounds_meta["source_korean"].fillna("-")))

    # 약초별 그룹
    compound_to_aff = aff_pivot["mean_affinity"].to_dict()
    by_herb: dict[str, list] = {}
    for c, src in src_map.items():
        if src in ("-", "synthetic", "다중", None) or pd.isna(src):
            continue
        by_herb.setdefault(src, []).append((c, compound_to_aff.get(c, np.nan)))

    herb_rows = []
    for herb, items in by_herb.items():
        valid = [(c, a) for c, a in items if not pd.isna(a)]
        if len(valid) < 2:
            continue
        avg = np.mean([a for _, a in valid])
        herb_rows.append({
            "herb_korean": herb,
            "n_compounds": len(valid),
            "compounds": ", ".join(c for c, _ in sorted(valid, key=lambda x: -x[1])[:3]),
            "mean_affinity": round(avg, 3),
        })
    herb_df = pd.DataFrame(herb_rows).sort_values("mean_affinity", ascending=False)
    herb_df.to_csv(OUT / "herb_synergy.csv", index=False)
    print(herb_df.head(15).to_string(index=False))

    # 6. 종합 통계
    print("\n" + "=" * 90)
    print("📊 종합 통계")
    print("=" * 90)
    print(f"  분석된 (compound × disease) 쌍: {len(long_df)}")
    print(f"  unique 화합물: {long_df['compound'].nunique()}")
    print(f"  평가 질환: {long_df['disease'].nunique()}")
    print(f"  4-5 질환 동시 hit (mean ≥ 0.4): {len(multi_pp)} 화합물")
    print(f"  per-disease specialty: {len(unique_df)} 화합물")
    print(f"  multi-compound 약초: {len(herb_df)}종")
    print(f"\n✅ 출력: {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
