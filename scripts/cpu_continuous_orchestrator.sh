#!/usr/bin/env bash
# Continuous CPU saturator — rotates through 6 paper-tier tasks back-to-back
# until /tmp/cpu_orchestrator_run is removed. Each task is genuinely different
# from the others, NOT the same loop.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

TRIGGER=/tmp/cpu_orchestrator_run
touch $TRIGGER
LOG=pilot/cpu_orchestrator.log
mkdir -p pilot/cpu_meaningful/orchestrator

log() { echo "[$(date +%H:%M:%S)] $1" | tee -a $LOG; }

CYCLE=0
while [ -f $TRIGGER ]; do
    CYCLE=$((CYCLE + 1))
    log "=== Cycle $CYCLE ==="

    # Task A: xtb extended (top 500 BRICS by paper score) — quantum energies
    log "[A] xtb extended quantum energies (top 500)"
    python -c "
from multiprocessing import Pool
import pandas as pd, numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
RDLogger.DisableLog('rdApp.*')

def xtb_one(args):
    idx, smi = args
    try:
        from xtb.interface import Calculator, Param
        from xtb.libxtb import VERBOSITY_MUTED
        m = Chem.MolFromSmiles(smi)
        if not m: return {'idx': idx, 'error': 'parse'}
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=42) < 0:
            return {'idx': idx, 'error': 'embed'}
        try: AllChem.MMFFOptimizeMolecule(m, maxIters=500)
        except: pass
        atoms = np.array([a.GetAtomicNum() for a in m.GetAtoms()])
        c = m.GetConformer()
        xyz = np.array([[c.GetAtomPosition(i).x, c.GetAtomPosition(i).y, c.GetAtomPosition(i).z] for i in range(m.GetNumAtoms())]) * 1.8897259886
        calc = Calculator(Param.GFN2xTB, atoms, xyz)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        return {'idx': idx, 'smi': smi, 'energy_eh': float(res.get_energy()), 'n_atoms': int(m.GetNumAtoms())}
    except Exception as e:
        return {'idx': idx, 'error': str(e)[:80]}

df = pd.read_csv('pilot/cpu_queue_v5/brics_with_novelty.csv')
df = df.sort_values('combined', ascending=False).head(500).reset_index(drop=True)
print(f'xtb extended: {len(df)} mol')
args = [(f'brics{i:04d}_{df.iloc[i][\"parent\"][:8]}', df.iloc[i]['smiles']) for i in range(len(df))]
with Pool(24) as p:
    rs = p.map(xtb_one, args)
ok = [r for r in rs if 'energy_eh' in r]
pd.DataFrame(ok).to_csv(f'pilot/cpu_meaningful/orchestrator/cycle${CYCLE}_xtb500.csv', index=False)
print(f'  cycle ${CYCLE}: xtb {len(ok)}/500 success')
" >> $LOG 2>&1
    log "  task A done"
    [ ! -f $TRIGGER ] && break

    # Task B: ChemBERTa cosine similarity matrix 2336 × 2336
    log "[B] ChemBERTa similarity matrix"
    python -c "
import numpy as np
import pandas as pd

E = np.load('pilot/cpu_meaningful/chemberta_embeddings.npy')
# normalize
norms = np.linalg.norm(E, axis=1, keepdims=True)
En = E / (norms + 1e-10)
# cosine similarity
S = En @ En.T
np.save(f'pilot/cpu_meaningful/orchestrator/cycle${CYCLE}_chemberta_cosine.npy', S.astype(np.float32))
print(f'  ChemBERTa cosine matrix: {S.shape}, mean off-diag {S[~np.eye(S.shape[0], dtype=bool)].mean():.3f}')

# Top-5 nearest neighbors for top integrated 45
df_top = pd.read_csv('pilot/cpu_meaningful/integrated_top_candidates_per_target.csv')
df_admet = pd.read_csv('pilot/cpu_meaningful/admet_screen_combined.csv').dropna(subset=['smiles']).reset_index(drop=True)
smi2idx = {s: i for i, s in enumerate(df_admet['smiles'])}

rows = []
for _, r in df_top.dropna(subset=['smiles']).iterrows():
    if r['smiles'] not in smi2idx: continue
    i = smi2idx[r['smiles']]
    sims = S[i].copy()
    sims[i] = -1
    top5 = np.argsort(sims)[-5:][::-1]
    for j in top5:
        rows.append({
            'query_target': r['target'],
            'query_compound': r['compound'],
            'query_smiles': r['smiles'],
            'neighbor_smiles': df_admet.iloc[j]['smiles'],
            'neighbor_source': df_admet.iloc[j].get('source', '?'),
            'cosine': float(sims[j]),
        })
pd.DataFrame(rows).to_csv(f'pilot/cpu_meaningful/orchestrator/cycle${CYCLE}_chemberta_neighbors.csv', index=False)
print(f'  saved {len(rows)} ChemBERTa neighbor pairs')
" >> $LOG 2>&1
    log "  task B done"
    [ ! -f $TRIGGER ] && break

    # Task C: Hierarchical Murcko scaffold tree
    log "[C] Hierarchical Murcko scaffold tree"
    python -c "
from multiprocessing import Pool
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold
from collections import Counter
RDLogger.DisableLog('rdApp.*')

def murcko_chain(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if not m: return []
        chain = []
        cur = m
        for _ in range(5):
            sc = MurckoScaffold.GetScaffoldForMol(cur)
            sc_smi = Chem.MolToSmiles(sc)
            if sc_smi == Chem.MolToSmiles(cur): break
            chain.append(sc_smi)
            cur = sc
        return chain
    except: return []

df = pd.read_csv('pilot/cpu_meaningful/admet_screen_combined.csv')
smis = df['smiles'].dropna().tolist()
with Pool(24) as p:
    chains = p.map(murcko_chain, smis)
all_levels = Counter()
for c in chains:
    for s in c:
        all_levels[s] += 1
pd.DataFrame(all_levels.most_common(), columns=['scaffold', 'count']).to_csv(
    f'pilot/cpu_meaningful/orchestrator/cycle${CYCLE}_murcko_hierarchy.csv', index=False)
print(f'  hierarchical scaffolds: {len(all_levels)} unique across {len(chains)} mol')
" >> $LOG 2>&1
    log "  task C done"
    [ ! -f $TRIGGER ] && break

    # Task D: Property landscape — physchem vs paper score scatter
    log "[D] Physchem-paper-score landscape"
    python -c "
import pandas as pd
df = pd.read_csv('pilot/cpu_meaningful/full_cofold_ranking.csv')
df = df.dropna(subset=['paper_tier_score', 'logP'])
print(f'  paper_score vs logP/hERG/Skin/AMES correlations:')
for col in ['logP','hERG','AMES','Skin_Reaction']:
    if col in df.columns:
        sub = df[['paper_tier_score', col]].dropna()
        if len(sub) > 5:
            corr = sub['paper_tier_score'].corr(sub[col])
            print(f'    {col:15s}: r={corr:+.3f}, n={len(sub)}')
" >> $LOG 2>&1
    log "  task D done"
    [ ! -f $TRIGGER ] && break

    # Task E: ECFP6 (radius 3) extended fingerprint
    log "[E] ECFP6 extended fingerprint"
    python -c "
from multiprocessing import Pool
import pandas as pd, numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
RDLogger.DisableLog('rdApp.*')

def fp6(smi):
    m = Chem.MolFromSmiles(smi)
    return AllChem.GetMorganFingerprintAsBitVect(m, 3, 4096) if m else None

df = pd.read_csv('pilot/cpu_meaningful/admet_screen_combined.csv').dropna(subset=['smiles'])
with Pool(24) as p:
    fps = p.map(fp6, df['smiles'].tolist())
valid = [(i, f) for i, f in enumerate(fps) if f]
print(f'  ECFP6: {len(valid)} valid')

# Self-similarity stats: max nearest-neighbor T per molecule
def nn_one(args):
    i, fp_i, all_fps = args
    sims = DataStructs.BulkTanimotoSimilarity(fp_i, [f for k,f in all_fps if k != i])
    return max(sims) if sims else 0
args_list = [(k, f, valid[:1000]) for k,f in valid[:500]]    # subset for speed
with Pool(24) as p:
    nn = p.map(nn_one, args_list)
print(f'  ECFP6 max-NN: mean={sum(nn)/len(nn):.3f}, max={max(nn):.3f}')
" >> $LOG 2>&1
    log "  task E done"
    [ ! -f $TRIGGER ] && break

    log "=== Cycle $CYCLE complete ==="
done
log "STOPPED"
