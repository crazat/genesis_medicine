#!/bin/bash
ROOT=/home/crazat/genesis_medicine
ENVBIN=/home/crazat/miniforge3/envs/genesis-md/bin
LOG=$ROOT/pilot/cpu_meaningful/cpu_chain_624_to_720_2026_05_05.log
ts() { date '+%Y-%m-%d %H:%M:%S'; }
echo "[$(ts)] waiting for hetero10 624 main PID 1566543 to exit" | tee -a $LOG
while kill -0 1566543 2>/dev/null; do sleep 15; done
echo "[$(ts)] 624 done — launching 720 ladder" | tee -a $LOG
cd $ROOT
PATH=$ENVBIN:$PATH $ENVBIN/python -u scripts/cpu_xtb_hetero10_refine_720.py \
  > pilot/cpu_meaningful/hetero10_720_2026_05_05.log 2>&1
rc=$?
echo "[$(ts)] 720 rc=$rc" | tee -a $LOG
