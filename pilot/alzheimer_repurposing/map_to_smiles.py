"""TxGNN Top 20 후보 → PubChem로 SMILES 변환.

메인 Alzheimer disease idx=1510의 Ranked List에서 상위 20개 약물 이름을 받아
PubChem REST API로 SMILES 검색.
"""

from __future__ import annotations

import pickle
import sys
import time
from pathlib import Path

import pandas as pd
import requests

BASE = Path(__file__).parent
RESULT = BASE / "results"
CACHE = Path.home() / "genesis_medicine" / ".cache" / "pubchem_smiles"
CACHE.mkdir(parents=True, exist_ok=True)


def pubchem_smiles(name: str, timeout: float = 20.0) -> dict | None:
    """PubChem REST API — 이름으로 SMILES + CID + 분자량 조회."""
    cache_file = CACHE / f"{name.replace('/', '_').replace(' ', '_')}.json"
    if cache_file.exists():
        import json
        return json.loads(cache_file.read_text())

    # PubChem 2025+: CanonicalSMILES → SMILES / IsomericSMILES로 이름 변경
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/SMILES,IsomericSMILES,MolecularWeight,IUPACName/JSON"
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            j = r.json()
            props = j["PropertyTable"]["Properties"][0]
            data = {
                "name": name,
                "cid": props.get("CID"),
                "smiles": props.get("IsomericSMILES") or props.get("SMILES"),
                "mw": props.get("MolecularWeight"),
                "iupac": props.get("IUPACName"),
            }
            import json
            cache_file.write_text(json.dumps(data))
            return data
        return None
    except Exception as e:
        print(f"  [{name}] error: {e}")
        return None


def main() -> int:
    data = pickle.loads((RESULT / "alzheimer_indication_raw.pkl").read_bytes())
    result = data["result"]
    name_map = result["Name"]

    # 메인 "Alzheimer disease" 키 찾기
    alz_key = [k for k, v in name_map.items() if v == "Alzheimer disease"][0]
    ranked = result["Ranked List"][alz_key]
    print(f"메인 Alzheimer disease: {len(ranked)} 약물 랭킹")

    top_n = 20
    top_list = ranked[:top_n]
    print(f"\n=== Top {top_n} PubChem 검색 ===")

    rows = []
    for rank, drug in enumerate(top_list, 1):
        t0 = time.time()
        info = pubchem_smiles(drug)
        status = "✅" if info and info.get("smiles") else "❌"
        row = {
            "rank": rank,
            "drug_name": drug,
            "cid": info.get("cid") if info else None,
            "smiles": info.get("smiles") if info else None,
            "mw": info.get("mw") if info else None,
            "status": status,
        }
        rows.append(row)
        smi_short = (row["smiles"] or "")[:50] if row["smiles"] else "—"
        print(f"  {status} {rank:2d}. {drug:40s} CID={row['cid']}  SMILES[{smi_short}]  ({time.time()-t0:.1f}s)")
        time.sleep(0.25)  # PubChem rate limit

    df = pd.DataFrame(rows)
    out = RESULT / "top20_smiles.csv"
    df.to_csv(out, index=False)

    hits = df["smiles"].notna().sum()
    print(f"\n✅ {hits}/{top_n} SMILES 확보 → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
