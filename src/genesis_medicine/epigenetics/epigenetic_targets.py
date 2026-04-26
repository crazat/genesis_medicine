"""Epigenetic targets for fibrosis (EZH2, DNMT, TET, etc.).

PNAS 2016 + Springer 2026:
  - EZH2 (H3K27me3) — fibroblast 활성화 master, 모든 fibrosis 공통 driver
  - G9a (EHMT2) — H3K9 methylation, lung fibrosis
  - DNMT1/3A/3B — DNA methylation, IPF aberrant
  - TET1/2/3 — DNA demethylation, anti-fibrotic
  - HDAC class I — anti-fibrotic target

Genesis_Medicine v3 통합:
  - 5 epigenetic 타겟 추가 (14 → 19 타겟)
  - EMB-3 epigenetic effect 가설 검증
  - Korean CRO ChIP-seq + RRBS ₩10M
"""

from __future__ import annotations

from dataclasses import dataclass


# 핵심 epigenetic 표적 (UniProt + 기능)
EPIGENETIC_TARGETS = [
    {"key": "EZH2", "uniprot": "Q15910", "tier": "histone_methyl",
     "function": "H3K27me3 methyltransferase, fibroblast 활성화 master",
     "fibrosis_role": "↑ in IPF/scleroderma — 차단 시 회복",
     "drug_target_status": "Inhibitor desired (tazemetostat 입증)",
     "max_seq_len": 750},
    {"key": "EHMT2", "uniprot": "Q96KQ7", "tier": "histone_methyl",
     "function": "G9a — H3K9 dimethylation",
     "fibrosis_role": "Lung fibrosis 진행",
     "drug_target_status": "Inhibitor desired",
     "max_seq_len": 600},
    {"key": "DNMT1", "uniprot": "P26358", "tier": "dna_methyl",
     "function": "DNA methyltransferase 1 — 유지",
     "fibrosis_role": "Aberrant methylation in IPF fibroblast",
     "drug_target_status": "Inhibitor (decitabine, azacitidine)",
     "max_seq_len": 600},
    {"key": "TET2", "uniprot": "Q6N021", "tier": "dna_demethyl",
     "function": "DNA demethylation (5mC → 5hmC)",
     "fibrosis_role": "Reduced in fibrosis — activator desired",
     "drug_target_status": "Activator (vitamin C 보조)",
     "max_seq_len": 600},
    {"key": "HDAC1", "uniprot": "Q13547", "tier": "histone_deacetyl",
     "function": "Class I HDAC",
     "fibrosis_role": "↑ in IPF — pan-HDAC inhibitor anti-fibrotic",
     "drug_target_status": "Inhibitor (vorinostat, romidepsin)",
     "max_seq_len": 482},
]


@dataclass
class EpigeneticTargetInfo:
    """Epigenetic 타겟 cofold 정보."""

    key: str
    uniprot: str
    tier: str
    expected_emb3_binding: str = "unknown"


def emb3_epigenetic_hypothesis() -> dict:
    """EMB-3 epigenetic effect 가설."""
    return {
        "hypothesis_main": (
            "EMB-3 (1,4-benzoquinone)은 SAH/SAM 사이클의 redox 상태 조절을 통해 "
            "EZH2/DNMT1 활성에 간접 영향. 또한 quinone group이 catalytic Cys 잔기 "
            "(EZH2 SET domain Cys663)에 covalent 결합 가능."
        ),
        "test_priorities": [
            "1. Boltz-2 cofold: EMB-3 × EZH2 (Q15910) — covalent docking 권장 (CarsiDock-Cov)",
            "2. EMB-3 × DNMT1 — DNA binding 차단",
            "3. EMB-3 × HDAC1 — 가장 druggable",
            "4. Wet lab: HSF에서 H3K27me3 ChIP-seq before/after EMB-3",
            "5. RRBS methylation profile → epigenetic age clock",
        ],
        "expected_outcome": (
            "EMB-3가 EZH2 또는 HDAC1 차단 입증 시 "
            "→ 'Quinone-mediated dual epigenetic + mechanical anti-fibrotic' paper 가능"
        ),
        "korean_cro_quote": {
            "ChIP-seq H3K27me3 (n=6)": "₩6M (4-6주)",
            "RRBS DNA methylation (n=6)": "₩4M",
            "EZH2 methyltransferase activity assay": "₩2M",
            "총": "₩12M (4-8주)",
        },
        "papers_to_cite": [
            "Bergmann et al. PNAS 2016 — EZH2 inhibition scleroderma",
            "Yang et al. Springer 2026 — Histone methylation fibrosis review",
            "Mau et al. PMC 12766317 2024 — Epigenetic clock skin aging",
        ],
    }
