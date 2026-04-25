"""Compound → Herb 역매핑 + 규제 친화도 점수.

핵심 원칙
---------
- 데이터 소스 라이선스 분리:
  * commercial 빌드: COCONUT 2.0 (CC0) + LOTUS (CC0) + NPASS 3 + Dr. Duke만
  * research 빌드: + HERB 2.0 + TCMSP + KTKP

- 출시물에서 "HERB/TCMSP 데이터 기반"이라는 마케팅 문구는 금지.
  단, 자연 제품 SMILES 자체는 자산이므로 commercial 사용 가능.

- KHP/KP (대한약전 한약재) 수록 화합물에 +α 가중치 (한국 임상 진입 우선).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from loguru import logger

from ..licensing import LicenseGate
from ..licensing.gate import BuildProfile


@dataclass
class HerbHit:
    compound_smiles: str
    inchikey: str
    herb_name: str
    herb_latin: str | None = None
    herb_korean: str | None = None
    sources: list[str] = field(default_factory=list)
    in_khp: bool = False
    in_kp: bool = False
    regulatory_score: float = 0.0
    associated_pathways: list[str] = field(default_factory=list)


def map_compounds_to_herbs(
    compounds: pd.DataFrame,
    *,
    coconut_index: Path | None = None,
    lotus_index: Path | None = None,
    npass_index: Path | None = None,
    drduke_index: Path | None = None,
    herb_index: Path | None = None,           # research only
    tcmsp_index: Path | None = None,          # research only
    khp_index: Path | None = None,
    kp_index: Path | None = None,
    build_profile: str = "commercial",
) -> list[HerbHit]:
    """SMILES → herb 역매핑.

    compounds : DataFrame with columns ['smiles', 'inchikey']
    """
    profile = BuildProfile.from_name(build_profile)
    gate = LicenseGate(profile)

    indices: dict[str, Path | None] = {}
    # commercial-safe 인덱스
    for key, path in [
        ("coconut_2", coconut_index),
        ("lotus", lotus_index),
        ("npass_3", npass_index),
        ("drduke", drduke_index),
        ("khp_kp", khp_index),
    ]:
        if path is not None:
            try:
                gate.require(key)
                indices[key] = path
            except Exception as e:
                logger.warning("{} 사용 불가 (build_profile={}): {}", key, build_profile, e)

    # research-only 인덱스 — research 빌드에서만 통과
    if build_profile == "research":
        for key, path in [
            ("herb_2_0", herb_index),
            ("tcmsp", tcmsp_index),
        ]:
            if path is not None:
                try:
                    gate.require(key)
                    indices[key] = path
                except Exception:
                    pass

    if not indices:
        logger.warning("매핑 인덱스 없음 — herbal mapping skip")
        return []

    # 각 인덱스 로드 + 매칭
    hits: dict[str, HerbHit] = {}
    for key, path in indices.items():
        if not path or not path.exists():
            continue
        df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
        for _, row in compounds.iterrows():
            ik = row["inchikey"]
            matches = df[df["inchikey"] == ik]
            for _, m in matches.iterrows():
                hit_key = f"{ik}|{m['herb_name']}"
                if hit_key not in hits:
                    hits[hit_key] = HerbHit(
                        compound_smiles=row["smiles"],
                        inchikey=ik,
                        herb_name=m["herb_name"],
                        herb_latin=m.get("herb_latin"),
                        herb_korean=m.get("herb_korean"),
                    )
                hits[hit_key].sources.append(key)

    # KHP / KP 라벨링 + regulatory_score
    if "khp_kp" in indices and indices["khp_kp"]:
        khp_df = pd.read_csv(indices["khp_kp"])
        khp_set = set(khp_df["herb_latin"].dropna())
        for hit in hits.values():
            if hit.herb_latin in khp_set:
                hit.in_khp = True
                hit.regulatory_score += 0.5

    # 다중 출처 가중
    for hit in hits.values():
        n_safe = sum(1 for s in hit.sources if s in {"coconut_2", "lotus", "npass_3", "drduke"})
        hit.regulatory_score += 0.1 * n_safe

    return list(hits.values())


def regulatory_score(hit: HerbHit) -> float:
    """규제 친화도 — KHP/KP 수록 + 다중 출처 + 임상 사용 이력."""
    score = 0.0
    if hit.in_khp:
        score += 0.5
    if hit.in_kp:
        score += 0.3
    score += 0.1 * len(hit.sources)
    return min(score, 1.0)
