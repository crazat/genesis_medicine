#!/usr/bin/env bash
# Overnight auto-chain: R12_23 → R14_5 → R13_13 (super-leader universal validation)
# Each step waits for prior chain completion (summary.json has all expected entries),
# launches next without idle gap.

set -e
cd /home/crazat/genesis_medicine

GENESIS_MD_PY=/home/crazat/miniforge3/envs/genesis-md/bin/python
LOG=pilot/overnight_chain.log
echo "[$(date)] Overnight chain start" > $LOG

# 1) Wait for R12_23 to finish (summary.json has 11 entries OR file unchanged 5min)
wait_chain() {
  local sjson="$1"
  local target_n="$2"
  local label="$3"
  echo "[$(date)] Waiting for $label ($target_n entries in $sjson)..." >> $LOG
  local last_size=0
  local stale_count=0
  while true; do
    if [ -f "$sjson" ]; then
      local n=$(python3 -c "import json; print(len(json.load(open('$sjson'))))" 2>/dev/null || echo 0)
      if [ "$n" -ge "$target_n" ]; then
        echo "[$(date)] $label done ($n/$target_n)" >> $LOG
        break
      fi
      local size=$(stat -c %s "$sjson" 2>/dev/null || echo 0)
      if [ "$size" = "$last_size" ]; then
        stale_count=$((stale_count + 1))
        if [ $stale_count -gt 30 ]; then  # 30 × 60s = 30 min stale → assume crashed
          echo "[$(date)] $label stale 30min, abort wait" >> $LOG
          break
        fi
      else
        stale_count=0
        last_size=$size
      fi
    fi
    sleep 60
  done
}

# Wait for current R12_23 chain
wait_chain "pilot/md_r12_23_full14/summary.json" 11 "R12_23"

# 2) Launch R14_5 × 10 missing targets (4th PAINS-free leader)
echo "[$(date)] Launching R14_5 chain..." >> $LOG
nohup $GENESIS_MD_PY scripts/run_r14_5_full14_md.py > pilot/r14_5_full14.log 2>&1 &
echo "  R14_5 PID: $!" >> $LOG
wait_chain "pilot/md_r14_5_full14/summary.json" 10 "R14_5"

# 3) Launch R13_13 × 10 missing targets (5th leader, prenyl variant; PAINS-flagged but interesting)
echo "[$(date)] Launching R13_13 chain..." >> $LOG
nohup $GENESIS_MD_PY scripts/run_r13_13_full14_md.py > pilot/r13_13_full14.log 2>&1 &
echo "  R13_13 PID: $!" >> $LOG
wait_chain "pilot/md_r13_13_full14/summary.json" 10 "R13_13"

echo "[$(date)] All overnight chains complete!" >> $LOG
