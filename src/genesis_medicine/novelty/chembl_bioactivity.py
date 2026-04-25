"""ChEMBL bioactivity REST 조회.

화합물의 알려진 IC50/Ki/Kd를 조회. 만약 우리 타겟에 대한 활성이 이미 보고되어 있다면
해당 발견은 "novel"이 아님.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import NoveltyContext, PriorArtRecord

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "novelty"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _chembl_search_compound(name: str) -> str | None:
    """이름으로 ChEMBL ID 검색."""
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule/search"
    params = {"q": name, "format": "json", "limit": 1}
    r = requests.get(url, params=params, timeout=20)
    if r.status_code != 200:
        return None
    j = r.json()
    mols = j.get("molecules", [])
    if not mols:
        return None
    return mols[0].get("molecule_chembl_id")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _chembl_target_chembl_id(uniprot: str) -> str | None:
    """UniProt → ChEMBL target ID."""
    url = "https://www.ebi.ac.uk/chembl/api/data/target.json"
    params = {"target_components__accession": uniprot, "limit": 1}
    r = requests.get(url, params=params, timeout=20)
    if r.status_code != 200:
        return None
    j = r.json()
    targets = j.get("targets", [])
    if not targets:
        return None
    return targets[0].get("target_chembl_id")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _chembl_activities(mol_id: str, target_id: str) -> list[dict]:
    url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    params = {
        "molecule_chembl_id": mol_id,
        "target_chembl_id": target_id,
        "limit": 50,
    }
    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        return []
    return r.json().get("activities", [])


def chembl_known_activities(ctx: NoveltyContext) -> PriorArtRecord:
    """ChEMBL에서 (compound, target) 알려진 활성 조회."""
    if not ctx.target_uniprot:
        return PriorArtRecord(source="chembl", n_hits=0,
                              notable_finding="target uniprot not provided")

    cache = CACHE_DIR / (
        f"chembl_{ctx.compound_name.lower().replace(' ','_')}_"
        f"{ctx.target_uniprot}.json"
    )
    if cache.exists():
        d = json.loads(cache.read_text())
        return PriorArtRecord(**d)

    try:
        mol_id = _chembl_search_compound(ctx.compound_name)
        if not mol_id:
            rec = PriorArtRecord(source="chembl", n_hits=0,
                                 notable_finding=f"화합물 '{ctx.compound_name}' ChEMBL 미등록")
            cache.write_text(json.dumps(rec.__dict__, default=list))
            return rec

        target_id = _chembl_target_chembl_id(ctx.target_uniprot)
        if not target_id:
            rec = PriorArtRecord(source="chembl", n_hits=0,
                                 notable_finding=f"타겟 {ctx.target_uniprot} ChEMBL 미등록")
            cache.write_text(json.dumps(rec.__dict__, default=list))
            return rec

        acts = _chembl_activities(mol_id, target_id)
        n = len(acts)
        # 가장 강한 활성 추출
        notable = None
        if acts:
            ic50s = [a for a in acts if a.get("standard_type") in ("IC50", "Ki", "Kd")
                     and a.get("standard_value")]
            if ic50s:
                # 작은 값(강한 결합) 우선
                best = min(ic50s, key=lambda a: float(a.get("standard_value") or 1e9))
                v = best.get("standard_value")
                u = best.get("standard_units", "nM")
                t = best.get("standard_type")
                notable = f"Reported {t}={v} {u} (ChEMBL {best.get('activity_id')})"

        rec = PriorArtRecord(
            source="chembl",
            n_hits=n,
            notable_finding=notable,
            raw_url=f"https://www.ebi.ac.uk/chembl/g/#search_results/all/query={mol_id}%20{target_id}",
        )
        cache.write_text(json.dumps(rec.__dict__, default=list))
        return rec
    except Exception as e:
        return PriorArtRecord(source="chembl", n_hits=-1,
                              notable_finding=f"error: {e}")
