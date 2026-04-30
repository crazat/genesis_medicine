#!/bin/bash
# R15 chromanol × 14 targets Boltz-2 cofold chain.
# batch2 30ns GPU 작업과 GPU memory 공존 가능 (~2GB used / 32GB).
#
# Output: pilot/cpu_meaningful/output_r15_chromanol/

set -e
cd /home/crazat/genesis_medicine
source .venv/bin/activate

OUT=pilot/cpu_meaningful
INDIR=$OUT/inputs_r15_chromanol
OUTDIR=$OUT/output_r15_chromanol
LOG=pilot/r15_chromanol_chain.log

log() { echo "[$(date)] $*" | tee -a $LOG; }

log "=== R15 chromanol × 14 targets cofold chain start ==="
log "Candidate: OCC1COc2cc(O)ccc2C1 (R12_4 chromanol, ADMET triple-safe)"

NIN=$(ls $INDIR/*.yaml | wc -l)
log "Inputs: $NIN YAMLs in $INDIR"

mkdir -p $OUTDIR
boltz predict $INDIR --out_dir $OUTDIR \
    --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
    --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
    --affinity_mw_correction --devices 1 \
    2>&1 | tee -a $LOG

log "=== R15 chromanol cofold chain complete ==="
ls $OUTDIR/predictions/ | head -20 | tee -a $LOG
