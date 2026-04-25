"""TxGNN 결과에서 알츠하이머 상위 재창출 후보 추출."""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd

RESULT = Path(__file__).parent / "results"


def main() -> None:
    data = pickle.loads((RESULT / "alzheimer_indication_raw.pkl").read_bytes())
    result = data["result"]
    prediction = data["prediction"]

    print("=" * 90)
    print("TxGNN Alzheimer zero-shot drug repurposing — Top candidates")
    print("=" * 90)

    # Name 매핑
    name_map = result["Name"]
    ranked_map = result["Ranked List"]
    score_map = result.get("Score", {})

    summary_rows = []
    for disease_key, name in name_map.items():
        rl = ranked_map.get(disease_key, [])
        scores = score_map.get(disease_key, [])
        pred_dict = prediction.get(disease_key, {})

        print(f"\n[{name}] (key={disease_key[:30]}...)")
        print(f"  총 랭킹된 약물: {len(rl)}")
        # Top 20
        top_20 = rl[:20]
        for rank, drug in enumerate(top_20, 1):
            score = scores[rank-1] if rank-1 < len(scores) else None
            print(f"  {rank:2d}. {drug}" + (f"   score={score:.3f}" if score else ""))
            summary_rows.append({
                "disease": name,
                "rank": rank,
                "drug_name": drug,
                "score": score,
            })

    out = pd.DataFrame(summary_rows)
    out_csv = RESULT / "top_candidates_by_disease.csv"
    out.to_csv(out_csv, index=False)
    print(f"\n✅ 저장: {out_csv}")

    # 메인 "Alzheimer disease" (idx=1510)의 top 50
    alz_main_key = [k for k, v in name_map.items() if v == "Alzheimer disease"][0]
    main_rl = ranked_map[alz_main_key]
    main_scores = score_map.get(alz_main_key, [])
    top_50_main = [
        {"rank": i+1, "drug_name": d, "score": main_scores[i] if i < len(main_scores) else None}
        for i, d in enumerate(main_rl[:50])
    ]
    pd.DataFrame(top_50_main).to_csv(RESULT / "alzheimer_main_top50.csv", index=False)
    print(f"✅ 메인 AD top 50: {RESULT / 'alzheimer_main_top50.csv'}")


if __name__ == "__main__":
    main()
