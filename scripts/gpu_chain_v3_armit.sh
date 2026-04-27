#!/bin/bash
# Chain v3 — AR + MITF rerun with --diffusion_samples_affinity 1
# (large protein speedup: 5h → ~1h per cofold)
#
# Wait for current GPU process (PID 329057, jun cofold) to complete.
# Then run AR with samples 1, then MITF with samples 1.

set -e
cd /home/crazat/genesis_medicine
LOG=pilot/cpu_meaningful/chain_v3_armit.log

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }

log "=== chain v3 AR/MITF rerun start ==="

# Wait for current GPU process (PID 329057 jun + PID 321745 chain v2 master)
PID_JUN=329057
while kill -0 $PID_JUN 2>/dev/null; do
    sleep 60
done
log "JUN cofold done"

# Wait for chain v2 to finish DCT and ChEMBL too
PID_CHAIN=321745
while kill -0 $PID_CHAIN 2>/dev/null; do
    sleep 60
done
log "Chain v2 (DCT/ChEMBL) done"

# AR rerun with samples 1
if [ -d pilot/cpu_meaningful/inputs_ar ]; then
    log "Starting AR cofold (--diffusion_samples_affinity 1)"
    rm -rf pilot/cpu_meaningful/output_ar_v3
    .venv/bin/boltz predict pilot/cpu_meaningful/inputs_ar \
        --out_dir pilot/cpu_meaningful/output_ar_v3 \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        2>&1 | tee -a pilot/cpu_meaningful/ar_v3_cofold.log
    log "AR v3 done"
fi

# MITF rerun
if [ -d pilot/cpu_meaningful/inputs_mitf ]; then
    log "Starting MITF cofold (--diffusion_samples_affinity 1)"
    rm -rf pilot/cpu_meaningful/output_mitf_v3
    .venv/bin/boltz predict pilot/cpu_meaningful/inputs_mitf \
        --out_dir pilot/cpu_meaningful/output_mitf_v3 \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        2>&1 | tee -a pilot/cpu_meaningful/mitf_v3_cofold.log
    log "MITF v3 done"
fi

# Refresh consolidated affinity table
.venv/bin/python -c "
from pathlib import Path
import json, pandas as pd
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
df.to_csv('pilot/cpu_meaningful/all_boltz2_affinity_consolidated_v3.csv', index=False)
print(f'consolidated v3: {len(df)} cofold rows')
print(df.groupby('target').size())
" 2>&1 | tee -a $LOG

log "=== chain v3 done ==="
