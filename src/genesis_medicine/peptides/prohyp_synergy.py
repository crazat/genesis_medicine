"""Pro-Hyp (Prolyl-hydroxyproline) bioactive peptide + Triple Combination.

PMC 7728856 + 2024 LC-MS/MS:
  Pro-Hyp = collagen-derived dipeptide
  - PEPT1 transporter → 장 흡수 → 혈액 → 피부 도달
  - Fibroblast 성장 자극 (위축성 흉터 회복 핵심)
  - Gly-Pro-Hyp tripeptide도 활성

Recover 한방 외용제 라인 (Triple combination):
  - Shikonin + EMB-3 (자운고 baseline + AI 강화)
  - + Pro-Hyp (collagen 합성 자극)
  → 위축성 + 비후성 흉터 동시 적응증

Dual-mechanism 가설:
  - Atrophic scar (papillary fibroblast 손상): Pro-Hyp + Asiaticoside
  - Hypertrophic scar (reticular over-active): EMB-3 + Embelin
  - Mixed: triple combination
"""

from __future__ import annotations

from dataclasses import dataclass


PROHYP_PEPTIDES = {
    "Pro-Hyp": {
        "smiles": "C1C[C@H](N(C1)C(=O)[C@@H]1CC[C@H](N1)O)C(=O)O",
        "mw": 230.22,
        "function": "fibroblast 성장 자극, collagen 합성",
        "evidence": "PMC 7728856 (Yamamoto 2020)",
    },
    "Gly-Pro-Hyp": {
        "smiles": "OC(=O)CNC(=O)C1CCC(O)N1C(=O)C(O)C1CCN1",  # 단순화
        "mw": 285.30,
        "function": "PEPT1 전달, 가장 활성 sequence",
        "evidence": "JAFC 2017",
    },
    "Hyp-Gly": {
        "smiles": "O[C@H]1CC(N)CN1C(=O)CN",
        "mw": 174.16,
        "function": "fibroblast 성장 (FBS-free 배양)",
    },
}


@dataclass
class TripleCombinationProfile:
    """Recover 흉터 외용제 triple combination."""

    name: str = ""
    components: dict = None       # {compound: percentage}
    target_indication: str = ""
    mechanism: list = None
    dual_action: bool = False


# Recover 표준 처방 (자운고 + EMB-3 + Pro-Hyp)
RECOVER_TRIPLE_FORMULATIONS = [
    TripleCombinationProfile(
        name="Recover Scar Triple Cream — Universal",
        components={
            "Shikonin": 20, "Acetylshikonin": 12,
            "EMB-3": 25, "Pro-Hyp": 8,
            "Vehicle (sesame oil + beeswax)": 35,
        },
        target_indication="흉터 일반 (위축성 + 비후성 + 켈로이드)",
        mechanism=[
            "shikonin 1,4-naphthoquinone — broad antimicrobial + anti-fibrotic",
            "EMB-3 small molecule — TGFB1/MMP1/CTGF/SMAD3/PDGFRB 5-tier 차단",
            "Pro-Hyp dipeptide — fibroblast 성장 자극 (collagen 합성)",
        ],
        dual_action=True,   # anti-fibrotic + pro-collagen
    ),
    TripleCombinationProfile(
        name="Recover Atrophic Cream — 위축성 우세",
        components={
            "Asiaticoside": 30, "Madecassoside": 15,
            "Pro-Hyp": 20, "EMB-3": 5,
            "Vehicle": 30,
        },
        target_indication="위축성 흉터, 여드름 흉터",
        mechanism=[
            "Asiaticoside + Madecassoside — 혈관 신생 (papillary fibroblast)",
            "Pro-Hyp — collagen 합성 자극 강함",
            "EMB-3 low-dose — anti-fibrotic minimal protection",
        ],
        dual_action=False,
    ),
    TripleCombinationProfile(
        name="Recover Hypertrophic Cream — 비후성 우세",
        components={
            "Shikonin": 25, "Acetylshikonin": 15,
            "EMB-3": 30, "Embelin": 5,
            "Pro-Hyp": 5, "Vehicle": 20,
        },
        target_indication="비후성 흉터, 켈로이드",
        mechanism=[
            "EMB-3 + Embelin — anti-fibrotic 강력 (Tier 1+2+3)",
            "shikonin/acetylshikonin — 한방 baseline",
            "Pro-Hyp low — papillary fibroblast 보호 (regenerative balance)",
        ],
        dual_action=True,
    ),
]


def predict_synergy_chou_talalay() -> dict:
    """Triple combination Chou-Talalay 시뮬 가설."""
    return {
        "design": (
            "5×5×5 dose matrix (EMB-3 × Shikonin × Pro-Hyp) "
            "in HSF (Human Skin Fibroblast)"
        ),
        "endpoint": "TGF-β1-induced collagen 1A1 expression (qPCR)",
        "expected_results": {
            "EMB-3 IC50 alone": "~5 µM (Boltz-2 0.749 → IC50 추정)",
            "Shikonin IC50 alone": "~3 µM (literature)",
            "Pro-Hyp EC50 (col1a1 합성)": "~50 µM",
            "Triple CI": "<0.4 (강한 시너지 가설)",
        },
        "korean_cro_quote": {
            "5×5×5 matrix HSF assay": "₩5M (3-4주, 300 wells)",
            "qPCR collagen 1A1, MMP1": "₩2M",
            "총": "₩7M",
        },
        "paper_value": (
            "Triple combination CI < 0.4 입증 시 → 'Korean medicine + AI + "
            "bioactive peptide triple synergy' Nat Comm 가능"
        ),
    }
