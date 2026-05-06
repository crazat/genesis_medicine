#!/usr/bin/env bash
# CPU queue v6 — CONTINUOUS truly heavy work, runs until killed.
# v5 fixed bug. v6 makes each cycle substantial (10-15 min) for proper saturation.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

OUT=pilot/cpu_queue_v6
mkdir -p $OUT

log() { echo "[$(date +%H:%M:%S)] $1"; }

ITER=0
while [ -f /tmp/cpu_queue_v6_run ]; do
    ITER=$((ITER+1))
    log "=== Cycle $ITER ==="

    # Heavy task: Conformer ensembles for top-200 v5 candidates × 200 confs each
    log "Cycle $ITER: 200-conformer ensemble for 200 candidates"
    python -c "
from multiprocessing import Pool
import pandas as pd
import numpy as np
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

df = pd.read_csv('pilot/cpu_queue_v5/top100_novel_candidates.csv').head(200)

def gen_one(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None: return None
        m = Chem.AddHs(m)
        n = AllChem.EmbedMultipleConfs(m, numConfs=200, randomSeed=42, useRandomCoords=True)
        if n > 0:
            AllChem.MMFFOptimizeMoleculeConfs(m, maxIters=500)
        return {'smiles': smi, 'n_confs': m.GetNumConformers()}
    except Exception as e:
        return {'smiles': smi, 'n_confs': 0, 'error': str(e)[:60]}

with Pool(24) as p:
    results = p.map(gen_one, df['smiles'].dropna().tolist())
out = pd.DataFrame([r for r in results if r])
out.to_csv('pilot/cpu_queue_v6/cycle_${ITER}_conformers.csv', index=False)
print(f'Cycle $ITER: {(out[\"n_confs\"] > 0).sum()} success, mean confs {out[\"n_confs\"].mean():.1f}')
" > $OUT/cycle_${ITER}_conformers.log 2>&1
    log "  conformers done"

    # Heavy task 2: ECFP fingerprint pairwise novelty matrix on 2241 BRICS variants
    log "Cycle $ITER: Pairwise ECFP novelty matrix"
    python -c "
import pandas as pd, numpy as np
from multiprocessing import Pool
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

df = pd.read_csv('pilot/cpu_queue_v5/brics_massive.csv').head(500)

def fp_one(smi):
    m = Chem.MolFromSmiles(smi)
    return AllChem.GetMorganFingerprintAsBitVect(m, 3, 4096) if m else None

with Pool(24) as p:
    fps = p.map(fp_one, df['smiles'].tolist())
fps_valid = [(i, f) for i, f in enumerate(fps) if f]
print(f'Valid fps: {len(fps_valid)}')

# Pairwise tanimoto: compute upper triangle in parallel
def row_sim(args):
    i, fp_i, all_fps = args
    return DataStructs.BulkTanimotoSimilarity(fp_i, all_fps)

args_list = [(i, fp, [f for _, f in fps_valid]) for i, (i_orig, fp) in enumerate(fps_valid)]
with Pool(24) as p:
    rows = p.map(row_sim, args_list)
M = np.array(rows, dtype=np.float32)
np.save('pilot/cpu_queue_v6/cycle_${ITER}_pairwise_sim.npy', M)
# Diversity: mean off-diagonal similarity
mask = ~np.eye(M.shape[0], dtype=bool)
print(f'Cycle $ITER pairwise: {M.shape}, mean off-diag {M[mask].mean():.3f}, max {M[mask].max():.3f}')
" > $OUT/cycle_${ITER}_pairwise.log 2>&1
    log "  pairwise done"

    log "=== Cycle $ITER complete ==="
    sleep 5
done
log "STOPPED"
