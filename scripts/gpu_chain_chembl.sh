#!/usr/bin/env bash
# GPU chain: 5-target Boltz-2 batch이 끝나는 즉시 ChEMBL extended 95 inhibitor × MMP-1 cofold batch 이어서 실행.
# GPU idle 방지 — 메모리 hard requirement.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

log() { echo "[$(date +%H:%M:%S)] $1"; }

# Wait until previous gpu_queue_worker.sh fully completes (5 batches ctgf/sirt1/lox/ar/mitf)
log "Waiting for gpu_queue_worker.sh (PID 277604) to finish 5-target sequence..."
while pgrep -f "gpu_queue_worker.sh" > /dev/null; do
    sleep 60
done
log "5-target sequence done — chaining ChEMBL extended batch"

# ChEMBL extended × MMP-1 calibration extension cofold
INPUT_DIR=pilot/cpu_meaningful/chembl_extended_inputs
OUT_DIR=pilot/cpu_meaningful/chembl_extended_output

NCOUNT=$(ls $INPUT_DIR/*.yaml 2>/dev/null | wc -l)
log "ChEMBL extended cofold: $NCOUNT inhibitors × MMP-1"

if [ "$NCOUNT" -gt 0 ]; then
    boltz predict $INPUT_DIR \
        --out_dir $OUT_DIR \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 5 \
        --affinity_mw_correction --devices 1 \
        > pilot/cpu_meaningful/chembl_extended_cofold.log 2>&1
    log "ChEMBL extended cofold done"
else
    log "No ChEMBL yamls found — skipping"
fi

# After ChEMBL: extract all results into consolidated CSV
log "Re-extracting all Boltz-2 affinity results"
python <<'PY' >> pilot/cpu_meaningful/task1_extract.log 2>&1
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
                'target': tgt_part,
                'compound': cmpd_part,
                'source': str(affinity_json.parent.parent.name),
                'affinity_pred': d.get('affinity_pred_value'),
                'affinity_prob_binary': d.get('affinity_probability_binary'),
            })
        except Exception:
            pass
df = pd.DataFrame(results).drop_duplicates(['target','compound'])
df.to_csv('pilot/cpu_meaningful/all_boltz2_affinity_consolidated.csv', index=False)
print(f'Final consolidation: {len(df)} unique cofold rows')
print(df.groupby('target').size().sort_values(ascending=False))
PY
log "=== GPU chain complete ==="
