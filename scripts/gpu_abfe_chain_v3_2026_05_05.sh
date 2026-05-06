#!/bin/bash
# GPU ABFE MSS chain v3 — pgrep-free, foreground-block design.
#
# Strategy:
#   - Resume CHEMBL415: solvent leg + combine (complex_leg already done with PHASE5A_OK).
#   - Then run remaining compounds in pIC50 order, foreground-blocking each.
#
# Compounds (low pIC50 = stronger inhibitor):
#   CHEMBL415 (Batimastat 4 nM, complex done — finishing solvent + combine)
#   CHEMBL94487 (RS-130830 12 nM)
#   CHEMBL257077 (prinomastat-like 15 nM)
#   CHEMBL301236 (fluoro-aryl HX 42 nM)
#   CHEMBL292707 (Ilomastat 200 nM)
#   CHEMBL2105729 (negative control 18 μM)

set -u
ROOT=/home/crazat/genesis_medicine
CONDA_ENV_BIN=/home/crazat/miniforge3/envs/genesis-md/bin
PYTHON=$CONDA_ENV_BIN/python

# Critical: prepend conda env bin so subprocess.run(["tleap", ...]) resolves correctly.
export PATH=$CONDA_ENV_BIN:$PATH

LOG=$ROOT/pilot/abfe_benchmark_chembl/abfe_chain_v3_2026_05_05.log

ts() { date '+%Y-%m-%d %H:%M:%S'; }

run_full_compound() {
    local cmpd=$1
    local work=$ROOT/pilot/abfe_benchmark_chembl/$cmpd
    if [ ! -f "$work/complex/PHASE4_OK" ]; then
        echo "[$(ts)] SKIP $cmpd — Phase 4 gate missing" | tee -a $LOG
        return 1
    fi
    if [ -f "$work/abfe_production_mss/PHASE5_OK" ] \
       || [ -f "$work/abfe_production_mss/PHASE5_INCONCLUSIVE" ]; then
        echo "[$(ts)] SKIP $cmpd — already has final PHASE5 marker" | tee -a $LOG
        return 0
    fi
    echo "[$(ts)] launching ABFE MSS (full): $cmpd" | tee -a $LOG
    cd $ROOT
    $PYTHON -u scripts/zaff_phase5_abfe_production_mss.py \
        --work pilot/abfe_benchmark_chembl/$cmpd \
        --leg all > $work/abfe_production_mss.log 2>&1
    local rc=$?
    echo "[$(ts)] $cmpd python rc=$rc" | tee -a $LOG
    return $rc
}

run_solvent_then_combine() {
    local cmpd=$1
    local work=$ROOT/pilot/abfe_benchmark_chembl/$cmpd
    echo "[$(ts)] $cmpd: solvent leg" | tee -a $LOG
    cd $ROOT
    $PYTHON -u scripts/zaff_phase5_abfe_production_mss.py \
        --work pilot/abfe_benchmark_chembl/$cmpd \
        --leg solvent >> $work/abfe_production_mss.log 2>&1
    local rc=$?
    echo "[$(ts)] $cmpd solvent rc=$rc" | tee -a $LOG
    if [ "$rc" -ne 0 ]; then return $rc; fi

    echo "[$(ts)] $cmpd: combine" | tee -a $LOG
    $PYTHON -u scripts/zaff_phase5_abfe_production_mss.py \
        --work pilot/abfe_benchmark_chembl/$cmpd \
        --leg combine >> $work/abfe_production_mss.log 2>&1
    rc=$?
    echo "[$(ts)] $cmpd combine rc=$rc" | tee -a $LOG
    return $rc
}

echo "[$(ts)] === GPU ABFE MSS CHAIN v3 START (pgrep-free, conda-env PATH) ===" | tee -a $LOG
echo "[$(ts)] PATH=$PATH" | tee -a $LOG
echo "[$(ts)] tleap=$(which tleap 2>/dev/null || echo NOT_FOUND)" | tee -a $LOG

# Step 1: finish CHEMBL415 (solvent leg + combine; complex already done)
run_solvent_then_combine CHEMBL415

# Step 2-6: full pipeline for remaining compounds
for cmpd in CHEMBL94487 CHEMBL257077 CHEMBL301236 CHEMBL292707 CHEMBL2105729; do
    run_full_compound $cmpd
done

echo "[$(ts)] === GPU ABFE MSS CHAIN v3 COMPLETE ===" | tee -a $LOG
