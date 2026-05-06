"""Build a master gap-closure matrix for world-class drug discovery claims.

This is a lightweight integration layer. It does not launch compute and does
not import TensorFlow/ADMET-AI. It consolidates the many local gates into one
candidate-level decision table so expensive compute, manuscript claims, and
CRO/wet-lab follow-up all use the same conservative rules.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

import pandas as pd
from rdkit import Chem, RDLogger


RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/WORLD_CLASS_GAP_CLOSURE.md"
CSV_OUT = OUT / "world_class_gap_closure_matrix.csv"
POLICY_OUT = ROOT / "pilot/auto_queue_decision_policy.json"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def prepare_table(df: pd.DataFrame) -> pd.DataFrame:
    """Add cheap normalized helper columns used by repeated candidate matching."""
    if df.empty:
        return df
    df = df.copy()
    if "canonical_smiles" in df.columns:
        df["_canonical_smiles"] = df["canonical_smiles"].fillna("").astype(str).map(canonical)
    elif "smiles" in df.columns:
        df["_canonical_smiles"] = df["smiles"].fillna("").astype(str).map(canonical)
    for col in ("candidate_id", "compound", "analog_id", "job_id", "np_id", "design_id", "compound_id"):
        if col in df.columns:
            df[f"_{col}"] = df[col].fillna("").astype(str)
    if "target" in df.columns:
        df["_target"] = df["target"].fillna("").astype(str).str.lower().replace({"nan": ""})
    return df


def clean(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def canonical(smiles: str) -> str:
    mol = Chem.MolFromSmiles(clean(smiles))
    return Chem.MolToSmiles(mol, canonical=True) if mol else clean(smiles)


def first_present(row: pd.Series, names: Iterable[str], default: str = "") -> str:
    for name in names:
        if name in row:
            value = clean(row.get(name))
            if value:
                return value
    return default


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return max(sum(1 for _ in csv.reader(handle)) - 1, 0)
    except Exception:
        return 0


def json_ok_total(path: Path, expected: int = 0) -> tuple[int, int]:
    if not path.exists() or path.stat().st_size == 0:
        return 0, expected
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0, expected
    if not isinstance(rows, list):
        return 0, expected
    return sum(1 for row in rows if row.get("status") == "ok"), max(len(rows), expected)


def collect_candidates() -> list[dict[str, object]]:
    """Collect candidate rows from all major lead/triage sources."""
    candidates: dict[tuple[str, str, str], dict[str, object]] = {}

    def add(candidate_id: str, target: str, smiles: str, source: str, score: object = "") -> None:
        candidate_id = clean(candidate_id)
        target = clean(target).lower()
        smiles = canonical(smiles)
        if not smiles:
            return
        if not candidate_id:
            candidate_id = smiles
        key = (candidate_id, target, smiles)
        row = candidates.setdefault(
            key,
            {
                "candidate_id": candidate_id,
                "target": target,
                "smiles": smiles,
                "sources": set(),
                "upstream_scores": [],
            },
        )
        row["sources"].add(source)
        if clean(score):
            row["upstream_scores"].append(clean(score))

    source_specs = [
        (OUT / "structure_consensus_v2.csv", "structure_consensus_v2", ["compound", "candidate_id"], ["target"], ["smiles"], ["consensus_v2_score"]),
        (OUT / "free_energy_validation_plan.csv", "free_energy_plan", ["compound", "candidate_id"], ["target"], ["smiles"], ["priority_score"]),
        (OUT / "r16_chromanol_topical_cofold.csv", "r16_chromanol_cofold", ["analog_id", "compound", "candidate_id"], ["target"], ["smiles"], ["affinity_probability_binary"]),
        (OUT / "r15_chromanol_cofold_14targets.csv", "r15_chromanol_cofold", ["compound", "candidate_id"], ["target"], ["smiles"], ["affinity_probability_binary"]),
        (OUT / "active_learning_next_candidates.csv", "active_learning", ["candidate_id"], ["target"], ["smiles"], ["acquisition_score"]),
        (OUT / "npass_xtb_refine_best_candidates.csv", "npass_xtb", ["np_id", "candidate_id"], ["target"], ["smiles"], ["topical_xtb_priority"]),
        (OUT / "chromanol_generative_optimizer.csv", "chromanol_generator", ["design_id", "candidate_id"], ["target"], ["smiles"], ["local_design_priority"]),
        (OUT / "dermal_regulatory_safety_gate.csv", "dermal_regulatory", ["candidate_id"], ["target"], ["smiles"], [""]),
        (OUT / "quinone_safety_gate.csv", "quinone_safety", ["candidate_id"], ["target"], ["smiles"], [""]),
    ]
    for path, source, id_cols, target_cols, smiles_cols, score_cols in source_specs:
        df = read_csv(path)
        if df.empty:
            continue
        for _, row in df.iterrows():
            add(
                first_present(row, id_cols),
                first_present(row, target_cols),
                first_present(row, smiles_cols),
                source,
                first_present(row, score_cols),
            )

    for path in sorted(OUT.glob("r17_chromanol_generative_batch*_cofold.csv")):
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        for _, row in df.iterrows():
            add(
                first_present(row, ["job_id", "design_id", "candidate_id"]),
                first_present(row, ["target"]),
                first_present(row, ["smiles"]),
                path.name,
                first_present(row, ["affinity_probability_binary", "local_design_priority"]),
            )

    for path in sorted(OUT.glob("active_learning_next_cofold_batch*.csv")):
        if path.stem.endswith("_manifest"):
            continue
        df = read_csv(path)
        if df.empty or "smiles" not in df.columns:
            continue
        for _, row in df.iterrows():
            add(
                first_present(row, ["candidate_id", "job_id"]),
                first_present(row, ["target"]),
                first_present(row, ["smiles"]),
                path.name,
                first_present(row, ["affinity_probability_binary", "affinity_probability", "acquisition_score"]),
            )

    out = []
    for row in candidates.values():
        row["sources"] = ";".join(sorted(row["sources"]))
        row["upstream_scores"] = ";".join(row["upstream_scores"][:6])
        out.append(row)
    return out


def target_match(df: pd.DataFrame, target: str) -> pd.DataFrame:
    if df.empty or "target" not in df.columns or not target:
        return df.iloc[0:0]
    return df[df["target"].fillna("").astype(str).str.lower().eq(target)]


def candidate_matches(
    df: pd.DataFrame,
    candidate_id: str,
    target: str,
    smiles: str,
    id_cols: Iterable[str] = ("candidate_id", "compound", "analog_id", "job_id", "np_id", "design_id"),
) -> pd.DataFrame:
    if df.empty:
        return df
    masks = []
    candidate_id = clean(candidate_id)
    target = clean(target).lower()
    smiles = canonical(smiles)
    for col in id_cols:
        norm_col = f"_{col}"
        if norm_col in df.columns and candidate_id:
            masks.append(df[norm_col].eq(candidate_id))
    if "_canonical_smiles" in df.columns and smiles:
        masks.append(df["_canonical_smiles"].eq(smiles))
    if not masks:
        return df.iloc[0:0]
    mask = masks[0]
    for item in masks[1:]:
        mask = mask | item
    sub = df[mask].copy()
    if not sub.empty and "_target" in sub.columns and target:
        target_text = sub["_target"]
        exact = sub[target_text.eq(target)]
        blank = sub[target_text.eq("")]
        if not exact.empty:
            sub = exact
        elif not blank.empty:
            sub = blank
    return sub


def first_value(df: pd.DataFrame, col: str, default: str = "missing") -> str:
    if df.empty or col not in df.columns:
        return default
    for value in df[col].tolist():
        text = clean(value)
        if text:
            return text
    return default


def worst_value(df: pd.DataFrame, col: str, order: dict[str, int], default: str = "missing") -> str:
    if df.empty or col not in df.columns:
        return default
    values = [clean(v) for v in df[col].tolist() if clean(v)]
    if not values:
        return default
    return max(values, key=lambda v: order.get(v, -1))


def assess(row: dict[str, object], tables: dict[str, pd.DataFrame], zaff_status: str) -> dict[str, object]:
    candidate_id = clean(row["candidate_id"])
    target = clean(row["target"]).lower()
    smiles = clean(row["smiles"])

    prior = candidate_matches(tables["prior"], candidate_id, target, smiles)
    ip = candidate_matches(tables["ip"], candidate_id, target, smiles)
    synth = candidate_matches(tables["synth"], candidate_id, target, smiles)
    route = candidate_matches(tables["route"], candidate_id, target, smiles)
    structure = candidate_matches(tables["structure"], candidate_id, target, smiles, ("candidate_id", "compound", "job_id"))
    benchmark = candidate_matches(tables["benchmark"], candidate_id, target, smiles, ("candidate_id", "compound", "job_id"))
    fe = candidate_matches(tables["fe"], candidate_id, target, smiles, ("candidate_id", "compound", "job_id"))
    dermal = candidate_matches(tables["dermal"], candidate_id, target, smiles)
    dermal_reg = candidate_matches(tables["dermal_reg"], candidate_id, target, smiles)
    photo = candidate_matches(tables["photo"], candidate_id, target, smiles)
    quinone = candidate_matches(tables["quinone"], candidate_id, target, smiles)
    metabolite = candidate_matches(tables["metabolite"], candidate_id, target, smiles)
    phenomics = candidate_matches(tables["phenomics"], candidate_id, target, smiles)
    engagement = candidate_matches(tables["engagement"], candidate_id, target, smiles, ("candidate_id", "compound", "job_id"))
    cmc = candidate_matches(tables["cmc"], candidate_id, target, smiles)
    uncertainty = candidate_matches(tables["uncertainty"], candidate_id, target, smiles)
    dmtl = candidate_matches(tables["dmtl"], candidate_id, target, smiles)
    formulation = candidate_matches(tables["formulation"], candidate_id, target, smiles, ("candidate_id", "compound_id"))
    target_rows = target_match(tables["target"], target)

    precompute_gate = worst_value(
        prior,
        "precompute_gate",
        {
            "cheap_compute_allowed_prior_art_pending": 1,
            "hold_expensive_compute_until_markush_review": 2,
            "hold_expensive_compute_until_prior_art_review": 3,
            "deprioritize_or_benchmark_only": 4,
        },
    )
    ip_risk = worst_value(ip, "ip_fto_risk", {"baseline_watch": 1, "medium_review": 2, "high_review": 3})
    synthesis_gate = worst_value(synth, "synthesis_gate", {"green": 1, "yellow": 2, "red": 3})
    route_gate = worst_value(route, "route_gate", {"route_ready": 1, "route_review": 2, "route_hard": 3})
    claim_readiness = worst_value(
        structure,
        "claim_readiness",
        {"claim_ready_in_silico": 1, "claim_with_caveat": 2, "needs_cross_model": 3, "triage_only": 4},
    )
    benchmark_gate = worst_value(
        benchmark,
        "structure_benchmark_gate",
        {
            "benchmark_ready_as_caveat": 1,
            "benchmark_low_priority": 2,
            "cross_model_first": 3,
            "benchmark_decoys_required_before_strong_claim": 4,
        },
    )
    fe_method = first_value(fe, "recommended_fe_method")
    openfe_status = first_value(fe, "openfe_status")
    dermal_pbpk_gate = worst_value(
        dermal,
        "dermal_pbpk_gate",
        {"ivpt_pbpk_ready": 1, "formulation_rescue_needed": 2, "pbpk_low_confidence": 3, "structure_fix": 4},
    )
    dermal_gate = worst_value(dermal_reg, "dermal_gate", {"green": 1, "yellow": 2, "red": 3})
    photosafety_gate = worst_value(photo, "safety_gate_v2", {"green": 1, "yellow": 2, "red": 3})
    quinone_gate = worst_value(quinone, "quinone_safety_gate", {"no_quinone_alert": 1, "quinone_reactivity_review": 3})
    metabolite_gate = worst_value(metabolite, "metabolite_risk_gate", {"low_reactive_alert": 1, "reactive_metabolite_review": 3})
    phenomics_gate = worst_value(
        phenomics,
        "phenomics_gate",
        {
            "priority_cell_painting": 1,
            "phenomics_with_safety_counterscreen": 2,
            "reference_signature_lookup": 2,
            "hold_safety_first": 3,
        },
    )
    engagement_gate = worst_value(
        engagement,
        "target_engagement_gate",
        {
            "engagement_assay_ready": 1,
            "cellular_engagement_preferred": 1,
            "deconvolution_first": 2,
            "engagement_low_priority": 3,
        },
    )
    cmc_gate = worst_value(cmc, "developability_gate", {"green": 1, "yellow": 2, "red": 3})
    applicability_domain = worst_value(
        uncertainty,
        "applicability_domain",
        {"in_domain": 1, "activity_cliff_risk": 2, "novel_scaffold": 2, "high_model_uncertainty": 3},
    )
    target_gate = first_value(target_rows, "gate")
    dmtl_bucket = first_value(dmtl, "decision_bucket")
    formulation_action = first_value(formulation, "next_action")

    hard_blockers: list[str] = []
    caveats: list[str] = []
    boosts: list[str] = []

    if precompute_gate == "hold_expensive_compute_until_prior_art_review":
        hard_blockers.append("public exact/same-connectivity prior-art review required")
    elif precompute_gate == "hold_expensive_compute_until_markush_review":
        caveats.append("Markush/FTO review required before heavy follow-up")
    elif precompute_gate == "deprioritize_or_benchmark_only":
        hard_blockers.append("benchmark-only prior-art class")

    if ip_risk == "high_review":
        hard_blockers.append("high IP/FTO review risk")
    elif ip_risk == "medium_review":
        caveats.append("medium IP/FTO/Markush review risk")

    if target == "mmp1" and zaff_status != "ready_for_zaff_parameterization":
        hard_blockers.append("MMP-1 holo-Zn ZAFF/MCPB ABFE gate not passed")
    if "EMB" in candidate_id.upper() or quinone_gate == "quinone_reactivity_review":
        hard_blockers.append("quinone reactivity/sensitization package required")

    if synthesis_gate == "red" or route_gate == "route_hard":
        hard_blockers.append("synthesis route risk too high")
    elif synthesis_gate == "yellow" or route_gate == "route_review":
        caveats.append("true retrosynthesis or chemist route review required")

    if target_gate == "red":
        hard_blockers.append("target evidence red")
    elif target_gate == "yellow":
        caveats.append("target evidence yellow: phenotype/cell context required")

    if claim_readiness in {"needs_cross_model", "triage_only"}:
        caveats.append("cross-model/PLIF/negative-control validation required")
    if benchmark_gate in {"cross_model_first", "benchmark_decoys_required_before_strong_claim"}:
        caveats.append("benchmark decoys or orthogonal structure model required")
    if openfe_status == "openfe_missing_install_or_env" and fe_method in {"RBFE_network", "ABFE_scout", "ABFE_or_CBFE_scout"}:
        caveats.append("OpenFE/RBFE environment missing")

    if dermal_gate == "red" or photosafety_gate == "red":
        hard_blockers.append("dermal/photosafety red gate")
    elif dermal_gate == "yellow" or photosafety_gate == "yellow":
        caveats.append("OECD TG497/ICH S10 safety counterscreen required")
    if metabolite_gate == "reactive_metabolite_review":
        caveats.append("reactive metabolite review required")
    if dermal_pbpk_gate == "ivpt_pbpk_ready":
        boosts.append("finite-dose IVRT/IVPT/PBPK ready")
    elif dermal_pbpk_gate == "formulation_rescue_needed":
        caveats.append("formulation rescue before exposure claim")
    if cmc_gate == "red":
        hard_blockers.append("CMC/developability red gate")
    elif cmc_gate == "yellow":
        caveats.append("CMC/developability yellow gate")
    if applicability_domain in {"activity_cliff_risk", "novel_scaffold", "high_model_uncertainty"}:
        caveats.append(f"model applicability-domain caveat: {applicability_domain}")
    if phenomics_gate == "priority_cell_painting":
        boosts.append("Cell Painting / disease-cell phenotype priority")
    if engagement_gate in {"engagement_assay_ready", "cellular_engagement_preferred"}:
        boosts.append("target-engagement assay card ready")
    if dmtl_bucket == "single_point_wetlab_card":
        boosts.append("single-point wet-lab DMTL card ready")

    if hard_blockers:
        readiness = "hold_or_benchmark_only"
        heavy_permission = "hold"
        paper_permission = "methods_or_caveated_only"
        next_action = "; ".join(hard_blockers[:3])
    elif precompute_gate == "hold_expensive_compute_until_markush_review" or ip_risk == "medium_review":
        readiness = "cheap_compute_or_paper_with_fto_caveat"
        heavy_permission = "short_triage_only"
        paper_permission = "in_silico_with_fto_caveat"
        next_action = "prepare Markush/FTO package; use only completed data for caveated papers"
    elif claim_readiness in {"claim_ready_in_silico", "claim_with_caveat"} and boosts:
        readiness = "wetlab_translation_priority"
        heavy_permission = "wetlab_first_or_short_triage"
        paper_permission = "in_silico_main_table_with_caveats"
        next_action = "build CRO/DMTL package before larger GPU expansion"
    elif claim_readiness in {"claim_ready_in_silico", "claim_with_caveat"}:
        readiness = "paper_ready_in_silico"
        heavy_permission = "eligible_after_orthogonal_check"
        paper_permission = "in_silico_main_table_with_caveats"
        next_action = "add orthogonal model/decoy/PLIF or FE plan before stronger claim"
    else:
        readiness = "triage_accumulating"
        heavy_permission = "cheap_compute_only"
        paper_permission = "supplement_or_atlas_only"
        next_action = "; ".join(caveats[:3]) if caveats else "continue cheap triage and rank consolidation"

    return {
        **row,
        "precompute_gate": precompute_gate,
        "ip_fto_risk": ip_risk,
        "target_gate": target_gate,
        "synthesis_gate": synthesis_gate,
        "route_gate": route_gate,
        "claim_readiness": claim_readiness,
        "structure_benchmark_gate": benchmark_gate,
        "recommended_fe_method": fe_method,
        "openfe_status": openfe_status,
        "dermal_gate": dermal_gate,
        "dermal_pbpk_gate": dermal_pbpk_gate,
        "photosafety_gate": photosafety_gate,
        "quinone_safety_gate": quinone_gate,
        "metabolite_risk_gate": metabolite_gate,
        "phenomics_gate": phenomics_gate,
        "target_engagement_gate": engagement_gate,
        "developability_gate": cmc_gate,
        "applicability_domain": applicability_domain,
        "dmtl_bucket": dmtl_bucket,
        "formulation_next_action": formulation_action,
        "global_readiness": readiness,
        "heavy_compute_permission": heavy_permission,
        "paper_permission": paper_permission,
        "hard_blockers": "; ".join(hard_blockers),
        "caveats": "; ".join(caveats),
        "positive_translation_signals": "; ".join(boosts),
        "next_best_action": next_action,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    tables = {
        "prior": prepare_table(read_csv(OUT / "precompute_prior_art_gate.csv")),
        "ip": prepare_table(read_csv(OUT / "ip_fto_watchlist.csv")),
        "synth": prepare_table(read_csv(OUT / "synthesis_retrosynthesis_gate.csv")),
        "route": prepare_table(read_csv(OUT / "route_enumeration_gate.csv")),
        "structure": prepare_table(read_csv(OUT / "structure_consensus_v2.csv")),
        "benchmark": prepare_table(read_csv(OUT / "structure_benchmark_decoy_gate.csv")),
        "fe": prepare_table(read_csv(OUT / "free_energy_validation_plan.csv")),
        "dermal": prepare_table(read_csv(OUT / "dermal_pbpk_ivpt_gate.csv")),
        "dermal_reg": prepare_table(read_csv(OUT / "dermal_regulatory_safety_gate.csv")),
        "photo": prepare_table(read_csv(OUT / "photosafety_sensitization_v2.csv")),
        "quinone": prepare_table(read_csv(OUT / "quinone_safety_gate.csv")),
        "metabolite": prepare_table(read_csv(OUT / "metabolite_reactive_risk_gate.csv")),
        "target": prepare_table(read_csv(OUT / "target_evidence_gate.csv")),
        "phenomics": prepare_table(read_csv(OUT / "phenomics_signature_gate.csv")),
        "engagement": prepare_table(read_csv(OUT / "target_engagement_assay_gate.csv")),
        "cmc": prepare_table(read_csv(OUT / "developability_cmc_gate.csv")),
        "uncertainty": prepare_table(read_csv(OUT / "model_validation_uncertainty_gate.csv")),
        "dmtl": prepare_table(read_csv(OUT / "dmtl_experiment_cards.csv")),
        "formulation": prepare_table(read_csv(OUT / "topical_formulation_bo_plan.csv")),
    }
    creative = read_csv(OUT / "creative_discovery_gap_matrix.csv")
    creative_policy = {}
    creative_policy_path = ROOT / "pilot/creative_discovery_queue_policy.json"
    if creative_policy_path.exists() and creative_policy_path.stat().st_size > 0:
        try:
            loaded = json.loads(creative_policy_path.read_text(encoding="utf-8"))
            creative_policy = loaded if isinstance(loaded, dict) else {}
        except Exception:
            creative_policy = {}
    zaff = read_csv(OUT / "mmp1_zaff_abfe_gate.csv")
    zaff_status = first_value(zaff, "status", "missing")
    rows = [assess(row, tables, zaff_status) for row in collect_candidates()]

    order = {
        "wetlab_translation_priority": 0,
        "paper_ready_in_silico": 1,
        "cheap_compute_or_paper_with_fto_caveat": 2,
        "triage_accumulating": 3,
        "hold_or_benchmark_only": 4,
    }
    rows.sort(key=lambda r: (order.get(clean(r["global_readiness"]), 9), clean(r["candidate_id"]), clean(r["target"])))

    fieldnames = [
        "candidate_id",
        "target",
        "smiles",
        "sources",
        "upstream_scores",
        "global_readiness",
        "heavy_compute_permission",
        "paper_permission",
        "precompute_gate",
        "ip_fto_risk",
        "target_gate",
        "synthesis_gate",
        "route_gate",
        "claim_readiness",
        "structure_benchmark_gate",
        "recommended_fe_method",
        "openfe_status",
        "dermal_gate",
        "dermal_pbpk_gate",
        "photosafety_gate",
        "quinone_safety_gate",
        "metabolite_risk_gate",
        "phenomics_gate",
        "target_engagement_gate",
        "developability_gate",
        "applicability_domain",
        "dmtl_bucket",
        "positive_translation_signals",
        "hard_blockers",
        "caveats",
        "next_best_action",
        "formulation_next_action",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])

    readiness_counts = Counter(clean(row["global_readiness"]) for row in rows)
    permission_counts = Counter(clean(row["heavy_compute_permission"]) for row in rows)
    paper_counts = Counter(clean(row["paper_permission"]) for row in rows)
    by_target = defaultdict(Counter)
    for row in rows:
        by_target[clean(row["target"]) or "untargeted"][clean(row["global_readiness"])] += 1
    creative_status_counts = (
        Counter(clean(value) for value in creative["current_status"].tolist())
        if not creative.empty and "current_status" in creative.columns
        else Counter()
    )
    creative_gate_counts = (
        Counter(clean(value) for value in creative["readiness_gate"].tolist())
        if not creative.empty and "readiness_gate" in creative.columns
        else Counter()
    )
    target_cache_policy = creative_policy.get("target_cache", {}) if isinstance(creative_policy, dict) else {}

    r17_60_ok, r17_60_total = json_ok_total(
        ROOT / "pilot/md_r17_chromanol_generative_expanded_green_60ns/summary.json",
        expected=3,
    )
    policy = {
        "timestamp": now,
        "matrix_csv": str(CSV_OUT.relative_to(ROOT)),
        "matrix_doc": str(DOC.relative_to(ROOT)),
        "readiness_counts": dict(readiness_counts),
        "heavy_compute_permission_counts": dict(permission_counts),
        "paper_permission_counts": dict(paper_counts),
        "mmp1_zaff_status": zaff_status,
        "r17_expanded_green_60ns_ok": r17_60_ok,
        "r17_expanded_green_60ns_total": r17_60_total,
        "creative_discovery_status_counts": dict(creative_status_counts),
        "creative_discovery_gate_counts": dict(creative_gate_counts),
        "target_msa_missing_count": target_cache_policy.get("missing_a3m_count", "missing"),
        "global_queue_policy": {
            "finish_already_running_r17_expanded_60ns": r17_60_ok < r17_60_total,
            "allow_cpu_cheap_atlas": True,
            "no_new_chromanol_100_200ns_or_fe_or_synthesis_until_markush_fto": True,
            "no_mmp1_abfe_confirmed_claim_until_zaff_gate_pass": zaff_status != "ready_for_zaff_parameterization",
            "emb3_quinone_requires_wetlab_safety_package": True,
            "boltz_only_claims_require_cross_model_decoy_or_plif_before_strong_language": True,
            "wetlab_first_when_dmtl_or_ivpt_ready": True,
            "creative_generation_requires_synthesis_or_prior_art_guard": True,
            "active_learning_short_cofold_fallback_enabled": True,
            "cryptic_pocket_generation_requires_ensemble_pocket_gate": True,
            "phenomics_generation_requires_signature_or_assay_gate": True,
            "target_msa_coverage_gap_blocks_target_queue": bool(target_cache_policy.get("missing_a3m_count", 0)),
            "new_scaffold_gpu_followup_requires_uncertainty_and_benchmark_gate": True,
        },
        "top_next_actions": [
            {
                "candidate_id": row["candidate_id"],
                "target": row["target"],
                "readiness": row["global_readiness"],
                "heavy_compute_permission": row["heavy_compute_permission"],
                "next_best_action": row["next_best_action"],
            }
            for row in rows[:20]
        ],
    }
    POLICY_OUT.write_text(json.dumps(policy, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# World-Class Drug Discovery Gap Closure",
        "",
        f"- timestamp: `{now}`",
        f"- candidate_rows: `{len(rows)}`",
        f"- matrix_csv: `{CSV_OUT.relative_to(ROOT)}`",
        f"- queue_policy_json: `{POLICY_OUT.relative_to(ROOT)}`",
        f"- readiness_counts: `{dict(readiness_counts)}`",
        f"- heavy_compute_permission_counts: `{dict(permission_counts)}`",
        f"- creative_discovery_status_counts: `{dict(creative_status_counts)}`",
        f"- target MSA missing count: `{target_cache_policy.get('missing_a3m_count', 'missing')}`",
        f"- MMP-1 ZAFF status: `{zaff_status}`",
        "",
        "## Meaning",
        "",
        "이 파일은 개별 gate를 하나로 합친 master decision layer다. 후보가 좋은 cofold/MD 값을 가져도 prior-art, Markush/FTO, synthesis, safety, target biology, model uncertainty, dermal translation, FE readiness 중 하나가 막히면 비싼 계산이나 강한 claim으로 자동 승격하지 않는다.",
        "",
        "## Queue Policy",
        "",
        f"- R17 expanded green-target 60 ns: `{r17_60_ok}/{r17_60_total}` complete; already-running panel은 완료시킨다.",
        "- 새 chromanol 100-200 ns, RBFE/ABFE, synthesis/purchase, commercial novelty claim은 Markush/FTO review 전까지 보류한다.",
        "- NPASS/xTB/descriptor/atlas 같은 cheap CPU 계산은 계속 허용한다.",
        "- MMP-1 direct-binding 강화 claim은 ZAFF/MCPB holo-Zn ABFE gate 통과 전까지 금지한다.",
        "- EMB-3/quinone류는 GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox, photostability, skin S9/metabolite package 전까지 safety-positive claim 금지다.",
        "- creative generation은 synthesis/prior-art/novelty/uncertainty/phenomics guard 없이 신규 long-MD/FE/lead claim으로 올리지 않는다.",
        "- active-learning short cofold는 GPU 유휴 방지용 triage로 허용하지만, 결과는 master gate 통과 전까지 보조 evidence다.",
        "- target-key MSA가 없는 target은 cofold queue에서 차단하고 cache 준비를 먼저 한다.",
        "- `wetlab_translation_priority`는 더 큰 GPU 반복보다 CRO/DMTL/IVRT/IVPT/Cell Painting package를 먼저 만든다.",
        "",
        "## Readiness By Target",
        "",
        "| target | wetlab | paper | FTO-caveated | triage | hold |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for target, counts in sorted(by_target.items()):
        lines.append(
            f"| {target} | {counts.get('wetlab_translation_priority', 0)} | {counts.get('paper_ready_in_silico', 0)} | {counts.get('cheap_compute_or_paper_with_fto_caveat', 0)} | {counts.get('triage_accumulating', 0)} | {counts.get('hold_or_benchmark_only', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Top Action Rows",
            "",
            "| candidate | target | readiness | heavy compute | paper | blockers/caveats | next |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for item in rows[:50]:
        blockers = clean(item.get("hard_blockers")) or clean(item.get("caveats")) or clean(item.get("positive_translation_signals"))
        lines.append(
            f"| {item['candidate_id']} | {item['target']} | {item['global_readiness']} | {item['heavy_compute_permission']} | {item['paper_permission']} | {blockers} | {item['next_best_action']} |"
        )

    lines.extend(
        [
            "",
            "## System Gaps Now Covered",
            "",
            "- Cross-model/decoy/PLIF gap: `STRUCTURE_CONSENSUS_V2`와 `STRUCTURE_BENCHMARK_DECOY_GATE`를 master gate에 반영한다.",
            "- Free-energy gap: `FREE_ENERGY_VALIDATION_PLAN`, `RBFE_UPGRADE_READINESS`, `MMP1_ZAFF_ABFE_GATE`를 반영한다.",
            "- Prior-art/FTO gap: `PRECOMPUTE_PRIOR_ART_GATE`와 `IP_FTO_WATCHLIST`를 heavy-compute blocker로 반영한다.",
            "- Synthesis/route gap: `SYNTHESIS_RETROSYNTHESIS_GATE`와 `ROUTE_ENUMERATION_GATE`를 반영한다.",
            "- Topical translation gap: dermal regulatory, photosafety, dermal PBPK/IVPT, formulation BO, CMC gate를 반영한다.",
            "- Biology/phenotype gap: target evidence, phenomics, target engagement, DMTL card를 반영한다.",
            "- ML/governance gap: applicability-domain uncertainty와 model governance/provenance caveat를 queue policy에 반영한다.",
            "- Creative discovery gap: active-learning GPU fallback, target MSA coverage, scaffold-hop, synthesis-native generation, cryptic-pocket, ultra-large, reward-benchmark, phenomics-first rules를 반영한다.",
            "",
            "## Curator Rule",
            "",
            "- `hold_or_benchmark_only`: 비싼 GPU/FE/합성/상업 claim 금지. 논문은 limitation, method, benchmark로만 사용한다.",
            "- `cheap_compute_or_paper_with_fto_caveat`: 이미 끝난 데이터로 caveated in-silico paper는 가능하나 신규 long-MD/FE/synthesis는 보류한다.",
            "- `paper_ready_in_silico`: main table 가능하지만 confirmed binding, clinical efficacy, commercial novelty 표현은 금지한다.",
            "- `wetlab_translation_priority`: 다음 자원 투입은 CRO/wet-lab package가 우선이며, GPU 반복은 보조다.",
            "- active-learning cofold 결과는 완료 즉시 이 matrix에 들어오지만, short triage evidence라 long-MD/FE 승격은 synthesis/prior-art/safety/phenomics/uncertainty gate를 다시 통과해야 한다.",
            "- MC1R/RARG/TLR2/NLRP3처럼 target-key MSA가 없는 target은 cache 준비 전 자동 cofold를 큐잉하지 않는다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {CSV_OUT.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Saved {POLICY_OUT.relative_to(ROOT)}")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
