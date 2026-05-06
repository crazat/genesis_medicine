#!/usr/bin/env bash
# CPU meaningful queue — sequential paper-tier tasks while GPU runs Boltz-2 batches.
# Each task produces unique value, NOT repetitive cycles.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

OUT=pilot/cpu_meaningful
mkdir -p $OUT

log() { echo "[$(date +%H:%M:%S)] $1"; }

# Task 1: Extract Boltz-2 affinity from completed batches as they appear
log "Task 1: Extract Boltz-2 batch affinity results (rolling)"
python <<'PY' > $OUT/task1_extract.log 2>&1 || log "Task 1 failed"
"""Watch GPU queue output dirs + extract affinity_pred + prob_binary for each
completed cofold. Aggregates into single CSV ready for preprint integration."""
import json
from pathlib import Path
import pandas as pd
import time

results = []
for target_dir_pattern in ['mmp1', 'tgfb1', 'top100', 'ctgf', 'sirt1', 'lox', 'ar', 'mitf']:
    for output_dir in Path('pilot').rglob(f'boltz_results_*'):
        # find affinity .json
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
print(f'✅ {len(df)} unique cofold affinity rows extracted')
print(df.groupby('target').size().sort_values(ascending=False))
PY
log "  done task 1"

# Task 2: ChEMBL extended 89 inhibitors → MMP-1 calibration extension yamls
log "Task 2: ChEMBL extended cofold input prep"
python <<'PY' > $OUT/task2_chembl_yamls.log 2>&1 || log "Task 2 failed"
import pandas as pd, yaml
from pathlib import Path
df = pd.read_csv('pilot/cpu_queue/chembl_mmp1_extended.csv')
print(f'ChEMBL extended: {len(df)} inhibitors')
mmp1_seq = 'LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG'
out = Path('pilot/cpu_meaningful/chembl_extended_inputs')
out.mkdir(parents=True, exist_ok=True)
n = 0
for i, r in df.iterrows():
    smi = r.get('smiles', '')
    cid = r.get('chembl_id', '')
    if isinstance(smi, str) and smi and isinstance(cid, str) and cid:
        yaml_data = {
            'version': 1,
            'sequences': [
                {'protein': {'id':'A', 'sequence': mmp1_seq, 'msa': '/home/crazat/genesis_medicine/data/msa/mmp1.a3m'}},
                {'ligand': {'id':'B', 'smiles': smi}},
            ],
            'properties': [{'affinity': {'binder': 'B'}}],
        }
        (out / f'mmp1__{cid}.yaml').write_text(yaml.safe_dump(yaml_data, sort_keys=False))
        n += 1
print(f'✅ {n} yamls written for ChEMBL extended × MMP-1')
PY
log "  done task 2"

# Task 3: PDF rebuild for all 12 preprints (parallel via xargs)
log "Task 3: PDF rebuild all 12 preprints (parallel)"
ls preprints/ | head -12 | xargs -I{} -P 6 bash -c '
    cd preprints/{} 2>/dev/null
    if [ -f manuscript.md ]; then
        pandoc manuscript.md -o manuscript.html --embed-resources --standalone 2>/dev/null
        google-chrome --headless --disable-gpu --no-sandbox --print-to-pdf=manuscript.pdf --print-to-pdf-no-header "file://$(pwd)/manuscript.html" 2>/dev/null
        echo "  {} : $(stat -c%s manuscript.pdf 2>/dev/null) B"
    fi
' > $OUT/task3_pdf_rebuild.log 2>&1
log "  done task 3"

# Task 4: BRICS variant scaffold filtering — top 100 unique by topical-score across parents
log "Task 4: Cross-parent best variants"
python <<'PY' > $OUT/task4_cross_parent.log 2>&1 || log "Task 4 failed"
import pandas as pd
from pathlib import Path
df = pd.read_csv('pilot/cpu_queue_v5/brics_with_novelty.csv')
# diverse top: 1 per parent per scaffold class
df['scaffold_size'] = df['mw'].round(-1).astype(int)
diverse = df.sort_values('combined', ascending=False).drop_duplicates(['parent','scaffold_size']).head(100)
diverse.to_csv('pilot/cpu_meaningful/cross_parent_diverse_100.csv', index=False)
print(f'✅ {len(diverse)} cross-parent diverse, parents: {diverse["parent"].value_counts().to_dict()}')
PY
log "  done task 4"

log "=== CPU meaningful queue ALL DONE ==="
ls -la $OUT/ 2>&1 | head -10
