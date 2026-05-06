"""Heavy CPU 24-core: 1000 conformers × 200 mol with MMFF94s + RMSD pairwise.
Genuine paper-tier conformer ensemble study.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def conf_one(args):
    idx, smi, n_confs = args
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return None
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=n_confs,
                                            randomSeed=42,
                                            useRandomCoords=True,
                                            numThreads=1)
        if len(cids) == 0:
            return {"idx": idx, "smi": smi, "n_confs": 0, "error": "embed"}
        # MMFF94s minimize all conformers
        try:
            results = AllChem.MMFFOptimizeMoleculeConfs(m, mmffVariant="MMFF94s",
                                                         maxIters=500,
                                                         numThreads=1)
            energies = [r[1] for r in results if r[0] == 0]
        except Exception:
            energies = []

        # Pairwise RMSD on minimized (sample 30 to keep tractable)
        n = m.GetNumConformers()
        if n >= 2 and energies:
            sampled = list(range(min(n, 30)))
            rmsds = []
            for i in sampled:
                for j in sampled[i+1:]:
                    try:
                        rms = AllChem.GetConformerRMS(m, i, j)
                        rmsds.append(rms)
                    except Exception:
                        pass
        else:
            rmsds = []

        return {
            "idx": idx,
            "smi": smi,
            "n_confs": n,
            "n_minimized": len(energies),
            "min_energy": float(min(energies)) if energies else None,
            "max_energy": float(max(energies)) if energies else None,
            "energy_range": float(max(energies) - min(energies)) if energies else None,
            "mean_rmsd": float(np.mean(rmsds)) if rmsds else None,
            "max_rmsd": float(np.max(rmsds)) if rmsds else None,
            "rmsd_diversity": float(np.std(rmsds)) if rmsds else None,
        }
    except Exception as e:
        return {"idx": idx, "smi": smi, "n_confs": 0, "error": str(e)[:120]}


def main():
    print("=" * 72)
    print("Heavy conformer ensemble — 1000 confs × 200 mol with MMFF94s")
    print("=" * 72)

    df = pd.read_csv(ROOT / "pilot/cpu_queue_v5/brics_with_novelty.csv")
    # Top-200 by combined (qed - max_sim) score
    df = df.sort_values("combined", ascending=False).head(200).reset_index(drop=True)
    print(f"Mol for conformer ensemble: {len(df)}")

    args_list = [(i, df.iloc[i]["smiles"], 1000) for i in range(len(df))]

    import time
    t0 = time.time()
    with Pool(processes=24) as pool:
        results = pool.map(conf_one, args_list)
    print(f"\nWall time: {(time.time() - t0) / 60:.1f} min")

    res_df = pd.DataFrame([r for r in results if r])
    res_df.to_csv(OUT / "heavy_conformer_ensemble.csv", index=False)
    print(f"\n✅ heavy_conformer_ensemble.csv ({len(res_df)} rows)")
    if "n_confs" in res_df.columns:
        success = (res_df["n_confs"] > 0).sum()
        print(f"  Successful: {success}/{len(res_df)}")
        if "energy_range" in res_df.columns:
            er = res_df["energy_range"].dropna()
            print(f"  Energy range: {er.min():.1f}-{er.max():.1f} kcal/mol, mean {er.mean():.1f}")
        if "max_rmsd" in res_df.columns:
            rm = res_df["max_rmsd"].dropna()
            print(f"  Max RMSD: {rm.min():.2f}-{rm.max():.2f} Å, mean {rm.mean():.2f}")


if __name__ == "__main__":
    sys.exit(main())
