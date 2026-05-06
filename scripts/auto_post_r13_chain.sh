#!/bin/bash
# R13 종료 후 자동 chain:
#   1) R13 affinity consolidate
#   2) Bayesian v10 → R14 candidates
#   3) auto_r13_decision.py → STOP or PROCEED to R14
#   4) R12 super-leaders MD ensemble (병렬: R14 chain GPU 점유와 stagger)
cd /home/crazat/genesis_medicine
LOG=pilot/auto_post_r13.log
log() { echo "[$(date)] $*" | tee -a $LOG; }

source .venv/bin/activate
log "=== Auto post-R13 pipeline start ==="

# R13 chain 종료 대기 (max 4h)
for i in {1..240}; do
    if ! pgrep -f gpu_r13_chain.sh > /dev/null; then
        log "R13 chain ended."
        break
    fi
    sleep 60
done

# Step 1: R13 consolidate
log "Step 1: R13 affinity consolidation"
python scripts/cpu_consolidate_r13_affinity.py 2>&1 | tee -a $LOG

# Step 2: Bayesian v10 R14 candidates
log "Step 2: Bayesian v10 R14 candidates"
python scripts/cpu_bayesian_v10_post_r13.py 2>&1 | tee -a $LOG

# Step 3: R14 자율 결정
log "Step 3: R14 자율 결정 (EI saturate + leader continuity)"
python scripts/auto_r13_decision.py 2>&1 | tee -a $LOG
DECISION=$?

# Step 4: R12 super-leaders MD ensemble (genesis-md env, 75 min GPU)
log "Step 4: R12 super-leaders MD ensemble (R12_4 + R12_11 + R12_23 × 7 targets)"
source ~/miniforge3/etc/profile.d/conda.sh && conda activate genesis-md
python scripts/run_r12_super_leaders_md.py 2>&1 | tee -a $LOG
conda deactivate

# Step 5: R14 chain (only if not stop)
source .venv/bin/activate
if [ $DECISION -eq 2 ]; then
    log "❌ Decision: STOP (Bayesian saturate). R12_4 + R12_11 + R12_23 + R11_0 quad-leader 확정."
    log "=== Auto post-R13 pipeline END (saturate) ==="
    exit 0
fi

log "Step 6: R14 cached-MSA yamls + chain"
python scripts/gen_r14_cached_msa_yamls.py 2>&1 | tee -a $LOG
nohup bash scripts/gpu_r14_chain.sh > pilot/r14_chain.log 2>&1 &
echo $! > pilot/r14_pid.txt
log "R14 chain started PID=$(cat pilot/r14_pid.txt)"

log "=== Auto post-R13 pipeline complete ==="
