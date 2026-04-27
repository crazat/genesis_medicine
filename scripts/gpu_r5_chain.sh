#!/bin/bash
# Round 5 Boltz-2 cofold chain — R4 expanded top 100 × 5 selective targets
# Approx 100 mol × 5 targets × ~12s = ~100min per target = ~8.5h total

set -e
cd /home/crazat/genesis_medicine
LOG=pilot/cpu_meaningful/r5_chain.log

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }

log "=== R5 cofold chain start ==="

for tgt in tgfb1 ar ctgf sirt1 lox; do
    if [ ! -d pilot/cpu_meaningful/inputs_r5_$tgt ]; then
        log "skip $tgt (no inputs)"
        continue
    fi
    log "R5 $tgt cofold start"
    rm -rf pilot/cpu_meaningful/output_r5_$tgt
    .venv/bin/boltz predict pilot/cpu_meaningful/inputs_r5_$tgt \
        --out_dir pilot/cpu_meaningful/output_r5_$tgt \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        2>&1 | tee -a pilot/cpu_meaningful/r5_${tgt}_cofold.log
    log "R5 $tgt cofold done"
done

log "=== R5 chain done ==="

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
df.to_csv('pilot/cpu_meaningful/all_boltz2_affinity_consolidated_r5.csv', index=False)
print(f'CONSOLIDATED R5: {len(df)} cofold rows')
print(df.groupby('target').size().sort_values(ascending=False))
" 2>&1 | tee -a $LOG
