"""TxGNN 피부 5개 핵심 질환 zero-shot 재창출.

흉터(keloid) / 색소(vitiligo+hyperpigmentation) / AGA / 여드름 / 아토피
각 질환마다 1801개 약물에 대해 ranked indication score.

CPU에서 ~30-40초/질환 × 5질환 = 약 3분.
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

CKPT = Path.home() / "genesis_medicine" / ".cache" / "txgnn" / "model_ckpt"
RESULT = Path(__file__).parent / "results"
RESULT.mkdir(parents=True, exist_ok=True)


# 핵심 피부 질환 (find_skin_disease_idxs.py 결과)
SKIN_TARGETS = {
    "scar_keloid":   [15220.0, 730.0, 1031.0, 8416.0],     # keloid formation 외
    "pigment":       [15896.0, 6546.0, 2362.0, 15149.0],   # vitiligo, hyperpigmentation
    "alopecia":      [14659.0, 14574.0, 15982.0, 14576.0], # androgenetic, areata, universalis
    "acne":          [1232.0, 14064.0, 14140.0],           # acne, acneiform, rosacea
    "atopic":        [1133.0, 12622.0, 14144.0, 14068.0],  # dermatitis, eczema, seborrheic, contact
}


def main() -> int:
    print(f"=== TxGNN 피부 5질환 재창출 ===")
    for cat, idxs in SKIN_TARGETS.items():
        print(f"  {cat}: {len(idxs)} disease idx")

    from txgnn import TxData, TxGNN, TxEval
    print("\n--- TxData(full_graph) prepare ---")
    TxDataObj = TxData(data_folder_path=str(CKPT))
    TxDataObj.prepare_split(split="full_graph", seed=42)
    print("✅ ready")

    print("\n--- TxGNN init + load_pretrained ---")
    TxGNNObj = TxGNN(
        data=TxDataObj,
        weight_bias_track=False,
        proj_name="genesis_skin",
        exp_name="repurpose",
        device="cpu",
    )
    TxGNNObj.model_initialize(
        n_hid=128, n_inp=128, n_out=128, proto=True, proto_num=3,
        attention=False, sim_measure='all_nodes_profile',
        agg_measure='rarity', num_walks=200, walk_mode='bit', path_length=2,
    )
    TxGNNObj.load_pretrained(str(CKPT))
    print("✅ pretrained loaded")

    tx_eval = TxEval(model=TxGNNObj)

    nm = pickle.loads((CKPT / "name_mapping.pkl").read_bytes())
    id2name = nm["id2name_disease"]
    idx2id = nm["idx2id_disease"]

    summary = {}
    for cat, idxs in SKIN_TARGETS.items():
        print(f"\n--- {cat}: eval_disease_centric for {len(idxs)} idxs ---")
        try:
            result = tx_eval.eval_disease_centric(
                disease_idxs=idxs,
                relation="indication",
                return_raw=True,
                save_result=True,
                save_name=str(RESULT / f"{cat}_indication_raw.pkl"),
            )
        except Exception as e:
            print(f"  ❌ {cat} 실패: {type(e).__name__}: {e}")
            continue

        # Top 30 추출 (result["result"]["Ranked List"])
        rl = result.get("result", {}).get("Ranked List", {})
        if not rl:
            print(f"  ⚠️  {cat}: Ranked List 없음. keys={list(result.keys())}")
            continue
        per_disease = {}
        for d_id, ranked in rl.items():
            d_name = id2name.get(d_id, str(d_id))
            top = ranked[:30]
            per_disease[d_name] = top

        summary[cat] = per_disease
        # 카테고리 통합 — 모든 sub-disease 합쳐서 빈도 계산
        votes = {}
        for d_name, top in per_disease.items():
            for rank, drug in enumerate(top):
                votes[drug] = votes.get(drug, 0) + (30 - rank)
        sorted_votes = sorted(votes.items(), key=lambda x: -x[1])[:30]
        print(f"  통합 top 10 ({cat}):")
        for drug, score in sorted_votes[:10]:
            print(f"    {drug:35s} consensus={score}")

    # 저장
    out_path = RESULT / "skin_repurposing_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n✅ {out_path}")

    # CSV로도 — 각 카테고리별 통합 top 30
    import pandas as pd
    rows = []
    for cat, per_disease in summary.items():
        votes = {}
        for d_name, top in per_disease.items():
            for rank, drug in enumerate(top):
                votes[drug] = votes.get(drug, 0) + (30 - rank)
        for rank, (drug, score) in enumerate(sorted(votes.items(), key=lambda x: -x[1])[:30], 1):
            rows.append({
                "category": cat,
                "rank": rank,
                "drug_name": drug,
                "consensus_score": score,
            })
    df = pd.DataFrame(rows)
    csv_path = RESULT / "skin_repurposing_top30_by_category.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
