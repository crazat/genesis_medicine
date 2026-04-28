"""5000-conformer ensemble on R8 top 30 — heavy CPU."""
from __future__ import annotations
import sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def gen5000(args):
    idx, smi = args
    try:
        m = Chem.MolFromSmiles(smi)
        if not m: return None
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=5000, randomSeed=42,
                                            useRandomCoords=True, numThreads=1,
                                            pruneRmsThresh=0.5)
        if not cids: return {"idx": idx, "n_confs": 0}
        results = AllChem.MMFFOptimizeMoleculeConfs(m, mmffVariant="MMFF94s",
                                                     maxIters=1000, numThreads=1)
        energies = sorted([r[1] for r in results if r[0] == 0])
        if len(energies) < 2: return {"idx": idx, "n_confs": len(energies)}
        kt = 0.5959
        rel = np.array(energies) - min(energies)
        weights = np.exp(-rel / kt); weights /= weights.sum()
        eff = (weights ** 2).sum() ** -1
        return {"idx": idx, "smi": smi, "n_confs": len(energies),
                "min_E": float(min(energies)),
                "energy_range": float(max(energies) - min(energies)),
                "boltzmann_eff_confs": float(eff),
                "n_within_2kcal": int((rel < 2).sum())}
    except Exception as e:
        return {"idx": idx, "error": str(e)[:100]}


def main():
    df = pd.read_csv(OUT / "bayesian_v4_round8_candidates.csv").head(30)
    print(f"5000 confs × R8 top {len(df)}")
    args = [(i, df.iloc[i]["smiles"]) for i in range(len(df))]
    t0 = time.time()
    with Pool(16) as p:
        results = p.map(gen5000, args)
    print(f"Wall: {(time.time()-t0)/60:.1f} min")
    valid = [r for r in results if r and "boltzmann_eff_confs" in r]
    pd.DataFrame(valid).to_csv(OUT / "conformers_5000_r8_top30.csv", index=False)
    print(f"✅ conformers_5000_r8_top30.csv ({len(valid)})")


if __name__ == "__main__":
    sys.exit(main())
