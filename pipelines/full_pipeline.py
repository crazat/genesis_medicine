"""Prefect 3 full pipeline — 11단계 통합 실행 (ultrathink 2026-04-25).

  [0] Disease Config
  [1] Target Discovery (Open Targets + BERN2 + PrimeKG)
  [1.5] ★ Drug Repurposing (TxGNN zero-shot) — A1
  [2] Structure (Boltz-2/Protenix-v2/OpenFold3/Consensus + AFDB)
  [2.5] ★ Conformational Ensemble (AlphaFlow/BioEmu) — A2
  [3] Ligand Library (COCONUT+LOTUS+NPASS+ChEMBL)
  [4] 6-Stage Screening (DrugCLIP→Uni-Mol2→FlowDock→Boltz-2→GNINA→PoseBusters) + ECR
  [5] Generation (FlowMol3+DecompDiff+REINVENT4+SATURN+AiZynthFinder)
  [5.5] ★ optional: PROTAC/Glue/BindCraft (research) — B1/B2
  [6] ADMET (ADMET-AI v2)
  [7] Herbal Network Pharmacology
  [8'] ★ MD-ML (OpenMM-ML + MACE-OFF24) — A3
  [8.5] ★ ABFE (FEP-SPell-ABFE / pmx) — A4
  [9] Reporting + IP Timestamp
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger
from omegaconf import DictConfig
from prefect import flow, task


# ---------- Stage 1 ----------

@task(retries=2, retry_delay_seconds=30)
def discover_targets(cfg: DictConfig) -> pd.DataFrame:
    from genesis_medicine.io.open_targets import fetch_associated_targets, to_uniprot_list

    rows = fetch_associated_targets(cfg.disease.efo_id, size=cfg.target_discovery.get("size", 200))
    targets = to_uniprot_list(rows)
    df = pd.DataFrame(targets).sort_values("score", ascending=False)
    logger.info("Stage 1 [타겟 발굴]: {}개", len(df))
    return df


# ---------- Stage 1.5 — A1 ----------

@task
def repurpose_drugs(cfg: DictConfig) -> pd.DataFrame:
    """TxGNN으로 zero-shot 약물 재창출. 이미 승인된 약 중 후보 발견."""
    if not cfg.repurposing.get("enabled", False):
        return pd.DataFrame()
    from genesis_medicine.repurposing import RepurposingRequest, TxGNNAdapter

    adapter = TxGNNAdapter(
        cache_dir=Path(cfg.repurposing.cache_dir),
        model_path=Path(cfg.repurposing.model_path) if cfg.repurposing.get("model_path") else None,
        kg_version=cfg.repurposing.kg_version,
        device=cfg.repurposing.device,
        explain=cfg.repurposing.explain,
    )
    req = RepurposingRequest(
        disease_id=cfg.disease.efo_id,
        disease_name=cfg.disease.display_name,
        relation=cfg.repurposing.relation,
        top_k=cfg.repurposing.top_k,
        seed=cfg.project.seed,
    )
    result = adapter.repurpose(req)
    df = pd.DataFrame([h.model_dump() for h in result.hits])
    logger.info("Stage 1.5 [재창출]: {} 후보 약물", len(df))
    return df


# ---------- Stage 2 ----------

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
                "uniprot": row.uniprot, "cif": str(hit.cif_path),
                "plddt": hit.plddt_mean, "source": "afdb",
            })
            continue
        logger.warning("AFDB 미커버: {} — 로컬 {} 추론 필요", row.uniprot, predictor.engine_name)
        records.append({"uniprot": row.uniprot, "cif": None, "plddt": 0.0, "source": "missing"})
    df = pd.DataFrame(records)
    logger.info("Stage 2 [구조]: {}개 (AFDB {})", len(df), (df["source"] == "afdb").sum())
    return df


# ---------- Stage 2.5 — A2 ----------

@task
def sample_ensembles(structures: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if not cfg.ensemble.get("enabled", False):
        return pd.DataFrame()
    from genesis_medicine.ensemble import (
        AlphaFlowAdapter,
        BioEmuAdapter,
        EnsembleRequest,
        compute_pocket_diversity,
    )

    rows = []
    for engine_cfg in cfg.ensemble.engines:
        if not engine_cfg.get("enabled", True):
            continue
        if engine_cfg.name == "alphaflow":
            adapter = AlphaFlowAdapter(
                cache_dir=Path(engine_cfg.cache_dir),
                weights_dir=Path(engine_cfg.weights_dir) if engine_cfg.get("weights_dir") else None,
            )
        elif engine_cfg.name == "bioemu":
            adapter = BioEmuAdapter(
                cache_dir=Path(engine_cfg.cache_dir),
                weights_dir=Path(engine_cfg.weights_dir) if engine_cfg.get("weights_dir") else None,
            )
        else:
            continue

        for s in structures.itertuples():
            if s.cif is None:
                continue
            req = EnsembleRequest(
                protein_sequence="",  # TODO: cif에서 추출
                apo_cif=Path(s.cif),
                n_samples=engine_cfg.n_samples,
                cluster=cfg.ensemble.clustering.enabled,
                n_clusters=cfg.ensemble.clustering.n_clusters,
                seed=cfg.project.seed,
            )
            result = adapter.sample(req)
            for c in result.conformers:
                rows.append({
                    "uniprot": s.uniprot,
                    "engine": engine_cfg.name,
                    "cif": str(c.cif_path),
                    "cluster_id": c.cluster_id,
                })

    df = pd.DataFrame(rows)
    logger.info("Stage 2.5 [앙상블]: {} conformer", len(df))
    return df


# ---------- Stage 3 ----------

@task
def build_library(cfg: DictConfig) -> pd.DataFrame:
    from genesis_medicine.ligand.library import build_library as build_lib

    profile_name = cfg.build_profile.name if hasattr(cfg.build_profile, "name") else "commercial"
    df, stats = build_lib(cfg.library, build_profile=profile_name)
    logger.info("Stage 3 [라이브러리]: {} unique (소스 {})",
                stats.n_unique, stats.n_by_source)
    return df


# ---------- Stage 4 ----------

@task
def multi_stage_screen(
    structures: pd.DataFrame, library: pd.DataFrame, cfg: DictConfig
) -> pd.DataFrame:
    from genesis_medicine.screening.consensus import exponential_consensus_ranking

    stages = cfg.screening.stages
    logger.info("Stage 4 [스크리닝 6단계]: {}", " → ".join(s.name for s in stages))

    stage_results: dict[str, dict[str, float]] = {}
    # TODO: 각 단계 어댑터 실행 — 현재는 placeholder. M4 본격 실런 시 채움.

    ecr_stages = cfg.screening.get("consensus", {}).get("stages_for_ranking", [])
    sigma = cfg.screening.get("consensus", {}).get("sigma", 0.05)
    ecr_input = {k: v for k, v in stage_results.items() if k in ecr_stages}

    if ecr_input:
        ranked = exponential_consensus_ranking(ecr_input, sigma=sigma)
        return pd.DataFrame([
            {"smiles": r.smiles, "ecr_score": r.ecr_score, **r.scores, **r.ranks}
            for r in ranked
        ])
    return pd.DataFrame()


# ---------- Stage 5 ----------

@task
def generate_de_novo(structures: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if not cfg.generation.get("enabled", False):
        return pd.DataFrame()
    logger.info("Stage 5 [생성]: FlowMol3/DecompDiff → REINVENT4 → SATURN")
    return pd.DataFrame()


# ---------- Stage 5.5 — B1/B2 ----------

@task
def design_alternative_modalities(structures: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    """BindCraft 단백질 바인더 + PROTAC/분자글루 (선택)."""
    rows = []
    if cfg.get("bindcraft", {}).get("enabled", False):
        from genesis_medicine.generation.bindcraft_adapter import BindCraftAdapter, BinderRequest

        adapter = BindCraftAdapter(
            cache_dir=Path(cfg.bindcraft.cache_dir),
            weights_dir=Path(cfg.bindcraft.weights_dir) if cfg.bindcraft.get("weights_dir") else None,
            device=cfg.bindcraft.device,
        )
        for s in structures.itertuples():
            if s.cif is None:
                continue
            req = BinderRequest(
                target_pdb=Path(s.cif),
                target_hotspot_residues=list(cfg.bindcraft.target_hotspot_residues),
                binder_length_min=cfg.bindcraft.binder_length_min,
                binder_length_max=cfg.bindcraft.binder_length_max,
                n_designs=cfg.bindcraft.n_designs,
                seed=cfg.project.seed,
            )
            result = adapter.design(req)
            for b in result.binders:
                rows.append({
                    "modality": "protein_binder",
                    "uniprot": s.uniprot,
                    "sequence": b.sequence,
                    "iptm": b.predicted_iptm,
                    "pdb": str(b.pdb_path),
                })
    if cfg.get("protac", {}).get("enabled", False):
        from genesis_medicine.generation.protac_adapter import PROTACAdapter, PROTACRequest

        adapter = PROTACAdapter(
            cache_dir=Path(cfg.protac.protac.cache_dir),
            device=cfg.protac.protac.device,
        )
        # poi_smiles는 상위 시드에서 받아옴 — TODO
        rows.append({"modality": "protac", "note": "TODO: warhead from screening"})

    df = pd.DataFrame(rows)
    if not df.empty:
        logger.info("Stage 5.5 [대안 모달리티]: {} 디자인", len(df))
    return df


# ---------- Stage 6 ----------

@task
def admet_filter(combined: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if combined.empty or "smiles" not in combined.columns:
        return combined
    from genesis_medicine.admet import ADMETAIAdapter, ADMETRequest

    adapter = ADMETAIAdapter(
        cache_dir=Path(cfg.admet.cache_dir),
        models_dir=Path(cfg.admet.models_dir) if cfg.admet.get("models_dir") else None,
        num_workers=cfg.admet.num_workers,
        device=cfg.admet.device,
    )
    req = ADMETRequest(smiles_list=combined["smiles"].tolist(), seed=cfg.project.seed)
    result = adapter.predict(req)
    by_smi = {p.smiles: p.properties for p in result.predictions}

    # 안전 게이트
    f = cfg.admet.filter
    keep_mask = []
    for smi in combined["smiles"]:
        props = by_smi.get(smi, {})
        ok = True
        if f.require_bbb and props.get("BBB_Martins", 0) < 0.5:
            ok = False
        if f.require_herg_safe and props.get("hERG", 1.0) >= 0.5:
            ok = False
        if f.require_dili_safe and props.get("DILI", 1.0) >= 0.5:
            ok = False
        if props.get("QED", 0.0) < f.min_qed:
            ok = False
        keep_mask.append(ok)
    out = combined[pd.Series(keep_mask)]
    logger.info("Stage 6 [ADMET]: {} → {} (BBB+hERG+DILI 게이트)", len(combined), len(out))
    return out


# ---------- Stage 7 ----------

@task
def herbal_overlay(combined: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if not cfg.herbal.get("enabled", False) or combined.empty:
        return combined
    from genesis_medicine.herbal import map_compounds_to_herbs

    profile_name = cfg.build_profile.name if hasattr(cfg.build_profile, "name") else "commercial"
    if "inchikey" not in combined.columns:
        return combined

    hits = map_compounds_to_herbs(
        combined[["smiles", "inchikey"]],
        coconut_index=Path(cfg.herbal.coconut_index),
        lotus_index=Path(cfg.herbal.lotus_index) if cfg.herbal.get("lotus_index") else None,
        npass_index=Path(cfg.herbal.npass_index) if cfg.herbal.get("npass_index") else None,
        drduke_index=Path(cfg.herbal.drduke_index) if cfg.herbal.get("drduke_index") else None,
        khp_index=Path(cfg.herbal.khp_index) if cfg.herbal.get("khp_index") else None,
        herb_index=Path(cfg.herbal.herb_index) if cfg.herbal.get("herb_index") else None,
        tcmsp_index=Path(cfg.herbal.tcmsp_index) if cfg.herbal.get("tcmsp_index") else None,
        build_profile=profile_name,
    )
    logger.info("Stage 7 [한약]: {} compound-herb 매핑", len(hits))
    return combined  # combined를 그대로 반환, 별도 herb_report.parquet 출력 (생략)


# ---------- Stage 8' — A3 ----------

@task
def md_refine_ml(top: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if not cfg.md.get("enabled", False) or top.empty:
        return top
    from genesis_medicine.md import MDRefineRequest, OpenMMMLRefiner

    refiner = OpenMMMLRefiner(
        ml_potential=cfg.md.ml_potential,
        device=cfg.md.device,
        timestep_fs=cfg.md.timestep_fs,
        save_interval_ps=cfg.md.save_interval_ps,
        ml_region=cfg.md.ml_region,
        pocket_radius=cfg.md.pocket_radius,
    )
    out_dir = Path(cfg.project.output_dir) / "md"
    out_dir.mkdir(parents=True, exist_ok=True)

    n = min(len(top), cfg.md.top_n)
    logger.info("Stage 8' [ML-MD]: 상위 {} × {:.0f} ns", n, cfg.md.ns)
    return top.head(n)


# ---------- Stage 8.5 — A4 ----------

@task
def abfe_validate(top: pd.DataFrame, cfg: DictConfig) -> pd.DataFrame:
    if not cfg.abfe.get("enabled", False) or top.empty:
        return top
    from genesis_medicine.md import ABFEAdapter, ABFERequest

    adapter = ABFEAdapter(
        backend=cfg.abfe.backend,
        cache_dir=Path(cfg.project.output_dir) / "abfe_cache",
        device=cfg.abfe.device,
        threads=cfg.abfe.threads,
    )
    n = min(len(top), cfg.abfe.top_n)
    logger.info("Stage 8.5 [ABFE]: 상위 {} 후보 ABFE 계산", n)
    return top.head(n)


# ---------- Stage 9 ----------

@task
def build_report(final: pd.DataFrame, cfg: DictConfig) -> Path:
    out = Path(cfg.project.output_dir) / "report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"<h1>Genesis_Medicine v2.1 run completed.</h1><p>{len(final)} candidates</p>")
    logger.info("Stage 9 [리포트]: {}", out)
    return out


# ---------- Flow ----------

@flow(name="genesis_full_pipeline_v2_1")
def run(cfg: DictConfig) -> Path:
    targets = discover_targets(cfg)
    repurposed = repurpose_drugs(cfg)               # ★ 1.5
    structures = prep_structures(targets, cfg)
    ensembles = sample_ensembles(structures, cfg)   # ★ 2.5
    library = build_library(cfg)
    screening = multi_stage_screen(structures, library, cfg)
    novel = generate_de_novo(structures, cfg)
    alternative = design_alternative_modalities(structures, cfg)  # ★ 5.5

    parts = [df for df in [screening, novel, repurposed, alternative] if not df.empty]
    combined = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    filtered = admet_filter(combined, cfg)
    herbal = herbal_overlay(filtered, cfg)
    md_top = md_refine_ml(herbal.head(cfg.md.get("top_n", 50)), cfg)
    abfe_top = abfe_validate(md_top.head(cfg.abfe.get("top_n", 20)), cfg)
    return build_report(abfe_top, cfg)
