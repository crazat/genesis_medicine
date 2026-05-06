#!/bin/bash
# CPU follow-up queue: 현재 가동 중인 xtb refine 두 개가 끝나면 sequential하게
# 다음 batch (hetero3, hetero10)를 자동으로 launch. 12h 자율운전용.
set -u

ROOT=/home/crazat/genesis_medicine
PY=$ROOT/.venv/bin/python
LOG=$ROOT/pilot/cpu_followup_queue.log
LOCK=/tmp/genesis_cpu_followup_queue.lock

mkdir -p $ROOT/pilot

# Lock so duplicate launch is no-op
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date -Is)] cpu_followup_queue already running — exiting duplicate" | tee -a $LOG
  exit 0
fi

log() { echo "[$(date -Is)] $*" | tee -a $LOG; }

cd $ROOT

log "=== CPU follow-up queue started ==="
log "  monitoring pgrep -f cpu_xtb_npass_top_refine"

# Step 1: wait for currently-running refine jobs to finish
# We poll every 5 min (max 12h)
for i in $(seq 1 144); do
    n=$(pgrep -fc cpu_xtb_npass_top_refine || true)
    if [ "$n" -le 1 ]; then  # pgrep counts itself sometimes; treat <=1 as 'done'
        # Re-verify with a stricter check (excluding our own pgrep child)
        if ! pgrep -af cpu_xtb_npass_top_refine | grep -v "pgrep" | grep -q .; then
            log "current xtb refine jobs ended (after $((i*5)) min wait)"
            break
        fi
    fi
    sleep 300
done

# Step 2: launch round 1 — hetero3 (less restrictive, more candidates)
log "Round 1: launching top3000 hetero3 384conf"
nohup $PY -u scripts/cpu_xtb_npass_top_refine.py \
    --topn 3000 --workers 12 --num-confs 384 --min-hetero-atoms 3 \
    --out xtb_npass_top3000_hetero3_refine_384conf.csv \
    > $ROOT/pilot/cpu_xtb_top3000_hetero3_384.log 2>&1 &
R1_PID=$!
log "  Round 1 PID=$R1_PID"
wait $R1_PID
R1_RC=$?
log "  Round 1 rc=$R1_RC"

# Step 3: launch round 2 — hetero10 (most restrictive, smallest subset, fast)
log "Round 2: launching top3000 hetero10 384conf"
nohup $PY -u scripts/cpu_xtb_npass_top_refine.py \
    --topn 3000 --workers 12 --num-confs 384 --min-hetero-atoms 10 \
    --out xtb_npass_top3000_hetero10_refine_384conf.csv \
    > $ROOT/pilot/cpu_xtb_top3000_hetero10_384.log 2>&1 &
R2_PID=$!
log "  Round 2 PID=$R2_PID"
wait $R2_PID
R2_RC=$?
log "  Round 2 rc=$R2_RC"

# Step 4: round 3 — top10000 hetero5 expansion (large pool, slowest — fills any remaining time)
log "Round 3: launching top10000 hetero5 384conf (large pool fill)"
nohup $PY -u scripts/cpu_xtb_npass_top_refine.py \
    --topn 10000 --workers 12 --num-confs 384 --min-hetero-atoms 5 \
    --out xtb_npass_top10000_hetero5_refine_384conf.csv \
    > $ROOT/pilot/cpu_xtb_top10000_hetero5_384.log 2>&1 &
R3_PID=$!
log "  Round 3 PID=$R3_PID"
wait $R3_PID
R3_RC=$?
log "  Round 3 rc=$R3_RC"

log "=== CPU follow-up queue done (R1=$R1_RC R2=$R2_RC R3=$R3_RC) ==="
echo CPU_FOLLOWUP_DONE
