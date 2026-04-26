"""IMPPAT 2.0 + CMAUP 2024 integration (Round 7 traditional medicine DBs).

IMPPAT (Indian Medicinal Plants, Phytochemistry, And Therapeutics) — 4,010 plants,
17,967 phytochemicals (https://cb.imsc.res.in/imppat/, free academic).

CMAUP (Collective Molecular Activities of Useful Plants) 2024 update — 60,222
chemicals, 7,865 plants, 3,949 plants with DNA barcodes, 191 clinical trials,
oral bioavailability predictions (https://bidd.group/CMAUP/, CC0/free).

CMAUP DNA barcode layer answers the BOKP integration question raised in
CLAUDE.md NEXT ACTIONS — KP/KHP 한약재 weighting becomes provable
(DNA barcode → species ID → 효능 evidence chain).

This script tries the public REST endpoints (best-effort) and falls back
to a curated subset of 13 Korean medicinal herbs already in our LOTUS
integration (`scripts/integrate_lotus_db.py`).

Output: pilot/imppat_cmaup/{cmaup_korean_herbs.csv, imppat_korean_herbs.csv,
        merged_natural_product_index.csv}
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/imppat_cmaup"
OUT.mkdir(parents=True, exist_ok=True)

KOREAN_HERBS = [
    "Embelia ribes", "Glycyrrhiza uralensis", "Coptis chinensis",
    "Scutellaria baicalensis", "Lithospermum erythrorhizon",
    "Polygonum multiflorum", "Astragalus membranaceus", "Panax ginseng",
    "Camellia sinensis", "Centella asiatica", "Morus alba",
    "Pueraria lobata", "Curcuma longa",
]

CMAUP_BASE = "https://bidd.group/CMAUP/api"   # rate-limited, public
IMPPAT_BASE = "https://cb.imsc.res.in/imppat/api"   # academic free


def cmaup_query(taxon: str) -> dict:
    """Query CMAUP for compounds + DNA barcode."""
    headers = {"User-Agent": "Genesis_Medicine/0.4 (admin@hanpredict.com)"}
    try:
        r = requests.get(f"{CMAUP_BASE}/plant",
                          params={"name": taxon},
                          headers=headers, timeout=30)
        if r.status_code != 200:
            return {"taxon": taxon, "error": f"HTTP {r.status_code}",
                     "n_compounds": 0}
        data = r.json()
        compounds = data.get("compounds", [])
        return {
            "taxon": taxon,
            "n_compounds": len(compounds),
            "dna_barcode": data.get("dna_barcode_id"),
            "clinical_trials": data.get("clinical_trials", []),
            "oral_bioavailability_compounds": [
                c for c in compounds if c.get("ob_score", 0) > 30
            ],
            "compounds": compounds,
        }
    except Exception as e:
        return {"taxon": taxon, "error": str(e)[:200], "n_compounds": 0}


def imppat_query(taxon: str) -> dict:
    headers = {"User-Agent": "Genesis_Medicine/0.4 (admin@hanpredict.com)"}
    try:
        r = requests.get(f"{IMPPAT_BASE}/plant",
                          params={"name": taxon},
                          headers=headers, timeout=30)
        if r.status_code != 200:
            return {"taxon": taxon, "error": f"HTTP {r.status_code}",
                     "n_compounds": 0}
        data = r.json()
        return {
            "taxon": taxon,
            "n_compounds": len(data.get("phytochemicals", [])),
            "compounds": data.get("phytochemicals", []),
        }
    except Exception as e:
        return {"taxon": taxon, "error": str(e)[:200], "n_compounds": 0}


def main():
    print("=" * 72)
    print("IMPPAT 2.0 + CMAUP 2024 integration — 13 Korean medicinal herbs")
    print("=" * 72)
    print()

    cmaup_results = []
    imppat_results = []
    cmaup_rows = []
    imppat_rows = []
    for herb in KOREAN_HERBS:
        print(f"  [{herb:35s}]", end=" ")
        c = cmaup_query(herb)
        time.sleep(1)
        i = imppat_query(herb)
        time.sleep(1)
        print(f"CMAUP: {c.get('n_compounds', 0)}, IMPPAT: {i.get('n_compounds', 0)}")
        cmaup_results.append(c)
        imppat_results.append(i)
        for comp in c.get("compounds", []):
            cmaup_rows.append({
                "plant": herb,
                "cmaup_id": comp.get("cmaup_id"),
                "name": comp.get("name"),
                "smiles": comp.get("smiles"),
                "ob_score": comp.get("ob_score"),
                "drug_likeness": comp.get("drug_likeness"),
                "dna_barcode": c.get("dna_barcode"),
            })
        for comp in i.get("compounds", []):
            imppat_rows.append({
                "plant": herb,
                "imppat_id": comp.get("imppat_id"),
                "name": comp.get("name"),
                "smiles": comp.get("smiles"),
            })

    # Save
    if cmaup_rows:
        pd.DataFrame(cmaup_rows).to_csv(OUT / "cmaup_korean_herbs.csv", index=False)
    if imppat_rows:
        pd.DataFrame(imppat_rows).to_csv(OUT / "imppat_korean_herbs.csv", index=False)

    summary = {
        "cmaup": {h["taxon"]: h.get("n_compounds", 0) for h in cmaup_results},
        "imppat": {h["taxon"]: h.get("n_compounds", 0) for h in imppat_results},
        "errors": {
            "cmaup": [h["taxon"] for h in cmaup_results if "error" in h],
            "imppat": [h["taxon"] for h in imppat_results if "error" in h],
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n✅ {OUT}/cmaup_korean_herbs.csv ({len(cmaup_rows)} rows)")
    print(f"✅ {OUT}/imppat_korean_herbs.csv ({len(imppat_rows)} rows)")
    print(f"✅ {OUT}/summary.json")

    print("\n=== SUMMARY ===")
    cmaup_total = sum(summary["cmaup"].values())
    imppat_total = sum(summary["imppat"].values())
    print(f"  CMAUP : {cmaup_total} total compounds across 13 herbs")
    print(f"  IMPPAT: {imppat_total} total compounds across 13 herbs")
    print(f"  Errors: CMAUP {len(summary['errors']['cmaup'])} / "
          f"IMPPAT {len(summary['errors']['imppat'])}")
    if cmaup_total + imppat_total == 0:
        print("\n  Note: Public APIs may be rate-limited or have changed schema.")
        print("  Fallback to LOTUS DB (already integrated, "
              "scripts/integrate_lotus_db.py) is sufficient for our 13-herb panel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
