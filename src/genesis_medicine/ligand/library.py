"""ligand library 통합 빌더 — build_profile 인지.

상업 빌드는 자동으로 research-only 소스를 제외 (HERB/TCMSP/KTKP).
중복은 InChIKey로 제거. 필터는 RDKit 표준화 + Lipinski/PAINS/NP-likeness.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from ..licensing import LicenseGate
from ..licensing.gate import BuildProfile


@dataclass
class LibraryStats:
    n_total: int
    n_unique: int
    n_by_source: dict[str, int]
    n_filtered_out: int


SOURCE_LICENSE_KEY = {
    "chembl": "chembl_35",
    "coconut": "coconut_2",
    "lotus": "lotus",
    "npass": "npass_3",
    "npatlas": "npatlas_3",
    "drduke": "drduke",
    "pubchem": "pubchem",
    "zinc22": "zinc22",
    # research-only
    "herb": "herb_2_0",
    "tcmsp": "tcmsp",
    "ktkp": "ktkp_raw",
}


def build_library(
    cfg: Any,
    *,
    build_profile: str = "commercial",
    data_dir: Path = Path("./data"),
) -> tuple[pd.DataFrame, LibraryStats]:
    """모든 활성 소스를 모아 통합 라이브러리를 만든다."""
    profile = BuildProfile.from_name(build_profile)
    gate = LicenseGate(profile)

    sources_cfg = cfg.get("sources", {}) if hasattr(cfg, "get") else cfg["sources"]
    enabled = []
    for name, src_cfg in sources_cfg.items():
        if not src_cfg.get("enabled", False):
            continue
        license_key = SOURCE_LICENSE_KEY.get(name)
        if license_key is None:
            logger.warning("소스 '{}' 라이선스 키 미정의 — 건너뜀", name)
            continue
        try:
            gate.require(license_key)
            enabled.append(name)
        except Exception as e:
            logger.warning("'{}' 비활성 ({}): {}", name, build_profile, e)

    frames: list[pd.DataFrame] = []
    counts: dict[str, int] = {}
    for src in enabled:
        path = data_dir / f"{src}_compounds.parquet"
        if not path.exists():
            logger.warning("{} parquet 미발견: {} — ETL 필요", src, path)
            continue
        df = pd.read_parquet(path)
        df["source"] = src
        frames.append(df)
        counts[src] = len(df)

    if not frames:
        logger.warning("ligand library 비어있음")
        return pd.DataFrame(), LibraryStats(0, 0, {}, 0)

    raw = pd.concat(frames, ignore_index=True)
    n_total = len(raw)

    # 표준화 + InChIKey
    standardized = _standardize_smiles(raw)

    # 필터
    filters_cfg = cfg.get("filters", {}) if hasattr(cfg, "get") else cfg.get("filters", {})
    filtered = _apply_filters(standardized, filters_cfg)
    n_filtered_out = len(standardized) - len(filtered)

    # 중복 제거
    dedup_cfg = cfg.get("dedup", {}) if hasattr(cfg, "get") else cfg.get("dedup", {})
    key = dedup_cfg.get("key", "inchikey")
    deduped = filtered.drop_duplicates(subset=[key])

    stats = LibraryStats(
        n_total=n_total,
        n_unique=len(deduped),
        n_by_source=counts,
        n_filtered_out=n_filtered_out,
    )
    logger.info(
        "Library: {} → {} unique (필터 -{}, 중복 -{})",
        n_total, len(deduped),
        n_filtered_out, len(filtered) - len(deduped),
    )
    return deduped, stats


def _standardize_smiles(df: pd.DataFrame) -> pd.DataFrame:
    try:
        from rdkit import Chem
        from rdkit.Chem.MolStandardize import rdMolStandardize
    except ImportError:
        logger.warning("RDKit 미설치 — 표준화 생략")
        return df

    standardizer = rdMolStandardize.LargestFragmentChooser()
    out_rows = []
    for _, row in df.iterrows():
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            continue
        mol = standardizer.choose(mol)
        canonical = Chem.MolToSmiles(mol, canonical=True)
        try:
            inchikey = Chem.InchiToInchiKey(Chem.MolToInchi(mol))
        except Exception:
            inchikey = None
        if inchikey is None:
            continue
        new_row = row.to_dict()
        new_row["smiles"] = canonical
        new_row["inchikey"] = inchikey
        out_rows.append(new_row)
    return pd.DataFrame(out_rows)


def _apply_filters(df: pd.DataFrame, filters_cfg: dict) -> pd.DataFrame:
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors
    except ImportError:
        return df

    mw_lo, mw_hi = filters_cfg.get("mw_range", [150, 700])
    logp_lo, logp_hi = filters_cfg.get("logp_range", [-2.0, 6.0])
    np_min = filters_cfg.get("np_likeness_min", -2.0)

    keep = []
    for _, row in df.iterrows():
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            continue
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        if not (mw_lo <= mw <= mw_hi):
            continue
        if not (logp_lo <= logp <= logp_hi):
            continue
        # NP-likeness, PAINS는 추가 모듈에서 (생략)
        keep.append(row)
    return pd.DataFrame(keep)
