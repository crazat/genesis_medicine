#!/bin/bash
# Chain: wait R4 boltz chain to finish → trigger ABFE 12h on r3_6 × TGFB1
# Eliminates GPU idle gap

set -e
cd /home/crazat/genesis_medicine
LOG=pilot/cpu_meaningful/abfe_chain_master.log

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }

log "=== ABFE chain wait start ==="

# Wait for R4 boltz chain (PID 348230) to finish
while kill -0 348230 2>/dev/null; do
    sleep 60
done
log "R4 boltz chain done"

# Verify R4 results saved
ls -la pilot/cpu_meaningful/all_boltz2_affinity_consolidated_r4.csv 2>&1 | tee -a $LOG

# Verify GPU free
nvidia-smi --query-gpu=memory.used --format=csv,noheader 2>&1 | tee -a $LOG
sleep 10  # let VRAM release

# Run integrated EMB-3 ABFE openmmtools pipeline (existing baseline)
# This is the working v3 attempt — TGFB1 (zinc-free) + r3_6 (round 3 winner)
log "Starting EMB-3 ABFE openmmtools (12h) on r3_6 × TGFB1"

if [ -f scripts/run_emb3_abfe_openmmtools.py ]; then
    nohup .venv/bin/python scripts/run_emb3_abfe_openmmtools.py \
        --target tgfb1 --compound r3_6 --duration_h 12 \
        > pilot/cpu_meaningful/abfe_r3_6_tgfb1.log 2>&1 &
    ABFE_PID=$!
    log "ABFE PID $ABFE_PID started"
    log "Estimated completion: $(date -d '+12 hours' +%Y-%m-%d_%H:%M)"
else
    log "ERROR: scripts/run_emb3_abfe_openmmtools.py not found"
fi

log "=== ABFE chain master done ==="
