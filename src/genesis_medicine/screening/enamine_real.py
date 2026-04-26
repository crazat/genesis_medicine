"""Enamine REAL Space (29 billion compounds) Tanimoto matching.

Enamine REAL Space: 29 billion synthesizable compounds (on-demand).
ZINC22 통합: REAL + WuXi GalaXi (2.5B) + Mcule Ultimate (128M).

전체 29B 검색은 large GPU cluster 필요. 현실적 접근:
  1. Tanimoto top-N from 1M subset (manageable on RTX 5090)
  2. 한약 fragment query (centella/shikonin/EGCG/embelin scaffold)
  3. Tanimoto > 0.5 → top 10k → Boltz-2 cofold prioritize
  4. 결과 nM affinity 후보 발견

다운로드 가이드:
  Enamine REAL: https://enamine.net/compound-collections/real-compounds
  ZINC22 web: https://cartblanche22.docking.org/
  GitHub deepdock: https://github.com/jcorreia11/deepdock (Deep Docking 가속)

라이선스: ZINC22 (free academic + commercial), Enamine catalog (Apache 2.0 SMILES,
purchase 시 별도 가격).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs, Descriptors, Crippen

RDLogger.DisableLog("rdApp.*")


@dataclass
class TanimotoMatchConfig:
    """Tanimoto match parameters."""

    fp_bits: int = 2048
    fp_radius: int = 2
    threshold: float = 0.5      # Tanimoto > 0.5 = "유사"
    top_k: int = 10000
    use_gpu: bool = False        # cupy 사용 시 True


@dataclass
class MatchedCompound:
    """Enamine REAL에서 매칭된 화합물."""

    enamine_id: str = ""
    smiles: str = ""
    query_smiles: str = ""       # 어떤 fragment에 매칭됐는지
    tanimoto: float = 0.0
    mw: float = 0.0
    estimated_price_usd: float = 0.0   # Enamine 평균 ~$200-500/mg
    metadata: dict = field(default_factory=dict)


def fingerprint(smiles: str, radius: int = 2, n_bits: int = 2048):
    """Morgan FP."""
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(m, radius, nBits=n_bits)


def tanimoto_search(
    query_smiles: list[str],
    candidate_smiles: list[str],
    cfg: TanimotoMatchConfig | None = None,
) -> list[MatchedCompound]:
    """Tanimoto match — query × candidates pairwise.

    Args:
        query_smiles: 한약 fragment SMILES (e.g. herbal_fragments.smi)
        candidate_smiles: Enamine REAL subset (또는 ZINC22)
        cfg: matching config

    Returns:
        list of MatchedCompound sorted by Tanimoto desc.
    """
    cfg = cfg or TanimotoMatchConfig()

    # query fingerprints
    query_fps = [(s, fingerprint(s, cfg.fp_radius, cfg.fp_bits))
                  for s in query_smiles]
    query_fps = [(s, fp) for s, fp in query_fps if fp is not None]

    matches = []
    for cand_smi in candidate_smiles:
        cand_fp = fingerprint(cand_smi, cfg.fp_radius, cfg.fp_bits)
        if cand_fp is None:
            continue
        # 가장 유사한 query 찾기
        best_q, best_t = None, 0.0
        for q_smi, q_fp in query_fps:
            t = DataStructs.TanimotoSimilarity(q_fp, cand_fp)
            if t > best_t:
                best_t, best_q = t, q_smi
        if best_t >= cfg.threshold:
            m = Chem.MolFromSmiles(cand_smi)
            mw = float(Descriptors.MolWt(m))
            matches.append(MatchedCompound(
                smiles=cand_smi, query_smiles=best_q,
                tanimoto=best_t, mw=mw,
                estimated_price_usd=200 + (mw - 200) * 0.5,  # 매우 거친 추정
            ))

    matches.sort(key=lambda x: -x.tanimoto)
    return matches[:cfg.top_k]


def filter_topical_compatible(
    matches: list[MatchedCompound],
    mw_max: float = 500,
    logp_range: tuple = (1.5, 3.5),
) -> list[MatchedCompound]:
    """외용 적합 필터 (MW + logP)."""
    out = []
    for m in matches:
        mol = Chem.MolFromSmiles(m.smiles)
        if mol is None:
            continue
        if Descriptors.MolWt(mol) > mw_max:
            continue
        logp = Crippen.MolLogP(mol)
        if not (logp_range[0] <= logp <= logp_range[1]):
            continue
        m.metadata["logp"] = logp
        out.append(m)
    return out


def download_enamine_subset_instructions() -> str:
    """Enamine REAL subset 다운로드 가이드."""
    return """
# Enamine REAL Subset 다운로드 가이드 (29B 전체 → 1M subset)

## 1. CartBlanche (ZINC22 web)
URL: https://cartblanche22.docking.org/
- "Browse" → REAL 카탈로그 선택
- Tranches by MW, logP 필터 적용 → "drug-like" subset (~1M)
- SMILES 파일 다운로드 (gzip)

## 2. Enamine 직접
URL: https://enamine.net/compound-collections/real-compounds/real-database
- Free download: REAL Database (500M 분자, gzip)
- 1M subset: Tanimoto pre-filter 후 추출

## 3. ZINC22 SMI files (특정 tranche)
```bash
# 예: MW 200-400, logP 1-3.5 (drug-like)
wget https://files.docking.org/zinc22/2d/H/HACA/HACAML.zinc22.smi.gz
```

## 4. 우리 시스템 적용
```python
from genesis_medicine.screening.enamine_real import tanimoto_search

# 한약 fragment query
herbal_query = open("/home/crazat/genesis_medicine/external/herbal_fragments.smi").readlines()
herbal_query = [s.strip() for s in herbal_query if s.strip()]

# Enamine REAL 1M subset 로드
import gzip
with gzip.open("enamine_real_1M_drug_like.smi.gz", "rt") as f:
    enamine = [line.strip().split()[0] for line in f]

matches = tanimoto_search(herbal_query, enamine, threshold=0.5, top_k=1000)
```

## 5. 다음 단계 (top 1000)
- 외용 적합 필터 (MW ≤ 500, logP 1.5-3.5)
- ADMET-AI + logKp 게이트
- Boltz-2 cofold (TGFB1, MMP1) — 1000 cofold ≈ 7시간 RTX 5090
- top 50 → MD validation
- top 5 → ABFE 정량
"""


def estimate_screening_cost_and_time(
    n_candidates: int,
    cofold_seconds: int = 25,
    md_minutes: int = 7,
) -> dict:
    """Enamine REAL screening의 비용·시간 추정."""
    # Tanimoto match: ~1000 cand/sec → 1M = 1000s
    tanimoto_sec = n_candidates / 1000
    cofold_total_h = (n_candidates * 0.001) * cofold_seconds / 3600
    # 보통 top 1% = 10000 → 0.1% = 1000 → 0.01% = 100 MD
    n_md = int(n_candidates * 0.0001)
    md_total_h = n_md * md_minutes / 60

    return {
        "n_candidates": n_candidates,
        "tanimoto_match_seconds": int(tanimoto_sec),
        "cofold_top_0.1pct_hours": round(cofold_total_h, 1),
        "md_top_0.01pct_count": n_md,
        "md_total_hours": round(md_total_h, 1),
        "total_estimated_gpu_days": round(
            (cofold_total_h + md_total_h) / 24, 1
        ),
        "synthesis_cost_top5_usd": 5 * 500,
    }
