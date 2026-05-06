#!/bin/bash
set -u
ROOT=/home/crazat/genesis_medicine
ENVBIN=/home/crazat/miniforge3/envs/genesis-md/bin
export PATH=$ENVBIN:$PATH
LOG=$ROOT/pilot/abfe_benchmark_chembl/CHEMBL257077/warmup_abfe_2026_05_05.log
ts() { date '+%Y-%m-%d %H:%M:%S'; }
cd $ROOT
echo "[$(ts)] === CHEMBL257077 warmup ===" | tee -a $LOG
$ENVBIN/python -u scripts/zaff_phase5_warmup_generic.py \
  --work pilot/abfe_benchmark_chembl/CHEMBL257077 \
  --leg complex >> $LOG 2>&1
rc=$?
echo "[$(ts)] warmup rc=$rc" | tee -a $LOG
if [ "$rc" -ne 0 ]; then exit $rc; fi

echo "[$(ts)] === CHEMBL257077 ABFE retry ===" | tee -a $LOG
# clean stale partial run
rm -rf $ROOT/pilot/abfe_benchmark_chembl/CHEMBL257077/abfe_production_mss/complex_leg
$ENVBIN/python -u scripts/zaff_phase5_abfe_production_mss.py \
  --work pilot/abfe_benchmark_chembl/CHEMBL257077 \
  --leg all >> $LOG 2>&1
rc=$?
echo "[$(ts)] ABFE rc=$rc" | tee -a $LOG
