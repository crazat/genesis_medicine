"""네트워크 약리학 — compound × target × pathway 교차.

상업 빌드: Reactome (CC BY 4.0) + WikiPathways (CC0)
연구 빌드: + KEGG (유료)

Pathway 효소집합 enrichment — 단순 hypergeometric.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats

from ..licensing import LicenseGate
from ..licensing.gate import BuildProfile


@dataclass
class PathwayHit:
    pathway_id: str
    name: str
    source: str  # reactome | wikipathways | kegg
    overlap_genes: list[str] = field(default_factory=list)
    pvalue: float = 1.0
    fdr: float = 1.0
    enriched_compounds: list[str] = field(default_factory=list)


def overlay_compounds_on_pathways(
    compound_target_df: pd.DataFrame,
    *,
    reactome_index: Path | None = None,
    wikipathways_index: Path | None = None,
    kegg_index: Path | None = None,
    build_profile: str = "commercial",
) -> list[PathwayHit]:
    """compound→target 매핑을 pathway 위에 오버레이.

    compound_target_df : columns ['smiles', 'target_uniprot', 'target_gene']
    """
    profile = BuildProfile.from_name(build_profile)
    gate = LicenseGate(profile)

    sources: list[tuple[str, Path | None]] = []
    try:
        gate.require("reactome")
        if reactome_index:
            sources.append(("reactome", reactome_index))
    except Exception:
        pass
    try:
        gate.require("wikipathways")
        if wikipathways_index:
            sources.append(("wikipathways", wikipathways_index))
    except Exception:
        pass
    if build_profile == "research":
        try:
            gate.require("kegg_pathways")
            if kegg_index:
                sources.append(("kegg", kegg_index))
        except Exception:
            pass

    hits: list[PathwayHit] = []
    target_genes = set(compound_target_df["target_gene"].dropna().unique())

    for source_name, idx_path in sources:
        if not idx_path or not idx_path.exists():
            continue
        df = pd.read_parquet(idx_path) if idx_path.suffix == ".parquet" else pd.read_csv(idx_path)
        # df expected columns: pathway_id, pathway_name, gene_symbol
        for pid, group in df.groupby("pathway_id"):
            pathway_genes = set(group["gene_symbol"])
            overlap = target_genes & pathway_genes
            if not overlap:
                continue
            # hypergeometric: M = total genes in DB, n = pathway size, N = our targets, k = overlap
            M = 25_000  # 휴먼 단백질 코딩 유전자 추정
            n = len(pathway_genes)
            N = len(target_genes)
            k = len(overlap)
            pvalue = stats.hypergeom.sf(k - 1, M, n, N)
            comp_smiles = list(
                compound_target_df[compound_target_df["target_gene"].isin(overlap)]["smiles"].unique()
            )
            hits.append(PathwayHit(
                pathway_id=str(pid),
                name=str(group["pathway_name"].iloc[0]),
                source=source_name,
                overlap_genes=sorted(overlap),
                pvalue=float(pvalue),
                enriched_compounds=comp_smiles,
            ))

    # BH FDR
    pvals = np.array([h.pvalue for h in hits])
    if len(pvals) > 0:
        order = np.argsort(pvals)
        ranks = np.argsort(order)
        bh = pvals * len(pvals) / (ranks + 1)
        for hit, fdr in zip(hits, bh):
            hit.fdr = float(min(fdr, 1.0))

    hits.sort(key=lambda h: h.pvalue)
    logger.info("Pathway enrichment: {} pathways (top FDR={:.2e})",
                len(hits), hits[0].fdr if hits else 1.0)
    return hits


def compute_pathway_enrichment(
    compound_target_df: pd.DataFrame,
    *,
    fdr_threshold: float = 0.05,
    **kwargs,
) -> list[PathwayHit]:
    """오버레이 + FDR 컷."""
    all_hits = overlay_compounds_on_pathways(compound_target_df, **kwargs)
    return [h for h in all_hits if h.fdr <= fdr_threshold]
