#!/usr/bin/env bash
# CPU queue worker — runs while GPU ABFE is busy.
# Runs CPU/network tasks sequentially in background, logs each.
# Usage: nohup bash scripts/cpu_queue_worker.sh > /tmp/cpu_queue.log 2>&1 &

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

OUT=pilot/cpu_queue
mkdir -p $OUT

log() { echo "[$(date +%H:%M:%S)] $1"; }

# === Task 1: ChemBERTa-3 embeddings for 124 compounds ===
log "Task 1/8: ChemBERTa-3 124-compound embeddings"
python <<'PY' > $OUT/task1_chemberta_emb.log 2>&1 || log "Task 1 failed (non-fatal)"
import pandas as pd, numpy as np
from pathlib import Path
from genesis_medicine.foundation import ChemBERTa3Adapter
df = pd.read_csv('pilot/round5_application/full_compound_sweep.csv').head(50)  # batch
a = ChemBERTa3Adapter(device='cpu')
r = a.embed(df['smiles'].tolist())
if r.embeddings is not None:
    np.save('pilot/cpu_queue/chemberta_embeddings_50.npy', r.embeddings)
    print(f'OK: {r.embeddings.shape}')
else:
    print(f'unavailable: {r.note}')
PY
log "  done task 1"

# === Task 2: Open Targets multi-disease batch ===
log "Task 2/8: Open Targets disease-target batch query"
python <<'PY' > $OUT/task2_opentargets.log 2>&1 || log "Task 2 failed"
import requests, json, time
from pathlib import Path
diseases = {
    'EFO_0000270': 'systemic_sclerosis',
    'EFO_0000768': 'idiopathic_pulmonary_fibrosis',
    'EFO_0009551': 'hypertrophic_keloid_scar',
    'EFO_0009566': 'renal_interstitial_fibrosis',
    'EFO_0008502': 'hepatic_fibrosis',
    'MONDO_0019588': 'androgenetic_alopecia',
    'EFO_0003884': 'melasma',
    'MONDO_0011117': 'acne_vulgaris',
}
URL = 'https://api.platform.opentargets.org/api/v4/graphql'
Q = """query Q($id: String!) {
  disease(efoId: $id) {
    id name
    associatedTargets(page: {index:0, size:30}) {
      count rows { target { approvedSymbol id } score }
    }
  }
}"""
all_rows = []
for eid, name in diseases.items():
    try:
        r = requests.post(URL, json={'query':Q, 'variables':{'id':eid}}, timeout=20)
        d = r.json().get('data',{}).get('disease',{})
        if d:
            for row in d.get('associatedTargets',{}).get('rows',[]):
                all_rows.append({
                    'efo': eid, 'disease': name,
                    'symbol': row['target']['approvedSymbol'],
                    'ensembl': row['target']['id'],
                    'score': row['score'],
                })
        time.sleep(0.5)
    except Exception as e:
        print(f'  {name}: {e}')
import pandas as pd
pd.DataFrame(all_rows).to_csv('pilot/cpu_queue/opentargets_8diseases.csv', index=False)
print(f'OK: {len(all_rows)} target-disease pairs')
PY
log "  done task 2"

# === Task 3: AlphaFold structure → ligand binding site detection ===
log "Task 3/8: AlphaFold pocket / binding site simple detection"
python <<'PY' > $OUT/task3_pocket_detect.log 2>&1 || log "Task 3 failed"
"""Simple ligand-pocket detection: find largest concavity by surface curvature."""
from pathlib import Path
from openmm.app import PDBFile
import numpy as np

results = []
for pdb_path in sorted(Path('data/alphafold_structures').glob('*.pdb')):
    sym = pdb_path.stem.split('_')[0]
    try:
        pdb = PDBFile(str(pdb_path))
        n_atoms = pdb.topology.getNumAtoms()
        n_res = sum(1 for _ in pdb.topology.residues())
        positions = np.array([(p.x, p.y, p.z) for p in pdb.positions.value_in_unit(__import__('openmm').unit.nanometer)])
        com = positions.mean(axis=0)
        radii = np.linalg.norm(positions - com, axis=1)
        # Heuristic: deeply buried Cys atoms = catalytic / disulfide → ligand-pocket clue
        cys_indices = [a.index for a in pdb.topology.atoms()
                        if a.residue.name == 'CYS' and a.name == 'SG']
        cys_buried = sum(1 for i in cys_indices
                          if np.linalg.norm(positions[i] - com) < 0.7 * radii.max())
        results.append({
            'gene': sym, 'n_atoms': n_atoms, 'n_residues': n_res,
            'radius_nm': float(radii.max()),
            'cys_total': len(cys_indices),
            'cys_buried': cys_buried,
        })
        print(f'  {sym}: {n_res} res, {len(cys_indices)} Cys ({cys_buried} buried)')
    except Exception as e:
        print(f'  {sym}: {e}')
import pandas as pd
pd.DataFrame(results).to_csv('pilot/cpu_queue/alphafold_pocket_summary.csv', index=False)
print(f'OK: {len(results)} structures characterized')
PY
log "  done task 3"

# === Task 4: PoseBusters re-run to capture round9_application + new artifacts ===
log "Task 4/8: PoseBusters expanded re-run"
python scripts/run_posebusters_v2.py > $OUT/task4_pb_rerun.log 2>&1 || log "Task 4 failed"
log "  done task 4"

# === Task 5: Snakemake DAG render + summary ===
log "Task 5/8: Snakemake DAG visualization"
snakemake --dag 2>/dev/null | dot -Tsvg > $OUT/snakemake_dag.svg 2>$OUT/task5_snakemake.log || log "Task 5 graphviz unavailable"
snakemake --rulegraph 2>/dev/null | dot -Tsvg > $OUT/snakemake_rulegraph.svg 2>>$OUT/task5_snakemake.log || true
log "  done task 5"

# === Task 6: ChEMBL extended MMP-1 calibration set fetch (>15) ===
log "Task 6/8: ChEMBL extended MMP-1 inhibitor lookup"
python <<'PY' > $OUT/task6_chembl_extended.log 2>&1 || log "Task 6 failed"
import requests, time, json
from pathlib import Path
import pandas as pd
# UniProt P03956 = MMP-1; ChEMBL target = CHEMBL321 (interstitial collagenase)
URL = 'https://www.ebi.ac.uk/chembl/api/data/activity.json'
params = {'target_chembl_id': 'CHEMBL321',
          'standard_type': 'IC50',
          'standard_units': 'nM',
          'limit': 100}
r = requests.get(URL, params=params, timeout=30)
data = r.json()
acts = data.get('activities', [])
rows = []
for a in acts:
    val = a.get('standard_value')
    smi = a.get('canonical_smiles')
    cid = a.get('molecule_chembl_id')
    if val and smi and cid:
        try:
            ic50 = float(val)
            if ic50 > 0:
                rows.append({
                    'chembl_id': cid, 'smiles': smi,
                    'ic50_nm': ic50,
                    'pIC50': -__import__('math').log10(ic50 * 1e-9),
                    'relation': a.get('standard_relation'),
                    'doc': a.get('document_chembl_id'),
                })
        except: pass
df = pd.DataFrame(rows).drop_duplicates('chembl_id')
df.to_csv('pilot/cpu_queue/chembl_mmp1_extended.csv', index=False)
print(f'OK: {len(df)} unique MMP-1 inhibitors')
PY
log "  done task 6"

# === Task 7: GitHub Actions CI status check ===
log "Task 7/8: GitHub Actions recent runs"
gh run list -L 5 > $OUT/task7_gh_runs.log 2>&1 || log "Task 7 gh CLI unavailable"
log "  done task 7"

# === Task 8: Sphinx docs HTML build (if docs/sphinx exists) ===
log "Task 8/8: Sphinx HTML build (if applicable)"
if [ -d docs/sphinx ]; then
    cd docs/sphinx && make html > ../../$OUT/task8_sphinx.log 2>&1 && cd ../.. || log "Task 8 build failed"
else
    log "  no docs/sphinx — skipped"
fi

log "=== CPU queue ALL TASKS DONE ==="
ls -la $OUT/ | head -20
