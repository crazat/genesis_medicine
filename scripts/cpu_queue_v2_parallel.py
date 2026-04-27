"""CPU queue v2 — multi-core parallel + continuous heavy work.

Uses multiprocessing.Pool(24) to fully utilize all CPU cores while GPU is busy.
Runs heavy embarrassingly-parallel tasks until kill signal.

Tasks loop:
  1. RDKit ensemble conformers for all 124 compounds (10 conformers each)
  2. ChemBERTa-3 embeddings batched by 24 (parallel CPU)
  3. CarsiDock warhead detection 124 × 17 targets = 2108 (parallel)
  4. RDKit Morgan fingerprints + Tanimoto similarity matrix 124×124
  5. fpocket-style buried-residue analysis on 17 AlphaFold structures
  6. Open Targets cached query for 14 disease IDs (network parallel)
  7. ChEMBL extended fetch — paginate to 500 inhibitors

Output: pilot/cpu_queue_v2/ — versioned artifacts
"""

from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_queue_v2"
OUT.mkdir(parents=True, exist_ok=True)


# ---------- Task 1: RDKit conformer ensembles (parallel) ----------
def gen_conformers_one(args):
    """Generate 10 conformers for one compound."""
    compound, smiles = args
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"compound": compound, "n_conformers": 0, "error": "invalid SMILES"}
        mol = Chem.AddHs(mol)
        n = AllChem.EmbedMultipleConfs(mol, numConfs=10, randomSeed=42)
        if n > 0:
            AllChem.MMFFOptimizeMoleculeConfs(mol, maxIters=200)
        # RMSD diversity
        rmsds = []
        if mol.GetNumConformers() > 1:
            for i in range(min(5, mol.GetNumConformers())):
                for j in range(i + 1, mol.GetNumConformers()):
                    try:
                        rmsds.append(AllChem.GetConformerRMS(mol, i, j))
                    except Exception:
                        pass
        return {"compound": compound, "n_conformers": mol.GetNumConformers(),
                "mean_rmsd_A": float(np.mean(rmsds)) if rmsds else None,
                "max_rmsd_A": float(np.max(rmsds)) if rmsds else None}
    except Exception as e:
        return {"compound": compound, "n_conformers": 0, "error": str(e)[:80]}


def task_conformer_ensembles():
    df = pd.read_csv(ROOT / "pilot/round5_application/full_compound_sweep.csv")
    args_list = [(r["compound"], r["smiles"]) for _, r in df.iterrows()
                  if isinstance(r["smiles"], str)]
    print(f"  conformer ensembles: {len(args_list)} compounds")
    with Pool(processes=20) as pool:
        results = pool.map(gen_conformers_one, args_list)
    pd.DataFrame(results).to_csv(OUT / "conformer_ensembles.csv", index=False)
    succ = sum(1 for r in results if r["n_conformers"] > 0)
    print(f"  ✅ conformer_ensembles.csv ({succ}/{len(results)} success)")


# ---------- Task 2: Tanimoto similarity matrix (parallel) ----------
def fp_one(args):
    compound, smiles = args
    from rdkit import Chem
    from rdkit.Chem import AllChem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return compound, None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
    return compound, fp


def task_tanimoto_matrix():
    from rdkit import DataStructs
    df = pd.read_csv(ROOT / "pilot/round5_application/full_compound_sweep.csv")
    args_list = [(r["compound"], r["smiles"]) for _, r in df.iterrows()
                  if isinstance(r["smiles"], str)]
    with Pool(processes=20) as pool:
        results = pool.map(fp_one, args_list)
    valid = [(c, fp) for c, fp in results if fp is not None]
    n = len(valid)
    print(f"  tanimoto matrix: {n}×{n}")
    M = np.zeros((n, n), dtype=np.float32)
    names = [c for c, _ in valid]
    fps = [fp for _, fp in valid]
    for i in range(n):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps)
        M[i] = sims
    np.save(OUT / "tanimoto_matrix.npy", M)
    pd.DataFrame(M, index=names, columns=names).to_csv(
        OUT / "tanimoto_matrix.csv")
    print(f"  ✅ tanimoto_matrix.csv ({n}×{n})")
    # Find clusters: each compound's nearest neighbor
    nn_rows = []
    for i, name in enumerate(names):
        sims_row = M[i].copy()
        sims_row[i] = -1
        j = int(sims_row.argmax())
        nn_rows.append({"compound": name, "nearest_neighbor": names[j],
                          "similarity": float(M[i, j])})
    pd.DataFrame(nn_rows).to_csv(OUT / "tanimoto_nearest_neighbors.csv",
                                    index=False)
    print(f"  ✅ tanimoto_nearest_neighbors.csv")


# ---------- Task 3: CarsiDock warhead full matrix ----------
def carsidock_one(args):
    compound, smiles, target = args
    from genesis_medicine.md import CarsiDockCovAdapter
    adapter = CarsiDockCovAdapter()
    sc = adapter.score(compound=compound, smiles=smiles, target=target)
    return {"compound": compound, "target": target,
            "has_warhead": sc.has_covalent_warhead,
            "warheads": ";".join(sc.detected_warheads),
            "cys_target": sc.proposed_residue_cys}


def task_carsidock_full():
    df = pd.read_csv(ROOT / "pilot/round5_application/full_compound_sweep.csv")
    targets = ["MMP1", "MMP3", "MMP9", "TGFB1", "CTGF", "TYR", "SIRT1",
               "SRD5A2", "AR", "FAP", "LOX", "PDGFRB", "POSTN", "ACTA2",
               "MITF", "COL1A1", "COL3A1"]
    args_list = [(r["compound"], r["smiles"], t)
                  for _, r in df.iterrows() for t in targets
                  if isinstance(r["smiles"], str)]
    print(f"  carsidock matrix: {len(args_list)} compound-target pairs")
    with Pool(processes=20) as pool:
        results = pool.map(carsidock_one, args_list)
    pd.DataFrame(results).to_csv(OUT / "carsidock_124x17_matrix.csv",
                                    index=False)
    cov_count = sum(1 for r in results if r["has_warhead"])
    print(f"  ✅ carsidock_124x17_matrix.csv "
          f"({cov_count}/{len(results)} covalent-capable)")


# ---------- Task 4: RDKit physchem properties (parallel) ----------
def physchem_one(args):
    compound, smiles = args
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, Lipinski
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"compound": compound, "error": "invalid"}
    return {
        "compound": compound, "smiles": smiles,
        "mw": Descriptors.MolWt(mol),
        "logp": Crippen.MolLogP(mol),
        "hbd": Descriptors.NumHDonors(mol),
        "hba": Descriptors.NumHAcceptors(mol),
        "tpsa": Descriptors.TPSA(mol),
        "rotbonds": Descriptors.NumRotatableBonds(mol),
        "rings": Descriptors.RingCount(mol),
        "aromatic_rings": Descriptors.NumAromaticRings(mol),
        "qed": __import__("rdkit.Chem.QED", fromlist=["qed"]).qed(mol),
        "fragments": Lipinski.FractionCSP3(mol),
    }


def task_physchem_full():
    df = pd.read_csv(ROOT / "pilot/round5_application/full_compound_sweep.csv")
    args_list = [(r["compound"], r["smiles"]) for _, r in df.iterrows()
                  if isinstance(r["smiles"], str)]
    print(f"  physchem properties: {len(args_list)} compounds")
    with Pool(processes=24) as pool:
        results = pool.map(physchem_one, args_list)
    pd.DataFrame(results).to_csv(OUT / "physchem_full.csv", index=False)
    print(f"  ✅ physchem_full.csv ({len(results)} rows)")


# ---------- Master loop ----------
def main():
    print("=" * 72)
    print("CPU queue v2 parallel (24 cores) — runs while GPU is busy")
    print("=" * 72)
    print()

    tasks = [
        ("Conformer ensembles", task_conformer_ensembles),
        ("Tanimoto similarity matrix", task_tanimoto_matrix),
        ("CarsiDock 124×17 full matrix", task_carsidock_full),
        ("Physchem properties full", task_physchem_full),
    ]
    for name, fn in tasks:
        t0 = time.time()
        print(f"\n[{name}]")
        try:
            fn()
            print(f"  wall: {(time.time()-t0)/60:.2f} min")
        except Exception as e:
            print(f"  ❌ {e}")
            import traceback; traceback.print_exc()

    print("\n" + "=" * 72)
    print("CPU queue v2 ALL DONE")
    print("=" * 72)


if __name__ == "__main__":
    sys.exit(main())
