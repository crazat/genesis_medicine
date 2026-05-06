#!/bin/bash
ROOT=/home/crazat/genesis_medicine
ENVBIN=/home/crazat/miniforge3/envs/genesis-md/bin
LOG=$ROOT/pilot/cpu_meaningful/cpu_chain_720_to_816_2026_05_05.log
ts() { date '+%Y-%m-%d %H:%M:%S'; }
echo "[$(ts)] waiting for hetero10 720 main PID 2271100 to exit" | tee -a $LOG
while kill -0 2271100 2>/dev/null; do sleep 15; done
echo "[$(ts)] 720 done — launching 816 ladder" | tee -a $LOG
cd $ROOT
PATH=$ENVBIN:$PATH $ENVBIN/python -u scripts/cpu_xtb_hetero10_refine_816.py   > pilot/cpu_meaningful/hetero10_816_2026_05_05.log 2>&1
rc=$?
echo "[$(ts)] 816 rc=$rc" | tee -a $LOG
