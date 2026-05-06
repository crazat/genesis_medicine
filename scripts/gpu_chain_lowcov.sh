#!/usr/bin/env bash
# GPU chain step 4: After TYR completes, run low-coverage targets sequentially.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

log() { echo "[$(date +%H:%M:%S)] $1"; }

log "Waiting for gpu_chain_tyr.sh..."
while pgrep -f "gpu_chain_tyr.sh" > /dev/null; do
    sleep 60
done
log "TYR done — starting low-coverage chain"

for target in srd5a2 ptgs2 jun dct; do
    INPUT_DIR=pilot/cpu_meaningful/inputs_${target}
    OUT_DIR=pilot/cpu_meaningful/output_${target}
    NCOUNT=$(ls $INPUT_DIR/*.yaml 2>/dev/null | wc -l)
    log "$target: $NCOUNT yamls"
    if [ "$NCOUNT" -gt 0 ]; then
        boltz predict $INPUT_DIR \
            --out_dir $OUT_DIR \
            --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
            --sampling_steps_affinity 200 --diffusion_samples_affinity 5 \
            --affinity_mw_correction --devices 1 \
            > pilot/cpu_meaningful/${target}_cofold.log 2>&1
        log "  $target done"
    fi
done

# Final consolidation
log "Final consolidation across all batches"
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
print(f'COMPLETE FINAL: {len(df)} cofold rows')
print(df.groupby('target').size().sort_values(ascending=False))
PY
log "=== Full GPU chain complete (5 + ChEMBL + TYR + 4 lowcov) ==="
