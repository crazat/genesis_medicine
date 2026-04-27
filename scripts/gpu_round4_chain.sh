#!/bin/bash
# Round 4 Boltz-2 cofold chain — top 30 R4 mol × MMP-1 + TGFB1 + CTGF
# ~30 mol × 3 targets × 25 sampling × 1 sample = ~1.5h

set -e
cd /home/crazat/genesis_medicine
LOG=pilot/cpu_meaningful/round4_chain.log

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }

log "=== R4 cofold chain start ==="

for tgt in mmp1 tgfb1 ctgf; do
    if [ ! -d pilot/cpu_meaningful/inputs_round4_$tgt ]; then
        log "skip $tgt (no inputs)"
        continue
    fi
    log "Round 4 $tgt cofold start"
    rm -rf pilot/cpu_meaningful/output_round4_$tgt
    .venv/bin/boltz predict pilot/cpu_meaningful/inputs_round4_$tgt \
        --out_dir pilot/cpu_meaningful/output_round4_$tgt \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        2>&1 | tee -a pilot/cpu_meaningful/round4_${tgt}_cofold.log
    log "Round 4 $tgt cofold done"
done

log "=== R4 chain done ==="

# Refresh consolidated affinity table after R4
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
df.to_csv('pilot/cpu_meaningful/all_boltz2_affinity_consolidated_r4.csv', index=False)
print(f'CONSOLIDATED R4: {len(df)} cofold rows')
print(df.groupby('target').size().sort_values(ascending=False))
" 2>&1 | tee -a $LOG
