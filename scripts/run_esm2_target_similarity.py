"""ESM2 embedding으로 14 타겟 cross-similarity 매트릭스.

Genesis_Medicine v3 14 fibrotic 타겟 sequence → ESM2-650M embedding (1280-d) →
pairwise cosine 유사도. 우리 흉터 lead가 다른 타겟에도 cross-active 가능성을
sequence-level 사전 예측.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = Path.home() / "genesis_medicine" / "data"
MSA_CACHE = DATA / "msa"
OUT = ROOT / "pilot/scaffold_hop/esm2_targets"
OUT.mkdir(parents=True, exist_ok=True)


# UniProt → Genesis_Medicine 14 타겟
TARGETS = {
    "TGFB1":  "P01137", "MMP1":   "P03956", "CTGF":   "P29279",
    "TYR":    "P14679", "TYRP1":  "P17643", "DCT":    "P40126",
    "SRD5A2": "P31213", "AR":     "P10275", "CTNNB1": "P35222",
    "PTGS2":  "P35354", "SIRT1":  "Q96EB6", "JUN":    "P05412",
    "LOX":    "P28300", "SMAD3":  "P84022",
}


def fetch_uniprot_seq(acc: str) -> str:
    cache = MSA_CACHE / f"{acc}.fasta"
    if cache.exists():
        text = cache.read_text()
    else:
        r = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta",
                          timeout=30)
        r.raise_for_status()
        text = r.text
        cache.write_text(text)
    return "".join(line for line in text.splitlines() if not line.startswith(">"))


def main() -> int:
    from genesis_medicine.proteomics.esm3_adapter import get_protein_embedding

    print("=== ESM2 14 타겟 cross-similarity 매트릭스 ===\n")
    embeddings = {}
    for key, acc in TARGETS.items():
        seq = fetch_uniprot_seq(acc)
        # ESM2 max length 1024; truncate
        if len(seq) > 1022:
            seq = seq[:1022]
        print(f"  [{key:6s}] {acc} {len(seq)} AA → embedding…")
        r = get_protein_embedding(seq, "esm2-650m")
        if r.embedding:
            embeddings[key] = np.array(r.embedding)
        else:
            print(f"    ⚠️  실패: {r.metadata.get('error')}")

    if len(embeddings) < 2:
        print("❌ 충분한 embedding 없음")
        return 1

    keys = list(embeddings.keys())
    n = len(keys)
    sim = np.zeros((n, n))
    for i, k1 in enumerate(keys):
        for j, k2 in enumerate(keys):
            v1, v2 = embeddings[k1], embeddings[k2]
            sim[i, j] = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    df_sim = pd.DataFrame(sim, index=keys, columns=keys)
    df_sim.to_csv(OUT / "target_similarity.csv", float_format="%.4f")

    print(f"\n=== Pairwise cosine 유사도 (top diagonal 제외) ===")
    print(df_sim.round(3).to_string())

    # Top similar pairs (≥ 0.85 = cross-active 후보)
    print(f"\n=== Cross-active 후보 (similarity ≥ 0.85, 자기 제외) ===")
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            s = sim[i, j]
            if s >= 0.85:
                pairs.append((keys[i], keys[j], s))
    pairs.sort(key=lambda x: -x[2])
    for k1, k2, s in pairs[:15]:
        print(f"  {k1:8s} ↔ {k2:8s}  cos = {s:.3f}")

    # EMB-3 우리 lead — TGFB1, MMP1 비슷한 타겟 추천
    if "TGFB1" in embeddings:
        print(f"\n=== TGFB1 가장 유사한 타겟 (EMB-3 cross-active 후보) ===")
        tgfb1_v = embeddings["TGFB1"]
        scores = {k: float(np.dot(tgfb1_v, embeddings[k]) /
                            (np.linalg.norm(tgfb1_v) * np.linalg.norm(embeddings[k])))
                   for k in keys if k != "TGFB1"}
        for k, s in sorted(scores.items(), key=lambda x: -x[1])[:5]:
            print(f"  TGFB1 ↔ {k:8s}  cos = {s:.3f}")

    print(f"\n✅ {OUT}/target_similarity.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
