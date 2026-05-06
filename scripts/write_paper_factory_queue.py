"""Write the current paper-production queue from local result files.

This is a lightweight status generator. It does not launch compute and does not
import TensorFlow/ADMET-AI. The goal is to keep manuscript production tied to
what has actually finished on disk.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/PAPER_FACTORY_QUEUE.md"


def count_preprints() -> int:
    return len([p for p in (ROOT / "preprints").glob("*/manuscript.md")])


def count_pdf_preprints() -> int:
    return len([p for p in (ROOT / "preprints").glob("*/manuscript.pdf")])


def json_ok_total(path: Path, expected: int | None = None) -> tuple[int, int]:
    if not path.exists():
        return 0, expected or 0
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return 0, expected or 0
    if not isinstance(rows, list):
        return 0, expected or 0
    total = max(len(rows), expected or 0)
    return sum(1 for row in rows if row.get("status") == "ok"), total


def csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open(newline="") as handle:
            return max(0, sum(1 for _ in csv.reader(handle)) - 1)
    except Exception:
        return 0


def load_json_obj(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text())
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def exists(path: Path) -> str:
    return "yes" if path.exists() and path.stat().st_size > 0 else "no"


def has_draft(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def figure_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len([p for p in path.glob("*.png") if p.stat().st_size > 0])


def line_item(
    idx: int,
    title: str,
    status: str,
    evidence: str,
    next_action: str,
) -> str:
    return (
        f"| P{idx:02d} | {title} | {status} | {evidence} | {next_action} |"
    )


def main() -> int:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    r15_cofold_rows = csv_rows(OUT / "r15_chromanol_cofold_14targets.csv")
    r15_triage_rows = csv_rows(OUT / "r15_master_triage.csv")
    r16_cofold_rows = csv_rows(OUT / "r16_chromanol_topical_cofold.csv")
    r16_matrix_rows = csv_rows(OUT / "r16_topical_chromanol_30ns_matrix_summary.csv")
    npass_best_rows = csv_rows(OUT / "npass_xtb_refine_best_candidates.csv")

    r15_top3_ok, r15_top3_total = json_ok_total(PILOT / "md_r15_chromanol_top3_30ns/summary.json", 3)
    r16_tgfb1_60_ok, r16_tgfb1_60_total = json_ok_total(
        PILOT / "md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json", 6
    )
    pigment_60_ok, pigment_60_total = json_ok_total(
        PILOT / "md_r16_chromanol_topical_pigment_representative_60ns/summary.json", 3
    )
    anchor_100_ok, anchor_100_total = json_ok_total(
        PILOT / "md_r16_chromanol_anchor_triad_100ns/summary.json", 3
    )
    anchor_200_ok, anchor_200_total = json_ok_total(
        PILOT / "md_r16_chromanol_anchor_triad_200ns/summary.json", 3
    )
    extended_ok, extended_total = json_ok_total(PILOT / "md_extended_30ns_batch2/summary.json", 5)
    p17_draft = has_draft(ROOT / "preprints/16_r15_chromanol_safety_triage/manuscript.md")
    p16_draft = has_draft(ROOT / "preprints/17_r16_topical_chromanol_lead/manuscript.md")
    p17_complete = (
        p17_draft
        and exists(ROOT / "preprints/16_r15_chromanol_safety_triage/manuscript.pdf") == "yes"
        and figure_count(ROOT / "preprints/16_r15_chromanol_safety_triage/figures") >= 4
        and r15_top3_ok >= 3
    )
    p16_complete = (
        p16_draft
        and exists(ROOT / "preprints/17_r16_topical_chromanol_lead/manuscript.pdf") == "yes"
        and figure_count(ROOT / "preprints/17_r16_topical_chromanol_lead/figures") >= 5
        and anchor_200_ok >= 3
    )
    p23_outline = has_draft(ROOT / "docs/P23_PIGMENTATION_CHROMANOL_OUTLINE.md")
    p24_outline = has_draft(ROOT / "docs/P24_SCAR_FIBROSIS_TOPICAL_OUTLINE.md")
    pose_gate = load_json_obj(OUT / "chromanol_pose_sanity_gate_summary.json")
    target_gate = load_json_obj(OUT / "target_evidence_gate_summary.json")
    pose_gate_counts = pose_gate.get("gate_counts", {})
    target_gate_counts = target_gate.get("gate_counts", {})
    pose_gate_text = (
        "pose gate pass/review/fail="
        f"{pose_gate_counts.get('pass', 0)}/{pose_gate_counts.get('review', 0)}/{pose_gate_counts.get('fail', 0)}"
        if pose_gate_counts
        else "pose gate pending"
    )
    target_gate_text = (
        "target gate green/yellow/red="
        f"{target_gate_counts.get('green', 0)}/{target_gate_counts.get('yellow', 0)}/{target_gate_counts.get('red', 0)}"
        if target_gate_counts
        else "target gate pending"
    )
    modality_rows = csv_rows(OUT / "target_modality_matrix.csv")
    novelty_rows = csv_rows(OUT / "candidate_local_novelty_gate.csv")
    synthesis_rows = csv_rows(OUT / "synthesis_retrosynthesis_gate.csv")
    active_learning_rows = csv_rows(OUT / "active_learning_next_candidates.csv")
    active_learning_cofold_rows = sum(
        csv_rows(path)
        for path in OUT.glob("active_learning_next_cofold_batch*.csv")
        if not path.stem.endswith("_manifest")
    )
    active_learning_cofold_manifest_rows = sum(
        csv_rows(path) for path in OUT.glob("active_learning_next_cofold_batch*_manifest.csv")
    )
    bo_plan_rows = csv_rows(OUT / "multi_fidelity_bo_plan.csv")
    pocket_rows = csv_rows(OUT / "pocket_evidence_gate.csv")
    consensus_rows = csv_rows(OUT / "structure_consensus_calibration.csv")
    consensus_v2_rows = csv_rows(OUT / "structure_consensus_v2.csv")
    generative_rows = csv_rows(OUT / "chromanol_generative_optimizer.csv")
    r17_cofold_rows = sum(
        csv_rows(path) for path in OUT.glob("r17_chromanol_generative_batch*_cofold.csv")
    )
    planner = load_json_obj(PILOT / "auto_result_planner_latest.json")
    r17_cofold_target = (
        planner.get("gpu", {}).get("target_rows")
        if planner.get("gpu", {}).get("paper_candidate") == "r17_chromanol_generative_atlas"
        else None
    ) or 128
    r17_md_10_ok, r17_md_10_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_top_green_10ns/summary.json",
        expected=3,
    )
    r17_md_30_ok, r17_md_30_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_top_green_30ns/summary.json",
        expected=3,
    )
    r17_md_60_ok, r17_md_60_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_top_green_60ns/summary.json",
        expected=3,
    )
    r17_next_md_10_ok, r17_next_md_10_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_next_green_10ns/summary.json",
        expected=3,
    )
    r17_next_md_30_ok, r17_next_md_30_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_next_green_30ns/summary.json",
        expected=3,
    )
    r17_next_md_60_ok, r17_next_md_60_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_next_green_60ns/summary.json",
        expected=3,
    )
    r17_expanded_md_10_ok, r17_expanded_md_10_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_expanded_green_10ns/summary.json",
        expected=3,
    )
    r17_expanded_md_30_ok, r17_expanded_md_30_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_expanded_green_30ns/summary.json",
        expected=3,
    )
    r17_expanded_md_60_ok, r17_expanded_md_60_total = json_ok_total(
        PILOT / "md_r17_chromanol_generative_expanded_green_60ns/summary.json",
        expected=3,
    )
    route_enum_rows = csv_rows(OUT / "route_enumeration_gate.csv")
    skin_cell_rows = csv_rows(OUT / "skin_cell_state_evidence_gate.csv")
    photosafety_v2_rows = csv_rows(OUT / "photosafety_sensitization_v2.csv")
    quinone_safety_rows = csv_rows(OUT / "quinone_safety_gate.csv")
    dmtl_card_rows = csv_rows(OUT / "dmtl_experiment_cards.csv")
    skin_spatial_rows = csv_rows(OUT / "skin_spatial_atlas_gate.csv")
    target_engagement_rows = csv_rows(OUT / "target_engagement_assay_gate.csv")
    dermal_pbpk_rows = csv_rows(OUT / "dermal_pbpk_ivpt_gate.csv")
    metabolite_risk_rows = csv_rows(OUT / "metabolite_reactive_risk_gate.csv")
    genetic_causality_rows = csv_rows(OUT / "genetic_causality_direction_gate.csv")
    pharmacovigilance_rows = csv_rows(OUT / "pharmacovigilance_signal_gate.csv")
    single_cell_fm_rows = csv_rows(OUT / "single_cell_fm_reliability_gate.csv")
    structure_benchmark_rows = csv_rows(OUT / "structure_benchmark_decoy_gate.csv")
    formulation_rows = csv_rows(OUT / "topical_formulation_bo_plan.csv")
    fe_rows = csv_rows(OUT / "free_energy_validation_plan.csv")
    dermal_rows = csv_rows(OUT / "dermal_regulatory_safety_gate.csv")
    perturbation_rows = csv_rows(OUT / "perturbation_biology_gate.csv")
    hydration_rows = csv_rows(OUT / "hydration_kinetics_gate.csv")
    ultra_rows = csv_rows(OUT / "ultra_large_screening_roadmap.csv")
    uncertainty_rows = csv_rows(OUT / "model_validation_uncertainty_gate.csv")
    phenomics_rows = csv_rows(OUT / "phenomics_signature_gate.csv")
    cmc_rows = csv_rows(OUT / "developability_cmc_gate.csv")
    ip_fto_rows = csv_rows(OUT / "ip_fto_watchlist.csv")
    fair_rows = csv_rows(OUT / "fair_assay_dictionary.csv")
    wetlab_ingest_rows = csv_rows(OUT / "wetlab_feedback_ingested.csv")
    model_governance_rows = csv_rows(OUT / "ai_model_governance_registry.csv")
    world_gap_rows = csv_rows(OUT / "world_class_gap_closure_matrix.csv")
    world_policy = load_json_obj(PILOT / "auto_queue_decision_policy.json")
    world_readiness_counts = world_policy.get("readiness_counts", {})
    world_heavy_counts = world_policy.get("heavy_compute_permission_counts", {})
    creative_rows = csv_rows(OUT / "creative_discovery_gap_matrix.csv")
    creative_policy = load_json_obj(PILOT / "creative_discovery_queue_policy.json")
    creative_active = creative_policy.get("active_learning_short_cofold", {})
    creative_target_cache = creative_policy.get("target_cache", {})
    provenance_exists = exists(ROOT / "docs/RUN_PROVENANCE_MANIFEST.md")
    wetlab_exists = exists(ROOT / "docs/WETLAB_FEEDBACK_SCHEMA.md")

    items = [
        line_item(
            15,
            "Universal scaffold family across 14 skin targets",
            "ready/v1.8",
            f"PDF={exists(ROOT / 'preprints/15_universal_scaffold/manuscript.pdf')}; figures 1-10 integrated; batch2 {extended_ok}/{extended_total}",
            "Submit/update preprint; keep only in-silico claims.",
        ),
        line_item(
            16,
            "R16 topical chromanol lead paper",
            "complete PDF+figures; 200ns complete" if p16_complete else ("draft started + 100ns running" if anchor_100_ok < 3 else ("draft started + 200ns running" if anchor_200_ok < 3 else "draft started + 200ns complete")),
            f"R16 cofold rows={r16_cofold_rows}; 30ns matrix={r16_matrix_rows}; TGFB1 60ns={r16_tgfb1_60_ok}/{r16_tgfb1_60_total}; pigment 60ns={pigment_60_ok}/{pigment_60_total}; anchor 100ns={anchor_100_ok}/{anchor_100_total}; anchor 200ns={anchor_200_ok}/{anchor_200_total}; figures={figure_count(ROOT / 'preprints/17_r16_topical_chromanol_lead/figures')}; {pose_gate_text}",
            "Submission-ready as an in-silico preprint; next work is CRO/Markush/FTO package, not stronger efficacy or commercial claims." if p16_complete else ("Update manuscript/figures with the complete 200 ns long-horizon anchor triad; keep all claims in-silico and wet-lab-pending." if anchor_200_ok >= 3 else ("Keep drafting now; 100 ns is complete, then fold in 200 ns long-horizon anchor triad as it completes." if anchor_100_ok >= 3 else "Keep drafting now; fold in 100 ns anchor triad as soon as each target completes.")),
        ),
        line_item(
            17,
            "R15 chromanol safety-first fragment triage",
            "complete PDF+figures; prior-art caveat added" if p17_complete else ("draft started" if p17_draft else "ready for draft"),
            f"triage rows={r15_triage_rows}; 14-target cofold rows={r15_cofold_rows}; top3 30ns={r15_top3_ok}/{r15_top3_total}; figures={figure_count(ROOT / 'preprints/16_r15_chromanol_safety_triage/figures')}; {pose_gate_text}",
            "Submission-ready as a safety-first in-silico fragment triage; R15 parent exact PubChem hit keeps composition novelty/commercial claims blocked." if p17_complete else ("Build R15 figures/tables, pose-sanity table, and split-path discussion." if p17_draft else "Draft as split-path paper: systemic-safe fragment vs topical lead optimization; include pose-sanity gate table."),
        ),
        line_item(
            18,
            "NPASS topical natural-product xTB atlas",
            "accumulating",
            f"best candidate rows={npass_best_rows}; 96conf ladder partially complete",
            "Refresh ladder summary after each 96/120/144conf tier and select top candidates for Boltz-2 cofold.",
        ),
        line_item(
            19,
            "Conformer-ladder sensitivity in xTB natural-product triage",
            "accumulating",
            "12/24/36/48/72conf complete; 96conf running",
            "Compare rank stability by conformer depth; write methodology/results note after 96conf full tier.",
        ),
        line_item(
            20,
            "Skin PBPK + Potts-Guy permeability methodology",
            "existing preprint; update candidate",
            "preprint #14 exists; NPASS logKp proxy now feeds downstream ranking",
            "Revise with NPASS atlas examples and current Recover topical formulation caveats.",
        ),
        line_item(
            21,
            "Boltz-2/MD validation methodology and failure modes",
            "existing preprint; update candidate",
            f"preprint #8 exists; extended MD drift caveats and chromanol PoseBusters gate now available ({pose_gate_text})",
            "Update with SREBP1 x R14_5 late drift, raw-pose clash review, MD relaxation, and ABFE limitations.",
        ),
        line_item(
            22,
            "Korean herbal scaffold alignment and Tanimoto evidence",
            "draft candidate",
            "R14_5-ferulic acid 0.42; R12_23-EGCG 0.34; R12_4-EGCG 0.30",
            "Build herbal-alignment figures and write as translational perspective, not efficacy claim.",
        ),
        line_item(
            23,
            "Pigmentation-target focused chromanol/pterocarpan paper",
            "outline started" if p23_outline else ("ready for outline" if pigment_60_ok >= 3 else "awaiting more GPU"),
            f"DCT/TYR R16 30ns matrix complete; pigment 60ns={pigment_60_ok}/{pigment_60_total}",
            "Expand outline into manuscript sections and add pigment-focused figures/tables." if p23_outline else ("Outline DCT/TYR/TYRP1-focused narrative from completed pigment 60ns panel." if pigment_60_ok >= 3 else "After pigment representative 60ns completes, split DCT/TYR/TYRP1 narrative from universal scaffold paper."),
        ),
        line_item(
            24,
            "Scar/fibrosis TGFB1/MMP1-focused topical lead paper",
            "outline started" if p24_outline else "ready for outline",
            "R16 TGFB1 top6 60ns complete; MMP1 R12_4/R14_5 extended 30ns strong",
            "Expand outline into manuscript sections and CRO endpoint table." if p24_outline else "Draft target-focused paper for TGFB1/MMP1, with wet-lab CRO endpoint table.",
        ),
        line_item(
            25,
            "Target evidence and modality-gated dermatology discovery map",
            "ready for methods/results outline",
            f"{target_gate_text}; modality rows={modality_rows}; novelty rows={novelty_rows}",
            "Write as systems-improvement paper: Open Targets evidence, modality fit, and compute queue gating.",
        ),
        line_item(
            26,
            "Reproducible autonomous in-silico dermatology workflow",
            "ready for methods update",
            f"provenance manifest={provenance_exists}; wet-lab feedback schema={wetlab_exists}; auto planner/daemon active",
            "Use as methodology paper/update: provenance hashes, wet-lab feedback loop, and queue decision protocol.",
        ),
        line_item(
            27,
            "Synthesis-aware chromanol/natural-product candidate triage",
            "ready for methods/results outline",
            f"synthesis/retrosynthesis gate rows={synthesis_rows}; novelty rows={novelty_rows}",
            "Write as practical candidate-selection paper: availability, analog novelty, SA gate, and no-retrosynthesis caveat.",
        ),
        line_item(
            28,
            "Active-learning and multi-fidelity autonomous queueing",
            "ready for methods/results outline",
            f"active-learning rows={active_learning_rows}; BO/action plan rows={bo_plan_rows}; provenance manifest={provenance_exists}",
            "Write as systems paper: surrogate acquisition, cost-aware fidelity ladder, and protected queue rules.",
        ),
        line_item(
            29,
            "Topical formulation BO and IVRT/IVPT feedback workflow",
            "ready for translational-methods outline",
            f"formulation BO rows={formulation_rows}; wet-lab schema={wetlab_exists}",
            "Use for CRO-ready translational paper/RFQ appendix: IVRT, IVPT, retention, irritation, stability.",
        ),
        line_item(
            30,
            "Pocket and structure-consensus calibration for DL cofolding",
            "ready for methodology outline",
            f"pocket gate rows={pocket_rows}; structure consensus rows={consensus_rows}; {pose_gate_text}",
            "Write calibration/failure-mode paper around Boltz confidence, PoseBusters, MD, pocket plausibility, and missing cross-model consensus.",
        ),
        line_item(
            31,
            "Free-energy validation plan for chromanol lead prioritization",
            "ready for methodology outline",
            f"FE plan rows={fe_rows}; RBFE readiness doc={exists(ROOT / 'docs/RBFE_UPGRADE_READINESS.md')}",
            "Write as staged validation paper/protocol: Boltz/MD triage to OpenFE RBFE/ABFE/CBFE without overclaiming.",
        ),
        line_item(
            32,
            "Dermal regulatory safety and topical IVPT pre-gate",
            "ready for translational-methods outline",
            f"dermal regulatory rows={dermal_rows}; formulation rows={formulation_rows}",
            "Use OECD TG497, ICH S10, and FDA IVPT framing for topical lead safety/translation paper.",
        ),
        line_item(
            33,
            "Perturbation-biology gate for skin target validation",
            "ready for systems-biology outline",
            f"perturbation target rows={perturbation_rows}; wet-lab schema={wetlab_exists}",
            "Write as virtual-cell/phenotype bridge: target evidence, cell context, and wet-lab endpoint linkage.",
        ),
        line_item(
            34,
            "Hydration and residence-time follow-up for stable chromanol poses",
            "ready for methodology outline",
            f"hydration/kinetics rows={hydration_rows}; structure consensus rows={consensus_rows}",
            "Write as MD limitation paper: RMSD stability is not kinetics; propose WaterKit/GIST/SMD follow-up.",
        ),
        line_item(
            35,
            "Ultra-large active-learning screening roadmap for dermatology leads",
            "ready for roadmap/methods outline",
            f"ultra-large roadmap rows={ultra_rows}; active-learning rows={active_learning_rows}",
            "Use as scalable discovery systems paper: NPASS to ZINC/REAL/active docking without brute-force overreach.",
        ),
        line_item(
            36,
            "Model validation, applicability domain, and uncertainty in autonomous triage",
            "ready for methods/results outline",
            f"uncertainty rows={uncertainty_rows}; active-learning rows={active_learning_rows}",
            "Write as rigorous ML validation paper: scaffold domain, activity-cliff risk, and conformal-style intervals.",
        ),
        line_item(
            37,
            "Cell Painting phenomics bridge for dermatology candidate triage",
            "ready for translational-methods outline",
            f"phenomics rows={phenomics_rows}; wet-lab schema={wetlab_exists}",
            "Use as phenotype-bridge paper/protocol: JUMP/CPJUMP-style morphology, disease-cell assay anchors, and no-MOA-claim caveat.",
        ),
        line_item(
            38,
            "Developability and CMC pre-gate for topical chromanol/NPASS leads",
            "ready for translational-methods outline",
            f"CMC rows={cmc_rows}; dermal regulatory rows={dermal_rows}; formulation rows={formulation_rows}",
            "Write as lead-de-risking paper: solubility, pH stability, excipient compatibility, solid-form, and scale-up risk.",
        ),
        line_item(
            39,
            "Patent/FTO watchlist and claim-discipline workflow",
            "ready for operations/IP outline",
            f"IP/FTO rows={ip_fto_rows}; local novelty rows={novelty_rows}",
            "Use as internal/commercial-translational methods note; keep legal/FTO conclusions pending manual review.",
        ),
        line_item(
            40,
            "FAIR assay metadata and CRO feedback ingestion workflow",
            "ready for reproducibility-methods outline",
            f"FAIR dictionary rows={fair_rows}; wet-lab ingested rows={wetlab_ingest_rows}",
            "Write as reproducibility/CRO handoff paper: ISA/BAO/RO-Crate-ready metadata and queue feedback rules.",
        ),
        line_item(
            41,
            "Regulatory-grade AI/model governance registry for autonomous discovery",
            "ready for governance-methods outline",
            f"model registry rows={model_governance_rows}; provenance manifest={provenance_exists}",
            "Write as AI governance paper: context-of-use, model cards, risk tiers, validation status, and claim limits.",
        ),
        line_item(
            42,
            "Cross-model structure consensus and negative-control readiness",
            "ready for methods/results outline",
            f"structure consensus v1 rows={consensus_rows}; v2 rows={consensus_v2_rows}; {pose_gate_text}",
            "Write as DL cofolding claim-discipline paper: Boltz/PoseBusters/MD/pocket/applicability-domain plus cross-model gaps.",
        ),
        line_item(
            43,
            "Constrained generative chromanol analog design queue",
            "near-ready; R17 Boltz-2 atlas running"
            if 0 < r17_cofold_rows < r17_cofold_target
            else (
                "near-ready; R17 expanded green-target 60ns running"
                if 0 < r17_expanded_md_60_ok < r17_expanded_md_60_total
                else (
                    "complete PDF+figures"
                    if (
                        r17_expanded_md_60_ok >= r17_expanded_md_60_total
                        and exists(ROOT / "preprints/43_r17_chromanol_generative_atlas/manuscript.pdf") == "yes"
                        and figure_count(ROOT / "preprints/43_r17_chromanol_generative_atlas/figures") >= 4
                    )
                    else "ready for methods/results outline"
                    if r17_expanded_md_60_ok >= r17_expanded_md_60_total
                    else
                    "near-ready; R17 expanded green-target 60ns pending/running"
                    if r17_expanded_md_30_ok >= r17_expanded_md_30_total
                    else
                    "near-ready; R17 expanded green-target 30ns running"
                    if 0 < r17_expanded_md_30_ok < r17_expanded_md_30_total
                    else
                    "near-ready; R17 expanded green-target 30ns pending/running"
                    if r17_expanded_md_10_ok >= r17_expanded_md_10_total
                    else
                    "near-ready; R17 expanded green-target 10ns running"
                    if 0 < r17_expanded_md_10_ok < r17_expanded_md_10_total
                    else
                    "near-ready; R17 next green-target 60ns running"
                    if 0 < r17_next_md_60_ok < r17_next_md_60_total
                    else (
                        "ready for methods/results outline"
                        if r17_next_md_60_ok >= r17_next_md_60_total
                        else
                        "near-ready; R17 next green-target 60ns pending/running"
                        if r17_next_md_30_ok >= r17_next_md_30_total
                        else
                        "near-ready; R17 next green-target 30ns running"
                        if 0 < r17_next_md_30_ok < r17_next_md_30_total
                        else
                        "near-ready; R17 next green-target 30ns pending/running"
                        if r17_next_md_10_ok >= r17_next_md_10_total
                        else
                "near-ready; R17 top green-target 60ns running"
                if 0 < r17_md_60_ok < r17_md_60_total
                else (
                    "ready for methods/results outline"
                    if r17_md_60_ok >= r17_md_60_total
                    else
                    "near-ready; R17 top green-target 60ns pending/running"
                    if r17_md_30_ok >= r17_md_30_total
                    else
                    "near-ready; R17 top green-target 30ns running"
                    if 0 < r17_md_30_ok < r17_md_30_total
                    else (
                        "near-ready; R17 top green-target 30ns pending/running"
                        if r17_md_10_ok >= r17_md_10_total
                        else
                    "near-ready; R17 top green-target 10ns running"
                    if 0 < r17_md_10_ok < r17_md_10_total
                    else "ready for methods/results outline"
                    )
                )
                    )
                )
            ),
            f"generative chromanol rows={generative_rows}; R17 cofold rows={r17_cofold_rows}/{r17_cofold_target}; R17 top green-target 10ns={r17_md_10_ok}/{r17_md_10_total}; R17 top green-target 30ns={r17_md_30_ok}/{r17_md_30_total}; R17 top green-target 60ns={r17_md_60_ok}/{r17_md_60_total}; R17 next green-target 10ns={r17_next_md_10_ok}/{r17_next_md_10_total}; R17 next green-target 30ns={r17_next_md_30_ok}/{r17_next_md_30_total}; R17 next green-target 60ns={r17_next_md_60_ok}/{r17_next_md_60_total}; R17 expanded green-target 10ns={r17_expanded_md_10_ok}/{r17_expanded_md_10_total}; R17 expanded green-target 30ns={r17_expanded_md_30_ok}/{r17_expanded_md_30_total}; R17 expanded green-target 60ns={r17_expanded_md_60_ok}/{r17_expanded_md_60_total}; figures={figure_count(ROOT / 'preprints/43_r17_chromanol_generative_atlas/figures')}; PDF={exists(ROOT / 'preprints/43_r17_chromanol_generative_atlas/manuscript.pdf')}; route enumeration rows={route_enum_rows}; photosafety v2 rows={photosafety_v2_rows}",
            f"After the {r17_cofold_target}-row R17 cofold atlas completes, stratify green-target DCT/TYR/TGFB1 candidates versus red-target PTGS2 caveats before MD or manuscript tables."
            if 0 < r17_cofold_rows < r17_cofold_target
            else (
                "Write as hit-to-lead expansion paper/protocol; keep expanded fluorinated candidates as in-silico, wet-lab-pending examples."
                if r17_expanded_md_60_ok >= r17_expanded_md_60_total
                else (
                    "Let the expanded green-target 60 ns follow-up finish before adding these rows to the main robustness table."
                    if r17_expanded_md_30_ok >= r17_expanded_md_30_total
                    else
                    "Run or let the expanded green-target 30 ns follow-up finish, then decide whether the safety-green fluorinated candidates merit 60 ns robustness."
                    if r17_expanded_md_10_ok >= r17_expanded_md_10_total
                    else
                    "Let the expanded green-target 10 ns screen finish; keep all claims in-silico and photosafety-gated."
                    if 0 < r17_expanded_md_10_ok < r17_expanded_md_10_total
                    else
                    "Let the 60 ns green-target robustness panel finish, then split halogen-review candidates from the photosafety-green comparator before manuscript claims."
                    if 0 < r17_md_60_ok < r17_md_60_total
                    else (
                    "Write as hit-to-lead expansion paper/protocol; keep aryl-halogen candidates photosafety-gated and wet-lab-pending."
                    if r17_md_60_ok >= r17_md_60_total
                    else
                    "Run or let the 60 ns green-target robustness panel finish, then split halogen-review candidates from the photosafety-green comparator before manuscript claims."
                    if r17_md_30_ok >= r17_md_30_total
                    else
                    "Run or let the 30 ns green-target screen finish, then split halogen-review candidates from the photosafety-green comparator before manuscript claims."
                    if r17_md_10_ok >= r17_md_10_total
                    else
                "Let the 10 ns green-target screen finish, then decide whether halogen-review candidates need photosafety-gated 30 ns follow-up or stay as caveated design examples."
                if 0 < r17_md_10_ok < r17_md_10_total
                else "Write as hit-to-lead expansion paper/protocol; queue only non-duplicate designs when GPU is free."
                    )
                )
            ),
        ),
        line_item(
            44,
            "Route-enumerated synthesis planning for chromanol/NPASS leads",
            "ready for translational-methods outline",
            f"route enumeration rows={route_enum_rows}; synthesis gate rows={synthesis_rows}; CMC rows={cmc_rows}",
            "Use as synthesis-readiness paper/RFQ appendix; avoid lead expansion for route_review/route_hard candidates.",
        ),
        line_item(
            45,
            "Skin cell-state anchored dermatology target validation",
            "ready for systems-biology outline",
            f"skin cell-state rows={skin_cell_rows}; perturbation rows={perturbation_rows}; phenomics rows={phenomics_rows}",
            "Write as disease-cell endpoint paper: melanocyte/fibroblast/sebocyte/keratinocyte mapping and phenotype-first rules.",
        ),
        line_item(
            46,
            "Photosafety and skin-sensitization preclinical assay package",
            "ready for translational-safety outline",
            f"photosafety v2 rows={photosafety_v2_rows}; dermal regulatory rows={dermal_rows}",
            "Write as topical-safety gate paper/RFQ appendix using OECD TG497 and ICH S10 caveats.",
        ),
        line_item(
            47,
            "Design-make-test-learn experiment-card workflow",
            "ready for CRO/wet-lab operations outline",
            f"DMTL cards={dmtl_card_rows}; wet-lab ingested rows={wetlab_ingest_rows}; FAIR dictionary rows={fair_rows}",
            "Use as closed-loop operating paper: compute result to CRO assay card to wet-lab feedback ingestion.",
        ),
        line_item(
            48,
            "Benchmark-grade decoy validation for DL cofolding",
            "ready for validation-methods outline",
            f"structure benchmark rows={structure_benchmark_rows}; structure consensus v2 rows={consensus_v2_rows}; {pose_gate_text}",
            "Build decoy/cross-model/PLIF protocol paper and keep binding claims caveated until benchmark controls exist.",
        ),
        line_item(
            49,
            "Human skin spatial-atlas anchored target triage",
            "ready for systems-biology outline",
            f"skin spatial rows={skin_spatial_rows}; skin cell-state rows={skin_cell_rows}; {target_gate_text}",
            "Add site/cell/niche tables to target-focused papers and prioritize atlas anchors over docking-only ranking.",
        ),
        line_item(
            50,
            "Target engagement and deconvolution assay readiness",
            "ready for DMTL/CRO outline",
            f"target engagement rows={target_engagement_rows}; DMTL cards={dmtl_card_rows}; {target_gate_text}",
            "Write CETSA/TPP/SPR/reporter readiness table and separate direct engagement from phenotype-only claims.",
        ),
        line_item(
            51,
            "Dermal PBPK and finite-dose IVRT/IVPT workflow",
            "ready for translational-methods outline",
            f"dermal PBPK rows={dermal_pbpk_rows}; dermal regulatory rows={dermal_rows}; formulation rows={formulation_rows}",
            "Build finite-dose IVRT/IVPT/PBPK parameter table and CRO RFQ appendix before stronger topical exposure claims.",
        ),
        line_item(
            52,
            "Genetic causality and direction-of-effect target validation",
            "ready for evidence-methods outline",
            f"genetic causality rows={genetic_causality_rows}; {target_gate_text}",
            "Use Open Targets Genetics/MR/pQTL/eQTL or phenotype evidence caveats before direction-of-effect claims.",
        ),
        line_item(
            53,
            "Metabolism and reactive-metabolite risk gate",
            "ready for safety-methods outline",
            f"metabolite risk rows={metabolite_risk_rows}; photosafety v2 rows={photosafety_v2_rows}; quinone safety rows={quinone_safety_rows}",
            "Write BioTransformer/FAME-style follow-up plan and block safety-positive language for reactive-alert candidates.",
        ),
        line_item(
            54,
            "Pharmacovigilance signal and class-safety caveat workflow",
            "ready for safety-surveillance outline",
            f"pharmacovigilance rows={pharmacovigilance_rows}; model registry rows={model_governance_rows}",
            "Draft AEMS/FAERS/literature-signal workflow and state explicitly that signal is not causation.",
        ),
        line_item(
            55,
            "Single-cell foundation-model reliability for virtual-cell claims",
            "ready for ML-reliability outline",
            f"single-cell FM rows={single_cell_fm_rows}; perturbation rows={perturbation_rows}; phenomics rows={phenomics_rows}",
            "Write zero-shot reliability and simple-baseline control paper before using foundation-model claims as primary evidence.",
        ),
        line_item(
            56,
            "Quinone reactivity and sensitization gate for EMB-3-class leads",
            "ready for safety-methods outline" if quinone_safety_rows else "awaiting gate output",
            f"quinone safety rows={quinone_safety_rows}; photosafety v2 rows={photosafety_v2_rows}; metabolite risk rows={metabolite_risk_rows}",
            "Write as EMB-3/Embelin-class safety caveat paper or appendix: GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, and skin S9 metabolism before safety-positive claims.",
        ),
        line_item(
            57,
            "World-class gap-closure master gate for autonomous discovery",
            "ready for systems/operations paper",
            f"master rows={world_gap_rows}; readiness counts={world_readiness_counts}; heavy-compute counts={world_heavy_counts}",
            "Use as the top-level decision layer tying prior-art/FTO, structure consensus, FE, synthesis, dermal translation, phenotype biology, uncertainty, and governance into one queue policy.",
        ),
        line_item(
            58,
            "Creative-discovery gap matrix and active-learning fallback",
            "ready for systems/creative-discovery paper",
            f"creative gap rows={creative_rows}; active-learning candidates={active_learning_rows}; active cofold manifests={active_learning_cofold_manifest_rows}; completed short-cofold rows={active_learning_cofold_rows}; pending short-cofold pairs={creative_active.get('pending_short_cofold_pairs', 'missing')}; runnable short-cofold pairs={creative_active.get('runnable_short_cofold_pairs', 'missing')}; blocked missing-MSA pairs={creative_active.get('blocked_missing_msa_pairs', 'missing')}; missing target A3M={creative_target_cache.get('missing_a3m_count', 'missing')}",
            "Write as the creative-discovery operating paper: synthesis-native generation, scaffold hopping, target MSA cache, cryptic-pocket, phenomics-first objective, and GPU fallback rules.",
        ),
    ]

    lines = [
        "# Paper Factory Queue",
        "",
        f"- timestamp: `{now}`",
        f"- manuscript_md_count: `{count_preprints()}`",
        f"- manuscript_pdf_count: `{count_pdf_preprints()}`",
        "- principle: 논문 수를 늘리되, 같은 결과를 과장 반복하지 않는다. 각 paper는 독립 질문, 독립 figure set, 명확한 in silico limitation을 가져야 한다.",
        "",
        "## Production Rule",
        "",
        "1. 결과가 완료되면 먼저 `summary.json`/CSV를 검증한다.",
        "2. 논문 후보는 `ready`, `near-ready`, `accumulating`, `awaiting more GPU`로 분류한다.",
        "3. `ready` 후보는 원고 초안/figure/table을 만들고, `near-ready` 후보는 마지막 계산 완료 즉시 승격한다.",
        "4. wet-lab claim, clinical claim, efficacy claim은 금지한다. 표현은 `in silico`, `candidate`, `prioritization`, `hypothesis`로 제한한다.",
        "",
        "## Current Queue",
        "",
        "| ID | Paper candidate | Status | Evidence now | Next action |",
        "|---|---|---|---|---|",
        *items,
        "",
        "## Immediate Writing Priority",
        "",
        "1. P16/P17: R16 topical chromanol lead paper와 R15 safety-first triage paper는 PDF+figures 완료 상태로 유지한다; 다음은 submit/CRO/FTO 패키지다." if p16_complete and p17_complete else "1. P16/P17: 완성되지 않은 chromanol 원고를 먼저 PDF+figures 완료 상태로 만든다.",
        "2. P43: R17 constrained generative chromanol analog paper는 expanded green-target 60 ns 3/3 완료로 PDF+figures complete 상태다; 다음은 Markush/FTO, cross-model/decoy/PLIF, wet-lab/formulation 패키지다.",
        "3. P18/P19: NPASS xTB atlas/methodology pair. 96conf tier 완료 후 자동 승격한다.",
        "4. P24: scar/fibrosis TGFB1/MMP1 focused paper. CRO RFQ와 직접 연결되는 translational paper로 쓴다.",
        "5. P25/P26: target evidence gate와 provenance/wet-lab feedback schema는 기존 논문들의 방법론 보강 또는 독립 systems paper로 분리 가능하다.",
        "6. P27/P28: synthesis gate와 active-learning/multi-fidelity planner는 계산 큐가 왜 특정 후보를 고르는지 설명하는 독립 방법론 논문으로 바로 작성 가능하다.",
        "7. P29/P30: formulation BO와 structure consensus calibration은 wet-lab/CRO 연결성과 DL cofolding 한계를 보강하는 별도 논문 후보로 유지한다.",
        "8. P31/P32: free-energy validation과 dermal regulatory safety gate는 R16/R15 lead claim의 가장 중요한 보강 축이다.",
        "9. P33-P36: perturbation biology, hydration/kinetics, ultra-large roadmap, ML uncertainty는 글로벌 SOTA 대비 부족한 부분을 메우는 methodology paper 후보로 유지한다.",
        "10. P37-P41: phenomics, CMC, IP/FTO, FAIR assay ingestion, model governance는 compute-only 시스템을 translational operating system으로 확장하는 논문 후보로 유지한다.",
        "11. P42-P47: cross-model consensus, generative chromanol design, route enumeration, skin cell-state, photosafety, DMTL card는 글로벌 SOTA gap-closure 논문 후보로 유지한다.",
        "12. P48-P56: decoy benchmark, spatial atlas, target engagement, dermal PBPK/IVPT, genetic causality, metabolite risk, pharmacovigilance, single-cell FM reliability, quinone safety는 최신 translational SOTA gap-closure 논문 후보로 유지한다.",
        "13. P57: world-class gap-closure master gate는 모든 gate를 하나로 묶는 운영/방법론 paper로 유지하고, 새 GPU/FE/합성 승격 판단의 최상위 근거로 쓴다.",
        "14. P58: creative-discovery gap matrix는 chromanol 주변 최적화에서 벗어나 synthesis-native, scaffold-hop, phenomics-first, cryptic-pocket, target-cache-aware discovery로 확장하는 독립 시스템 논문 후보로 쓴다.",
        "",
        "## Compute-to-Paper Decision Logic",
        "",
        "- target evidence gate `green` + stable MD/cofold + plausible safety -> compute expansion and target-focused paper 후보.",
        "- synthesis gate `green` + novelty `novel_or_distinct` + active-learning acquisition high -> Boltz-2 또는 MD 후속 후보.",
        "- multi-fidelity BO plan이 `single-point wet-lab`을 추천하면 더 큰 GPU 확장보다 assay/IVRT/IVPT 설계를 우선 고려한다.",
        "- structure consensus `high_confidence`는 main table 후보, `usable_with_caveat`는 보조 표 또는 limitation 후보로 둔다.",
        "- pocket gate가 `hard_or_indirect`인 target은 direct binding claim을 피하고 phenotype/network claim으로 낮춘다.",
        "- formulation BO rows가 생기면 CRO RFQ appendix와 P29 manuscript table에 동시에 반영한다.",
        "- free-energy validation plan이 `RBFE_network`를 추천해도 GPU가 이미 MD에 쓰이면 production FE는 보류하고 protocol/edge plan만 갱신한다.",
        "- dermal regulatory gate `red` 후보는 topical lead claim에서 제외하고, `yellow`는 OECD TG497/ICH S10/FDA IVPT caveat를 붙인다.",
        "- perturbation biology `high` target은 phenotype/LINCS/Geneformer/scGPT 연결 후보로 올리고, `low` target은 direct biology claim을 피한다.",
        "- hydration/kinetics gate의 residence proxy 후보는 60-100 ns 안정성 이후에만 SMD/tauRAMD-style follow-up으로 올린다.",
        "- ultra-large roadmap stage1 이상은 외부 library/storage/license 확인 전에는 실제 download/docking을 큐잉하지 않는다.",
        "- model uncertainty `activity_cliff_risk` 또는 `novel_scaffold`는 direct Boltz/pose/MD 없이 paper main table에 올리지 않는다.",
        "- phenomics gate `priority_cell_painting`은 더 큰 GPU 반복보다 disease-cell phenotype/Cell Painting assay 설계를 우선 고려한다.",
        "- CMC gate `yellow/red` 후보는 lead claim보다 solubility, pH stability, excipient compatibility, solid-form risk 보강으로 돌린다.",
        "- IP/FTO watchlist `high_review` 후보는 patent/FTO 수동 검토 전까지 novelty/commercial claim을 금지한다.",
        "- FAIR assay schema 필수 metadata가 없는 wet-lab row는 논문 main evidence가 아니라 QC 보류로 둔다.",
        "- model governance `tier2` component가 main claim에 영향을 주면 orthogonal check 또는 explicit limitation을 붙인다.",
        "- structure consensus v2 `needs_cross_model`은 Chai-1/DiffDock/Vina/PLIF/negative-control 중 하나 이상을 먼저 요구한다.",
        "- chromanol generative optimizer `Boltz-2_next_when_GPU_free`는 현재 GPU MD가 끝난 뒤 non-duplicate 후보만 큐잉한다.",
        "- route enumeration `route_review/route_hard`는 synthesis route 확인 전 lead expansion에서 제외한다.",
        "- skin cell-state `phenotype_first`는 추가 docking보다 cell assay endpoint 설계를 우선한다.",
        "- photosafety v2 `yellow`는 OECD TG497/ICH S10 assay package를 같이 붙이고, `red`는 topical lead claim에서 제외한다.",
        "- quinone safety `quinone_reactivity_review`는 GSH/NAC trapping, DPRA/KeratinoSens/h-CLAT, ROS/redox cycling, ICH S10 photostability, skin S9 metabolism 전까지 EMB-3/quinone safety-positive claim을 금지한다.",
        "- DMTL `single_point_wetlab_card`는 추가 GPU 반복보다 CRO/wet-lab quote/assay ordering 후보로 승격한다.",
        "- structure benchmark `benchmark_decoys_required_before_strong_claim`은 cross-model/decoy/PLIF control 전까지 direct binding strong claim을 금지한다.",
        "- skin spatial atlas `spatially_anchorable`은 site/cell/niche table을 target paper main evidence로 올리고, `atlas_review`는 docking보다 atlas/literature 확인을 우선한다.",
        "- target engagement `engagement_assay_ready`는 DMTL/wet-lab card로 승격하고, `deconvolution_first`는 direct target engagement claim을 보류한다.",
        "- dermal PBPK/IVPT `ivpt_pbpk_ready`는 finite-dose IVRT/IVPT/PBPK table 후보로 올리고, `formulation_rescue_needed`는 추가 docking보다 formulation BO를 우선한다.",
        "- genetic causality `direction_needs_genetic_or_phenotype_support`는 Open Targets Genetics/MR/pQTL/eQTL 또는 phenotype evidence 없이는 direction-of-effect claim을 금지한다.",
        "- metabolite risk `reactive_metabolite_review`는 BioTransformer/FAME-style follow-up 전까지 safety-positive language를 금지한다.",
        "- pharmacovigilance `pv_signal_review`는 AEMS/FAERS/literature signal check 전까지 class-safety claim을 제한한다.",
        "- single-cell FM `zero_shot_reliability_review`는 simple baseline/fine-tuning/cell-type proximity control 없이는 virtual-cell 결과를 보조 evidence로만 둔다.",
        "- world-class master gate `hold_or_benchmark_only` 또는 `heavy_compute_permission=hold`는 신규 long-MD/FE/합성/상업 claim을 차단한다.",
        "- world-class master gate `wetlab_translation_priority`는 더 큰 GPU 반복보다 CRO/DMTL/IVRT/IVPT/Cell Painting package를 우선한다.",
        "- creative discovery matrix의 `target_msa_coverage` gap은 target-specific cofold를 차단한다. MC1R처럼 target-key A3M이 없으면 cache 준비가 먼저다.",
        "- active-learning short cofold 결과는 GPU 유휴 방지용 triage다. 완료 row는 master gate에 들어가지만 long-MD/FE/lead claim은 synthesis/prior-art/safety/phenomics/uncertainty gate 이후다.",
        "- 새 scaffold 또는 scaffold-hop queue는 synthesis-native generation, novelty/diversity guard, decoy/benchmark guard 없이 paper main lead로 올리지 않는다.",
        "- target evidence gate `yellow` -> phenotype/cell/wet-lab endpoint가 같이 있어야 manuscript claim에 포함한다.",
        "- target evidence gate `red` -> negative-control, limitation, future-work로만 사용한다.",
        "- GPU MD stable + cofold affinity meaningful + ADMET/skin-window plausible -> target-focused paper 후보.",
        "- 대량 CPU screen만 있고 target cofold가 없으면 atlas/methodology paper 후보로 유지한다.",
        "- drift 또는 toxicity caveat가 있으면 failure-mode/methodology paper로 전환한다.",
        "- 같은 molecule/target 결과라도 universal-scaffold paper, topical-lead paper, methodology paper의 질문이 다르면 분리 가능하다.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
