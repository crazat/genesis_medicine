#!/bin/bash
set -u
ROOT=/home/crazat/genesis_medicine
ENVBIN=/home/crazat/miniforge3/envs/genesis-md/bin
export PATH=$ENVBIN:$PATH
LOG=$ROOT/pilot/abfe_benchmark_chembl/warmup_chain_remaining_2026_05_05.log
ts() { date '+%Y-%m-%d %H:%M:%S'; }
cd $ROOT
echo "[$(ts)] === warmup chain: 301236 → 292707 → 2105729 ===" | tee -a $LOG
for c in CHEMBL301236 CHEMBL292707 CHEMBL2105729; do
    echo "[$(ts)] $c warmup start" | tee -a $LOG
    $ENVBIN/python -u scripts/zaff_phase5_warmup_generic.py \
        --work pilot/abfe_benchmark_chembl/$c \
        --leg complex >> $LOG 2>&1
    rc=$?
    echo "[$(ts)] $c warmup rc=$rc" | tee -a $LOG
    if [ "$rc" -ne 0 ]; then echo "[$(ts)] FAIL $c — stop chain"; exit $rc; fi
done
echo "[$(ts)] === warmup chain DONE ===" | tee -a $LOG
