#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
VENV_PY="$ROOT/.venv/bin/python"
LOG="$ROOT/pilot/world_class_gap_watchdog.log"
LOCK="/tmp/genesis_world_class_gap_watchdog.lock"
TRIGGER="/tmp/genesis_world_class_gap_enabled"
DRAIN="$ROOT/pilot/QUEUE_DRAIN_MODE"
INTERVAL="${GENESIS_WORLD_CLASS_GAP_INTERVAL_SEC:-900}"

mkdir -p "$ROOT/pilot"
cd "$ROOT"
if [[ -f "$DRAIN" ]]; then
  printf '[%s] world-class gap watchdog not started: QUEUE_DRAIN_MODE present\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi
touch "$TRIGGER"

exec 8>"$LOCK"
if ! flock -n 8; then
  printf '[%s] world-class gap watchdog already running; exiting duplicate\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"
}

run_light() {
  local name="$1"
  shift
  log "run $name"
  if ! timeout 240s "$@" >>"$LOG" 2>&1; then
    log "WARN $name failed or timed out"
    return 0
  fi
}

log "world-class gap watchdog start interval=${INTERVAL}s"
while [[ -f "$TRIGGER" && ! -f "$DRAIN" ]]; do
  (
    exec 8>&-
    cd "$ROOT"
    run_light "precompute_prior_art_gate" "$VENV_PY" scripts/write_precompute_prior_art_gate.py
    run_light "structure_consensus_v2" "$VENV_PY" scripts/write_structure_consensus_v2.py
    run_light "structure_benchmark_decoy_gate" "$VENV_PY" scripts/write_structure_benchmark_decoy_gate.py
    run_light "free_energy_validation_plan" "$VENV_PY" scripts/write_free_energy_validation_plan.py
    run_light "world_class_gap_closure" "$VENV_PY" scripts/write_world_class_gap_closure.py
    run_light "paper_factory_queue" "$VENV_PY" scripts/write_paper_factory_queue.py
    run_light "live_status_report" "$VENV_PY" scripts/write_live_status_report.py
  )
  sleep "$INTERVAL"
done
if [[ -f "$DRAIN" ]]; then
  log "world-class gap watchdog stopped: QUEUE_DRAIN_MODE present"
else
  log "world-class gap watchdog stopped: trigger removed"
fi
