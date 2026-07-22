#!/usr/bin/env python
"""verify_panel_identity_pubchem.py — settle the 15-ligand panel's identity against a primary source.

WHY (2026-07-16). `data/chembl_mmp1_calibration.csv` annotates each of its 15 entries with a ChEMBL
identifier and a literature attribution ("prinomastat (AG3340); Shalinsky 1999", "Batimastat (BB-94);
Brown 1995", …). No script generates the file and it carries no retrieval record, so those annotations are
unverified. Two of them are load-bearing for paper_A v6's headline claim and are demonstrably wrong: the
structures filed under CHEMBL406 and CHEMBL98 are not indapamide and not vorinostat.

The obvious check — "does this SMILES match the named drug?" — is exactly where I went wrong once already
today: I compared against SMILES written from memory and concluded five labels were wrong, when in fact my
reference for marimastat was the wrong one. Memory is not a source. This script therefore asks a primary
database instead, and asks it by STRUCTURE, so no label can mediate the answer:

    panel SMILES --RDKit--> InChIKey --PubChem--> CID + registered synonyms

An InChIKey lookup is exact: PubChem returns the compound whose structure *is* that structure, and its
synonym list is what the world calls it. If the panel's own attribution appears in that list, the label is
corroborated; if the synonyms name a different drug, the label is refuted; if the key is unknown to
PubChem, we learn that too and claim nothing.

NOTE ON SCOPE. This resolves *identity* only. The panel's potency annotations (ic50_nm) cannot be checked
this way — that needs ChEMBL activity records, and the EBI API is unreachable from this host (status.json
times out; the webresource client fails on /spore with HTTP 500). Re-pulling potency remains open work.

PubChem asks for ≤5 requests/second; we stay well under.
"""
import csv
import json
import sys
import time
import urllib.parse

import requests
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors as rdMD

RDLogger.DisableLog("rdApp.*")

GM = "/home/crazat/genesis_medicine"
PANEL = f"{GM}/data/chembl_mmp1_calibration.WITHDRAWN.csv"  # renamed 2026-07-21; forensic tool reads it on purpose
OUT = f"{GM}/preprints/23_paper_A_v6_mmp1_5nnp_xtb/SI/panel_identity_pubchem_verification.csv"
BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
S = requests.Session()


def pubchem(path, timeout=25):
    try:
        r = S.get(f"{BASE}/{path}", timeout=timeout)
        return r.json() if r.ok else None
    except Exception:
        return None


def by_inchikey(key):
    """CID + synonyms + formula for an exact structure. Returns None if PubChem does not know it."""
    d = pubchem(f"compound/inchikey/{key}/property/MolecularFormula,IUPACName/JSON")
    if not d:
        return None
    props = d.get("PropertyTable", {}).get("Properties", [])
    if not props:
        return None
    cid = props[0].get("CID")
    time.sleep(0.25)
    syn = pubchem(f"compound/cid/{cid}/synonyms/JSON")
    names = []
    if syn:
        info = syn.get("InformationList", {}).get("Information", [])
        if info:
            names = info[0].get("Synonym", [])[:12]
    return {"cid": cid, "formula": props[0].get("MolecularFormula"),
            "iupac": props[0].get("IUPACName"), "synonyms": names}


def claimed_name(reference, notes):
    """the drug name the CSV claims, e.g. 'prinomastat (AG3340); Shalinsky 1999' -> 'prinomastat'"""
    head = reference.split(";")[0].split("(")[0].strip()
    return head


def main():
    rows = list(csv.DictReader(open(PANEL)))
    out = []
    print("=" * 108)
    print(f"15-ligand panel identity — structure-first lookup against PubChem   (source: {PANEL.split('/')[-1]})")
    print("=" * 108)
    print(f"{'chembl_id':<14}{'claimed label':<22}{'formula':<16}{'PubChem CID':<12}{'PubChem says it is':<28}verdict")
    print("-" * 108)
    for r in rows:
        m = Chem.MolFromSmiles(r["smiles"])
        if m is None:
            print(f"{r['chembl_id']:<14}{'':<22}{'UNPARSEABLE':<16}")
            continue
        key = Chem.MolToInchiKey(m)
        formula = rdMD.CalcMolFormula(m)
        claim = claimed_name(r.get("reference", ""), r.get("notes", ""))
        info = by_inchikey(key)
        time.sleep(0.25)

        if not info:
            says, verdict, cid = "(structure unknown to PubChem)", "UNRESOLVED", ""
        else:
            cid = info["cid"]
            syns = [s.lower() for s in info["synonyms"]]
            says = (info["synonyms"][0] if info["synonyms"] else "(no synonym)")[:26]
            hit = claim and any(claim.lower() in s for s in syns)
            verdict = "LABEL CONFIRMED" if hit else "LABEL NOT CORROBORATED"
        print(f"{r['chembl_id']:<14}{claim[:20]:<22}{formula:<16}{str(cid):<12}{says:<28}{verdict}")
        out.append({"chembl_id": r["chembl_id"], "claimed_label": claim, "formula": formula,
                    "inchikey": key, "pubchem_cid": cid,
                    "pubchem_top_synonym": (info["synonyms"][0] if info and info["synonyms"] else ""),
                    "pubchem_synonyms": "|".join(info["synonyms"]) if info else "",
                    "verdict": verdict, "ic50_nm_claimed": r.get("ic50_nm", "")})

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    n_ok = sum(1 for d in out if d["verdict"] == "LABEL CONFIRMED")
    n_no = sum(1 for d in out if d["verdict"] == "LABEL NOT CORROBORATED")
    n_un = sum(1 for d in out if d["verdict"] == "UNRESOLVED")
    print("-" * 108)
    print(f"  confirmed {n_ok} / not corroborated {n_no} / unresolved {n_un}   (of {len(out)})")
    print(f"  -> {OUT}")
    print("\n  Identity only. Potency (ic50_nm) is NOT checked here and remains unverified: it needs ChEMBL")
    print("  activity records, and the EBI API is unreachable from this host.")


if __name__ == "__main__":
    main()
