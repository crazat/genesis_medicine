"""GTEx tissue expression 자동 조회.

각 타겟이 실제 피부 조직에서 발현되는지 검증. paper의 강력한 지원 데이터.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

CACHE_DIR = Path.home() / "genesis_medicine" / ".cache" / "external_apis" / "gtex"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# GTEx tissue codes 일부
SKIN_TISSUES = [
    "Skin_Sun_Exposed_Lower_leg",
    "Skin_Not_Sun_Exposed_Suprapubic",
]


def _resolve_gencode_id(gene_symbol: str) -> str | None:
    """Gene symbol → GENCODE ID (versioned)."""
    cache = CACHE_DIR / f"gencode_{gene_symbol}.json"
    if cache.exists():
        return json.loads(cache.read_text()).get("gencodeId")
    try:
        r = requests.get(
            "https://gtexportal.org/api/v2/reference/gene",
            params={"geneId": gene_symbol}, timeout=30,
        )
        r.raise_for_status()
        rows = r.json().get("data", [])
        gid = rows[0]["gencodeId"] if rows else None
        cache.write_text(json.dumps({"gencodeId": gid}))
        return gid
    except Exception:
        return None


def gtex_tissue_distribution(gene_symbol: str) -> dict:
    """GTEx에서 해당 gene의 모든 조직 median TPM."""
    cache = CACHE_DIR / f"tissue_{gene_symbol}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    gid = _resolve_gencode_id(gene_symbol)
    if not gid:
        return {"gene": gene_symbol, "error": "gencodeId not found"}

    url = "https://gtexportal.org/api/v2/expression/medianGeneExpression"
    try:
        r = requests.get(url, params={
            "gencodeId": gid,
            "format": "json",
        }, timeout=30)
        if r.status_code != 200:
            return {"gene": gene_symbol, "error": f"HTTP {r.status_code}"}
        data = r.json()
        records = data.get("data", [])
        result = {
            "gene": gene_symbol,
            "gencodeId": gid,
            "n_tissues": len(records),
            "by_tissue": {
                rec.get("tissueSiteDetailId", "?"): float(rec.get("median", 0))
                for rec in records
            },
        }
        cache.write_text(json.dumps(result))
        return result
    except Exception as e:
        return {"gene": gene_symbol, "error": str(e)}


def gtex_skin_expression(gene_symbol: str) -> dict:
    """피부 조직 expression만 추출 + 다른 조직 대비 순위."""
    full = gtex_tissue_distribution(gene_symbol)
    if "error" in full:
        return full
    by_tissue = full.get("by_tissue", {})
    skin_vals = {t: by_tissue.get(t, 0.0) for t in SKIN_TISSUES}
    skin_max = max(skin_vals.values()) if skin_vals else 0.0

    # 모든 조직 sorted, skin 순위
    sorted_tissues = sorted(by_tissue.items(), key=lambda x: -x[1])
    skin_ranks = {}
    for t in SKIN_TISSUES:
        for i, (tname, _) in enumerate(sorted_tissues, 1):
            if tname == t:
                skin_ranks[t] = i
                break

    return {
        "gene": gene_symbol,
        "skin_tpm_max": skin_max,
        "skin_tpm_by_tissue": skin_vals,
        "skin_rank_among_all": skin_ranks,
        "n_tissues_total": len(by_tissue),
        "interpretation": _interpret(skin_max, skin_ranks),
    }


def _interpret(skin_tpm: float, ranks: dict) -> str:
    if skin_tpm == 0:
        return "❌ 발현 없음 — 피부 타겟으로 부적합"
    if skin_tpm < 1:
        return "⚠️ 매우 낮은 발현 (TPM < 1)"
    if skin_tpm < 10:
        return "🟡 낮은-중간 발현 (TPM < 10)"
    rank_min = min(ranks.values()) if ranks else 999
    if rank_min <= 5:
        return "🟢 피부 매우 높은 발현 (top 5 tissue)"
    if rank_min <= 15:
        return "🟢 피부 높은 발현 (top 15)"
    return "🟢 적정 피부 발현"


def batch_skin_validation(gene_symbols: list[str]) -> dict:
    """여러 타겟의 피부 발현 일괄 검증."""
    results = {}
    for g in gene_symbols:
        results[g] = gtex_skin_expression(g)
    return results
