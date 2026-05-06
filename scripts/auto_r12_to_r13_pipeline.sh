#!/bin/bash
# R12 종료 후 자동 chain: consolidate → Bayesian v9 → R13 yamls → R13 chain
# Triggered by wakeup at 22:35
cd /home/crazat/genesis_medicine
source .venv/bin/activate
LOG=pilot/auto_r12_to_r13.log
log() { echo "[$(date)] $*" | tee -a $LOG; }

log "=== Auto R12→R13 pipeline start ==="

# R12 chain 종료 대기 (max 60 min)
for i in {1..60}; do
    if ! pgrep -f gpu_r12_chain.sh > /dev/null; then
        log "R12 chain ended."
        break
    fi
    sleep 60
done

# R12 affinity consolidate
log "Step 1: R12 affinity consolidation"
python scripts/cpu_consolidate_r12_affinity.py 2>&1 | tee -a $LOG

# Bayesian v9 → R13 candidates
log "Step 2: Bayesian v9 R13 candidates"
python scripts/cpu_bayesian_v9_post_r12.py 2>&1 | tee -a $LOG

# R13 yamls
log "Step 3: R13 cached-MSA yamls"
python scripts/gen_r13_cached_msa_yamls.py 2>&1 | tee -a $LOG

# R13 chain
log "Step 4: R13 chain start (background)"
nohup bash scripts/gpu_r13_chain.sh > pilot/r13_chain.log 2>&1 &
echo $! > pilot/r13_pid.txt
log "R13 chain started PID=$(cat pilot/r13_pid.txt)"

log "=== Auto R12→R13 pipeline complete ==="
