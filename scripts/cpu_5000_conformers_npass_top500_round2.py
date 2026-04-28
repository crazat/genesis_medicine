"""5000-conformer ensemble × NPASS rank 500-1000 by permeability — extended saturation."""
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
        cids = AllChem.EmbedMultipleConfs(m, numConfs=2000, randomSeed=42,
                                            useRandomCoords=True, numThreads=1,
                                            pruneRmsThresh=0.5)
        if not cids: return {"idx": idx, "n_confs": 0}
        results = AllChem.MMFFOptimizeMoleculeConfs(m, mmffVariant="MMFF94s",
                                                     maxIters=500, numThreads=1)
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
    npass = pd.read_csv(OUT / "npass_2026_pottsguy_logkp_10k.csv")
    # Skip top-500 (already done) → next 500
    sorted_df = npass.sort_values("log_kp_pottsguy", ascending=False).reset_index(drop=True)
    target = sorted_df.iloc[500:1000]
    print(f"NPASS rank 500-1000: {target['log_kp_pottsguy'].min():.2f} to {target['log_kp_pottsguy'].max():.2f}")

    args = [(i + 500, target.iloc[i]["smiles"]) for i in range(len(target))]
    t0 = time.time()
    with Pool(16) as p:
        results = p.map(gen5000, args)
    print(f"Wall: {(time.time()-t0)/60:.1f} min")
    valid = [r for r in results if r and "boltzmann_eff_confs" in r]
    pd.DataFrame(valid).to_csv(OUT / "conformers_2000_npass_rank500_1000.csv", index=False)
    print(f"✅ conformers_2000_npass_rank500_1000.csv ({len(valid)})")


if __name__ == "__main__":
    sys.exit(main())
