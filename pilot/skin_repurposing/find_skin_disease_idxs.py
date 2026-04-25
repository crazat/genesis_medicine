"""TxGNN PrimeKG에서 피부 질환 인덱스 자동 탐색.

대상 키워드:
- scar / keloid / cicatrix
- melasma / hyperpigmentation
- alopecia / hair loss
- acne
- atopic dermatitis / eczema
- psoriasis
- photoaging / skin aging
- vitiligo
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

CKPT = Path.home() / "genesis_medicine" / ".cache" / "txgnn" / "model_ckpt"
OUT = Path(__file__).parent / "results"
OUT.mkdir(parents=True, exist_ok=True)


KEYWORDS = {
    "scar":     ["scar", "keloid", "cicatrix", "fibrosis"],
    "pigment":  ["melasma", "hyperpigmentation", "vitiligo", "albinism", "freckle"],
    "alopecia": ["alopecia", "hair loss", "androgenetic"],
    "acne":     ["acne", "rosacea"],
    "atopic":   ["atopic", "eczema", "dermatitis"],
    "psoriasis": ["psoriasis"],
    "photoaging": ["photoaging", "skin aging"],
}


def main() -> None:
    nm = pickle.loads((CKPT / "name_mapping.pkl").read_bytes())
    id2name = nm["id2name_disease"]
    idx2id = nm["idx2id_disease"]
    id_to_idx = {v: k for k, v in idx2id.items()}

    by_category: dict[str, list[dict]] = {k: [] for k in KEYWORDS}
    for d_id, name in id2name.items():
        if not isinstance(name, str):
            continue
        nm_l = name.lower()
        for cat, kws in KEYWORDS.items():
            if any(kw in nm_l for kw in kws):
                idx = id_to_idx.get(d_id)
                if idx is not None and isinstance(idx, (int, float)):
                    by_category[cat].append({
                        "idx": idx, "id": d_id, "name": name,
                    })
                break

    for cat, hits in by_category.items():
        print(f"\n=== {cat} ({len(hits)} matches) ===")
        for h in hits[:20]:
            print(f"  idx={h['idx']:<10}  name={h['name'][:80]}")

    out_path = OUT / "skin_disease_idxs.json"
    out_path.write_text(json.dumps(by_category, indent=2, ensure_ascii=False))
    print(f"\n✅ {out_path}")


if __name__ == "__main__":
    main()
