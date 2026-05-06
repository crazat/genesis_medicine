#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
PY="$ROOT/.venv/bin/python"
LOG="$ROOT/pilot/p43_r17_finalizer.log"
SUMMARY="$ROOT/pilot/md_r17_chromanol_generative_expanded_green_60ns/summary.json"

cd "$ROOT"

echo "$(date -Is) P43 finalizer started" >> "$LOG"

for tick in $(seq 1 144); do
  ok_count="$($PY - <<'PY'
import json
from pathlib import Path
p = Path("pilot/md_r17_chromanol_generative_expanded_green_60ns/summary.json")
if not p.exists():
    print(0)
else:
    try:
        rows = json.loads(p.read_text())
    except Exception:
        rows = []
    print(sum(1 for r in rows if isinstance(r, dict) and r.get("status") == "ok"))
PY
)"
  echo "$(date -Is) tick=$tick expanded_60ns_ok=${ok_count}/3" >> "$LOG"
  if [[ "$ok_count" -ge 3 ]]; then
    "$PY" scripts/write_r17_chromanol_generative_preprint.py >> "$LOG" 2>&1
    "$PY" scripts/write_paper_factory_queue.py >> "$LOG" 2>&1
    echo "$(date -Is) P43 finalizer completed" >> "$LOG"
    exit 0
  fi
  sleep 300
done

echo "$(date -Is) P43 finalizer timed out waiting for $SUMMARY" >> "$LOG"
exit 2
