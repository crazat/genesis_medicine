#!/bin/bash
# Overnight GPU chain: run after embelin Phase 5 (--leg all) finishes.
# Then chain ABFE benchmark Tier-1 orchestrator (~8 day wall).
# All log to pilot/abfe_benchmark_chembl/overnight_gpu_chain.log

set -u
cd /home/crazat/genesis_medicine
PY=/home/crazat/miniforge3/envs/genesis-md/bin/python
LOG=pilot/abfe_benchmark_chembl/overnight_gpu_chain.log
mkdir -p pilot/abfe_benchmark_chembl

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }
log "=== OVERNIGHT GPU CHAIN START ==="

# Wait for embelin Phase 5 (parallel complex + solvent legs) to finish
log "waiting for embelin Phase 5 parallel legs (complex + solvent) to complete..."
while pgrep -f "zaff_phase5_abfe_production_embelin.py" >/dev/null; do
    sleep 120
done
log "embelin Phase 5 finished — running combine"

# Run combine step
$PY -u scripts/zaff_phase5_abfe_production_embelin.py --leg combine >> "$LOG" 2>&1
log "combine rc=$?"

PHASE5_OK=pilot/abfe_mmp1_holo_zn_embelin/abfe_production/PHASE5_OK
PHASE5_INC=pilot/abfe_mmp1_holo_zn_embelin/abfe_production/PHASE5_INCONCLUSIVE
if [ -f "$PHASE5_OK" ]; then
    log "embelin Phase 5 PASS"
elif [ -f "$PHASE5_INC" ]; then
    log "embelin Phase 5 INCONCLUSIVE (acceptable for paper #A H3 — proceeding to benchmark)"
else
    log "embelin Phase 5 unclear (no gate file) — proceeding anyway"
fi

# Stage 1: ABFE benchmark Tier-1 orchestrator (~8 days wall)
log ">>> Stage 1: ABFE benchmark Tier-1 orchestrator (~8 days wall)"
$PY -u scripts/abfe_benchmark_orchestrator.py --subset tier1 >> "$LOG" 2>&1
log "<<< Stage 1 done rc=$?"

log "=== OVERNIGHT GPU CHAIN COMPLETE ==="
