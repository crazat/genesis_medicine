"""name_mapping.pkl + 그래프에서 알츠하이머 인덱스 찾기."""

from __future__ import annotations

import pickle
from pathlib import Path

CKPT = Path.home() / "genesis_medicine" / ".cache" / "txgnn" / "model_ckpt"


def main() -> None:
    nm = pickle.loads((CKPT / "name_mapping.pkl").read_bytes())
    id2name = nm["id2name_disease"]   # {id: name}
    idx2id = nm["idx2id_disease"]     # {idx: id}

    # 1) name에서 'alzheimer' 검색 → id
    hits_id = [(id_, name) for id_, name in id2name.items()
               if "alzheimer" in str(name).lower()]
    print(f"=== id2name_disease 'alzheimer' hits: {len(hits_id)} ===")
    for id_, name in hits_id[:30]:
        print(f"  id={id_}  name={name}")

    # 2) id → idx 역매핑
    id_to_idx = {v: k for k, v in idx2id.items()}
    print(f"\n=== idx 역매핑 ===")
    alz_idxs = []
    for id_, name in hits_id:
        if id_ in id_to_idx:
            idx = id_to_idx[id_]
            alz_idxs.append(idx)
            print(f"  idx={idx}  id={id_}  name={name}")
        else:
            print(f"  [miss] id={id_} (not in idx2id) name={name}")

    print(f"\n찾은 알츠하이머 idx: {alz_idxs}")
    (CKPT / "alz_idxs.txt").write_text(",".join(str(i) for i in alz_idxs))
    print(f"저장: {CKPT / 'alz_idxs.txt'}")


if __name__ == "__main__":
    main()
