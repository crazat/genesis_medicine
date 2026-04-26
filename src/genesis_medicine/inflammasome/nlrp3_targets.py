"""NLRP3 inflammasome — IPF + acne 공통 fibrotic + inflammatory driver.

Springer Cell Biochem 2025 (Flavonoid NLRP3 IPF) +
PMC 9263782 (NLRP3 acne narrative review) + Nat Sci Rep 2023 (JT002):

  NLRP3 → ASC → Caspase-1 → IL-1β + IL-18 + GSDMD pyroptosis
  → fibrotic + inflammatory disease 공통 driver

표적:
  NLRP3 (NLR Family Pyrin domain 3, Q96P20)
  Caspase-1 (P29466) — downstream
  ASC (PYCARD, Q9ULZ3) — adaptor
  GSDMD (P57764) — pyroptosis effector

EMB-3 + 황련해독탕 (berberine + baicalin + baicalein) combination 가설:
  - 황련해독탕은 이미 NLRP3 차단 입증 (한방 천연 flavonoid)
  - EMB-3 + 황련해독탕 → IPF + acne dual-indication
  - 우리 시스템에서 정량 시너지 측정 (CI < 0.5 가설)
"""

from __future__ import annotations

from dataclasses import dataclass


NLRP3_PATHWAY_TARGETS = [
    {"key": "NLRP3", "uniprot": "Q96P20", "function": "NLR sensor",
     "max_seq_len": 1036,
     "fibrosis_role": "IPF: ↑ → IL-1β/IL-18/TGF-β 분비 → fibrosis",
     "acne_role": "C. acnes 인지 → 염증 perpetuation"},
    {"key": "CASP1", "uniprot": "P29466", "function": "caspase-1",
     "max_seq_len": 404,
     "role": "IL-1β/IL-18 cleavage + GSDMD activation"},
    {"key": "PYCARD", "uniprot": "Q9ULZ3", "function": "ASC adaptor",
     "max_seq_len": 195},
    {"key": "GSDMD", "uniprot": "P57764", "function": "pyroptosis effector",
     "max_seq_len": 484},
]


# 황련해독탕 핵심 활성 성분
HWANG_RYUN_HAE_DOK_TANG = {
    "Berberine": "OC1=CC2=C(C=C1OC)C3=NC=C4C=C5OCOC5=CC4=C3CC2",
    "Baicalin": "OC1=C(C(=O)C2=C(O1)C=CC(=C2)O[C@@H]3O[C@@H]([C@H]([C@@H]([C@H]3O)O)O)C(=O)O)O",
    "Baicalein": "C1=CC=C(C=C1)C2=CC(=O)C3=C(O2)C=C(C(=C3O)O)O",
    "Coptisine": "C1=CC2=CC3=CC4=C(C=C3CC2=N1)OCO4",
}


@dataclass
class NLRP3CombinationResult:
    """EMB-3 + 황련해독탕 NLRP3 차단 시뮬."""

    emb3_binding: float = 0.0
    berberine_binding: float = 0.0
    baicalin_binding: float = 0.0
    baicalein_binding: float = 0.0
    expected_synergy_ci: float = 0.0
    interpretation: str = ""


def predict_emb3_hwang_ryun_synergy() -> NLRP3CombinationResult:
    """EMB-3 + 황련해독탕 NLRP3 차단 가설 (예측)."""
    # Boltz-2 cofold 후 실측치 (현재는 가설값)
    return NLRP3CombinationResult(
        emb3_binding=0.55,           # 1,4-quinone Cys binding 예상
        berberine_binding=0.70,      # 알려진 NLRP3 차단
        baicalin_binding=0.65,       # flavonoid NLRP3 차단
        baicalein_binding=0.62,
        expected_synergy_ci=0.4,     # CI < 0.5 강한 시너지
        interpretation=(
            "EMB-3 quinone Cys covalent + 황련해독탕 flavonoid allosteric → "
            "다중 site NLRP3 차단. IPF + acne 두 적응증 동시 가능. "
            "Bergmann scleroderma model 패턴 적용."
        ),
    )


def integration_outline() -> dict:
    return {
        "step_1_cofold_prep": (
            "scripts/run_nlrp3_cofold_prep.py — 4 NLRP3 pathway 타겟 + "
            "EMB-3 + 황련해독탕 4 화합물 = 16 cofold YAML 생성"
        ),
        "step_2_cofold_run": (
            "Boltz-2 cofold 16 (~5분 GPU 후 ABFE 종료 후 실행)"
        ),
        "step_3_synergy_analysis": (
            "scripts/analyze_emb3_hwangryun_nlrp3.py — Chou-Talalay CI 계산"
        ),
        "step_4_paper": (
            "EMB-3 paper에 'Quinone-flavonoid combination NLRP3 inhibition' "
            "섹션 추가 → Nat Comm Chem 가능"
        ),
        "step_5_wet_lab": (
            "한국 CRO에 NLRP3 ASC speck assay + IL-1β ELISA ₩5M (3주)"
        ),
    }
