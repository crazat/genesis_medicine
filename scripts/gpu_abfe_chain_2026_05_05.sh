#!/bin/bash
# GPU ABFE MSS chain — auto-launch next compound after PREVIOUS one finishes
# Robust: checks marker files + active python ABFE process count.
#
# Compounds in pIC50 order (low pIC50 = stronger inhibitor):
#   CHEMBL415 (Batimastat 4 nM, RUNNING — chain waits)
#   CHEMBL94487 (RS-130830 12 nM)
#   CHEMBL257077 (prinomastat-like 15 nM)
#   CHEMBL301236 (fluoro-aryl HX 42 nM)
#   CHEMBL292707 (Ilomastat 200 nM)
#   CHEMBL2105729 (negative control 18 μM)

set -u
ROOT=/home/crazat/genesis_medicine
PYTHON=/home/crazat/miniforge3/envs/genesis-md/bin/python
LOG=$ROOT/pilot/abfe_benchmark_chembl/abfe_chain_master_2026_05_05.log

ts() { date '+%Y-%m-%d %H:%M:%S'; }

# Returns 0 if ANY zaff_phase5_abfe_production_mss python process is running
abfe_process_count() {
    pgrep -af "python.*zaff_phase5_abfe_production_mss" 2>/dev/null \
        | grep -v "$$" | grep -c python || echo 0
}

# Wait until $1's PHASE4_OK exists AND no abfe_production_mss process for $1 is running.
# Ready to launch next compound when both legs done OR previous proc gone for ≥60s.
wait_for_compound_done() {
    local cmpd=$1
    local work=$ROOT/pilot/abfe_benchmark_chembl/$cmpd
    local result_cx=$work/abfe_production_mss/complex_leg/result.json
    local result_sv=$work/abfe_production_mss/solvent_leg/result.json
    local marker_cx=$work/abfe_production_mss/complex_leg/PHASE5A_OK
    local marker_sv=$work/abfe_production_mss/solvent_leg/PHASE5B_OK

    while true; do
        # both legs marker files present → done
        if [ -f "$marker_cx" ] && [ -f "$marker_sv" ]; then
            echo "[$(ts)] $cmpd both legs PHASE5*_OK markers found — done" | tee -a $LOG
            return 0
        fi
        # OR no abfe python process at all (script crashed or completed)
        local n=$(pgrep -f "python.*zaff_phase5_abfe_production_mss" 2>/dev/null | wc -l)
        if [ "$n" -eq "0" ]; then
            sleep 10
            n=$(pgrep -f "python.*zaff_phase5_abfe_production_mss" 2>/dev/null | wc -l)
            if [ "$n" -eq "0" ]; then
                echo "[$(ts)] no ABFE MSS python process for ≥10s — assuming $cmpd terminated" | tee -a $LOG
                return 0
            fi
        fi
        sleep 30
    done
}

run_abfe() {
    local cmpd=$1
    local work=$ROOT/pilot/abfe_benchmark_chembl/$cmpd
    if [ ! -f "$work/complex/PHASE4_OK" ]; then
        echo "[$(ts)] SKIP $cmpd — Phase 4 gate missing" | tee -a $LOG
        return 1
    fi
    if [ -f "$work/abfe_production_mss/PHASE5_OK" ] \
       || [ -f "$work/abfe_production_mss/PHASE5_INCONCLUSIVE" ]; then
        echo "[$(ts)] SKIP $cmpd — already has PHASE5 result" | tee -a $LOG
        return 0
    fi
    echo "[$(ts)] launching ABFE MSS: $cmpd" | tee -a $LOG
    cd $ROOT
    $PYTHON -u scripts/zaff_phase5_abfe_production_mss.py \
        --work pilot/abfe_benchmark_chembl/$cmpd \
        --leg all > $work/abfe_production_mss.log 2>&1
    rc=$?
    echo "[$(ts)] $cmpd python returned rc=$rc" | tee -a $LOG
    return $rc
}

echo "[$(ts)] === GPU ABFE MSS CHAIN START (v2: marker-based wait) ===" | tee -a $LOG

# Step 1: wait for currently-running CHEMBL415 to finish
echo "[$(ts)] waiting for CHEMBL415 to complete (markers or process exit)" | tee -a $LOG
wait_for_compound_done CHEMBL415

# Step 2-6: chain remaining compounds
for cmpd in CHEMBL94487 CHEMBL257077 CHEMBL301236 CHEMBL292707 CHEMBL2105729; do
    run_abfe $cmpd
    sleep 5
    wait_for_compound_done $cmpd
done

echo "[$(ts)] === GPU ABFE MSS CHAIN COMPLETE ===" | tee -a $LOG
