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

log "CPU-only xTB refine watchdog start"
run_refine 500 2 24 12 xtb_npass_top500_hetero2_refine_24conf.csv
run_refine 1000 3 24 12 xtb_npass_top1000_hetero3_refine_24conf.csv
run_refine 3000 5 24 12 xtb_npass_top3000_hetero5_refine_24conf.csv
run_refine 5000 6 24 12 xtb_npass_top5000_hetero6_refine_24conf.csv
log "CPU-only xTB refine watchdog complete"
