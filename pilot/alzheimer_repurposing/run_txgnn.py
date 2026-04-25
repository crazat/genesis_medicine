"""TxGNN 알츠하이머 zero-shot 약물 재창출 실런.

NEXT ACTIONS #1c 실행.

기대 결과: BACE1 외 타겟 경로 (APOE, GSK3B, MAPT 등)를 통한
이미 승인된 약물 재활용 후보 top 100.
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

CKPT = Path.home() / "genesis_medicine" / ".cache" / "txgnn" / "model_ckpt"
RESULT_DIR = Path(__file__).parent / "results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def find_alzheimer_idx(name_mapping_path: Path) -> list[int] | None:
    """name_mapping.pkl에서 알츠하이머 인덱스 찾기."""
    with open(name_mapping_path, "rb") as f:
        nm = pickle.load(f)
    print(f"name_mapping keys: {list(nm.keys())[:10] if isinstance(nm, dict) else type(nm)}")
    if isinstance(nm, dict):
        # disease 또는 유사한 키
        for key in ("disease", "diseases", "disease_name", "nodes"):
            if key in nm:
                subset = nm[key]
                break
        else:
            subset = nm
        hits = []
        for k, v in subset.items() if hasattr(subset, 'items') else []:
            s = str(v).lower() if not isinstance(v, (int, float)) else str(k).lower()
            if "alzheimer" in s:
                hits.append((k, v))
        print(f"Alzheimer matches: {hits[:10]}")
        return [h[0] for h in hits if isinstance(h[0], int)]
    return None


def main() -> int:
    print("=== TxGNN 알츠하이머 재창출 ===")
    print(f"Checkpoint: {CKPT}")
    assert CKPT.exists(), f"체크포인트 디렉터리 없음: {CKPT}"

    # 1. name_mapping으로 알츠하이머 idx 찾기
    nm_path = CKPT / "name_mapping.pkl"
    if nm_path.exists():
        print("\n--- Step 1: 알츠하이머 인덱스 탐색 ---")
        idxs = find_alzheimer_idx(nm_path)
        if idxs:
            print(f"후보 idx: {idxs}")

    # 2. pretrained 로드 시도
    print("\n--- Step 2: TxGNN 사전 훈련 모델 로드 ---")
    from txgnn import TxData, TxGNN, TxEval

    # TxData — data_folder_path는 PrimeKG 원본 데이터가 있어야 함.
    # pretrained zip에서는 전처리된 full_graph_split1_eval.pkl만 있음.
    # 우선 TxData.prepare_split 없이 최소 로드 시도 — full_graph 모드.
    data_folder = str(CKPT)

    print(f"data_folder: {data_folder}")
    try:
        TxDataObj = TxData(data_folder_path=data_folder)
        TxDataObj.prepare_split(split="full_graph", seed=42)
        print("✅ TxData.prepare_split(full_graph) OK")
    except Exception as e:
        print(f"❌ TxData full_graph 실패: {type(e).__name__}: {e}")
        # complex_disease로 재시도
        try:
            TxDataObj = TxData(data_folder_path=data_folder)
            TxDataObj.prepare_split(split="complex_disease", seed=42)
            print("✅ TxData.prepare_split(complex_disease) OK")
        except Exception as e2:
            print(f"❌ complex_disease 도 실패: {type(e2).__name__}: {e2}")
            return 1

    # RTX 5090 Blackwell은 DGL 2.4/cu121 커널 미지원 → CPU 실행
    TxGNNObj = TxGNN(
        data=TxDataObj,
        weight_bias_track=False,
        proj_name="genesis_alz",
        exp_name="repurpose",
        device="cpu",
    )
    TxGNNObj.model_initialize(n_hid=128, n_inp=128, n_out=128, proto=True,
                              proto_num=3, attention=False,
                              sim_measure='all_nodes_profile',
                              agg_measure='rarity', num_walks=200,
                              walk_mode='bit', path_length=2)
    try:
        TxGNNObj.load_pretrained(str(CKPT))
        print("✅ pretrained 로드 OK")
    except Exception as e:
        print(f"❌ load_pretrained 실패: {type(e).__name__}: {e}")
        return 2

    # 3. 알츠하이머 disease-centric evaluation
    print("\n--- Step 3: 알츠하이머 중심 평가 ---")
    tx_eval = TxEval(model=TxGNNObj)

    # test_set 기반으로 구해서 저장
    try:
        result = tx_eval.eval_disease_centric(
            disease_idxs="test_set",
            relation="indication",
            return_raw=True,
            save_result=True,
            save_name=str(RESULT_DIR / "disease_centric_indication.pkl"),
        )
        print(f"✅ eval 완료. out type: {type(result).__name__}")
        # 요약 덤프
        summary_path = RESULT_DIR / "disease_centric_indication_summary.txt"
        with open(summary_path, "w") as f:
            f.write(f"Result type: {type(result).__name__}\n")
            if isinstance(result, dict):
                f.write(f"Keys: {list(result.keys())[:30]}\n")
                for k, v in list(result.items())[:3]:
                    f.write(f"\n{k} → {type(v).__name__}\n{str(v)[:500]}\n")
        print(f"   요약: {summary_path}")
    except Exception as e:
        print(f"❌ eval_disease_centric 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
