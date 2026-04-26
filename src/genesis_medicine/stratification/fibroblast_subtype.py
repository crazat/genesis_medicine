"""Papillary vs Reticular fibroblast 환자 stratification.

Frontiers Pharmacol 2025 + IJMS 2026 후속:
  - Papillary fibroblast (얕은 진피): 모낭/혈관 활성, COL6A5/PDPN/CCL19 marker
    → 위축성 흉터·광노화·탈모에 우세
  - Reticular fibroblast (깊은 진피): ECM 생산·fibrosis 주도, MGP/IGFBP3 marker
    → 비후성 흉터·켈로이드·IPF에 우세
  - Aging: papillary "priming" 감소, reticular ECM imbalance 증가

Recover 한의원 처방 매핑:
  - 위축성 흉터 (papillary 손상) → Asiaticoside (혈관 신생) + 당귀
  - 비후성 흉터 (reticular 과활성) → EMB-3 + Embelin (anti-fibrotic)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Marker genes from Nat Immunol 2025 + Frontiers 2025
PAPILLARY_MARKERS = ["COL6A5", "PDPN", "CCL19", "WIF1", "PRSS23",
                      "WNT5A", "F13A1"]
RETICULAR_MARKERS = ["MGP", "IGFBP3", "TAGLN", "ACTA2", "POSTN",
                      "COL1A1", "COL3A1", "FBLN1", "FN1"]


@dataclass
class FibroblastSubtypeProfile:
    """환자별 fibroblast subtype 추정."""

    patient_id: str = ""
    papillary_score: float = 0.0     # 0-1
    reticular_score: float = 0.0
    dominant_subtype: str = ""       # papillary | reticular | balanced
    aging_signature: float = 0.0     # 0=young, 1=aged
    recommended_compounds: list = field(default_factory=list)
    recommended_prescriptions: list = field(default_factory=list)


def classify_from_markers(marker_expression: dict[str, float],
                            patient_id: str = "") -> FibroblastSubtypeProfile:
    """marker gene expression 평균 → subtype 판정.

    Args:
        marker_expression: {gene_symbol: expression_zscore} 또는 normalized count
    """
    pap_vals = [marker_expression.get(g, 0.0) for g in PAPILLARY_MARKERS]
    ret_vals = [marker_expression.get(g, 0.0) for g in RETICULAR_MARKERS]
    pap_score = sum(pap_vals) / len(pap_vals) if pap_vals else 0
    ret_score = sum(ret_vals) / len(ret_vals) if ret_vals else 0

    # normalize 0-1 (가정: zscore -2~2)
    pap_norm = max(0, min(1, (pap_score + 2) / 4))
    ret_norm = max(0, min(1, (ret_score + 2) / 4))

    if pap_norm - ret_norm > 0.15:
        dominant = "papillary"
        compounds = ["Asiaticoside (CD31 + 혈관)", "Madecassoside",
                      "Ferulic acid (당귀)", "EGCG"]
        rxs = ["당귀음자 (혈허)", "센텔라 외용 (Madecassol)", "녹차 외용"]
    elif ret_norm - pap_norm > 0.15:
        dominant = "reticular"
        compounds = ["EMB-3 (anti-fibrotic)", "Embelin", "Tanshinone IIA",
                      "Shikonin"]
        rxs = ["자운고 + EMB-3 강화", "활혈거어탕", "단삼 외용"]
    else:
        dominant = "balanced"
        compounds = ["EGCG (universal)", "Asiaticoside + EMB-3 균형"]
        rxs = ["자운고 + 당귀음자 복합"]

    return FibroblastSubtypeProfile(
        patient_id=patient_id,
        papillary_score=float(pap_norm), reticular_score=float(ret_norm),
        dominant_subtype=dominant,
        recommended_compounds=compounds,
        recommended_prescriptions=rxs,
    )


def stratify_recover_patient_cohort(n_patients: int = 100, seed: int = 42):
    """가상 환자 코호트 stratification — Recover 환자 분포 시뮬."""
    import numpy as np
    rng = np.random.RandomState(seed)
    cohort = []
    for i in range(n_patients):
        # 각 marker random expression
        markers = {}
        # 위축성 흉터 (40%): papillary 우세
        # 비후성 흉터 (35%): reticular 우세
        # 균형 (25%)
        cls = rng.choice(["atrophic", "hypertrophic", "balanced"],
                          p=[0.4, 0.35, 0.25])
        for g in PAPILLARY_MARKERS:
            base = 1.0 if cls == "atrophic" else (-0.5 if cls == "hypertrophic" else 0.0)
            markers[g] = base + rng.normal(0, 0.5)
        for g in RETICULAR_MARKERS:
            base = -0.5 if cls == "atrophic" else (1.0 if cls == "hypertrophic" else 0.0)
            markers[g] = base + rng.normal(0, 0.5)
        profile = classify_from_markers(markers, patient_id=f"P{i:03d}")
        cohort.append({
            "patient_id": profile.patient_id,
            "true_class": cls,
            "predicted_subtype": profile.dominant_subtype,
            "papillary_score": round(profile.papillary_score, 2),
            "reticular_score": round(profile.reticular_score, 2),
            "primary_rx": profile.recommended_prescriptions[0]
                            if profile.recommended_prescriptions else "—",
        })
    return cohort
