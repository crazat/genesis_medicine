#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
PY="$ROOT/.venv/bin/python"
cd "$ROOT"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

active_refine_count() {
  pgrep -fc "scripts/cpu_xtb_npass_top_refine.py" || true
}

wait_for_refine_quiet() {
  local count
  while true; do
    count="$(active_refine_count)"
    if [[ "$count" -eq 0 ]]; then
      return 0
    fi
    log "waiting for active cpu_xtb_npass_top_refine.py processes: $count"
    sleep 120
  done
}

run_refine() {
  local topn="$1"
  local hetero="$2"
  local confs="$3"
  local workers="$4"
  local out="$5"

  if [[ -s "pilot/cpu_meaningful/$out" ]]; then
    log "skip existing $out"
    return 0
  fi

  wait_for_refine_quiet
  log "start $out topn=$topn hetero=$hetero confs=$confs workers=$workers"
  "$PY" -u scripts/cpu_xtb_npass_top_refine.py \
    --topn "$topn" \
    --workers "$workers" \
    --num-confs "$confs" \
    --min-hetero-atoms "$hetero" \
    --out "$out"
  log "done $out"
}

log "CPU-only xTB refine watchdog v2 start"
run_refine 7000 7 24 12 xtb_npass_top7000_hetero7_refine_24conf.csv
run_refine 9000 9 24 12 xtb_npass_top9000_hetero9_refine_24conf.csv
run_refine 9997 10 24 12 xtb_npass_top9997_hetero10_refine_24conf.csv
log "CPU-only xTB refine watchdog v2 complete"
