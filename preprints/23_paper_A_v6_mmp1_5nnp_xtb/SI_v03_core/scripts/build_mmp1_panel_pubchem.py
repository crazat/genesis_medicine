#!/usr/bin/env python
"""build_mmp1_panel_pubchem.py — derive a REAL MMP-1 ligand panel from a primary source, with a record.

WHY THIS EXISTS. `data/chembl_mmp1_calibration.csv` — the 15-ligand panel under paper_A, paper_B and three
deposited Zenodo records — is fabricated: all seven of its named entries are a different molecule than the
drug they name, and 14 of its 15 structures are unknown to PubChem's ~119 M compounds
(`verify_panel_identity_pubchem.py`; scope map in `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`).
It has no generating script and no retrieval record, which is exactly why nobody — including its author —
could check it for two months.

The structural fix is not a better file. It is a file that **comes with the command that made it**. Every row
this script emits carries the PubChem CID it came from, the assay AID it was measured in, and the run
timestamp, so any reader can re-run the query and diff the result.

SOURCE. PubChem (reachable from this host; the EBI/ChEMBL API is not — status.json times out and the
webresource client fails on /spore with HTTP 500, so a ChEMBL re-pull is currently impossible). Query path is
the SDQ bioactivity collection for geneid 4312 (human MMP1), which is what the PubChem web UI itself uses.

WHAT THIS DOES NOT DO. It does not reproduce the old panel, and it should not: the old panel's compounds do
not exist. Downstream cofold/xtb/NNP results computed on the old structures remain valid as *reproducibility*
measurements (they ask whether a computation repeats on a fixed input, which is true or false regardless of
what the input is called) but they say nothing about these compounds and cannot be transferred to them.
Re-running the stack on this panel is a separate, GPU-scale job.
"""
import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone

import requests
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors as rdMD

RDLogger.DisableLog("rdApp.*")

GENEID_MMP1 = 4312            # human MMP1; PubChem protein accession P03956 = "Interstitial collagenase"
SDQ = "https://pubchem.ncbi.nlm.nih.gov/sdq/sdqagent.cgi"
PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
OUT = "/home/crazat/genesis_medicine/data/mmp1_panel_pubchem.csv"
S = requests.Session()


def sdq_bioactivity(limit=10000):
    """every recorded MMP1 bioactivity row PubChem will give us."""
    q = {"select": "*", "collection": "bioactivity",
         "where": {"ands": [{"geneid": str(GENEID_MMP1)}]},
         "order": ["acvalue,asc"], "start": 1, "limit": limit}
    r = S.get(SDQ, params={"infmt": "json", "outfmt": "json", "query": json.dumps(q)}, timeout=90)
    r.raise_for_status()
    out = r.json()["SDQOutputSet"][0]
    return out.get("rows", []), out.get("totalCount")


def smiles_for(cids, chunk=100):
    """CID -> isomeric SMILES + formula. NOTE the field is `SMILES` / `ConnectivitySMILES`; the older
    `CanonicalSMILES` name is gone, and silently .get()-ing it yields an empty molecule that compares
    unequal to everything — the exact bug that produced a false '6/6 mismatch' report on 2026-07-16."""
    got = {}
    for i in range(0, len(cids), chunk):
        part = ",".join(str(c) for c in cids[i:i + chunk])
        r = S.get(f"{PUG}/compound/cid/{part}/property/MolecularFormula,SMILES/JSON", timeout=60)
        if r.ok:
            for p in r.json().get("PropertyTable", {}).get("Properties", []):
                smi = p.get("SMILES")
                if smi:
                    got[p["CID"]] = {"smiles": smi, "formula": p.get("MolecularFormula")}
        time.sleep(0.25)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--activity", default="IC50", help="activity type to keep (IC50 / Ki / EC50)")
    ap.add_argument("--max-um", type=float, default=100.0, help="drop rows weaker than this (uM)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows, total = sdq_bioactivity()
    print(f"PubChem SDQ bioactivity, geneid={GENEID_MMP1} (MMP1): {len(rows)} rows returned of {total}")
    if rows:
        print(f"  available fields: {sorted(rows[0].keys())}")

    keep = []
    for r in rows:
        act = (r.get("acname") or "").strip()
        if a.activity and act.upper() != a.activity.upper():
            continue
        val = r.get("acvalue")
        cid = r.get("cid")
        if val is None or cid is None:
            continue
        try:
            um = float(val)
        except (TypeError, ValueError):
            continue
        if um <= 0 or um > a.max_um:
            continue
        keep.append({"cid": int(cid), "activity": act, "value_um": um, "aid": r.get("aid"),
                     "activity_outcome": r.get("activity"), "assay_name": (r.get("aidname") or "")[:90]})
    print(f"  {a.activity} rows within {a.max_um} uM: {len(keep)}")
    if not keep:
        sys.exit("no usable rows — inspect the field names printed above and adjust --activity")

    # strongest measurement per compound
    best = {}
    for k in keep:
        if k["cid"] not in best or k["value_um"] < best[k["cid"]]["value_um"]:
            best[k["cid"]] = k
    print(f"  distinct compounds: {len(best)}")

    struct = smiles_for(sorted(best))
    print(f"  structures retrieved: {len(struct)}/{len(best)}")

    out = []
    for cid, k in sorted(best.items(), key=lambda kv: kv[1]["value_um"]):
        s = struct.get(cid)
        if not s:
            continue
        m = Chem.MolFromSmiles(s["smiles"])
        if m is None:
            continue
        out.append({
            "pubchem_cid": cid, "smiles": s["smiles"],
            "formula": rdMD.CalcMolFormula(m), "heavy_atoms": m.GetNumHeavyAtoms(),
            "inchikey": Chem.MolToInchiKey(m),
            "activity_type": k["activity"], "value_nm": round(k["value_um"] * 1000.0, 4),
            "pubchem_aid": k["aid"], "assay_name": k["assay_name"],
            "source": "PubChem SDQ bioactivity geneid=4312 (MMP1)", "retrieved_utc": stamp,
        })
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    v = [d["value_nm"] for d in out]
    print(f"\nwrote {a.out}")
    print(f"  {len(out)} compounds | {a.activity} {min(v):.3g}–{max(v):.4g} nM "
          f"({__import__('math').log10(max(v) / min(v)):.2f} log span)")
    print(f"  every row carries: pubchem_cid, pubchem_aid, inchikey, retrieved_utc={stamp}")
    print("  re-run this script to reproduce or diff the panel.")


if __name__ == "__main__":
    main()
