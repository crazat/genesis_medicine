#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
PROMPT="$ROOT/docs/CODEX_CURATOR_LOOP_PROMPT.md"
CONTEXT="$ROOT/pilot/codex_curator_context.md"
REQUEST="$ROOT/pilot/codex_curator_request.md"
LAST="$ROOT/pilot/codex_curator_last.md"
LOG="$ROOT/pilot/codex_curator_loop.log"
LOCK="/tmp/genesis_codex_curator_loop.lock"
TRIGGER="/tmp/genesis_codex_curator_enabled"
DRAIN="$ROOT/pilot/QUEUE_DRAIN_MODE"
INTERVAL="${CODEX_CURATOR_INTERVAL_SEC:-600}"
TIMEOUT_SEC="${CODEX_CURATOR_TIMEOUT_SEC:-1200}"
REASONING="${CODEX_CURATOR_REASONING:-high}"
CODEX_BIN="${CODEX_BIN:-codex}"

mkdir -p "$ROOT/pilot"
cd "$ROOT"
if [[ -f "$DRAIN" ]]; then
  printf '[%s] codex curator loop not started: QUEUE_DRAIN_MODE present\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi
touch "$TRIGGER"

exec 7>"$LOCK"
if ! flock -n 7; then
  printf '[%s] codex curator already running; exiting duplicate\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"
}

section() {
  printf '\n## %s\n\n' "$1"
}

maybe_cat_json() {
  local path="$1"
  if [[ -s "$path" ]]; then
    printf '### %s\n\n```json\n' "$path"
    python3 -m json.tool "$path" 2>/dev/null || cat "$path"
    printf '\n```\n'
  fi
}

maybe_tail() {
  local path="$1"
  local lines="${2:-80}"
  if [[ -s "$path" ]]; then
    printf '### %s tail -%s\n\n```text\n' "$path" "$lines"
    tail -n "$lines" "$path" || true
    printf '\n```\n'
  fi
}

refresh_lightweight_outputs() {
  log "refresh lightweight evidence/paper/provenance outputs"
  (
    exec 7>&-
    cd "$ROOT"
    timeout 240s "$ROOT/.venv/bin/python" scripts/write_target_evidence_gate.py >/tmp/genesis_target_evidence_gate.log 2>&1 || true
    timeout 180s "$ROOT/.venv/bin/python" scripts/write_synthesis_retrosynthesis_gate.py >/tmp/genesis_synthesis_retrosynthesis_gate.log 2>&1 || true
    timeout 180s "$ROOT/.venv/bin/python" scripts/write_active_learning_docking_surrogate.py >/tmp/genesis_active_learning_docking_surrogate.log 2>&1 || true
    timeout 180s "$ROOT/.venv/bin/python" scripts/write_multi_fidelity_bo_planner.py >/tmp/genesis_multi_fidelity_bo_planner.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_pocket_evidence_gate.py >/tmp/genesis_pocket_evidence_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_structure_consensus_calibration.py >/tmp/genesis_structure_consensus_calibration.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_structure_consensus_v2.py >/tmp/genesis_structure_consensus_v2.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_chromanol_generative_optimizer.py >/tmp/genesis_chromanol_generative_optimizer.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_route_enumeration_gate.py >/tmp/genesis_route_enumeration_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_skin_cell_state_gate.py >/tmp/genesis_skin_cell_state_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_photosafety_sensitization_v2.py >/tmp/genesis_photosafety_sensitization_v2.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_quinone_safety_gate.py >/tmp/genesis_quinone_safety_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_dmtl_experiment_card_factory.py >/tmp/genesis_dmtl_experiment_card_factory.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_skin_spatial_atlas_gate.py >/tmp/genesis_skin_spatial_atlas_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_target_engagement_assay_gate.py >/tmp/genesis_target_engagement_assay_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_dermal_pbpk_ivpt_gate.py >/tmp/genesis_dermal_pbpk_ivpt_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_metabolite_reactive_risk_gate.py >/tmp/genesis_metabolite_reactive_risk_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_genetic_causality_direction_gate.py >/tmp/genesis_genetic_causality_direction_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_pharmacovigilance_signal_gate.py >/tmp/genesis_pharmacovigilance_signal_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_single_cell_fm_reliability_gate.py >/tmp/genesis_single_cell_fm_reliability_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_structure_benchmark_decoy_gate.py >/tmp/genesis_structure_benchmark_decoy_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_wetlab_feedback_schema.py >/tmp/genesis_wetlab_feedback_schema.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_topical_formulation_bo_schema.py >/tmp/genesis_topical_formulation_bo_schema.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_free_energy_validation_plan.py >/tmp/genesis_free_energy_validation_plan.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_dermal_regulatory_safety_gate.py >/tmp/genesis_dermal_regulatory_safety_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_perturbation_biology_gate.py >/tmp/genesis_perturbation_biology_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_hydration_kinetics_gate.py >/tmp/genesis_hydration_kinetics_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_ultra_large_screening_roadmap.py >/tmp/genesis_ultra_large_screening_roadmap.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_model_validation_uncertainty_gate.py >/tmp/genesis_model_validation_uncertainty_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_phenomics_signature_gate.py >/tmp/genesis_phenomics_signature_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_developability_cmc_gate.py >/tmp/genesis_developability_cmc_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_ip_fto_watchlist.py >/tmp/genesis_ip_fto_watchlist.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_fair_assay_schema.py >/tmp/genesis_fair_assay_schema.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_wetlab_result_ingestor.py >/tmp/genesis_wetlab_result_ingestor.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_ai_model_governance_registry.py >/tmp/genesis_ai_model_governance_registry.log 2>&1 || true
    timeout 180s "$ROOT/.venv/bin/python" scripts/write_modality_ip_novelty_gate.py >/tmp/genesis_modality_ip_novelty_gate.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_run_provenance_manifest.py >/tmp/genesis_run_provenance_manifest.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_creative_discovery_gap_matrix.py >/tmp/genesis_creative_discovery_gap_matrix.log 2>&1 || true
    timeout 180s "$ROOT/.venv/bin/python" scripts/write_world_class_gap_closure.py >/tmp/genesis_world_class_gap_closure.log 2>&1 || true
    timeout 120s "$ROOT/.venv/bin/python" scripts/write_paper_factory_queue.py >/tmp/genesis_paper_factory_queue.log 2>&1 || true
  )
}

write_context() {
  {
    printf '# Codex Curator Context\n\n'
    printf 'timestamp: `%s`\n' "$(date -Is)"
    printf 'root: `%s`\n' "$ROOT"
    printf 'interval_sec: `%s`\n' "$INTERVAL"
    printf 'timeout_sec: `%s`\n' "$TIMEOUT_SEC"

    section "System"
    printf '```text\n'
    free -h || true
    uptime || true
    printf '\n'
    vmstat 1 2 || true
    printf '```\n'

    section "GPU"
    printf '```text\n'
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv || true
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader || true
    printf '```\n'

    section "Top CPU"
    printf '```text\n'
    ps aux --sort=-%cpu | head -20 || true
    printf '```\n'

    section "Protected And Project Processes"
    printf '```text\n'
    ps -ef | grep -E "(cpu_5000|cpu_xtb_npass_top_refine|run_extended|run_r15|run_r16|chromanol|boltz|auto_queue|monitor_supervisor|codex_curator)" | grep -v grep | head -120 || true
    printf '```\n'

    section "Triggers"
    printf '```text\n'
    ls -l /tmp/genesis_auto_queue_enabled /tmp/genesis_monitor_enabled /tmp/genesis_codex_curator_enabled 2>/dev/null || true
    printf '```\n'

    section "Planner"
    maybe_cat_json "pilot/auto_result_planner_latest.json"

    section "MD Summaries"
    maybe_cat_json "pilot/md_extended_30ns/summary.json"
    maybe_cat_json "pilot/md_extended_30ns_batch2/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_topical_priority_30ns/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_topical_tgfb1_extra_30ns/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_topical_top3_10ns/summary.json"
    maybe_cat_json "pilot/md_r15_chromanol_top3_10ns/summary.json"
    maybe_cat_json "pilot/md_r15_chromanol_top3_30ns/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_topical_tgfb1_top6_60ns/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_topical_pigment_representative_60ns/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_anchor_triad_100ns/summary.json"
    maybe_cat_json "pilot/md_r16_chromanol_anchor_triad_200ns/summary.json"
    maybe_cat_json "pilot/cpu_meaningful/target_evidence_gate_summary.json"
    maybe_cat_json "pilot/cpu_meaningful/chromanol_pose_sanity_gate_summary.json"
    maybe_cat_json "pilot/cpu_meaningful/active_learning_surrogate_summary.json"
    maybe_cat_json "pilot/cpu_meaningful/wetlab_result_ingestor_summary.json"
    maybe_cat_json "pilot/cpu_meaningful/model_validation_uncertainty_summary.json"
    maybe_cat_json "pilot/auto_queue_decision_policy.json"

    section "Latest Result Files"
    printf '```text\n'
    find pilot -maxdepth 3 \( -name 'summary.json' -o -name '*r15*.csv' -o -name '*r16*.csv' -o -name 'active_learning_next_cofold_batch*.csv' -o -name 'creative_discovery_gap_matrix.csv' -o -name 'xtb_npass_top*_refine_*conf.csv' \) \
      -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' 2>/dev/null | sort | tail -80 || true
    printf '```\n'

    section "CSV Snapshots"
    printf '```text\n'
    python3 - <<'PY' || true
from pathlib import Path
import pandas as pd

paths = [
    Path("pilot/cpu_meaningful/r15_master_triage.csv"),
    Path("pilot/cpu_meaningful/r15_chromanol_cofold_14targets.csv"),
    Path("pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv"),
    Path("pilot/cpu_meaningful/r16_topical_chromanol_30ns_matrix_summary.csv"),
    Path("pilot/cpu_meaningful/target_evidence_gate.csv"),
    Path("pilot/cpu_meaningful/target_modality_matrix.csv"),
    Path("pilot/cpu_meaningful/candidate_local_novelty_gate.csv"),
    Path("pilot/cpu_meaningful/synthesis_retrosynthesis_gate.csv"),
    Path("pilot/cpu_meaningful/active_learning_next_candidates.csv"),
    Path("pilot/cpu_meaningful/creative_discovery_gap_matrix.csv"),
    Path("pilot/cpu_meaningful/multi_fidelity_bo_plan.csv"),
    Path("pilot/cpu_meaningful/pocket_evidence_gate.csv"),
    Path("pilot/cpu_meaningful/structure_consensus_calibration.csv"),
    Path("pilot/cpu_meaningful/structure_consensus_v2.csv"),
    Path("pilot/cpu_meaningful/chromanol_generative_optimizer.csv"),
    Path("pilot/cpu_meaningful/route_enumeration_gate.csv"),
    Path("pilot/cpu_meaningful/skin_cell_state_evidence_gate.csv"),
    Path("pilot/cpu_meaningful/photosafety_sensitization_v2.csv"),
    Path("pilot/cpu_meaningful/quinone_safety_gate.csv"),
    Path("pilot/cpu_meaningful/dmtl_experiment_cards.csv"),
    Path("pilot/cpu_meaningful/skin_spatial_atlas_gate.csv"),
    Path("pilot/cpu_meaningful/target_engagement_assay_gate.csv"),
    Path("pilot/cpu_meaningful/dermal_pbpk_ivpt_gate.csv"),
    Path("pilot/cpu_meaningful/metabolite_reactive_risk_gate.csv"),
    Path("pilot/cpu_meaningful/genetic_causality_direction_gate.csv"),
    Path("pilot/cpu_meaningful/pharmacovigilance_signal_gate.csv"),
    Path("pilot/cpu_meaningful/single_cell_fm_reliability_gate.csv"),
    Path("pilot/cpu_meaningful/structure_benchmark_decoy_gate.csv"),
    Path("pilot/cpu_meaningful/topical_formulation_bo_plan.csv"),
    Path("pilot/cpu_meaningful/free_energy_validation_plan.csv"),
    Path("pilot/cpu_meaningful/dermal_regulatory_safety_gate.csv"),
    Path("pilot/cpu_meaningful/perturbation_biology_gate.csv"),
    Path("pilot/cpu_meaningful/hydration_kinetics_gate.csv"),
    Path("pilot/cpu_meaningful/ultra_large_screening_roadmap.csv"),
    Path("pilot/cpu_meaningful/model_validation_uncertainty_gate.csv"),
    Path("pilot/cpu_meaningful/phenomics_signature_gate.csv"),
    Path("pilot/cpu_meaningful/developability_cmc_gate.csv"),
    Path("pilot/cpu_meaningful/ip_fto_watchlist.csv"),
    Path("pilot/cpu_meaningful/fair_assay_dictionary.csv"),
    Path("pilot/cpu_meaningful/wetlab_feedback_ingested.csv"),
    Path("pilot/cpu_meaningful/wetlab_queue_decisions.csv"),
    Path("pilot/cpu_meaningful/ai_model_governance_registry.csv"),
    Path("pilot/cpu_meaningful/world_class_gap_closure_matrix.csv"),
]
paths.extend(sorted(Path("pilot/cpu_meaningful").glob("active_learning_next_cofold_batch*.csv"))[-6:])
for path in paths:
    if not path.exists() or path.stat().st_size == 0:
        continue
    print(f"\n### {path}")
    try:
        df = pd.read_csv(path)
        print(f"rows={len(df)} cols={list(df.columns)[:20]}")
        print(df.head(8).to_string(index=False))
    except Exception as exc:
        print(f"failed_to_read={exc}")
PY
    printf '```\n'

    section "Recent Logs"
    maybe_tail "pilot/auto_queue_cpu_gpu_daemon.log" 120
    maybe_tail "pilot/monitor_supervisor.log" 80
    maybe_tail "pilot/codex_curator_actions.log" 80
    maybe_tail "pilot/md_r16_chromanol_topical_tgfb1_extra_30ns_auto.log" 120
    maybe_tail "pilot/r16_chromanol_topical_chain.log" 100
    maybe_tail "pilot/r15_chromanol_chain.log" 100
    maybe_tail "pilot/md_r16_chromanol_anchor_triad_100ns_auto.log" 120
    maybe_tail "pilot/md_r16_chromanol_anchor_triad_200ns_auto.log" 120
    maybe_tail "docs/PAPER_FACTORY_QUEUE.md" 160
    maybe_tail "docs/TARGET_EVIDENCE_GATE.md" 160
    maybe_tail "docs/ACTIVE_LEARNING_DOCKING_SURROGATE.md" 120
    maybe_tail "docs/MULTI_FIDELITY_BO_PLANNER.md" 120
    maybe_tail "docs/STRUCTURE_CONSENSUS_CALIBRATION.md" 120
    maybe_tail "docs/STRUCTURE_CONSENSUS_V2.md" 120
    maybe_tail "docs/CHROMANOL_GENERATIVE_OPTIMIZER.md" 120
    maybe_tail "docs/ROUTE_ENUMERATION_GATE.md" 120
    maybe_tail "docs/SKIN_CELL_STATE_EVIDENCE_GATE.md" 120
    maybe_tail "docs/PHOTOSAFETY_SENSITIZATION_V2.md" 120
    maybe_tail "docs/QUINONE_SAFETY_GATE.md" 120
    maybe_tail "docs/DMTL_EXPERIMENT_CARD_FACTORY.md" 120
    maybe_tail "docs/SKIN_SPATIAL_ATLAS_GATE.md" 120
    maybe_tail "docs/TARGET_ENGAGEMENT_ASSAY_GATE.md" 120
    maybe_tail "docs/DERMAL_PBPK_IVPT_GATE.md" 120
    maybe_tail "docs/METABOLITE_REACTIVE_RISK_GATE.md" 120
    maybe_tail "docs/GENETIC_CAUSALITY_DIRECTION_GATE.md" 120
    maybe_tail "docs/PHARMACOVIGILANCE_SIGNAL_GATE.md" 120
    maybe_tail "docs/SINGLE_CELL_FM_RELIABILITY_GATE.md" 120
    maybe_tail "docs/STRUCTURE_BENCHMARK_DECOY_GATE.md" 120
    maybe_tail "docs/TOPICAL_FORMULATION_BO.md" 100
    maybe_tail "docs/FREE_ENERGY_VALIDATION_PLAN.md" 100
    maybe_tail "docs/DERMAL_REGULATORY_SAFETY_GATE.md" 100
    maybe_tail "docs/PERTURBATION_BIOLOGY_GATE.md" 100
    maybe_tail "docs/HYDRATION_KINETICS_GATE.md" 100
    maybe_tail "docs/ULTRA_LARGE_SCREENING_ROADMAP.md" 100
    maybe_tail "docs/MODEL_VALIDATION_UNCERTAINTY_GATE.md" 100
    maybe_tail "docs/PHENOMICS_SIGNATURE_GATE.md" 100
    maybe_tail "docs/DEVELOPABILITY_CMC_GATE.md" 100
    maybe_tail "docs/IP_FTO_WATCHLIST.md" 100
    maybe_tail "docs/FAIR_ASSAY_SCHEMA.md" 100
    maybe_tail "docs/WETLAB_RESULT_INGESTOR.md" 100
    maybe_tail "docs/MODEL_GOVERNANCE_REGISTRY.md" 100
    maybe_tail "docs/CREATIVE_DISCOVERY_GAP_MATRIX.md" 120
    maybe_tail "docs/WORLD_CLASS_GAP_CLOSURE.md" 140
  } > "$CONTEXT.tmp"
  mv "$CONTEXT.tmp" "$CONTEXT"
}

write_request() {
  {
    cat "$PROMPT"
    printf '\n\n---\n\n'
    printf '아래는 이번 tick의 자동 상태 스냅샷이다. 필요하면 repo 파일을 추가로 읽고, 중복 없이 다음 큐잉을 판단/실행하라.\n\n'
    cat "$CONTEXT"
  } > "$REQUEST.tmp"
  mv "$REQUEST.tmp" "$REQUEST"
}

run_codex_tick() {
  local model_arg=()
  if [[ -n "${CODEX_CURATOR_MODEL:-}" ]]; then
    model_arg=(-m "$CODEX_CURATOR_MODEL")
  fi

  log "curator tick start"
  refresh_lightweight_outputs
  write_context
  write_request

  (
    exec 7>&-
    timeout --kill-after=60s "$TIMEOUT_SEC" \
      "$CODEX_BIN" exec \
      -C "$ROOT" \
      --ephemeral \
      --dangerously-bypass-approvals-and-sandbox \
      -c "model_reasoning_effort=\"$REASONING\"" \
      "${model_arg[@]}" \
      -o "$LAST" \
      - < "$REQUEST"
  ) >> "$LOG" 2>&1
  local rc=$?
  if [[ "$rc" -eq 0 ]]; then
    log "curator tick complete"
  else
    log "curator tick failed rc=$rc"
    printf '[%s] curator failed rc=%s\n' "$(date -Is)" "$rc" >> "$ROOT/pilot/codex_curator_actions.log"
  fi
}

log "codex curator loop start interval=${INTERVAL}s timeout=${TIMEOUT_SEC}s reasoning=$REASONING"
while [[ -f "$TRIGGER" && ! -f "$DRAIN" ]]; do
  run_codex_tick || true
  (exec 7>&-; sleep "$INTERVAL")
done
if [[ -f "$DRAIN" ]]; then
  log "codex curator loop stopped: QUEUE_DRAIN_MODE present"
else
  log "codex curator loop stopped: trigger removed"
fi
