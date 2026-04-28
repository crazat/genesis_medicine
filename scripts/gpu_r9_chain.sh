#!/bin/bash
# R9 GPU chain
cd /home/crazat/genesis_medicine
source .venv/bin/activate
OUT=pilot/cpu_meaningful
LOG=pilot/r9_chain.log
log() { echo "[$(date)] $*" | tee -a $LOG; }

log "=== R9 chain start ==="
TARGETS=(tgfb1 mmp1 ctgf ar mitf lox sirt1 tyr tyrp1 dct srd5a1 srd5a2 srebp1 ptgs2)
for tgt in "${TARGETS[@]}"; do
    INDIR=$OUT/inputs_r9_$tgt
    OUTDIR=$OUT/output_r9_$tgt
    [ -d "$INDIR" ] || { log "skip $tgt"; continue; }
    NIN=$(ls $INDIR | wc -l)
    log "R9 $tgt cofold start ($NIN inputs)"
    rm -rf $OUTDIR
    boltz predict $INDIR --out_dir $OUTDIR \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        2>&1 | tail -5 | tee -a $LOG
    log "R9 $tgt cofold done"
done
log "=== R9 chain complete (14 × 30 = 420) ==="
