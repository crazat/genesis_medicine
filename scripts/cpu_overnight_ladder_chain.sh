#!/bin/bash
# Overnight CPU ladder chain: 528 (running) → 480 → 576 → AL round 3
# Polls 528 csv completion before chaining 480, then 576 sequential.
# Launched as nohup background; 12h sleep window 2026-05-05 22:48 → 10:48 KST.

set -u
ROOT=/home/crazat/genesis_medicine
CONDA_ENV_BIN=/home/crazat/miniforge3/envs/genesis-md/bin
PYTHON=$CONDA_ENV_BIN/python
export PATH=$CONDA_ENV_BIN:$PATH
LOG=$ROOT/pilot/cpu_meaningful/overnight_ladder_chain.log
TARGET_LINES=1000  # 1066 mol but allow 16 stragglers (timeout/error mol)
ts() { date '+%Y-%m-%d %H:%M:%S'; }

wait_for_csv_or_pid_done() {
    local csv=$1
    local pname=$2
    while true; do
        local lines=$(wc -l < "$csv" 2>/dev/null || echo 0)
        local nproc=$(pgrep -f "$pname" | wc -l)
        if [ "$lines" -ge "$TARGET_LINES" ] && [ "$nproc" -eq 0 ]; then
            echo "[$(ts)] DONE $csv lines=$lines nproc=0" | tee -a $LOG
            break
        fi
        if [ "$nproc" -eq 0 ] && [ "$lines" -ge 200 ]; then
            echo "[$(ts)] PROCESS_GONE $csv lines=$lines (assume done)" | tee -a $LOG
            break
        fi
        sleep 120
    done
}

run_ladder() {
    local script=$1
    local csv=$2
    echo "[$(ts)] launching $script" | tee -a $LOG
    cd $ROOT
    $PYTHON -u scripts/$script > pilot/cpu_meaningful/${script%.py}_chain_run.log 2>&1
    local rc=$?
    local lines=$(wc -l < $csv 2>/dev/null || echo 0)
    echo "[$(ts)] $script rc=$rc lines=$lines" | tee -a $LOG
}

echo "[$(ts)] === OVERNIGHT LADDER CHAIN START ===" | tee -a $LOG

# Step 1: wait for 528 (already running, PID launched 22:47) to drain
wait_for_csv_or_pid_done \
    $ROOT/pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_528conf.csv \
    cpu_xtb_hetero10_refine_528.py

# Step 2: launch 480 (resume from existing 81-line csv)
run_ladder cpu_xtb_hetero10_refine_480.py \
    $ROOT/pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_480conf.csv

# Step 3: launch 576
run_ladder cpu_xtb_hetero10_refine_576.py \
    $ROOT/pilot/cpu_meaningful/xtb_npass_top9997_hetero10_refine_576conf.csv

echo "[$(ts)] === OVERNIGHT LADDER CHAIN COMPLETE ===" | tee -a $LOG
