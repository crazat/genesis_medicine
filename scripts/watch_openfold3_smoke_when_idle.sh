#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/crazat/genesis_medicine}"
UTIL_LIMIT="${UTIL_LIMIT:-20}"
MEM_LIMIT_MIB="${MEM_LIMIT_MIB:-4500}"
POLL_SECONDS="${POLL_SECONDS:-120}"
LOG_DIR="$PROJECT_ROOT/pilot/openfold3_smoke"
LOG_FILE="$LOG_DIR/watch_openfold3_smoke_when_idle.log"

mkdir -p "$LOG_DIR"
export PATH="/usr/lib/wsl/lib:${PATH}"

echo "[$(date -Is)] watcher start util<=${UTIL_LIMIT}% mem<=${MEM_LIMIT_MIB}MiB" >> "$LOG_FILE"

while true; do
  IFS=',' read -r util mem <<<"$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits | head -1)"
  util="${util// /}"
  mem="${mem// /}"
  echo "[$(date -Is)] gpu util=${util}% mem=${mem}MiB" >> "$LOG_FILE"

  if [[ "$util" =~ ^[0-9]+$ && "$mem" =~ ^[0-9]+$ && "$util" -le "$UTIL_LIMIT" && "$mem" -le "$MEM_LIMIT_MIB" ]]; then
    echo "[$(date -Is)] idle condition met; running OpenFold3 smoke" >> "$LOG_FILE"
    set +e
    "$PROJECT_ROOT/scripts/run_openfold3_smoke.sh" >> "$LOG_DIR/openfold3_smoke_latest.log" 2>&1
    status=$?
    set -e
    echo "[$(date -Is)] OpenFold3 smoke finished with exit=$status" >> "$LOG_FILE"
    exit "$status"
  fi

  sleep "$POLL_SECONDS"
done
