#!/bin/bash
# Wait for EMB-3 ABFE Phase 5 to finish, then launch embelin variant.
# Sequential GPU usage: only one ABFE running at a time.
set -u

# Activate conda env so AmberTools (antechamber, parmchk2, tleap) is on PATH.
source /home/crazat/miniforge3/etc/profile.d/conda.sh
conda activate genesis-md

ROOT=/home/crazat/genesis_medicine
EMB3_OK=$ROOT/pilot/abfe_mmp1_holo_zn/abfe_production/PHASE5_OK
EMB3_INC=$ROOT/pilot/abfe_mmp1_holo_zn/abfe_production/PHASE5_INCONCLUSIVE
LOG=$ROOT/pilot/abfe_mmp1_holo_zn_embelin/launcher.log
LOCK=/tmp/genesis_zaff_embelin_launcher.lock

mkdir -p $ROOT/pilot/abfe_mmp1_holo_zn_embelin

# Lock so duplicate launches are no-op
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date -Is)] embelin launcher already running" | tee -a $LOG
  exit 0
fi

log() { echo "[$(date -Is)] $*" | tee -a $LOG; }

cd $ROOT

log "=== embelin ABFE launcher started ==="
log "  waiting for EMB-3 Phase 5 to finish ($EMB3_OK or $EMB3_INC)"

# Poll every 60s for up to 24h
for i in $(seq 1 1440); do
    if [[ -f "$EMB3_OK" ]]; then
        log "EMB-3 Phase 5 PASS detected (PHASE5_OK) after $((i*60))s wait"
        break
    fi
    if [[ -f "$EMB3_INC" ]]; then
        log "EMB-3 Phase 5 INCONCLUSIVE detected — proceeding with embelin anyway"
        break
    fi
    sleep 60
done

if [[ ! -f "$EMB3_OK" && ! -f "$EMB3_INC" ]]; then
    log "TIMEOUT: 24h elapsed without EMB-3 marker; aborting embelin launch"
    exit 1
fi

# Sanity: GPU should be free for embelin
gpu_busy_pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | tr -d ' ' | grep -v '^$' | wc -l)
log "  GPU compute apps still active: $gpu_busy_pids"

# Make sure no leftover Phase 5 processes are running on EMB-3
pgrep -fa "zaff_phase5_abfe_production.py" | tee -a $LOG || true

# Launch embelin orchestrator
log "==> launching embelin orchestrator"
CONDA_PY=/home/crazat/miniforge3/envs/genesis-md/bin/python
ORCH_LOG=$ROOT/pilot/abfe_mmp1_holo_zn_embelin/orchestrator_stdout.log

PYTHONUNBUFFERED=1 $CONDA_PY scripts/zaff_orchestrator_embelin.py --skip-60ns-wait \
    > $ORCH_LOG 2>&1 &
ORCH_PID=$!
log "  embelin orchestrator PID=$ORCH_PID, log=$ORCH_LOG"

# Wait for orchestrator
wait $ORCH_PID
RC=$?
log "<== embelin orchestrator exit rc=$RC"
log "ZAFF_EMBELIN_LAUNCHER_DONE rc=$RC"
exit $RC
