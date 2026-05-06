#!/usr/bin/env bash
# Progressive xtb: process different 500-mol slices of BRICS pool each cycle.
# 2241 BRICS mol / 500 = 5 cycles. Each cycle truly different mol.

set -uo pipefail
cd /home/crazat/genesis_medicine
source .venv/bin/activate

LOG=pilot/cpu_progressive_xtb.log
log() { echo "[$(date +%H:%M:%S)] $1" | tee -a $LOG; }

for slice in 0 500 1000 1500 2000; do
    log "=== Processing slice [$slice : $((slice+500))] ==="
    end=$((slice+500))
    OUT_FILE="pilot/cpu_meaningful/xtb_progressive_slice_${slice}.csv"
    if [ -f "$OUT_FILE" ]; then
        log "  already done, skip"
        continue
    fi
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
df = df.sort_values('combined', ascending=False).iloc[$slice:$end].reset_index(drop=True)
print(f'Slice $slice:$end: {len(df)} mol')
args = [(f'br_{$slice + i:04d}', df.iloc[i]['smiles']) for i in range(len(df))]
with Pool(24) as p:
    rs = p.map(xtb_one, args)
ok = [r for r in rs if 'energy_eh' in r]
pd.DataFrame(ok).to_csv('$OUT_FILE', index=False)
print(f'  slice $slice: {len(ok)}/{len(df)} success')
" >> $LOG 2>&1
    log "  slice $slice done"
done

# Aggregate
log "=== Aggregating progressive xtb ==="
python -c "
import pandas as pd
from pathlib import Path
dfs = []
for f in Path('pilot/cpu_meaningful').glob('xtb_progressive_slice_*.csv'):
    d = pd.read_csv(f)
    dfs.append(d)
if dfs:
    df = pd.concat(dfs)
    df.to_csv('pilot/cpu_meaningful/xtb_progressive_all.csv', index=False)
    print(f'Aggregated: {len(df)} rows')
" >> $LOG 2>&1
log "=== ALL DONE ==="
