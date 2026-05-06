#!/usr/bin/env bash
# CPU auto-processor — watches GPU chain output dirs for new completions and
# re-runs paper-tier processing pipeline as new data arrives.
# Targets idle period saturation: triggers heavy 24-core work each time a
# GPU batch completes, NOT polling for nothing.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

LOG=/home/crazat/genesis_medicine/pilot/cpu_auto_processor.log
TRIGGER_FILE=/tmp/cpu_auto_proc_run

touch $TRIGGER_FILE

log() { echo "[$(date +%H:%M:%S)] $1" | tee -a $LOG; }

last_count=0
while [ -f $TRIGGER_FILE ]; do
    # Count current completed cofold dirs
    cur_count=$(find pilot -name "boltz_results_*" -type d 2>/dev/null | wc -l)

    # Number of completed predictions
    cur_preds=$(find pilot -name "*affinity*.json" 2>/dev/null | wc -l)

    if [ "$cur_preds" -gt "$last_count" ]; then
        delta=$((cur_preds - last_count))
        log "Detected $delta new affinity predictions ($last_count → $cur_preds)"

        # Re-run extraction + ranking
        python scripts/cpu_boltz_deep_extract.py >> $LOG 2>&1
        python scripts/cpu_full_cofold_ranker.py >> $LOG 2>&1
        python scripts/cpu_korean_herbal_xref.py >> $LOG 2>&1
        python scripts/cpu_master_table.py >> $LOG 2>&1
        python scripts/cpu_paper_figures.py >> $LOG 2>&1
        python scripts/cpu_korean_herbal_figures.py >> $LOG 2>&1

        last_count=$cur_preds
        log "  re-processing complete"
    fi

    sleep 300    # check every 5 min (cache TTL aligned)
done

log "STOPPED"
