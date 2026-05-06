#!/usr/bin/env bash
# CPU queue v4 — CONTINUOUS heavy work, 24-core saturation, runs until killed.
# Cycles through paper-tier analyses repeatedly with rolling improvements.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

OUT=pilot/cpu_queue_v4
mkdir -p $OUT

log() { echo "[$(date +%H:%M:%S)] $1"; }

# Continuous loop until killed
ITER=0
while [ -f /tmp/cpu_queue_v4_run ]; do
    ITER=$((ITER+1))
    log "=== Cycle $ITER ==="

    # Task 1: Massive BRICS expansion (different seed per iter)
    log "Cycle $ITER Task 1: BRICS expansion seed $ITER"
    python -c "
import sys; sys.path.insert(0, 'scripts')
import numpy as np
np.random.seed($ITER)
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import BRICS, Descriptors, Crippen
from multiprocessing import Pool
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

LEADS = [('EMB-3','CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O'),
         ('Embelin','CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O'),
         ('EGCG','OC1=CC(=CC(=C1O)O)C2OC3=CC(=CC(=C3CC2OC(=O)c4cc(O)c(O)c(O)c4)O)O'),
         ('Curcumin','COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O'),
         ('Glabridin','CC(C)(C=C)c1ccc(C2COc3cc(O)ccc3C2)c(O)c1O'),
         ('Asiaticoside','CC1(C)CCC2(CCC3(C)C(=CCC4C5(C)CCC(O)C(C)(C)C5CCC34C)C2C1)C(=O)OC1OC(CO)C(O)C(O)C1O')]

def expand_one(args):
    name, smi = args
    parent = Chem.MolFromSmiles(smi)
    if not parent: return name, []
    frags = list(BRICS.BRICSDecompose(parent))[:50]
    builder = BRICS.BRICSBuild([Chem.MolFromSmiles(f) for f in frags if Chem.MolFromSmiles(f)], seed=$ITER)
    out = []
    for v in builder:
        try:
            s = Chem.MolToSmiles(v)
            m = Chem.MolFromSmiles(s)
            if not m: continue
            mw = Descriptors.MolWt(m)
            if 200 <= mw <= 500:
                out.append({'parent': name, 'smiles': s, 'mw': mw,
                            'logp': Crippen.MolLogP(m),
                            'qed': __import__('rdkit.Chem.QED', fromlist=['qed']).qed(m)})
            if len(out) >= 3000: break
        except: pass
    return name, out

with Pool(6) as pool:
    results = pool.map(expand_one, LEADS)
import pandas as pd, json
all_rows = [r for n, lst in results for r in lst]
pd.DataFrame(all_rows).to_csv('pilot/cpu_queue_v4/cycle_${ITER}_brics.csv', index=False)
print(f'Cycle $ITER BRICS: {len(all_rows)} variants')
" > $OUT/cycle_${ITER}_brics.log 2>&1
    log "  BRICS done"

    # Task 2: Conformer generation 24-core for new variants
    log "Cycle $ITER Task 2: Conformer ensemble for top-200 variants"
    python -c "
import pandas as pd
from multiprocessing import Pool
from pathlib import Path
df = pd.read_csv('pilot/cpu_queue_v4/cycle_${ITER}_brics.csv').head(200)

def gen_one(smi):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import RDLogger
    RDLogger.DisableLog('rdApp.*')
    mol = Chem.MolFromSmiles(smi)
    if mol is None: return None
    mol = Chem.AddHs(mol)
    n = AllChem.EmbedMultipleConfs(mol, numConfs=20, randomSeed=$ITER)
    if n > 0: AllChem.MMFFOptimizeMoleculeConfs(mol, maxIters=500)
    return n

with Pool(24) as p:
    counts = p.map(gen_one, df['smiles'].dropna().tolist())
print(f'Cycle $ITER conformers: mean {sum(c for c in counts if c)/len(counts):.1f} per molecule')
" > $OUT/cycle_${ITER}_conformers.log 2>&1
    log "  Conformers done"

    # Task 3: Cross-Tanimoto similarity (24-core)
    log "Cycle $ITER Task 3: Cross-Tanimoto vs known"
    python -c "
import pandas as pd, numpy as np
from multiprocessing import Pool
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

new_df = pd.read_csv('pilot/cpu_queue_v4/cycle_${ITER}_brics.csv')
known_df = pd.read_csv('pilot/round5_application/full_compound_sweep.csv')

def fp(smi):
    m = Chem.MolFromSmiles(smi)
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None

with Pool(24) as p:
    known_fps = p.map(fp, known_df['smiles'].dropna().tolist())
    new_fps = p.map(fp, new_df['smiles'].dropna().tolist())
known_fps = [f for f in known_fps if f]
new_fps = [f for f in new_fps if f]

def max_sim(args):
    fp_new, ref = args
    return float(max(DataStructs.BulkTanimotoSimilarity(fp_new, ref)))

with Pool(24) as p:
    sims = p.map(max_sim, [(fp, known_fps) for fp in new_fps])
new_df_valid = new_df[new_df['smiles'].apply(lambda s: Chem.MolFromSmiles(s) is not None)].copy()
new_df_valid['max_sim_to_known'] = sims
new_df_valid.to_csv('pilot/cpu_queue_v4/cycle_${ITER}_novelty.csv', index=False)
print(f'Cycle $ITER novelty: {len(new_df_valid)} scored, novel < 0.4: {sum(s < 0.4 for s in sims)}')
" > $OUT/cycle_${ITER}_novelty.log 2>&1
    log "  Novelty done"

    log "=== Cycle $ITER complete ==="
    sleep 5
done
log "STOPPED (sentinel removed)"
