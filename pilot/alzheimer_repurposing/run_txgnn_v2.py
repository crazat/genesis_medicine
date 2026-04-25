"""TxGNN 알츠하이머 재창출 (v2) — 6개 알츠하이머 idx 만 평가.

v1이 test_set 전체를 돌려서 45분+ 걸림 → 알츠하이머 6개만 타게팅.
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

CKPT = Path.home() / "genesis_medicine" / ".cache" / "txgnn" / "model_ckpt"
RESULT_DIR = Path(__file__).parent / "results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# find_alzheimer_idx.py 결과
ALZ_IDXS = [1510.0, 1282.0, 4887.0, 1207.0, 759.0, 14857.0]
# 우선순위: idx=1510 "Alzheimer disease" (메인), 나머지는 subtype


def main() -> int:
    print("=== TxGNN 알츠하이머 재창출 v2 ===")
    print(f"대상 idx: {ALZ_IDXS}")

    from txgnn import TxData, TxGNN, TxEval

    TxDataObj = TxData(data_folder_path=str(CKPT))
    TxDataObj.prepare_split(split="full_graph", seed=42)
    print("✅ TxData(full_graph) OK")

    TxGNNObj = TxGNN(
        data=TxDataObj,
        weight_bias_track=False,
        proj_name="genesis_alz",
        exp_name="repurpose_v2",
        device="cpu",
    )
    TxGNNObj.model_initialize(
        n_hid=128, n_inp=128, n_out=128, proto=True, proto_num=3,
        attention=False, sim_measure='all_nodes_profile',
        agg_measure='rarity', num_walks=200, walk_mode='bit', path_length=2,
    )
    TxGNNObj.load_pretrained(str(CKPT))
    print("✅ pretrained 로드 OK")

    tx_eval = TxEval(model=TxGNNObj)

    # 알츠하이머 6개 idx만 평가 (1회)
    print(f"\n--- eval_disease_centric (알츠하이머 {len(ALZ_IDXS)}개 idx) ---")
    result = tx_eval.eval_disease_centric(
        disease_idxs=ALZ_IDXS,
        relation="indication",
        return_raw=True,
        save_result=True,
        save_name=str(RESULT_DIR / "alzheimer_indication_raw.pkl"),
    )
    print(f"✅ eval 완료. type={type(result).__name__}")

    # 결과 덤프
    summary_path = RESULT_DIR / "summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Result type: {type(result).__name__}\n")
        if isinstance(result, dict):
            f.write(f"Keys: {list(result.keys())}\n\n")
            for k, v in list(result.items())[:10]:
                f.write(f"--- {k} ({type(v).__name__}) ---\n{repr(v)[:2000]}\n\n")
        else:
            f.write(f"Repr: {repr(result)[:5000]}\n")
    print(f"요약: {summary_path}")

    # 추천 약물 추출 시도 (TxGNN 내부 구조에 따라 다름)
    try:
        import pandas as pd
        if isinstance(result, dict):
            for alz_idx in ALZ_IDXS:
                key_candidates = [alz_idx, str(alz_idx), int(alz_idx)]
                for k in key_candidates:
                    if k in result:
                        entry = result[k]
                        if isinstance(entry, pd.DataFrame):
                            entry.to_csv(RESULT_DIR / f"alz_{alz_idx}_top.csv", index=False)
                            print(f"  idx={alz_idx}: {len(entry)} rows → alz_{alz_idx}_top.csv")
                        elif isinstance(entry, dict):
                            for sub_k, sub_v in entry.items():
                                if isinstance(sub_v, pd.DataFrame):
                                    sub_v.to_csv(RESULT_DIR / f"alz_{alz_idx}_{sub_k}.csv", index=False)
                                    print(f"  idx={alz_idx} [{sub_k}]: {len(sub_v)} rows")
                        break
    except Exception as e:
        print(f"후처리 중 error (무시): {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
