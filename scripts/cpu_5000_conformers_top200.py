"""5000-conformer ensemble on top 200 BRICS (NOT top 45). Heavy 30+ min."""
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
        if m is None:
            return None
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=5000, randomSeed=42,
                                            useRandomCoords=True, numThreads=1,
                                            pruneRmsThresh=0.5)
        if not cids:
            return {"idx": idx, "n_confs": 0}
        # MMFF94s minimize
        results = AllChem.MMFFOptimizeMoleculeConfs(m, mmffVariant="MMFF94s",
                                                     maxIters=1000, numThreads=1)
        energies = sorted([r[1] for r in results if r[0] == 0])
        if len(energies) < 2:
            return {"idx": idx, "n_confs": len(energies)}
        kt = 0.5959
        rel = np.array(energies) - min(energies)
        weights = np.exp(-rel / kt)
        weights /= weights.sum()
        eff = (weights ** 2).sum() ** -1
        return {
            "idx": idx,
            "smi": smi,
            "n_confs": len(energies),
            "min_E": float(min(energies)),
            "median_E": float(np.median(energies)),
            "energy_range": float(max(energies) - min(energies)),
            "n_within_2kcal": int((rel < 2).sum()),
            "n_within_5kcal": int((rel < 5).sum()),
            "boltzmann_eff_confs": float(eff),
        }
    except Exception as e:
        return {"idx": idx, "error": str(e)[:100]}


def main():
    df = pd.read_csv(ROOT / "pilot/cpu_queue_v5/brics_with_novelty.csv")
    df = df.sort_values("combined", ascending=False).head(200).reset_index(drop=True)
    print(f"Conformer ensemble: 5000 confs × {len(df)} mol (top 200 BRICS)")
    args = [(i, df.iloc[i]["smiles"]) for i in range(len(df))]
    t0 = time.time()
    with Pool(14) as p:
        results = p.map(gen5000, args)
    print(f"Wall: {(time.time()-t0)/60:.1f} min")
    valid = [r for r in results if r and "boltzmann_eff_confs" in r]
    pd.DataFrame(valid).to_csv(OUT / "conformers_5000x200.csv", index=False)
    print(f"✅ conformers_5000x200.csv ({len(valid)} success)")
    if valid:
        rng = [r["energy_range"] for r in valid]
        eff = [r["boltzmann_eff_confs"] for r in valid]
        print(f"  Energy range: {min(rng):.1f}-{max(rng):.1f} mean {np.mean(rng):.1f}")
        print(f"  Boltzmann eff confs: {min(eff):.1f}-{max(eff):.1f} mean {np.mean(eff):.1f}")


if __name__ == "__main__":
    sys.exit(main())
