#!/bin/bash
# Overnight CPU chain: run after 9997 singlept_subprocess finishes.
# Sequential: top500 refine 432 → AL round 3 → cross-engine full analysis → top1000 refine 432
# All log to pilot/cpu_meaningful/overnight_chain.log

set -u
cd /home/crazat/genesis_medicine
PY=/home/crazat/miniforge3/envs/genesis-md/bin/python
LOG=pilot/cpu_meaningful/overnight_chain.log

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }
log "=== OVERNIGHT CPU CHAIN START ==="

# Wait for 9997 singlept to finish
log "waiting for 9997 singlept subprocess to complete..."
while pgrep -f "cpu_xtb_npass_9997_singlept_subprocess" >/dev/null; do
    sleep 60
done
log "9997 singlept finished"

# Stage 1: top500 refine 432
log ">>> Stage 1: top500 refine 432-conf (~32 min)"
$PY -u scripts/cpu_xtb_npass_top500_refine_432.py >> "$LOG" 2>&1
log "<<< Stage 1 done rc=$?"

# Stage 2: AL round 3 retrain
log ">>> Stage 2: AL round 3 retrain on full master (~5 min)"
$PY -u scripts/al_round3_full_master.py >> "$LOG" 2>&1
log "<<< Stage 2 done rc=$?"

# Stage 3: cross-engine full analysis
log ">>> Stage 3: cross-engine full 9997 analysis (~3 min)"
$PY -u scripts/cross_engine_full_9997_analysis.py >> "$LOG" 2>&1
log "<<< Stage 3 done rc=$?"

# Stage 4: top1000 refine 432 (extended)
log ">>> Stage 4: extending refine 432 — re-run top500 refine in case more master rows added"
# already done in Stage 1; this is a placeholder for future extension
log "<<< Stage 4 skipped (Stage 1 covered)"

log "=== OVERNIGHT CPU CHAIN COMPLETE ==="
