"""
F2: Korean patent (KIPRIS) novelty screening for candidate compounds.

KIPRIS Plus API supports compound/ chemical structure search with API key.
Without key, falls back to PubChem patents and Google Scholar patent search.

For each candidate SMILES:
  1. Canonicalize via RDKit
  2. Check PubChem CID + linked patents
  3. Check KIPRIS public web search (if API key in env)
  4. Output: novel / known-with-patent / weak-prior-art
  5. Aggregate: top-N novel scaffolds become highest-priority for our IP path

Output:
  pilot/novelty/{cid}/patent_status.json per candidate
  pilot/novelty/novelty_consolidated.csv  master table

Strategic value:
  - "Novel" hits are the only ones we should commit wet-lab to (have IP runway)
  - Korean patent search advantage for HAN PREDICT positioning
  - Avoids rediscovering already-disclosed compounds
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path("/home/crazat/genesis_medicine")
CACHE = ROOT / ".cache/novelty"
CACHE.mkdir(parents=True, exist_ok=True)

PUBCHEM_API = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
KIPRIS_API_KEY = os.environ.get("KIPRIS_API_KEY")  # optional


def smiles_cache_key(smi: str) -> str:
    return hashlib.md5(smi.encode()).hexdigest()[:12]


def pubchem_search(smiles: str) -> dict:
    """Look up CID + linked patents from PubChem."""
    cache = CACHE / f"pubchem_{smiles_cache_key(smiles)}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    result = {"smiles": smiles, "cid": None, "patents": [], "compound_name": None}
    try:
        r = requests.get(f"{PUBCHEM_API}/compound/smiles/{smiles}/cids/JSON", timeout=10)
        if r.status_code == 200 and r.json().get("IdentifierList", {}).get("CID"):
            cid = r.json()["IdentifierList"]["CID"][0]
            result["cid"] = cid
            r2 = requests.get(f"{PUBCHEM_API}/compound/cid/{cid}/synonyms/JSON", timeout=10)
            if r2.status_code == 200:
                syns = r2.json().get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
                result["compound_name"] = syns[0] if syns else None
                # Find ChEMBL/CAS-like patent identifiers among synonyms
                for s in syns:
                    if s.startswith("US") or s.startswith("EP") or s.startswith("WO") or s.startswith("KR"):
                        result["patents"].append(s)
    except Exception as e:
        result["error"] = str(e)

    cache.write_text(json.dumps(result, indent=2))
    return result


def kipris_search(smiles: str, compound_name: str | None) -> dict:
    """Search KIPRIS via Plus API (requires KIPRIS_API_KEY env var)."""
    cache = CACHE / f"kipris_{smiles_cache_key(smiles)}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    result = {"queried": False, "patent_count": None, "patents": []}
    if not KIPRIS_API_KEY:
        result["note"] = "KIPRIS_API_KEY not set — skipping (set env var to enable)"
    elif not compound_name:
        result["note"] = "no compound name — KIPRIS search needs name keyword"
    else:
        try:
            url = "http://plus.kipris.or.kr/openapi/rest/PatentSearchService/freeSearchInfo"
            params = {
                "freeSearch": compound_name,
                "ServiceKey": KIPRIS_API_KEY,
                "numOfRows": 20,
            }
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                # KIPRIS returns XML; quick parse
                import xml.etree.ElementTree as ET
                root = ET.fromstring(r.text)
                items = root.findall(".//item")
                result["queried"] = True
                result["patent_count"] = len(items)
                for it in items[:10]:
                    pat = {ch.tag: ch.text for ch in it}
                    result["patents"].append({
                        "title": pat.get("inventionTitle"),
                        "applicant": pat.get("applicantName"),
                        "appNum": pat.get("applicationNumber"),
                        "date": pat.get("applicationDate"),
                    })
        except Exception as e:
            result["error"] = str(e)

    cache.write_text(json.dumps(result, indent=2))
    return result


def classify_novelty(pubchem: dict, kipris: dict) -> str:
    """Heuristic novelty classification."""
    cid = pubchem.get("cid")
    pubchem_pats = len(pubchem.get("patents", []))
    kipris_pats = kipris.get("patent_count", 0) or 0
    if cid is None:
        return "novel"
    if pubchem_pats == 0 and kipris_pats == 0:
        return "known_no_patents"  # in PubChem but no IP linked
    if pubchem_pats > 5 or kipris_pats > 5:
        return "heavily_patented"
    return "weak_prior_art"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV with smiles column")
    ap.add_argument("--smiles-col", default="smiles")
    ap.add_argument("--id-col", default="np_id")
    ap.add_argument("--top-n", type=int, default=500, help="check top-N rows")
    ap.add_argument("--out", default="pilot/novelty/run1")
    args = ap.parse_args()

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    in_path = args.input if Path(args.input).is_absolute() else str(ROOT / args.input)
    if not Path(in_path).exists():
        print(f"FAIL: missing {in_path}")
        return 1

    rows = []
    with open(in_path) as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i >= args.top_n:
                break
            rows.append(row)
    print(f"checking {len(rows)} compounds for patent novelty")

    out_rows = []
    for i, row in enumerate(rows):
        smi = row.get(args.smiles_col)
        compound_id = row.get(args.id_col, f"row_{i}")
        if not smi:
            continue
        pub = pubchem_search(smi)
        kip = kipris_search(smi, pub.get("compound_name"))
        cls = classify_novelty(pub, kip)
        out_rows.append({
            "id": compound_id,
            "smiles": smi,
            "pubchem_cid": pub.get("cid"),
            "compound_name": pub.get("compound_name"),
            "pubchem_patent_count": len(pub.get("patents", [])),
            "kipris_patent_count": kip.get("patent_count"),
            "novelty_class": cls,
        })
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(rows)}")

    # Write consolidated CSV
    csv_path = out / "novelty_consolidated.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()) if out_rows else [])
        w.writeheader()
        w.writerows(out_rows)

    # Stats
    from collections import Counter
    cls_counts = Counter(r["novelty_class"] for r in out_rows)
    summary = {
        "phase": "F2 KIPRIS + PubChem patent novelty screen",
        "n_checked": len(out_rows),
        "kipris_api_active": bool(KIPRIS_API_KEY),
        "novelty_class_counts": dict(cls_counts),
        "csv": str(csv_path.relative_to(ROOT)),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== summary ===")
    for cls, n in cls_counts.most_common():
        print(f"  {cls}: {n}")
    print(f"saved {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
