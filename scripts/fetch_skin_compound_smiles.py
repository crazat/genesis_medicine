"""data/skin_compounds_seed.csv → PubChem CID 기반 SMILES 채워서 curated.csv 생성.

Genesis_Medicine v3 — 피부 재생 핵심 라이브러리.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

DATA = Path(__file__).resolve().parents[1] / "data"
CACHE = Path.home() / "genesis_medicine" / ".cache" / "pubchem_smiles"
CACHE.mkdir(parents=True, exist_ok=True)


def fetch_by_cid(cid: int, timeout: float = 20.0) -> dict | None:
    cache_file = CACHE / f"cid_{cid}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/"
        "SMILES,IsomericSMILES,MolecularWeight,XLogP,HBondDonorCount,HBondAcceptorCount,"
        "TPSA,RotatableBondCount,IUPACName/JSON"
    )
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            props = r.json()["PropertyTable"]["Properties"][0]
            cache_file.write_text(json.dumps(props))
            return props
    except Exception as e:
        print(f"  [CID {cid}] {e}")
    return None


def main() -> int:
    seed = pd.read_csv(DATA / "skin_compounds_seed.csv")
    print(f"=== {len(seed)}개 천연물 PubChem SMILES 채우기 ===")

    rows = []
    for _, r in seed.iterrows():
        cid = r.get("cid")
        if pd.notna(cid):
            data = fetch_by_cid(int(cid))
        else:
            data = None
        smi = (data or {}).get("IsomericSMILES") or (data or {}).get("SMILES")
        rows.append({
            "name": r["name"],
            "source_botanical": r["source_botanical"],
            "source_korean": r["source_korean"],
            "cid": cid,
            "smiles": smi,
            "mw": (data or {}).get("MolecularWeight"),
            "logp": (data or {}).get("XLogP"),
            "hbd": (data or {}).get("HBondDonorCount"),
            "hba": (data or {}).get("HBondAcceptorCount"),
            "tpsa": (data or {}).get("TPSA"),
            "rotbonds": (data or {}).get("RotatableBondCount"),
            "category": r["category"],
            "target_hint": r.get("target_hint"),
            "evidence_level": r["evidence_level"],
            "khp_listed": r.get("khp_listed", "no"),
            "notes": r.get("notes", ""),
        })
        print(f"  {'✅' if smi else '❌'} {r['name']:35s} CID={cid}  MW={(data or {}).get('MolecularWeight','-')}")
        time.sleep(0.2)

    out = pd.DataFrame(rows)
    out.to_csv(DATA / "skin_compounds_curated.csv", index=False)
    n_ok = out["smiles"].notna().sum()
    print(f"\n✅ {n_ok}/{len(out)} SMILES 확보 → data/skin_compounds_curated.csv")

    # Lipinski 호환 통계
    lipinski_ok = (
        (out["mw"].astype(float) <= 500) & (out["logp"].astype(float) <= 5) &
        (out["hbd"].astype(float) <= 5) & (out["hba"].astype(float) <= 10)
    ).sum()
    print(f"   Lipinski Rule-of-5 통과: {lipinski_ok}/{n_ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
