#!/usr/bin/env bash
# Remainder GPU chain v2 — runs AFTER current ChEMBL extended boltz completes.
# Lightweight params (1 affinity sample) for large proteins.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

LOG=pilot/gpu_remainder_v2.log
log() { echo "[$(date +%H:%M:%S)] $1" | tee -a $LOG; }

# Wait for ChEMBL extended cofold to finish (currently running, PID 321533)
log "Waiting for chembl_extended boltz to complete..."
while pgrep -f "boltz predict pilot/cpu_meaningful/chembl_extended_inputs" > /dev/null; do
    sleep 60
done
log "ChEMBL extended done"

# TYR: 530 residues — moderate. Use 1 sample.
log "=== TYR (100 × top BRICS, 1 sample) ==="
boltz predict pilot/cpu_meaningful/inputs_tyr \
    --out_dir pilot/cpu_meaningful/output_tyr \
    --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
    --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
    --affinity_mw_correction --devices 1 \
    > pilot/cpu_meaningful/tyr_cofold.log 2>&1
log "  TYR done"

# Low-coverage targets: smaller proteins, 1 sample
for target in srd5a2 ptgs2 jun dct; do
    log "=== $target (100 × top BRICS, 1 sample) ==="
    INPUT_DIR=pilot/cpu_meaningful/inputs_${target}
    OUT_DIR=pilot/cpu_meaningful/output_${target}
    if [ ! -d "$INPUT_DIR" ]; then
        log "  $INPUT_DIR missing, skip"
        continue
    fi
    boltz predict $INPUT_DIR \
        --out_dir $OUT_DIR \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        > pilot/cpu_meaningful/${target}_cofold.log 2>&1
    log "  $target done"
done

# Final consolidation
log "=== Final consolidation ==="
python -c "
import json
from pathlib import Path
import pandas as pd
results = []
for output_dir in Path('pilot').rglob('boltz_results_*'):
    for affinity_json in output_dir.rglob('*affinity*.json'):
        try:
            d = json.loads(affinity_json.read_text())
            stem = affinity_json.stem.replace('affinity_', '')
            tgt_part = stem.split('__')[0] if '__' in stem else 'unknown'
            cmpd_part = stem.split('__')[-1].replace('_model_0','').replace('_affinity','')
            results.append({
                'target': tgt_part, 'compound': cmpd_part,
                'source': str(affinity_json.parent.parent.name),
                'affinity_pred': d.get('affinity_pred_value'),
                'affinity_prob_binary': d.get('affinity_probability_binary'),
            })
        except: pass
df = pd.DataFrame(results).drop_duplicates(['target','compound'])
df.to_csv('pilot/cpu_meaningful/all_boltz2_affinity_consolidated.csv', index=False)
print(f'FINAL: {len(df)} cofold rows')
print(df.groupby('target').size())
" >> $LOG 2>&1
log "=== ALL REMAINDER DONE ==="
