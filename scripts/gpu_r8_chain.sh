#!/bin/bash
# R8 GPU chain — 14 cached-MSA targets × 30 R8 candidates
cd /home/crazat/genesis_medicine
source .venv/bin/activate
OUT=pilot/cpu_meaningful
LOG=pilot/r8_chain.log
log() { echo "[$(date)] $*" | tee -a $LOG; }

log "=== R8 chain start ==="
TARGETS=(tgfb1 mmp1 ctgf ar mitf lox sirt1 tyr tyrp1 dct srd5a1 srd5a2 srebp1 ptgs2)
for tgt in "${TARGETS[@]}"; do
    INDIR=$OUT/inputs_r8_$tgt
    OUTDIR=$OUT/output_r8_$tgt
    [ -d "$INDIR" ] || { log "skip $tgt (no inputs)"; continue; }
    NIN=$(ls $INDIR | wc -l)
    log "R8 $tgt cofold start ($NIN inputs)"
    rm -rf $OUTDIR
    boltz predict $INDIR --out_dir $OUTDIR \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        2>&1 | tail -5 | tee -a $LOG
    log "R8 $tgt cofold done"
done
log "=== R8 chain complete (14 targets × 30 = 420 cofolds) ==="
