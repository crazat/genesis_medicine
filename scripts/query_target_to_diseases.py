"""Inverse Open Targets query: for each canonical anti-fibrotic target,
which fibrotic-spectrum diseases is it associated with at OT score >= 0.4?

Provides honest evidence base for the cross-disease hypothesis in preprint #9.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parents[1] / "pilot/open_targets"
OUT.mkdir(parents=True, exist_ok=True)

API = "https://api.platform.opentargets.org/api/v4/graphql"

# Canonical anti-fibrotic master-switch targets (Ensembl gene IDs)
# from Open Targets target search; verified via approvedSymbol
TARGETS = {
    "TGFB1":   "ENSG00000105329",
    "MMP1":    "ENSG00000196611",
    "MMP3":    "ENSG00000149968",
    "MMP9":    "ENSG00000100985",
    "CTGF":    "ENSG00000118523",   # CCN2
    "SMAD3":   "ENSG00000166949",
    "PDGFRB":  "ENSG00000113721",
    "LOX":     "ENSG00000113083",
    "COL1A1":  "ENSG00000108821",
}

# Fibrosis-spectrum disease keywords (we'll filter the OT result by disease name)
FIBROSIS_KEYWORDS = [
    "fibros", "scler", "keloid", "scar", "cirrhos",
    "interstit", "pulmonary fibros", "renal fibros", "liver fibros",
    "atrophy", "remodel"
]

QUERY = """
query AssociatedDiseases($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    id
    approvedSymbol
    associatedDiseases(page: { index: 0, size: 100 }) {
      count
      rows {
        disease {
          id
          name
          therapeuticAreas {
            id
            name
          }
        }
        score
      }
    }
  }
}
"""


def query_target(ensembl: str, retries: int = 3):
    for i in range(retries):
        try:
            r = requests.post(API, json={"query": QUERY,
                                          "variables": {"ensemblId": ensembl}},
                                timeout=30)
            if r.status_code == 200:
                return r.json()
            time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(2)
    return None


def main():
    print("=" * 72)
    print("Open Targets — anti-fibrotic master-switch targets → diseases")
    print("=" * 72)

    rows = []
    for symbol, ensembl in TARGETS.items():
        print(f"\n[{symbol}] {ensembl}")
        res = query_target(ensembl)
        if res is None or "errors" in res or res.get("data", {}).get("target") is None:
            print(f"  ⚠️ failed or not found")
            continue
        t = res["data"]["target"]
        n_total = t["associatedDiseases"]["count"]
        # Filter: OT score >= 0.4 AND disease name matches fibrosis keyword
        fibrotic_hits = []
        for entry in t["associatedDiseases"]["rows"]:
            d = entry["disease"]
            score = entry["score"]
            if score < 0.4: continue
            name_lower = d["name"].lower()
            if any(kw in name_lower for kw in FIBROSIS_KEYWORDS):
                fibrotic_hits.append({"disease_id": d["id"],
                                        "disease_name": d["name"],
                                        "ot_score": score})
        print(f"  {n_total} total, {len(fibrotic_hits)} fibrosis-spectrum at score>=0.4")
        for hit in fibrotic_hits[:5]:
            print(f"    - {hit['disease_name']} ({hit['ot_score']:.2f})")
        for hit in fibrotic_hits:
            rows.append({"target_symbol": symbol, **hit})
        time.sleep(1)

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUT / "antifibrotic_targets_to_diseases.csv", index=False)
        print(f"\n✅ {OUT}/antifibrotic_targets_to_diseases.csv ({len(df)} rows)")

        # Pivot: which diseases hit by how many of our targets
        disease_counts = df.groupby(["disease_id", "disease_name"]).agg(
            n_targets_hitting=("target_symbol", "nunique"),
            mean_score=("ot_score", "mean"),
            target_list=("target_symbol", lambda x: ",".join(sorted(set(x)))),
        ).reset_index().sort_values("n_targets_hitting", ascending=False)
        disease_counts.to_csv(OUT / "fibrosis_diseases_target_overlap.csv", index=False)
        print(f"✅ {OUT}/fibrosis_diseases_target_overlap.csv")
        print("\n=== Top fibrotic diseases by # canonical anti-fibrotic targets associated (OT score>=0.4) ===")
        print(disease_counts.head(12).to_string(index=False))
    else:
        print("\n⚠️ No fibrosis-spectrum hits — review keyword list")
    return 0


if __name__ == "__main__":
    sys.exit(main())
