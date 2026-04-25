"""EMB-3 cross-disease repurposing via Open Targets.

각 anti-fibrotic 타겟의 disease association → fibrosis-related 비-피부 질환 추출
→ EMB-3 affinity 가중 score → "skin scar lead → systemic anti-fibrotic" 가능성.

전제: scripts/run_fibrotic_network.py 완료 (network_full.csv 존재)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
NET = ROOT / "pilot/scaffold_hop/network_validation"
OUT = ROOT / "pilot/scaffold_hop/cross_disease"
OUT.mkdir(parents=True, exist_ok=True)

# Open Targets에서 타겟 → 연관 질환
OT = "https://api.platform.opentargets.org/api/v4/graphql"
QUERY = """
query AssocDiseasesByTarget($ensg: String!, $size: Int!) {
  target(ensemblId: $ensg) {
    id
    approvedSymbol
    associatedDiseases(page: { index: 0, size: $size }) {
      count
      rows {
        score
        disease { id name therapeuticAreas { id name } }
      }
    }
  }
}
"""

# UniProt → Ensembl gene ID
TARGET_TO_ENSG = {
    "TGFB1":  "ENSG00000105329",
    "MMP1":   "ENSG00000196611",
    "CTGF":   "ENSG00000118523",
    "JUN":    "ENSG00000177606",
    "LOX":    "ENSG00000113083",
    "SMAD3":  "ENSG00000166949",
    "PDGFRB": "ENSG00000113721",
}

# fibrosis 관련 키워드 (skin 외)
FIBROSIS_KW = [
    "pulmonary fibrosis", "idiopathic pulmonary", "cystic fibrosis",
    "kidney fibrosis", "renal fibrosis", "chronic kidney",
    "liver fibrosis", "hepatic fibrosis", "non-alcoholic", "nash",
    "cardiac fibrosis", "myocardial fibrosis",
    "scleroderma", "systemic sclerosis",
    "crohn", "intestinal fibrosis",
    "peritoneal fibrosis", "retroperitoneal",
    "myelofibrosis",
    "fibrosis",  # 일반 fallback
]

# skin/scar 관련은 제외 (이미 우리 타겟 indication)
SKIN_KW = ["scar", "keloid", "atrophic", "hypertrophic", "skin",
           "psoriasis", "eczema", "dermat"]


def is_fibrosis_disease(name: str) -> bool:
    n = name.lower()
    return any(kw in n for kw in FIBROSIS_KW)


def is_skin(name: str) -> bool:
    n = name.lower()
    return any(kw in n for kw in SKIN_KW)


def fetch_diseases_for_target(ensg: str, size: int = 200) -> list[dict]:
    r = requests.post(OT, json={"query": QUERY, "variables":
                                {"ensg": ensg, "size": size}},
                       timeout=60)
    r.raise_for_status()
    d = r.json()
    target = (d.get("data") or {}).get("target")
    if not target:
        return []
    rows = target["associatedDiseases"]["rows"]
    return [{"disease_id": r["disease"]["id"],
             "disease_name": r["disease"]["name"],
             "score": r["score"],
             "therapeutic_areas": [a["name"]
                                    for a in r["disease"]["therapeuticAreas"]]}
            for r in rows]


def main() -> int:
    network_csv = NET / "network_full.csv"
    if not network_csv.exists():
        print(f"❌ {network_csv} 없음 — A (run_fibrotic_network.py) 먼저 완료")
        return 1

    df = pd.read_csv(network_csv)
    # EMB-3 affinity per target
    emb3_aff = (df[df["compound"] == "emb3"]
                .set_index("target")["affinity_probability_binary"]
                .to_dict())
    print(f"=== EMB-3 affinity per target ===")
    for k, v in emb3_aff.items():
        print(f"  {k:8s} {v:.3f}")

    # 각 타겟 → 연관 질환 fetch
    print(f"\n=== Open Targets — 각 타겟 연관 질환 ===")
    target_diseases = {}
    for tgt, ensg in TARGET_TO_ENSG.items():
        try:
            diseases = fetch_diseases_for_target(ensg, size=300)
            target_diseases[tgt] = diseases
            n_fib = sum(1 for d in diseases
                        if is_fibrosis_disease(d["disease_name"])
                        and not is_skin(d["disease_name"]))
            print(f"  {tgt:8s} {len(diseases)} 연관 질환 / "
                  f"{n_fib} fibrosis-non-skin")
        except Exception as e:
            print(f"  {tgt:8s} ❌ {e}")
            target_diseases[tgt] = []

    # 질환 → 가중 score (sum of target_score × emb3_affinity)
    disease_scores = defaultdict(lambda: {
        "name": "", "targets": [], "ot_scores": [], "emb3_aff": [],
        "therapeutic_areas": set(), "weighted": 0,
    })
    for tgt, diseases in target_diseases.items():
        emb3 = emb3_aff.get(tgt, 0)
        if emb3 < 0.4:   # weak binding 제외
            continue
        for d in diseases:
            name = d["disease_name"]
            if is_skin(name) or not is_fibrosis_disease(name):
                continue
            ds = disease_scores[d["disease_id"]]
            ds["name"] = name
            ds["targets"].append(tgt)
            ds["ot_scores"].append(d["score"])
            ds["emb3_aff"].append(emb3)
            ds["therapeutic_areas"].update(d["therapeutic_areas"])
            ds["weighted"] += d["score"] * emb3

    # 정렬
    rows = [{"disease_id": did,
             "disease_name": v["name"],
             "n_targets_hit": len(v["targets"]),
             "targets": ",".join(v["targets"]),
             "weighted_score": round(v["weighted"], 3),
             "max_ot_score": round(max(v["ot_scores"]), 3),
             "therapeutic_areas": ", ".join(sorted(v["therapeutic_areas"])),
             }
            for did, v in disease_scores.items()]
    if not rows:
        print("\n⚠️ fibrosis-related 질환 0건")
        return 2
    out_df = pd.DataFrame(rows).sort_values("weighted_score", ascending=False)
    out_df.to_csv(OUT / "ranked_diseases.csv", index=False)

    print(f"\n=== TOP 15 — EMB-3 cross-disease 적용 가능성 ===")
    print(f"{'질환명':40s} {'타겟수':>5s} {'타겟':25s} {'가중':>7s}")
    print("-" * 90)
    for _, r in out_df.head(15).iterrows():
        nm = r["disease_name"][:40]
        tg = r["targets"][:25]
        print(f"{nm:40s} {r['n_targets_hit']:5d} {tg:25s} "
              f"{r['weighted_score']:7.2f}")
    print(f"\n✅ {OUT}/ranked_diseases.csv ({len(out_df)} 질환)")

    # 시장 가치 큰 질환 강조
    big = ["pulmonary", "kidney", "liver", "nash", "hepatic", "scleroderma",
           "myelofibrosis"]
    print(f"\n=== 시장 가치 큰 fibrosis 질환 (paper 강조 후보) ===")
    for kw in big:
        sub = out_df[out_df["disease_name"].str.contains(kw, case=False, na=False)]
        if not sub.empty:
            top = sub.iloc[0]
            print(f"  ✓ [{kw}] {top['disease_name'][:50]:50s} "
                  f"({top['n_targets_hit']} 타겟, weighted {top['weighted_score']:.2f})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
