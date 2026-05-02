#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/home/crazat/genesis_medicine}"
ROUNDS="${ROUNDS:-8}"
BATCH_SIZE="${BATCH_SIZE:-16}"
SLEEP_SECONDS="${SLEEP_SECONDS:-60}"
LOG="${LOG:-$ROOT/pilot/active_learning_gpu_backfill_d_native_loop.log}"

cd "$ROOT"
source .venv/bin/activate
export CC="${CC:-/usr/bin/gcc}"
export CXX="${CXX:-/usr/bin/g++}"
export TRITON_CACHE_DIR="${TRITON_CACHE_DIR:-/home/crazat/.cache/triton}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

active_gpu_job() {
  local self="$$"
  ps -eo pid=,comm=,args= | awk -v self="$self" '
    $1 == self { next }
    $2 !~ /^python[0-9.]*$/ { next }
    /boltz predict/ { found = 1 }
    /python -u scripts\/run_active_learning_next_cofold.py/ { found = 1 }
    END { exit found ? 0 : 1 }
  '
}

log() {
  printf '[%s] %s\n' "$(date '+%F %T %Z')" "$*" >> "$LOG"
}

for round in $(seq 1 "$ROUNDS"); do
  while active_gpu_job >/dev/null; do
    log "waiting for active Boltz before backfill round ${round}"
    sleep "$SLEEP_SECONDS"
  done

  log "launching active-learning GPU backfill round ${round}"
  .venv/bin/python -u scripts/run_active_learning_next_cofold.py --batch-size "$BATCH_SIZE" >> "$LOG" 2>&1 || {
    rc=$?
    log "backfill round ${round} exit=${rc}; stopping loop"
    exit "$rc"
  }

  if tail -80 "$LOG" | grep -q "No active-learning candidates pending"; then
    log "no pending candidates; stopping loop"
    exit 0
  fi
  sleep 20
done

log "completed configured backfill rounds"
