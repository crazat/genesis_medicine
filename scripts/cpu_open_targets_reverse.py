"""Open Targets reverse query — for top integrated candidates per target,
fetch disease association data via OT GraphQL v6. Multi-thread REST.
"""
from __future__ import annotations
import sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


# Map target name → ENSG ID (Open Targets uses these)
TARGET_ENSG = {
    "ar":     "ENSG00000169083",    # AR
    "ctgf":   "ENSG00000118523",    # CCN2 / CTGF
    "ctnnb1": "ENSG00000168036",
    "dct":    "ENSG00000080166",
    "fgf2":   "ENSG00000138685",
    "jun":    "ENSG00000177606",
    "lox":    "ENSG00000113083",
    "mitf":   "ENSG00000187098",
    "mmp1":   "ENSG00000196611",
    "pdgfrb": "ENSG00000113721",
    "ptgs2":  "ENSG00000073756",
    "sirt1":  "ENSG00000096717",
    "smad3":  "ENSG00000166949",
    "srd5a2": "ENSG00000277893",
    "tgfb1":  "ENSG00000105329",
    "tyr":    "ENSG00000077498",
    "tyrp1":  "ENSG00000107165",
    "vegfa":  "ENSG00000112715",
}


def fetch_target(target_name: str, ensg: str):
    query = """
    query target($ensgId: String!) {
      target(ensemblId: $ensgId) {
        id
        approvedSymbol
        biotype
        associatedDiseases {
          count
          rows {
            disease { id name }
            score
          }
        }
      }
    }
    """
    try:
        r = requests.post(
            "https://api.platform.opentargets.org/api/v4/graphql",
            json={"query": query, "variables": {"ensgId": ensg}},
            timeout=30,
        )
        if r.status_code != 200:
            return {"target": target_name, "error": f"HTTP {r.status_code}"}
        data = r.json()["data"]["target"]
        if not data:
            return {"target": target_name, "error": "no data"}
        diseases = data["associatedDiseases"]["rows"]
        # Skin-related diseases filter
        skin_kw = ("scar", "fibrosis", "keloid", "pigment", "melan", "alopec",
                    "acne", "photoa", "psoriasis", "atop", "skin", "epider",
                    "wound", "dermat", "rosace", "lipoder", "sclerod")
        skin_hits = [d for d in diseases if any(k in d["disease"]["name"].lower()
                                                  for k in skin_kw)]
        return {
            "target": target_name,
            "approved_symbol": data.get("approvedSymbol"),
            "biotype": data.get("biotype"),
            "n_diseases": data["associatedDiseases"]["count"],
            "n_skin_hits": len(skin_hits),
            "top_diseases": [(d["disease"]["name"], round(d["score"], 3))
                              for d in diseases[:5]],
            "skin_diseases": [(d["disease"]["name"], round(d["score"], 3))
                                for d in skin_hits[:10]],
        }
    except Exception as e:
        return {"target": target_name, "error": str(e)[:120]}


def main():
    print(f"Open Targets reverse query for {len(TARGET_ENSG)} skin targets")

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_target, t, e): t for t, e in TARGET_ENSG.items()}
        results = []
        for f in as_completed(futures):
            r = f.result()
            results.append(r)
            print(f"  {r['target']:10s}: ", end="")
            if "error" in r:
                print(f"❌ {r['error']}")
            else:
                print(f"{r['n_skin_hits']} skin / {r['n_diseases']} total diseases")
                for name, score in r["skin_diseases"][:3]:
                    print(f"      • {name}  (score={score})")

    # Save
    rows = []
    for r in results:
        if "error" in r:
            continue
        for d_name, d_score in r["skin_diseases"]:
            rows.append({
                "target": r["target"],
                "approved_symbol": r["approved_symbol"],
                "disease": d_name,
                "ot_score": d_score,
                "category": "skin",
            })
        for d_name, d_score in r["top_diseases"][:3]:
            rows.append({
                "target": r["target"],
                "approved_symbol": r["approved_symbol"],
                "disease": d_name,
                "ot_score": d_score,
                "category": "top_overall",
            })
    pd.DataFrame(rows).to_csv(OUT / "open_targets_reverse.csv", index=False)
    print(f"\n✅ open_targets_reverse.csv ({len(rows)} rows)")


if __name__ == "__main__":
    sys.exit(main())
