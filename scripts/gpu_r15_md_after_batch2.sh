#!/usr/bin/env bash
# Wait for extended 30 ns batch2 completion, then run R15 chromanol top-3 MD.

set -euo pipefail

cd /home/crazat/genesis_medicine

LOG=pilot/r15_chromanol_top3_md_after_batch2.log
SUMMARY=pilot/md_extended_30ns_batch2/summary.json
PY=/home/crazat/miniforge3/envs/genesis-md/bin/python

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

log "watcher start: waiting for batch2 summary length 5"
while true; do
    if [ -f "$SUMMARY" ]; then
        n=$(/usr/bin/python3 - <<'PY'
import json
try:
    print(len(json.load(open("pilot/md_extended_30ns_batch2/summary.json"))))
except Exception:
    print(0)
PY
)
    else
        n=0
    fi
    log "batch2 summary rows: $n/5"
    if [ "$n" = "5" ]; then
        break
    fi
    sleep 60
done

log "batch2 complete; launching R15 chromanol top-3 10 ns MD"
exec "$PY" scripts/run_r15_chromanol_top3_md.py
