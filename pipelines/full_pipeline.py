"""Prefect 3 full pipeline — 9단계 통합 실행.

v2 고도화: 6단계 스크리닝(DrugCLIP→Uni-Mol2→FlowDock→Boltz-2→GNINA 1.3→PoseBusters)
         + ECR 합의 스코어링
         + FlowMol3/DecompDiff 생성 + SATURN 합성 검증
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger
from omegaconf import DictConfig
from prefect import flow, task


@task(retries=2, retry_delay_seconds=30)
def discover_targets(cfg: DictConfig) -> pd.DataFrame:
    from genesis_medicine.io.open_targets import fetch_associated_targets, to_uniprot_list

    rows = fetch_associated_targets(cfg.disease.efo_id, size=cfg.target_discovery.get("size", 200))
    targets = to_uniprot_list(rows)
    df = pd.DataFrame(targets).sort_values("score", ascending=False)
    logger.info("타겟 {}개 발견", len(df))
    return df


@task
def prep_structures(targets: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    from genesis_medicine.structure import get_predictor
    from genesis_medicine.structure.alphafold_db_adapter import AlphaFoldDBAdapter

    afdb = AlphaFoldDBAdapter(cache_dir=Path(".cache/afdb"))
    predictor = get_predictor(cfg.structure)
    records = []
    for row in targets.head(cfg.get("max_targets", 10)).itertuples():
        hit = afdb.lookup(row.uniprot)
        if hit is not None:
            records.append({
                "uniprot": row.uniprot,
                "cif": str(hit.cif_path),
                "plddt": hit.plddt_mean,
                "source": "afdb",
            })
            continue
        logger.warning("AFDB 미커버: {} — 로컬 {} 추론 필요 (TODO)", row.uniprot, predictor.engine_name)
        records.append({"uniprot": row.uniprot, "cif": None, "plddt": 0.0, "source": "missing"})
    return pd.DataFrame(records)


@task
def build_library(cfg: DictConfig) -> pd.DataFrame:
    logger.info("TODO: ChEMBL + COCONUT + NPASS + LOTUS ETL")
    return pd.DataFrame()


@task
def multi_stage_screen(
    structures: pd.DataFrame, library: pd.DataFrame, cfg: DictConfig
) -> pd.DataFrame:
    """6단계 스크리닝 + ECR 합의 스코어링."""
    from genesis_medicine.screening.consensus import exponential_consensus_ranking

    stages = cfg.screening.stages
    logger.info(
        "6단계 스크리닝 시작: {}",
        " → ".join(s.name for s in stages),
    )

    # 각 스테이지 결과를 stage_name → {smiles: score} 형태로 수집
    stage_results: dict[str, dict[str, float]] = {}

    # TODO: 각 단계 어댑터 실행
    for stage in stages:
        logger.info("Stage [{}] engine={} — TODO: 실제 실행", stage.name, stage.engine)
        # stage_results[stage.name] = screener.screen(req) → {smi: score}

    # ECR 합의 스코어링
    ecr_stages = cfg.screening.get("consensus", {}).get("stages_for_ranking", [])
    sigma = cfg.screening.get("consensus", {}).get("sigma", 0.05)
    ecr_input = {k: v for k, v in stage_results.items() if k in ecr_stages}

    if ecr_input:
        ranked = exponential_consensus_ranking(ecr_input, sigma=sigma)
        logger.info("ECR 순위: 상위 5개 — {}", [(r.smiles[:30], r.ecr_score) for r in ranked[:5]])
        return pd.DataFrame([
            {"smiles": r.smiles, "ecr_score": r.ecr_score, **r.scores, **r.ranks}
            for r in ranked
        ])

    return pd.DataFrame()


@task
def generate_de_novo(structures: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    """FlowMol3/DecompDiff seed → REINVENT 4 RL → SATURN 합성 필터."""
    if not cfg.generation.get("enabled", False):
        return pd.DataFrame()

    logger.info(
        "생성 파이프라인: {} seed generators → REINVENT 4 RL → 합성 검증",
        sum(1 for g in cfg.generation.seed_generators if g.get("enabled", True)),
    )

    # TODO: seed generators 실행
    # TODO: REINVENT 4 RL 최적화
    # TODO: SATURN + AiZynthFinder 합성 검증
    return pd.DataFrame()


@task
def admet_filter(combined: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    logger.info("TODO: ADMET-AI v2 + Chemprop 2.0 실행")
    return combined


@task
def herbal_overlay(combined: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    logger.info("TODO: COCONUT/LOTUS/NPASS 천연물 매핑 + KHP 규제 필터")
    return combined


@task
def md_refine(top: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if not cfg.md.get("enabled", False):
        return top
    logger.info("TODO: OpenMM 10-50 ns")
    return top


@task
def build_report(final: pd.DataFrame, cfg: DictConfig) -> Path:
    out = Path(cfg.project.output_dir) / "report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("<h1>Genesis_Medicine v2 run completed.</h1>")
    logger.info("리포트 저장: {}", out)
    return out


@flow(name="genesis_full_pipeline")
def run(cfg: DictConfig) -> Path:
    targets = discover_targets(cfg)
    structures = prep_structures(targets, cfg)
    library = build_library(cfg)
    screening = multi_stage_screen(structures, library, cfg)
    novel = generate_de_novo(structures, cfg)
    combined = pd.concat([screening, novel], ignore_index=True) if not novel.empty else screening
    filtered = admet_filter(combined, cfg)
    herbal = herbal_overlay(filtered, cfg)
    refined = md_refine(herbal.head(cfg.md.get("top_n", 50)), cfg)
    return build_report(refined, cfg)
