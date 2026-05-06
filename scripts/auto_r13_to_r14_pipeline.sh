#!/bin/bash
# R13 종료 후 자동 chain: consolidate → Bayesian v10 → R14 결정 → R14 chain or stop
# Triggered by wakeup at 02:00
cd /home/crazat/genesis_medicine
source .venv/bin/activate
LOG=pilot/auto_r13_to_r14.log
log() { echo "[$(date)] $*" | tee -a $LOG; }

log "=== Auto R13→R14 pipeline start ==="

# R13 chain 종료 대기 (max 4h)
for i in {1..240}; do
    if ! pgrep -f gpu_r13_chain.sh > /dev/null; then
        log "R13 chain ended."
        break
    fi
    sleep 60
done

# R13 affinity consolidate
log "Step 1: R13 affinity consolidation"
python scripts/cpu_consolidate_r13_affinity.py 2>&1 | tee -a $LOG

# Bayesian v10 → R14 candidates
log "Step 2: Bayesian v10 R14 candidates"
python scripts/cpu_bayesian_v10_post_r13.py 2>&1 | tee -a $LOG

# R14 자동 결정
log "Step 3: R14 decision (EI saturate + leader continuity)"
python scripts/auto_r13_decision.py 2>&1 | tee -a $LOG
DECISION=$?

if [ $DECISION -eq 2 ]; then
    log "❌ Decision: STOP (Bayesian saturate confirmed). R12_0 + R13_0 dual-leader 확정."
    log "=== Auto R13→R14 pipeline END (saturate) ==="
    exit 0
fi

# R14 yamls + chain
log "Step 4: R14 cached-MSA yamls"
python scripts/gen_r14_cached_msa_yamls.py 2>&1 | tee -a $LOG

log "Step 5: R14 chain start (background)"
nohup bash scripts/gpu_r14_chain.sh > pilot/r14_chain.log 2>&1 &
echo $! > pilot/r14_pid.txt
log "R14 chain started PID=$(cat pilot/r14_pid.txt)"

log "=== Auto R13→R14 pipeline complete ==="
