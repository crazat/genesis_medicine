#!/bin/bash
# Stream A — replicate chain for paper #A sampling sensitivity.
# Sequential: 292707_rep2 → 415_rep2 → 94487_rep2
# Foreground-block (no pgrep). Conda env PATH prepended.

set -u
ROOT=/home/crazat/genesis_medicine
CONDA_ENV_BIN=/home/crazat/miniforge3/envs/genesis-md/bin
PYTHON=$CONDA_ENV_BIN/python
export PATH=$CONDA_ENV_BIN:$PATH
LOG=$ROOT/pilot/abfe_benchmark_chembl/abfe_replicate_stream_a.log
ts() { date '+%Y-%m-%d %H:%M:%S'; }

run_rep() {
    local cmpd=$1
    local work=$ROOT/pilot/abfe_benchmark_chembl/${cmpd}_rep2
    if [ ! -d "$work/complex" ]; then
        echo "[$(ts)] SKIP ${cmpd}_rep2 — complex/ symlink missing" | tee -a $LOG
        return 1
    fi
    echo "[$(ts)] launching ${cmpd}_rep2" | tee -a $LOG
    cd $ROOT
    $PYTHON -u scripts/zaff_phase5_abfe_production_mss.py \
        --work pilot/abfe_benchmark_chembl/${cmpd}_rep2 \
        --leg all > $work/abfe_rep2.log 2>&1
    local rc=$?
    echo "[$(ts)] ${cmpd}_rep2 rc=$rc" | tee -a $LOG
}

echo "[$(ts)] === STREAM A START (292707 → 415 → 94487) ===" | tee -a $LOG
for cmpd in CHEMBL292707 CHEMBL415 CHEMBL94487; do
    run_rep $cmpd
done
echo "[$(ts)] === STREAM A COMPLETE ===" | tee -a $LOG
