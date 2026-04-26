"""LOTUS Natural Product Database live integration (corrected REST API).

LOTUS (https://lotus.naturalproducts.net/) — 750k structure-organism pairs, CC0.
API endpoint: /api/search/simple?query=<text>&type=<organism|name|substructure>

Use case: enumerate compounds for our 13 Korean medicinal herbs of interest.
Output: pilot/lotus_db/{taxon}_compounds.csv per query + pooled.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/lotus_db"
OUT.mkdir(parents=True, exist_ok=True)

LOTUS_API = "https://lotus.naturalproducts.net/api/search/simple"

KOREAN_HERBS = [
    "Embelia ribes",                # 자단 / Vidanga
    "Glycyrrhiza uralensis",        # 감초
    "Coptis chinensis",             # 황련
    "Scutellaria baicalensis",      # 황금
    "Lithospermum erythrorhizon",   # 자초
    "Polygonum multiflorum",        # 하수오
    "Astragalus membranaceus",      # 황기
    "Panax ginseng",                # 인삼
    "Camellia sinensis",            # 녹차
    "Centella asiatica",            # 병풀
    "Morus alba",                   # 상백피
    "Pueraria lobata",              # 갈근
    "Curcuma longa",                # 강황
]


def lotus_query(taxon_name: str) -> dict:
    headers = {"User-Agent": "Genesis_Medicine/0.3 (admin@hanpredict.com)"}
    try:
        r = requests.get(LOTUS_API,
                         params={"query": taxon_name, "type": "organism"},
                         headers=headers, timeout=60)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "taxon": taxon_name}
        data = r.json()
        nps = data.get("naturalProducts", [])
        return {"taxon": taxon_name,
                "n_compounds": len(nps),
                "compounds": nps}
    except Exception as e:
        return {"error": str(e)[:200], "taxon": taxon_name}


def main():
    print("=" * 72)
    print("LOTUS DB live integration — 13 Korean medicinal plants")
    print("=" * 72)
    print()

    all_rows = []
    summary = []
    for plant in KOREAN_HERBS:
        print(f"  [{plant:35s}] querying...", end=" ")
        result = lotus_query(plant)
        if "error" in result:
            print(f"⚠️ {result['error'][:50]}")
            summary.append({"plant": plant, "n_compounds": 0,
                              "error": result["error"]})
        else:
            n = result["n_compounds"]
            print(f"✅ {n} compounds")
            summary.append({"plant": plant, "n_compounds": n})
            for c in result["compounds"]:
                wd = c.get("wikidata_id") or ""
                row = {
                    "plant": plant,
                    "lotus_id": c.get("lotus_id"),
                    "wikidata_id": wd.rsplit("/", 1)[-1] if wd else "",
                    "name": c.get("traditional_name") or c.get("iupac_name", ""),
                    "smiles": c.get("smiles2D") or c.get("smiles"),
                    "inchikey": c.get("inchikey"),
                    "molecular_formula": c.get("molecular_formula"),
                    "MW": c.get("molecular_weight"),
                    "n_atoms": c.get("heavy_atom_number"),
                    "n_rings": c.get("number_of_rings") or c.get("max_number_of_rings"),
                    "npl_score": c.get("npl_score"),
                }
                all_rows.append(row)
        time.sleep(2)

    # Save
    df = pd.DataFrame(all_rows)
    df_unique = df.drop_duplicates(subset="inchikey")
    df.to_csv(OUT / "korean_herbs_lotus_full.csv", index=False)
    df_unique.to_csv(OUT / "korean_herbs_lotus_unique.csv", index=False)
    pd.DataFrame(summary).to_csv(OUT / "summary.csv", index=False)
    print(f"\n✅ {OUT}/korean_herbs_lotus_full.csv   ({len(df)} total rows)")
    print(f"✅ {OUT}/korean_herbs_lotus_unique.csv ({len(df_unique)} unique compounds)")
    print(f"✅ {OUT}/summary.csv")
    print()

    print("=== SUMMARY ===")
    total = 0
    for row in summary:
        n = row.get("n_compounds", 0)
        total += n
        flag = "❌" if "error" in row else "✅"
        print(f"  {row['plant']:35s} → {n:5d} compounds {flag}")
    print(f"  TOTAL across 13 herbs: {total}")
    print(f"  Unique (by InChIKey): {len(df_unique)}")

    # Highlight Embelia ribes (our scaffold-hop seed)
    emb_rows = df[df["plant"] == "Embelia ribes"]
    if len(emb_rows) > 0:
        print(f"\n⭐ Embelia ribes (Vidanga / 자단): {len(emb_rows)} LOTUS records")
        print("  Top 8 (by NP-likeness score):")
        for _, r in emb_rows.sort_values("npl_score", ascending=False).head(8).iterrows():
            name = (r["name"] or "")[:40]
            smi = (r["smiles"] or "")[:50]
            print(f"    {name:40s} {smi}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
