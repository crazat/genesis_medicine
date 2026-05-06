#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/crazat/genesis_medicine}"
LOG_DIR="$PROJECT_ROOT/pilot/openfold3_smoke"
LOG_FILE="$LOG_DIR/watch_openfold3_nohup.out"

mkdir -p "$LOG_DIR"

nohup setsid bash -lc "cd '$PROJECT_ROOT' && exec env \
  PROJECT_ROOT='$PROJECT_ROOT' \
  UTIL_LIMIT='${UTIL_LIMIT:-20}' \
  MEM_LIMIT_MIB='${MEM_LIMIT_MIB:-4500}' \
  POLL_SECONDS='${POLL_SECONDS:-30}' \
  '$PROJECT_ROOT/scripts/watch_openfold3_smoke_when_idle.sh'" \
  > "$LOG_FILE" 2>&1 < /dev/null &

echo "$!"
