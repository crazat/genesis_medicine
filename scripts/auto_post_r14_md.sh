#!/bin/bash
# R14 종료 후 자동: R12 super-leaders MD ensemble (genesis-md python 직접 사용)
cd /home/crazat/genesis_medicine
LOG=pilot/auto_post_r14_md.log
log() { echo "[$(date)] $*" | tee -a $LOG; }
GENESIS_MD_PY=/home/crazat/miniforge3/envs/genesis-md/bin/python

log "=== Auto post-R14 MD start ==="

# R14 chain 종료 대기 (max 4h)
for i in {1..240}; do
    if ! pgrep -f gpu_r14_chain.sh > /dev/null; then
        log "R14 chain ended."
        break
    fi
    sleep 60
done

# R12 super-leaders MD ensemble (직접 genesis-md python 사용)
log "Step 1: R12 super-leaders MD ensemble (R12_4 + R12_11 + R12_23 × 7 targets)"
$GENESIS_MD_PY scripts/run_r12_super_leaders_md.py 2>&1 | tee -a $LOG

# R13 super-leaders MD (R13_11 + R13_13 식별됨)
log "Step 2: R13 super-leaders MD ensemble"
if [ -f scripts/run_r13_super_leaders_md.py ]; then
    $GENESIS_MD_PY scripts/run_r13_super_leaders_md.py 2>&1 | tee -a $LOG
else
    log "  R13 super-leaders MD script 미작성 — skip"
fi

# Preprint #15 R11_0/R12 universal scaffold paper draft
log "Step 3: Preprint #15 draft"
if [ -f scripts/cpu_preprint_15_universal_scaffold.py ]; then
    /home/crazat/genesis_medicine/.venv/bin/python scripts/cpu_preprint_15_universal_scaffold.py 2>&1 | tee -a $LOG
else
    log "  Preprint #15 script 미작성 — manual 후속"
fi

log "=== Auto post-R14 MD complete ==="
