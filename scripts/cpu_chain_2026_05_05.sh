#!/bin/bash
# 5-6h CPU chain after current ChEMBL refine completes
# Runs sequentially; each stage logs to its own file + master log.

set -u
ROOT=/home/crazat/genesis_medicine
PYTHON=/home/crazat/miniforge3/envs/genesis-md/bin/python
LOG=$ROOT/pilot/cpu_meaningful/cpu_chain_master_2026_05_05.log

ts() { date '+%Y-%m-%d %H:%M:%S'; }

echo "[$(ts)] === CPU CHAIN START ===" | tee -a $LOG

# --- Wait for current ChEMBL MMP-1 refine to finish ---
echo "[$(ts)] Stage 0: waiting for cpu_xtb_chembl_mmp1_refine_432 to finish" | tee -a $LOG
while pgrep -f "cpu_xtb_chembl_mmp1_refine_432" > /dev/null 2>&1; do
    sleep 30
done
echo "[$(ts)] Stage 0 (ChEMBL refine) done" | tee -a $LOG

# --- Stage 1: hetero10 432-conf complete (~2.75h, ~905 mol remaining) ---
echo "[$(ts)] Stage 1: hetero10 top9997 432-conf RESUME" | tee -a $LOG
cd $ROOT
$PYTHON -u scripts/cpu_xtb_hetero10_refine_432_resume.py \
    > pilot/cpu_meaningful/cpu_chain_stage1_hetero10_432.log 2>&1
echo "[$(ts)] Stage 1 done (hetero10 432-conf)" | tee -a $LOG

# --- Stage 2: ChEMBL pIC50 vs xtb correlation analysis ---
echo "[$(ts)] Stage 2: ChEMBL pIC50 vs xtb correlation" | tee -a $LOG
$PYTHON -u scripts/analyze_chembl_pic50_xtb_correlation.py \
    > pilot/cpu_meaningful/cpu_chain_stage2_chembl_corr.log 2>&1
echo "[$(ts)] Stage 2 done" | tee -a $LOG

# --- Stage 3: hetero10 cross-engine consistency (refine_432 vs singlept) ---
echo "[$(ts)] Stage 3: hetero10 cross-engine consistency" | tee -a $LOG
$PYTHON -u scripts/analyze_hetero10_cross_engine.py \
    > pilot/cpu_meaningful/cpu_chain_stage3_hetero10_consist.log 2>&1
echo "[$(ts)] Stage 3 done" | tee -a $LOG

# --- Stage 4: Active learning v3 (XGBoost on combined ChEMBL + NPAtlas) ---
echo "[$(ts)] Stage 4: AL v3 XGBoost combined" | tee -a $LOG
$PYTHON -u scripts/al_v3_xgboost_combined.py \
    > pilot/cpu_meaningful/cpu_chain_stage4_alv3.log 2>&1
echo "[$(ts)] Stage 4 done" | tee -a $LOG

# --- Stage 5: DUD-E F3 enrichment recompute with hetero10 432-conf ---
echo "[$(ts)] Stage 5: DUD-E enrichment recompute" | tee -a $LOG
$PYTHON -u scripts/dude_recompute_with_hetero10_432.py \
    > pilot/cpu_meaningful/cpu_chain_stage5_dude.log 2>&1
echo "[$(ts)] Stage 5 done" | tee -a $LOG

echo "[$(ts)] === CPU CHAIN COMPLETE ===" | tee -a $LOG
