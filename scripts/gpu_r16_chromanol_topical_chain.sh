#!/usr/bin/env bash
# R16 topical chromanol analog cofold chain: top 6 analogs × TGFB1/TYR/DCT.

set -euo pipefail

cd /home/crazat/genesis_medicine
source .venv/bin/activate

LOG=pilot/r16_chromanol_topical_chain.log
INDIR=pilot/cpu_meaningful/inputs_r16_chromanol_topical
OUTDIR=pilot/cpu_meaningful/output_r16_chromanol_topical

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

log "R16 topical chromanol cofold chain start"
python scripts/gen_r16_chromanol_topical_yamls.py 2>&1 | tee -a "$LOG"

rm -rf "$OUTDIR"
mkdir -p "$OUTDIR"

NIN=$(find "$INDIR" -name '*.yaml' | wc -l)
log "Boltz-2 inputs: $NIN"

boltz predict "$INDIR" \
    --out_dir "$OUTDIR" \
    --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
    --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
    --affinity_mw_correction --devices 1 \
    2>&1 | tee -a "$LOG"

log "R16 topical chromanol cofold chain complete"
