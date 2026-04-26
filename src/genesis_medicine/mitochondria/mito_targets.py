"""Mitochondrial metabolism targets for fibrosis.

Frontiers Cell Dev Biol 2025 + IPF mitochondrial dysfunction:
  - PGC-1α (PPARGC1A): mitochondrial biogenesis master regulator
  - TFAM: mtDNA maintenance + replication
  - NRF1, NRF2 (NFE2L1, NFE2L2): nuclear respiratory factors
  - OPA1, MFN1/2: mitochondrial dynamics

IPF + skin fibrosis 공통 메커니즘:
  ↓ PGC-1α → ↓ TFAM → ↑ mtDNA damage → ↑ senescence → fibrosis perpetuation

EMB-3 가설 (1,4-benzoquinone redox cycling):
  - Quinone redox = mtROS modulator?
  - PGC-1α 활성화 가능? (anti-fibrotic + 미토콘드리아 dual-action)
  - Embelin은 NF-κB 차단 보고 → mitochondrial UPR 영향?

추가 검증 필요:
  - 4 신규 cofold (PGC-1α, TFAM, NRF1, NRF2)
  - mtDNA copy number 측정 (PCR-based, ₩30K/sample)
  - Seahorse XF mitochondrial respiration assay
"""

from __future__ import annotations

from dataclasses import dataclass


# 핵심 mitochondrial targets — UniProt + sequence info
MITO_TARGETS = [
    {"key": "PPARGC1A", "uniprot": "Q9UBK2", "common_name": "PGC-1α",
     "tier": "master_regulator",
     "function": "Mitochondrial biogenesis master regulator",
     "fibrosis_connection": "Reduced in IPF fibroblasts, AT II epithelium",
     "drug_target_status": "Activator desired (반대 방향 — boost)",
     "max_seq_len": 798},
    {"key": "TFAM", "uniprot": "Q00059", "common_name": "TFAM",
     "tier": "mtDNA_maintenance",
     "function": "mtDNA replication + transcription, HMG-box protein",
     "fibrosis_connection": "Reduced TFAM → mtDNA damage → senescence",
     "drug_target_status": "Stabilizer desired",
     "max_seq_len": 246},
    {"key": "NRF1", "uniprot": "Q16656", "common_name": "Nuclear Respiratory Factor 1",
     "tier": "transcription_factor",
     "function": "Activates TFAM, COX subunits, mitochondrial protein expression",
     "fibrosis_connection": "PGC-1α downstream, mitochondrial bioenergetics",
     "drug_target_status": "Activator desired",
     "max_seq_len": 503},
    {"key": "NFE2L2", "uniprot": "Q16236", "common_name": "NRF2 (Antioxidant)",
     "tier": "antioxidant",
     "function": "Antioxidant response, KEAP1 binding",
     "fibrosis_connection": "ROS damage → fibroblast senescence 차단",
     "drug_target_status": "Activator desired (KEAP1 inhibition)",
     "max_seq_len": 605},
]


@dataclass
class MitoTargetCofoldPrep:
    """Cofold prep info for mitochondrial targets."""

    target_key: str = ""
    sequence_truncated: bool = False
    msa_status: str = "pending"        # pending | cached | failed
    cofold_yaml_generated: bool = False


def get_target_info(key: str) -> dict | None:
    for t in MITO_TARGETS:
        if t["key"] == key:
            return t
    return None


def emb3_mito_hypothesis() -> dict:
    """EMB-3가 미토콘드리아 표적에 영향 미치는지 가설."""
    return {
        "hypothesis": (
            "EMB-3 (1,4-benzoquinone)은 redox cycling으로 mtROS 조절 가능. "
            "낮은 dose에서 PGC-1α activator (eustress) → mitochondrial biogenesis ↑ → "
            "fibroblast senescence 회복 → anti-fibrotic dual-action."
        ),
        "alternative": (
            "높은 dose에서는 mtROS 과다 → 세포 사멸 → fibroblast 감소 (다른 메커니즘)"
        ),
        "test_method": [
            "1. Boltz-2 cofold: EMB-3 × 4 mito targets (PGC-1α, TFAM, NRF1, NRF2)",
            "2. Wet lab: HSF (Human Skin Fibroblast) Seahorse XF basal/maximal respiration",
            "3. mtDNA copy number qPCR before/after EMB-3 treatment",
            "4. PGC-1α/TFAM mRNA RT-qPCR",
            "5. β-galactosidase senescence marker",
        ],
        "expected_outcome": (
            "EMB-3가 anti-fibrotic + mitochondrial biogenesis booster 입증 시 "
            "→ paper 'dual-mechanism anti-fibrotic + senolytic' 가능"
        ),
        "korean_cro_quote": {
            "Seahorse XF (n=5)": "₩2,500,000",
            "mtDNA qPCR (n=10)": "₩300,000",
            "RT-qPCR PGC-1α/TFAM": "₩500,000",
            "β-gal staining": "₩400,000",
            "총": "₩3,700,000 (4-6주)",
        },
    }


def integration_plan() -> dict:
    """Genesis_Medicine v3 통합 plan."""
    return {
        "step_1_cofold": (
            "scripts/run_mito_cofold_prep.py — UniProt seq + MSA + 12 cofold YAML "
            "(4 타겟 × 3 화합물: EMB-3, Embelin, EGCG)"
        ),
        "step_2_analysis": (
            "scripts/analyze_mito_results.py — affinity per target → "
            "PGC-1α activation prediction"
        ),
        "step_3_paper": (
            "EMB-3 paper에 'mitochondrial dual-action' 섹션 추가 → "
            "discussion grand claim"
        ),
        "step_4_wet_lab": (
            "Recover Tier 1 CRO에 mito panel ₩3.7M 추가 → 총 Tier 1 ₩1,930만"
        ),
    }
