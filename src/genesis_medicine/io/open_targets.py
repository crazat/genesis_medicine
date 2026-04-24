"""Open Targets Platform GraphQL 클라이언트.

질병 EFO → 타겟 리스트 (association score + tractability + genetic evidence).
단순 문헌 빈도보다 훨씬 신뢰성 있는 baseline.
"""

from __future__ import annotations

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

OT_ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"

_QUERY = """
query TargetsByDisease($efoId: String!, $size: Int!) {
  disease(efoId: $efoId) {
    id
    name
    associatedTargets(page: { index: 0, size: $size }) {
      count
      rows {
        score
        datatypeScores { id score }
        target {
          id
          approvedSymbol
          approvedName
          proteinIds { id source }
          tractability { modality value }
        }
      }
    }
  }
}
"""


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=30))
def fetch_associated_targets(efo_id: str, size: int = 200) -> list[dict]:
    """Open Targets에서 질병과 연관된 타겟을 점수 순으로 반환."""
    r = requests.post(
        OT_ENDPOINT,
        json={"query": _QUERY, "variables": {"efoId": efo_id, "size": size}},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"Open Targets error: {data['errors']}")
    rows = data["data"]["disease"]["associatedTargets"]["rows"]
    logger.info(f"Open Targets: {len(rows)} targets for {efo_id}")
    return rows


def to_uniprot_list(rows: list[dict]) -> list[dict]:
    """GraphQL row → {uniprot, symbol, name, score, tractability} 목록."""
    out = []
    for row in rows:
        target = row["target"]
        uniprot = next(
            (p["id"] for p in target.get("proteinIds", []) if p.get("source") == "uniprot_swissprot"),
            None,
        )
        if not uniprot:
            continue
        tract = {t["modality"]: t["value"] for t in target.get("tractability", [])}
        out.append(
            {
                "uniprot": uniprot,
                "symbol": target["approvedSymbol"],
                "name": target["approvedName"],
                "score": row["score"],
                "tractability": tract,
            }
        )
    return out
