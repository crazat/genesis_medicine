"""Open Targets disease-target association query for fibrotic indications.

Fetches real target associations from Open Targets Platform v4 GraphQL API
for the 5 fibrotic indications cited in preprint #9 (cross-disease IPF).
Output: pilot/open_targets/fibrosis_targets.csv with per-disease target list.

This replaces fabricated cross-disease overlap percentages in preprint #9.
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

API_URL = "https://api.platform.opentargets.org/api/v4/graphql"

# EFO / MONDO IDs for the 5 fibrotic indications
DISEASES = {
    "skin_fibrosis_keloid": {
        "efo": "EFO_0009551",       # hypertrophic / keloid scar
        "label": "Hypertrophic / keloid scar",
    },
    "IPF": {
        "efo": "EFO_0000768",       # idiopathic pulmonary fibrosis
        "label": "Idiopathic pulmonary fibrosis (IPF)",
    },
    "systemic_sclerosis": {
        "efo": "EFO_0000270",       # systemic scleroderma — actual code may differ
        "label": "Systemic sclerosis (scleroderma)",
    },
    "renal_fibrosis": {
        "efo": "EFO_0009566",       # placeholder; may need MONDO mapping
        "label": "Renal interstitial fibrosis",
    },
    "hepatic_fibrosis": {
        "efo": "EFO_0008502",       # placeholder
        "label": "Hepatic fibrosis",
    },
}

# EMB-3 affinity profile from real Round-1 screen (preprint #3)
EMB3_AFFINITY = {
    "TGFB1": 0.749,
    "MMP1": 0.674,
    "CTGF": 0.678,
    "SMAD3": 0.649,
    "PDGFRB": 0.640,
    "LOX": 0.579,
    "JUN": 0.497,
    "FGF2": 0.484,
    "VEGFA": 0.563,
}

QUERY = """
query AssociatedTargets($efoId: String!) {
  disease(efoId: $efoId) {
    id
    name
    associatedTargets(page: { index: 0, size: 50 }) {
      count
      rows {
        target {
          id
          approvedSymbol
          approvedName
        }
        score
        datatypeScores {
          id
          score
        }
      }
    }
  }
}
"""


def query_disease(efo: str, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            r = requests.post(API_URL, json={"query": QUERY,
                                              "variables": {"efoId": efo}},
                                timeout=30)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"  HTTP {r.status_code} for {efo} (attempt {attempt+1})")
                time.sleep(2)
        except Exception as e:
            print(f"  Error querying {efo}: {e}")
            time.sleep(2)
    return None


def main():
    print("=" * 72)
    print("Open Targets fibrotic indication target query")
    print("=" * 72)

    all_results = {}
    rows = []

    for key, info in DISEASES.items():
        print(f"\n[{key}] {info['efo']} — {info['label']}")
        result = query_disease(info["efo"])
        if result is None:
            print(f"  ⚠️ failed to fetch")
            all_results[key] = {"efo": info["efo"], "label": info["label"],
                                  "targets": [], "error": "fetch_failed"}
            continue

        if "errors" in result:
            print(f"  ⚠️ GraphQL errors: {result['errors']}")
            all_results[key] = {"efo": info["efo"], "label": info["label"],
                                  "targets": [], "error": str(result["errors"])}
            continue

        disease_data = result.get("data", {}).get("disease")
        if disease_data is None:
            print(f"  ⚠️ disease not found in OT")
            all_results[key] = {"efo": info["efo"], "label": info["label"],
                                  "targets": [], "error": "disease_not_found"}
            continue

        assoc = disease_data["associatedTargets"]
        targets = []
        for t in assoc["rows"]:
            sym = t["target"]["approvedSymbol"]
            score = t["score"]
            targets.append({"symbol": sym,
                            "name": t["target"]["approvedName"],
                            "score": score})
            rows.append({
                "indication": key, "indication_label": info["label"],
                "target_symbol": sym,
                "target_name": t["target"]["approvedName"],
                "ot_score": score,
                "emb3_affinity": EMB3_AFFINITY.get(sym, None),
            })
        print(f"  {assoc['count']} associated targets, top: "
              f"{', '.join(t['symbol'] for t in targets[:8])}")
        all_results[key] = {
            "efo": info["efo"], "label": info["label"],
            "n_targets": assoc["count"],
            "targets": targets,
        }
        time.sleep(1)   # rate limit

    # Save raw JSON
    (OUT / "fibrosis_targets_raw.json").write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\n✅ {OUT}/fibrosis_targets_raw.json")

    # CSV with EMB-3 cross-overlap
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "fibrosis_targets.csv", index=False)
    print(f"✅ {OUT}/fibrosis_targets.csv ({len(df)} target-indication pairs)")

    # Compute EMB-3 overlap per indication (using OT score >= 0.4 as relevance threshold)
    overlap_summary = []
    for key, data in all_results.items():
        if "targets" not in data or not data["targets"]:
            overlap_summary.append({
                "indication": key, "label": data["label"],
                "n_targets_ot": 0, "n_emb3_overlap": 0,
                "fraction": 0.0, "note": "no OT data",
            })
            continue
        # Targets with OT score >= 0.4 (moderate-strong evidence)
        relevant = [t for t in data["targets"] if t["score"] >= 0.4]
        # EMB-3 engages if affinity >= 0.55 (moderate threshold)
        emb3_engages = [t for t in relevant
                          if EMB3_AFFINITY.get(t["symbol"], 0) >= 0.55]
        overlap_summary.append({
            "indication": key, "label": data["label"],
            "n_targets_ot": len(relevant),
            "n_emb3_overlap": len(emb3_engages),
            "fraction": (len(emb3_engages) / len(relevant)
                         if relevant else 0),
            "emb3_engaged_targets": [t["symbol"] for t in emb3_engages],
        })

    overlap_df = pd.DataFrame(overlap_summary)
    overlap_df.to_csv(OUT / "emb3_cross_disease_overlap.csv", index=False)
    print(f"✅ {OUT}/emb3_cross_disease_overlap.csv")
    print("\n=== EMB-3 cross-disease overlap (REAL Open Targets data) ===")
    print(overlap_df.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
