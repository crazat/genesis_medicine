"""Write a lightweight provenance manifest for key Genesis outputs."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
DOC = ROOT / "docs/RUN_PROVENANCE_MANIFEST.md"
CSV_OUT = OUT / "run_provenance_manifest.csv"
JSON_OUT = OUT / "run_provenance_manifest.json"

KEY_PATHS = [
    "pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv",
    "pilot/cpu_meaningful/r15_master_triage.csv",
    "pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv",
    "pilot/cpu_meaningful/r16_topical_chromanol_30ns_matrix_summary.csv",
    "pilot/cpu_meaningful/chromanol_pose_sanity_gate.csv",
    "pilot/cpu_meaningful/target_evidence_gate.csv",
    "pilot/cpu_meaningful/synthesis_retrosynthesis_gate.csv",
    "pilot/cpu_meaningful/active_learning_next_candidates.csv",
    "pilot/cpu_meaningful/multi_fidelity_bo_plan.csv",
    "pilot/cpu_meaningful/pocket_evidence_gate.csv",
    "pilot/cpu_meaningful/structure_consensus_calibration.csv",
    "pilot/cpu_meaningful/structure_consensus_v2.csv",
    "pilot/cpu_meaningful/chromanol_generative_optimizer.csv",
    "pilot/cpu_meaningful/route_enumeration_gate.csv",
    "pilot/cpu_meaningful/skin_cell_state_evidence_gate.csv",
    "pilot/cpu_meaningful/photosafety_sensitization_v2.csv",
    "pilot/cpu_meaningful/quinone_safety_gate.csv",
    "pilot/cpu_meaningful/quinone_safety_gate_summary.json",
    "pilot/cpu_meaningful/dmtl_experiment_cards.csv",
    "pilot/cpu_meaningful/skin_spatial_atlas_gate.csv",
    "pilot/cpu_meaningful/target_engagement_assay_gate.csv",
    "pilot/cpu_meaningful/dermal_pbpk_ivpt_gate.csv",
    "pilot/cpu_meaningful/metabolite_reactive_risk_gate.csv",
    "pilot/cpu_meaningful/genetic_causality_direction_gate.csv",
    "pilot/cpu_meaningful/pharmacovigilance_signal_gate.csv",
    "pilot/cpu_meaningful/single_cell_fm_reliability_gate.csv",
    "pilot/cpu_meaningful/structure_benchmark_decoy_gate.csv",
    "pilot/cpu_meaningful/topical_formulation_bo_plan.csv",
    "pilot/cpu_meaningful/free_energy_validation_plan.csv",
    "pilot/cpu_meaningful/dermal_regulatory_safety_gate.csv",
    "pilot/cpu_meaningful/perturbation_biology_gate.csv",
    "pilot/cpu_meaningful/hydration_kinetics_gate.csv",
    "pilot/cpu_meaningful/ultra_large_screening_roadmap.csv",
    "pilot/cpu_meaningful/model_validation_uncertainty_gate.csv",
    "pilot/cpu_meaningful/phenomics_signature_gate.csv",
    "pilot/cpu_meaningful/developability_cmc_gate.csv",
    "pilot/cpu_meaningful/ip_fto_watchlist.csv",
    "pilot/cpu_meaningful/fair_assay_dictionary.csv",
    "pilot/cpu_meaningful/wetlab_feedback_ingested.csv",
    "pilot/cpu_meaningful/wetlab_queue_decisions.csv",
    "pilot/cpu_meaningful/wetlab_result_ingestor_summary.json",
    "pilot/cpu_meaningful/ai_model_governance_registry.csv",
    "pilot/cpu_meaningful/rbfe_r16_edge_plan.csv",
    "pilot/cpu_meaningful/r17_chromanol_generative_batch01_rank001_032_cofold.csv",
    "pilot/cpu_meaningful/r17_chromanol_generative_batch02_rank033_064_cofold.csv",
    "pilot/cpu_meaningful/r17_chromanol_generative_batch03_rank065_096_cofold.csv",
    "pilot/cpu_meaningful/r17_chromanol_generative_batch04_rank097_128_cofold.csv",
    "pilot/md_r15_chromanol_top3_30ns/summary.json",
    "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json",
    "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json",
    "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json",
    "pilot/md_r16_chromanol_anchor_triad_200ns/summary.json",
    "pilot/md_r17_chromanol_generative_top_green_10ns/summary.json",
    "pilot/md_extended_30ns_batch2/summary.json",
    "docs/PAPER_FACTORY_QUEUE.md",
    "docs/CODEX_CURATOR_LOOP_PROMPT.md",
    "docs/TARGET_EVIDENCE_GATE.md",
    "docs/SYNTHESIS_RETROSYNTHESIS_GATE.md",
    "docs/ACTIVE_LEARNING_DOCKING_SURROGATE.md",
    "docs/MULTI_FIDELITY_BO_PLANNER.md",
    "docs/POCKET_EVIDENCE_GATE.md",
    "docs/STRUCTURE_CONSENSUS_CALIBRATION.md",
    "docs/STRUCTURE_CONSENSUS_V2.md",
    "docs/CHROMANOL_GENERATIVE_OPTIMIZER.md",
    "docs/ROUTE_ENUMERATION_GATE.md",
    "docs/SKIN_CELL_STATE_EVIDENCE_GATE.md",
    "docs/PHOTOSAFETY_SENSITIZATION_V2.md",
    "docs/QUINONE_SAFETY_GATE.md",
    "docs/DMTL_EXPERIMENT_CARD_FACTORY.md",
    "docs/SKIN_SPATIAL_ATLAS_GATE.md",
    "docs/TARGET_ENGAGEMENT_ASSAY_GATE.md",
    "docs/DERMAL_PBPK_IVPT_GATE.md",
    "docs/METABOLITE_REACTIVE_RISK_GATE.md",
    "docs/GENETIC_CAUSALITY_DIRECTION_GATE.md",
    "docs/PHARMACOVIGILANCE_SIGNAL_GATE.md",
    "docs/SINGLE_CELL_FM_RELIABILITY_GATE.md",
    "docs/STRUCTURE_BENCHMARK_DECOY_GATE.md",
    "docs/SOTA_GAP_REVIEW_2026-05-01_TRANSLATIONAL_LAYER.md",
    "docs/TOPICAL_FORMULATION_BO.md",
    "docs/FREE_ENERGY_VALIDATION_PLAN.md",
    "docs/DERMAL_REGULATORY_SAFETY_GATE.md",
    "docs/PERTURBATION_BIOLOGY_GATE.md",
    "docs/HYDRATION_KINETICS_GATE.md",
    "docs/ULTRA_LARGE_SCREENING_ROADMAP.md",
    "docs/MODEL_VALIDATION_UNCERTAINTY_GATE.md",
    "docs/PHENOMICS_SIGNATURE_GATE.md",
    "docs/DEVELOPABILITY_CMC_GATE.md",
    "docs/IP_FTO_WATCHLIST.md",
    "docs/FAIR_ASSAY_SCHEMA.md",
    "docs/WETLAB_RESULT_INGESTOR.md",
    "docs/MODEL_GOVERNANCE_REGISTRY.md",
    "docs/RBFE_UPGRADE_READINESS.md",
    "docs/WETLAB_FEEDBACK_SCHEMA.md",
    "data/fair_assay_metadata_template.csv",
    "data/fair_assay_schema.json",
    "data/wetlab_feedback_results_template.csv",
    "data/ip_fto_manual_review_template.csv",
    "scripts/codex_curator_loop.sh",
    "scripts/auto_result_planner.py",
    "scripts/run_r16_chromanol_anchor_triad_100ns.py",
    "scripts/run_r16_chromanol_anchor_triad_200ns.py",
    "scripts/run_r17_chromanol_generative_top_cofold.py",
    "scripts/run_r17_chromanol_generative_next32_cofold.py",
    "scripts/run_r17_chromanol_generative_top_green_10ns.py",
    "scripts/write_phenomics_signature_gate.py",
    "scripts/write_developability_cmc_gate.py",
    "scripts/write_ip_fto_watchlist.py",
    "scripts/write_fair_assay_schema.py",
    "scripts/write_wetlab_result_ingestor.py",
    "scripts/write_ai_model_governance_registry.py",
    "scripts/write_structure_consensus_v2.py",
    "scripts/write_chromanol_generative_optimizer.py",
    "scripts/write_route_enumeration_gate.py",
    "scripts/write_skin_cell_state_gate.py",
    "scripts/write_photosafety_sensitization_v2.py",
    "scripts/write_quinone_safety_gate.py",
    "scripts/write_dmtl_experiment_card_factory.py",
    "scripts/write_skin_spatial_atlas_gate.py",
    "scripts/write_target_engagement_assay_gate.py",
    "scripts/write_dermal_pbpk_ivpt_gate.py",
    "scripts/write_metabolite_reactive_risk_gate.py",
    "scripts/write_genetic_causality_direction_gate.py",
    "scripts/write_pharmacovigilance_signal_gate.py",
    "scripts/write_single_cell_fm_reliability_gate.py",
    "scripts/write_structure_benchmark_decoy_gate.py",
    "preprints/15_universal_scaffold/manuscript.md",
    "preprints/15_universal_scaffold/manuscript.pdf",
    "preprints/16_r15_chromanol_safety_triage/manuscript.md",
    "preprints/16_r15_chromanol_safety_triage/manuscript.pdf",
]


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return proc.stdout.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rel in KEY_PATHS:
        path = ROOT / rel
        if not path.exists():
            rows.append({"path": rel, "exists": False, "size_bytes": 0, "mtime": "", "sha256": ""})
            continue
        rows.append(
            {
                "path": rel,
                "exists": True,
                "size_bytes": path.stat().st_size,
                "mtime": datetime.fromtimestamp(path.stat().st_mtime, ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds"),
                "sha256": sha256_file(path),
            }
        )
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    rows = file_rows()
    git_head = run(["git", "rev-parse", "HEAD"])
    git_status_count = len([line for line in run(["git", "status", "--short"]).splitlines() if line.strip()])
    py_venv = run([str(ROOT / ".venv/bin/python"), "--version"])
    py_md = run(["/home/crazat/miniforge3/envs/genesis-md/bin/python", "--version"])

    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "size_bytes", "mtime", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    obj = {
        "timestamp": now,
        "git_head": git_head,
        "git_status_short_count": git_status_count,
        "python_venv": py_venv,
        "python_genesis_md": py_md,
        "files": rows,
    }
    JSON_OUT.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Run Provenance Manifest",
        "",
        f"- timestamp: `{now}`",
        f"- git_head: `{git_head}`",
        f"- git_status_short_count: `{git_status_count}`",
        f"- python_venv: `{py_venv}`",
        f"- python_genesis_md: `{py_md}`",
        "- purpose: 논문/규제/재현성 관점에서 주요 산출물의 file hash와 생성 상태를 고정한다.",
        "",
        "## Key Files",
        "",
        "| path | exists | size | sha256 |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        digest = str(row["sha256"])
        short = digest[:16] if digest else ""
        lines.append(f"| {row['path']} | {row['exists']} | {row['size_bytes']} | `{short}` |")
    lines.extend(
        [
            "",
            "## Curator Use",
            "",
            "- manuscript/PDF 업데이트 직후 이 manifest를 다시 생성한다.",
            "- 외부 제출 또는 CRO 전달 전에는 이 파일의 hash를 기준으로 산출물 버전을 고정한다.",
            "",
        ]
    )
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
