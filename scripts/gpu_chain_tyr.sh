#!/usr/bin/env bash
# GPU chain step 3: After gpu_chain_chembl.sh completes, run TYR (pigmentation).
# Keeps GPU saturated end-to-end.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

log() { echo "[$(date +%H:%M:%S)] $1"; }

# Wait for ChEMBL chain to finish
log "Waiting for gpu_chain_chembl.sh to finish..."
while pgrep -f "gpu_chain_chembl.sh" > /dev/null; do
    sleep 60
done
log "ChEMBL chain done — starting TYR (pigmentation) batch"

INPUT_DIR=pilot/cpu_meaningful/inputs_tyr
OUT_DIR=pilot/cpu_meaningful/output_tyr

NCOUNT=$(ls $INPUT_DIR/*.yaml 2>/dev/null | wc -l)
log "TYR cofold: $NCOUNT inhibitors × top100 BRICS"

if [ "$NCOUNT" -gt 0 ]; then
    boltz predict $INPUT_DIR \
        --out_dir $OUT_DIR \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 5 \
        --affinity_mw_correction --devices 1 \
        > pilot/cpu_meaningful/tyr_cofold.log 2>&1
    log "TYR cofold done"
fi

# Final consolidation
log "Final consolidation: re-extracting all Boltz-2 affinity"
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
print(f'FINAL: {len(df)} unique cofold rows')
print(df.groupby('target').size().sort_values(ascending=False))
PY
log "=== Full GPU chain complete (5 + ChEMBL + TYR) ==="
