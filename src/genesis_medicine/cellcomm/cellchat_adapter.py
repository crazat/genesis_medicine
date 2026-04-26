"""CellChat / NicheNet adapter for skin-lung fibrotic niche.

CellChat (Nat Comm 2021) + MultiNicheNet (bioRxiv 2023):
  - Ligand-Receptor pair quantification from scRNA-seq
  - Pathway-level signaling network
  - 정상 vs 질병 differential analysis

Genesis_Medicine v3 적용:
  - 흉터 fibroblast ↔ macrophage ↔ keratinocyte cross-talk
  - EMB-3가 LR pair (TGFB1-TGFBR1, CTGF-LRP6 등)에 미치는 영향
  - 새 표적 발굴: cross-talk hub LR (SPP1-CD44, IL11-IL11RA 등)

도구 비교 (PMC 9575221, 2022):
  - CellChat ≈ CellPhoneDB ≈ NicheNet ≈ ICELLNET (top 4)
  - 우리는 CellChat + NicheNet 조합 (LR + downstream effect)

라이선스: CellChat (GPL-3, R package — research only/subprocess),
         NicheNet (Apache, R), liana-py (GPL-3) 또는 CellPhoneDB (MIT, Python)

우리 commercial 빌드: **CellPhoneDB v5 (MIT)** 또는 **liana-py** 권장.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# 흉터 niche의 핵심 ligand-receptor pairs (CellChatDB + 문헌)
SCAR_NICHE_LR_PAIRS = [
    # TGFβ axis (master fibrotic signal)
    {"ligand": "TGFB1", "receptor": "TGFBR1+TGFBR2",
     "source_cell": "macrophage", "target_cell": "fibroblast",
     "pathway": "TGFB", "fibrotic_role": "master driver",
     "emb3_intervention": "direct binding (감소)"},
    {"ligand": "TGFB1", "receptor": "TGFBR3 (betaglycan)",
     "source_cell": "fibroblast", "target_cell": "fibroblast",
     "pathway": "TGFB", "fibrotic_role": "amplifier"},
    # IL11 axis (recently emerged anti-fibrotic target)
    {"ligand": "IL11", "receptor": "IL11RA",
     "source_cell": "fibroblast", "target_cell": "fibroblast (autocrine)",
     "pathway": "IL11", "fibrotic_role": "amplification loop",
     "emb3_intervention": "indirect (TGFB1 차단 → IL11 ↓)"},
    # SPP1 (osteopontin) — implant fibrosis driver
    {"ligand": "SPP1", "receptor": "CD44",
     "source_cell": "macrophage_SPP1+", "target_cell": "fibroblast",
     "pathway": "SPP1", "fibrotic_role": "myofibroblast 활성화"},
    # PDGF axis (ECM 생산)
    {"ligand": "PDGFB", "receptor": "PDGFRB",
     "source_cell": "endothelial/macrophage", "target_cell": "myofibroblast",
     "pathway": "PDGF", "fibrotic_role": "fibroblast proliferation",
     "emb3_intervention": "direct PDGFRB binding"},
    # CTGF axis (effector)
    {"ligand": "CCN2 (CTGF)", "receptor": "LRP6 + integrin α5β1",
     "source_cell": "fibroblast", "target_cell": "fibroblast (autocrine)",
     "pathway": "CCN", "fibrotic_role": "ECM deposition",
     "emb3_intervention": "direct CTGF binding"},
    # Wnt axis (모낭, 진피 재생)
    {"ligand": "WNT5A", "receptor": "FZD5 + ROR2",
     "source_cell": "papillary fibroblast", "target_cell": "keratinocyte",
     "pathway": "WNT", "fibrotic_role": "regenerative (preserve)"},
    # Notch axis (keloid)
    {"ligand": "JAG1", "receptor": "NOTCH1",
     "source_cell": "fibroblast", "target_cell": "fibroblast",
     "pathway": "Notch", "fibrotic_role": "keloid 진행"},
    # Integrin signaling (mechanotransduction)
    {"ligand": "FN1 (fibronectin)", "receptor": "ITGA5+ITGB1",
     "source_cell": "fibroblast", "target_cell": "myofibroblast",
     "pathway": "integrin", "fibrotic_role": "mechanosensing"},
]


@dataclass
class CellChatAnalysisResult:
    """CellChat 결과 wrapper."""

    sample_name: str = ""
    n_lr_pairs_significant: int = 0
    top_pathways: list = field(default_factory=list)
    differential_lr_disease_vs_normal: list = field(default_factory=list)
    proposed_targets: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def estimate_emb3_lr_impact() -> dict:
    """EMB-3가 흉터 niche LR pair에 미치는 영향 추정."""
    direct_targets = ["TGFB1", "MMP1", "CTGF", "PDGFRB"]   # 우리 검증된 binding
    impact = []
    for lr in SCAR_NICHE_LR_PAIRS:
        ligand_simple = lr["ligand"].split(" ")[0].split("(")[0].strip()
        receptor_genes = [r.strip() for r in lr["receptor"].split("+")]
        # 우리 EMB-3 직접 표적 매칭
        targets_hit = [t for t in direct_targets
                        if t == ligand_simple or t in receptor_genes]
        if targets_hit:
            impact.append({
                "lr_pair": f"{lr['ligand']} → {lr['receptor']}",
                "pathway": lr["pathway"],
                "fibrotic_role": lr["fibrotic_role"],
                "emb3_targets_hit": targets_hit,
                "expected_effect": (
                    "차단" if lr["fibrotic_role"] != "regenerative (preserve)"
                    else "🟡 주의 (regenerative — 손상 시 안 좋음)"
                ),
            })
    return {
        "n_lr_pairs_total": len(SCAR_NICHE_LR_PAIRS),
        "n_emb3_direct_impact": len(impact),
        "details": impact,
        "summary": (
            f"EMB-3는 흉터 niche {len(impact)}/{len(SCAR_NICHE_LR_PAIRS)} LR pair "
            "직접 차단 가능 (TGFB1, CTGF, PDGFRB axis). 주의: WNT5A "
            "regenerative axis는 보존 필요"
        ),
    }


def cellchat_analysis_workflow() -> str:
    """실제 분석 워크플로우 (R + scanpy 통합)."""
    return """
# CellChat 흉터 분석 워크플로우 (Recover 환자 데이터 사용 시)

## 1. 데이터 준비
- 환자 흉터 + 정상 피부 biopsy → scRNA-seq (10x Genomics, ₩1.5M/sample)
- 또는 공개 데이터 (Nat Immunol 2025 skin atlas)

## 2. CellChat (R)
```r
library(CellChat)
library(Seurat)

seurat_obj <- readRDS("recover_scar_scrna.rds")
cellchat <- createCellChat(object = seurat_obj, group.by = "cell_type")
cellchat@DB <- CellChatDB.human
cellchat <- subsetData(cellchat)
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)
cellchat <- computeCommunProb(cellchat)
cellchat <- filterCommunication(cellchat, min.cells = 10)
```

## 3. Differential analysis (정상 vs 흉터)
```r
cellchat.scar <- computeNetSimilarityPairwise(cellchat.scar, ...)
# 정상과 비교, 통계 유의 pair 추출
```

## 4. EMB-3 영향 매핑
- 위 estimate_emb3_lr_impact() 결과와 매칭
- 새 표적 발굴: 흉터에 우세하지만 우리 14 타겟에 없는 LR pair

## 5. 우리 시스템 통합
```python
from genesis_medicine.cellcomm.cellchat_adapter import (
    SCAR_NICHE_LR_PAIRS, estimate_emb3_lr_impact,
)

# CellChat output → 새 cofold 후보
new_targets = identify_unaddressed_lr_pairs(cellchat_results)
# Boltz-2 cofold for new targets
```

## 통합 비용
- R + scanpy 인프라: 1주
- Public data 분석: 2주
- 환자 sample: ₩1.5M/sample × 6 (3 정상 + 3 흉터) = ₩9M
- 총 paper 가치: 매우 높음 (paper Discussion 강력 hook)
"""
