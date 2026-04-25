"""BindingDB 결합 친화도 조회 (ChEMBL 보완).

BindingDB는 PDB 결합 데이터 + 일부 학술 데이터 통합. ChEMBL에 없는 entry 보완 가능.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "external_apis" / "bindingdb"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BDB_BASE = "https://bindingdb.org/rest"


def bindingdb_search(uniprot: str, smiles: str | None = None,
                     ic50_threshold_nm: float = 100_000.0) -> dict:
    """타겟 UniProt + 옵셔널 SMILES로 BindingDB 결합 조회.

    BindingDB REST는 단순한 GET API. UniProt → BDB target → ligands.
    """
    cache = CACHE_DIR / f"{uniprot}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    # Get ligands by UniProt
    url = f"{BDB_BASE}/getLigandsByUniprot"
    try:
        r = requests.get(url, params={
            "uniprot": uniprot,
            "cutoff": ic50_threshold_nm,
            "code": 0,    # 0=full, 1=summary
            "response": "application/xml",
        }, timeout=60)
        if r.status_code != 200:
            return {"uniprot": uniprot, "error": f"HTTP {r.status_code}",
                    "n_ligands": 0}
        root = ET.fromstring(r.text)
        # 간단 파싱 — 모든 affinity 추출
        affs = []
        for elem in root.iter():
            tag = elem.tag.split("}")[-1].lower()
            if tag in ("affinities", "affinity", "affinity_data"):
                for sub in elem:
                    text = sub.text
                    if text:
                        try:
                            v = float(text)
                            if 0 < v < ic50_threshold_nm:
                                affs.append(v)
                        except ValueError:
                            pass

        n_ligands_match = re.search(r'<NumLigands[^>]*>(\d+)', r.text)
        n_ligands = int(n_ligands_match.group(1)) if n_ligands_match else len(affs)

        result = {
            "uniprot": uniprot,
            "n_ligands": n_ligands,
            "n_affinities_under_threshold": len(affs),
            "best_ic50_nm": min(affs) if affs else None,
            "median_ic50_nm": sorted(affs)[len(affs)//2] if affs else None,
            "url": f"https://bindingdb.org/bind/searchby_uniprot.jsp?uniprot={uniprot}",
        }
        cache.write_text(json.dumps(result))
        return result
    except Exception as e:
        return {"uniprot": uniprot, "error": str(e), "n_ligands": 0}
