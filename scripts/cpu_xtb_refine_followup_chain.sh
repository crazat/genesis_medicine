#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
PY="$ROOT/.venv/bin/python"
cd "$ROOT"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

wait_for_current_hetero5() {
  while pgrep -f "cpu_xtb_npass_top_refine.py --topn 3000 .*--min-hetero-atoms 5" >/dev/null; do
    log "waiting for active top3000 hetero5 refinement"
    sleep 60
  done
}

run_refine() {
  local topn="$1"
  local hetero="$2"
  local out="$3"
  if [[ -s "pilot/cpu_meaningful/$out" ]]; then
    log "skip existing $out"
    return 0
  fi
  log "start $out"
  "$PY" -u scripts/cpu_xtb_npass_top_refine.py \
    --topn "$topn" \
    --workers 12 \
    --num-confs 12 \
    --min-hetero-atoms "$hetero" \
    --out "$out"
  log "done $out"
}

log "CPU xTB refine follow-up chain start"
wait_for_current_hetero5
run_refine 5000 6 xtb_npass_top5000_hetero6_refine_12conf.csv
run_refine 7000 7 xtb_npass_top7000_hetero7_refine_12conf.csv
log "CPU xTB refine follow-up chain complete"
