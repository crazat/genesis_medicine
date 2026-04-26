"""T10-3 Knowledge Graph Completion — PrimeKG + BioPathNet pattern.

근거: PrimeKG 2024 (17,080 diseases × 4M relationships, Harvard).
BioPathNet (NBFNet path reasoning) link prediction AUPRC 0.83.

설계: 외부 KG 호출 비용·복잡 → 우리는 **internal sub-KG**를 직접 구축.
EMB-3 lead의 fibrotic master switch + IPF cross-disease 기록을
TGFB1/MMP1/CTGF/SMAD3 등 노드로 그래프화. 자연어 query로 path 추론.

자연어 호출:
  "EMB-3 → TGFB1 → IPF 경로"
  "흉터 ↔ IPF 공유 타겟"
  → kg_path_query()
"""

from __future__ import annotations

from dataclasses import dataclass, field


# 내부 sub-KG (Genesis_Medicine 검증 결과 + Open Targets cross-disease)
INTERNAL_KG = {
    "compounds": {
        "EMB-3": {"smiles": "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
                   "scaffold_class": "1,4-benzoquinone",
                   "binds_targets": ["TGFB1", "MMP1", "CTGF", "SMAD3",
                                      "PDGFRB", "LOX"],
                   "selectivity_negatives": ["FGF2"],
                   "verified_assays": ["ABFE", "MD-10ns", "Boltz-2"]},
        "Embelin": {"smiles": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
                     "scaffold_class": "1,4-benzoquinone (parent)",
                     "binds_targets": ["TGFB1", "MMP1", "CTGF", "SMAD3"]},
        "EGCG": {"smiles": "OC1=CC(O)=CC(C2OC3=C(C(O)=O)C(O)=C(O)C(O)=C3C2)=C1",
                  "scaffold_class": "catechin",
                  "binds_targets": ["MMP1", "MMP9", "tyrosinase"]},
        "Asiaticoside": {"scaffold_class": "triterpenoid saponin",
                          "binds_targets": ["TGFB1", "COL1A1"]},
        "Shikonin": {"scaffold_class": "1,4-naphthoquinone",
                      "binds_targets": ["TGFB1", "MMP1"]},
    },
    "targets": {
        "TGFB1": {"uniprot": "P01137", "pathway": "TGF-β signaling",
                   "diseases": ["scar", "IPF", "scleroderma", "atopic"]},
        "MMP1": {"uniprot": "P03956", "pathway": "ECM remodeling",
                  "diseases": ["scar", "wrinkle", "photoaging"]},
        "CTGF": {"uniprot": "P29279", "pathway": "fibrosis",
                  "diseases": ["scar", "IPF", "renal_fibrosis"]},
        "SMAD3": {"uniprot": "P84022", "pathway": "TGF-β signaling",
                   "diseases": ["scar", "IPF"]},
        "PDGFRB": {"uniprot": "P09619", "pathway": "myofibroblast",
                    "diseases": ["IPF", "scleroderma"]},
        "LOX": {"uniprot": "P28300", "pathway": "collagen crosslink",
                "diseases": ["scar", "scleroderma"]},
    },
    "diseases": {
        "scar": {"icd10": "L91", "fibroblast_subtypes": ["papillary",
                                                          "reticular"]},
        "IPF": {"icd10": "J84.112", "orphan_drug": True,
                 "market_usd": 5_000_000_000},
        "scleroderma": {"icd10": "M34", "orphan_drug": True},
        "atopic": {"icd10": "L20"},
    },
}


@dataclass
class KGPath:
    """그래프 path 추론 결과."""

    start: str
    end: str
    path: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    confidence: float = 0.0
    natural_explanation: str = ""


def kg_path_query(start: str, end: str) -> KGPath:
    """A → B path 추론 (단순 BFS, 우리 sub-KG 한정)."""
    visited = {start}
    queue = [(start, [start], [])]
    while queue:
        node, path, edges = queue.pop(0)
        if node == end:
            return KGPath(
                start=start, end=end, path=path, edges=edges,
                confidence=min(1.0, 1.0 / len(path)),
                natural_explanation=(
                    f"{start} → {end}: {' → '.join(path)} "
                    f"(거리 {len(path)-1}, 신뢰도 {1.0/len(path):.2f})"
                ),
            )
        # 1) compound → target
        if node in INTERNAL_KG["compounds"]:
            for tgt in INTERNAL_KG["compounds"][node].get("binds_targets", []):
                if tgt not in visited:
                    visited.add(tgt)
                    queue.append((tgt, path + [tgt],
                                   edges + [(node, "binds", tgt)]))
        # 2) target → disease
        if node in INTERNAL_KG["targets"]:
            for d in INTERNAL_KG["targets"][node].get("diseases", []):
                if d not in visited:
                    visited.add(d)
                    queue.append((d, path + [d],
                                   edges + [(node, "implicated_in", d)]))
        # 3) disease → target (역방향)
        if node in INTERNAL_KG["diseases"]:
            for t, info in INTERNAL_KG["targets"].items():
                if node in info.get("diseases", []) and t not in visited:
                    visited.add(t)
                    queue.append((t, path + [t],
                                   edges + [(node, "involves", t)]))
    return KGPath(
        start=start, end=end, path=[], confidence=0.0,
        natural_explanation=f"{start} → {end} 경로 없음 (sub-KG 한정)",
    )


def shared_targets(disease_a: str, disease_b: str) -> dict:
    """두 질환 공유 타겟 — cross-disease 분자 기반."""
    targets_a = {t for t, info in INTERNAL_KG["targets"].items()
                  if disease_a in info.get("diseases", [])}
    targets_b = {t for t, info in INTERNAL_KG["targets"].items()
                  if disease_b in info.get("diseases", [])}
    shared = sorted(targets_a & targets_b)
    return {
        "tool": "shared_targets",
        "disease_a": disease_a, "disease_b": disease_b,
        "shared_targets": shared,
        "n_shared": len(shared),
        "natural_summary": (
            f"{disease_a} ↔ {disease_b} 공유 타겟 {len(shared)}개: "
            f"{', '.join(shared)}"
        ),
    }


def predict_repurposing_candidates(disease: str, top_k: int = 5) -> dict:
    """질환 → 화합물 예측 — 우리 sub-KG에서 binding 화합물 ranking."""
    targets = {t for t, info in INTERNAL_KG["targets"].items()
                if disease in info.get("diseases", [])}
    scores = []
    for cname, cinfo in INTERNAL_KG["compounds"].items():
        binds = set(cinfo.get("binds_targets", []))
        coverage = len(binds & targets) / max(1, len(targets))
        scores.append((cname, coverage, sorted(binds & targets)))
    scores.sort(key=lambda x: x[1], reverse=True)
    return {
        "tool": "predict_repurposing_candidates",
        "disease": disease, "n_targets": len(targets),
        "candidates": [
            {"compound": n, "coverage": round(c, 3), "matched_targets": m}
            for n, c, m in scores[:top_k]
        ],
        "natural_summary": (
            f"{disease} 재창출 1순위: {scores[0][0]} "
            f"(coverage {scores[0][1]:.1%})"
        ),
    }
