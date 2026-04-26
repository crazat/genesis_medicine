"""scFoundation / scGPT single-cell foundation model adapter.

⚠️ 중요한 경고 (Nat Methods 2025-08):
"Deep learning still does not outperform simple linear baselines for
perturbation prediction." (preLights / Nature Methods 2025)

→ scFoundation/scGPT 사용 시 **반드시 linear baseline (Ridge/Lasso) 동시 비교**.

Genesis_Medicine v3 통합:
  - IPF lung fibroblast scRNA-seq → EMB-3 같은 anti-fibrotic 분자 적용 시
    transcriptional response 예측
  - Cross-tissue: skin fibroblast (Recover 환자) ↔ lung fibroblast (IPF) 공통
    TGF-β signaling subtype 매핑

라이선스:
  - scFoundation: 상업 사용 가능 (xTrimo, BGI)
  - scGPT: MIT
  - Geneformer: Apache-2.0

데이터: 우리는 scRNA-seq 데이터 미보유. 공개 IPF atlas (PRJNA844548 등) 다운로드 필요.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")


@dataclass
class PerturbationPrediction:
    """단일 perturbation 예측 결과."""

    drug_smiles: str
    cell_type: str
    predicted_de_genes: list = field(default_factory=list)
    fold_changes: dict = field(default_factory=dict)
    confidence: float = 0.0
    baseline_score: float = 0.0   # linear baseline (필수)
    foundation_score: float = 0.0 # scFoundation/scGPT score
    delta_vs_baseline: float = 0.0 # foundation_score - baseline_score
    metadata: dict = field(default_factory=dict)


def linear_baseline_predict(drug_features: list, cell_features: list) -> dict:
    """Linear baseline (Ridge regression) — Nat Methods 2025 권장.

    실제 구현 시 sklearn Ridge + 천연물 SMILES descriptor + cell-type one-hot.
    """
    return {
        "model": "Ridge regression baseline",
        "instruction": (
            "1. Drug features: RDKit descriptor + Morgan FP\n"
            "2. Cell features: cell-type one-hot + tissue marker genes mean expr\n"
            "3. Target: log(perturbation/control) per gene\n"
            "4. Ridge alpha=1.0, sklearn 학습\n"
            "5. **Foundation 모델과 R²/MSE 동시 비교 — 능가 못 하면 baseline 선택**"
        ),
    }


def scfoundation_predict(drug_smiles: str, cell_type: str = "lung_fibroblast",
                          model: str = "scfoundation") -> PerturbationPrediction:
    """scFoundation/scGPT perturbation 예측.

    Returns placeholder until 실제 모델 + 데이터 통합.
    """
    return PerturbationPrediction(
        drug_smiles=drug_smiles, cell_type=cell_type,
        predicted_de_genes=[],
        baseline_score=0.0, foundation_score=0.0, delta_vs_baseline=0.0,
        metadata={
            "model": model, "stub": True,
            "instruction": (
                "1. scFoundation: HuggingFace biomap-research/scFoundation 다운로드\n"
                "2. IPF lung fibroblast scRNA-seq (GSE135893 등) 로드\n"
                "3. 약물 perturbation embedding → DE gene 예측\n"
                "4. Linear baseline 동시 학습/비교 (필수, Nat Methods 2025-08)\n"
                "5. delta_vs_baseline > 0 일 때만 foundation 채택"
            ),
            "warning": (
                "Nat Methods 2025-08: deep learning still does not outperform "
                "simple linear baselines for perturbation prediction."
            ),
        },
    )


def cross_tissue_fibroblast_match(skin_lead_smiles: str) -> dict:
    """Skin fibroblast ↔ Lung fibroblast 공통 anti-fibrotic 효능 예측.

    skin/lung fibroblast atlas (Nat Immunol 2025 + Cancer Cell 2024)에서
    TGF-β signaling fibroblast subtype 공유 입증됨.

    우리 EMB-3 같은 흉터 lead가 IPF에 cross-active 가능성 정량화.
    """
    return {
        "skin_lead": skin_lead_smiles,
        "shared_subtype": "TGF-β signaling fibroblast",
        "shared_markers": ["TGFB1", "ACTA2", "COL1A1", "FN1", "VIM"],
        "instruction": (
            "1. Skin fibroblast atlas (Nat Immunol 2025) + Lung fibroblast atlas (Sci Rep 2024)\n"
            "2. Shared TGF-β subtype 추출\n"
            "3. EMB-3 perturbation → 두 atlas에 동시 적용\n"
            "4. DE gene overlap > 50% → cross-tissue active claim"
        ),
        "expected_outcome": (
            "EMB-3가 lung fibroblast에서도 ACTA2, COL1A1 down-regulation 예측되면 "
            "→ paper의 IPF cross-disease hypothesis 강화."
        ),
    }
