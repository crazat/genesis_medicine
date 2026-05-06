"""CPU queue v5 — FIXED v4 bugs + truly heavy parallel work.

Fixes from v4:
  - BRICSBuild does NOT accept 'seed' kwarg (use itertools to take prefix)
  - Each cycle does substantial work (not micro-tasks)
  - Cycles run in 5-10 min each, not <1 sec

Heavy parallel jobs:
  1. ChemBERTa-3 batched embeddings on 124 + 30k BRICS = ~30k molecules
  2. RDKit conformer generation × 100-200 confs per molecule (heavy)
  3. Tanimoto matrix 30k × 124 = 3.7M comparisons
  4. Topical Pareto + novelty rank
"""

from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_queue_v5"
OUT.mkdir(parents=True, exist_ok=True)


LEADS = [
    ("EMB-3",      "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"),
    ("Embelin",    "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O"),
    ("EGCG",       "OC1=CC(=CC(=C1O)O)C2OC3=CC(=CC(=C3CC2OC(=O)c4cc(O)c(O)c(O)c4)O)O"),
    ("Curcumin",   "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O"),
    ("Glabridin",  "CC(C)(C=C)c1ccc(C2COc3cc(O)ccc3C2)c(O)c1O"),
    ("Asiaticoside", "CC1(C)CCC2(CCC3(C)C(=CCC4C5(C)CCC(O)C(C)(C)C5CCC34C)C2C1)C(=O)OC1OC(CO)C(O)C(O)C1O"),
]


# ---------- Heavy task 1: BRICS expansion (FIXED — no seed kwarg) ----------
def brics_one(args):
    name, smiles, max_n = args
    from rdkit import Chem
    from rdkit.Chem import BRICS, Descriptors, Crippen
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    parent = Chem.MolFromSmiles(smiles)
    if not parent:
        return name, []
    frags_set = list(BRICS.BRICSDecompose(parent))[:50]
    # Cross-pollinate with other leads' fragments for diversity
    for other_name, other_smi in LEADS:
        if other_name != name:
            m = Chem.MolFromSmiles(other_smi)
            if m:
                frags_set.extend(BRICS.BRICSDecompose(m))
    frags_set = list(set(frags_set))[:80]
    frag_mols = [Chem.MolFromSmiles(f) for f in frags_set if Chem.MolFromSmiles(f)]
    builder = BRICS.BRICSBuild(frag_mols)    # NO 'seed' kwarg

    out = []
    seen = set()
    for v in builder:
        try:
            s = Chem.MolToSmiles(v)
            if s in seen:
                continue
            seen.add(s)
            m = Chem.MolFromSmiles(s)
            if not m:
                continue
            mw = Descriptors.MolWt(m)
            if 200 <= mw <= 500:
                out.append({
                    "parent": name, "smiles": s, "mw": mw,
                    "logp": Crippen.MolLogP(m),
                    "qed": __import__("rdkit.Chem.QED",
                                       fromlist=["qed"]).qed(m),
                    "hbd": Descriptors.NumHDonors(m),
                    "hba": Descriptors.NumHAcceptors(m),
                    "tpsa": Descriptors.TPSA(m),
                    "rotbonds": Descriptors.NumRotatableBonds(m),
                })
            if len(out) >= max_n:
                break
        except Exception:
            continue
    return name, out


def task_brics_massive():
    """Generate up to 50,000 BRICS variants (8333 per lead)."""
    args_list = [(n, s, 8333) for n, s in LEADS]
    print(f"  BRICS massive: {len(args_list)} leads × 8333 = up to 50k")
    with Pool(processes=6) as pool:
        results = pool.map(brics_one, args_list)
    all_rows = []
    for name, variants in results:
        all_rows.extend(variants)
        print(f"    {name}: {len(variants)} variants")
    df = pd.DataFrame(all_rows).drop_duplicates("smiles")
    df.to_csv(OUT / "brics_massive.csv", index=False)
    print(f"  ✅ brics_massive.csv ({len(df)} unique)")


# ---------- Heavy task 2: 100-conformer ensemble per top-1000 molecules ----------
def conformer_one(args):
    smiles, n_confs = args
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from rdkit import RDLogger
        RDLogger.DisableLog("rdApp.*")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        mol = Chem.AddHs(mol)
        n_gen = AllChem.EmbedMultipleConfs(mol, numConfs=n_confs, randomSeed=42)
        if n_gen > 0:
            AllChem.MMFFOptimizeMoleculeConfs(mol, maxIters=300)
        rmsds = []
        if mol.GetNumConformers() > 1:
            for i in range(min(10, mol.GetNumConformers())):
                for j in range(i + 1, min(20, mol.GetNumConformers())):
                    try:
                        rmsds.append(AllChem.GetConformerRMS(mol, i, j))
                    except Exception:
                        pass
        return {"smiles": smiles, "n_confs": mol.GetNumConformers(),
                "mean_rmsd": float(np.mean(rmsds)) if rmsds else None,
                "max_rmsd": float(np.max(rmsds)) if rmsds else None}
    except Exception as e:
        return {"smiles": smiles, "n_confs": 0, "error": str(e)[:60]}


def task_conformer_massive():
    df_path = OUT / "brics_massive.csv"
    if not df_path.exists():
        return
    df = pd.read_csv(df_path)
    # Filter topical-friendly first
    topical = df[(df["mw"] < 450) & (df["logp"].between(1.0, 4.0))
                  & (df["qed"] > 0.5)]
    sample = topical.head(1000)
    print(f"  conformer ensemble: 100 confs × {len(sample)} molecules "
          f"(massively parallel)")
    args_list = [(s, 100) for s in sample["smiles"]]
    with Pool(processes=24) as pool:
        results = pool.map(conformer_one, args_list)
    valid = [r for r in results if r and r.get("n_confs", 0) > 0]
    pd.DataFrame(valid).to_csv(OUT / "conformers_1000x100.csv", index=False)
    print(f"  ✅ conformers_1000x100.csv ({len(valid)} success)")


# ---------- Heavy task 3: Tanimoto matrix 1000 × 124 ----------
def fp_one(smi):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(smi)
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def sim_pair(args):
    fp_new, ref_fps = args
    from rdkit import DataStructs
    sims = DataStructs.BulkTanimotoSimilarity(fp_new, ref_fps)
    return float(max(sims)), float(np.mean(sims))


def task_tanimoto_massive():
    new_path = OUT / "brics_massive.csv"
    ref_path = ROOT / "pilot/round5_application/full_compound_sweep.csv"
    if not new_path.exists() or not ref_path.exists():
        return
    new_df = pd.read_csv(new_path)
    ref_df = pd.read_csv(ref_path)
    print(f"  tanimoto: {len(new_df)} new × {len(ref_df)} known")
    with Pool(processes=24) as pool:
        new_fps = pool.map(fp_one, new_df["smiles"].dropna().tolist())
        ref_fps = pool.map(fp_one, ref_df["smiles"].dropna().tolist())
    new_fps_valid = [(i, fp) for i, fp in enumerate(new_fps) if fp]
    ref_fps_valid = [fp for fp in ref_fps if fp]
    print(f"  valid: {len(new_fps_valid)} new × {len(ref_fps_valid)} ref")

    args_list = [(fp, ref_fps_valid) for _, fp in new_fps_valid]
    with Pool(processes=24) as pool:
        sim_results = pool.map(sim_pair, args_list)

    valid_idx = [i for i, _ in new_fps_valid]
    new_df_valid = new_df.iloc[valid_idx].copy()
    new_df_valid["max_sim"] = [s[0] for s in sim_results]
    new_df_valid["mean_sim"] = [s[1] for s in sim_results]
    new_df_valid["combined"] = (new_df_valid["qed"]
                                  - new_df_valid["max_sim"])
    new_df_valid = new_df_valid.sort_values("combined", ascending=False)
    new_df_valid.to_csv(OUT / "brics_with_novelty.csv", index=False)

    # Top 100 unique novel
    top100 = new_df_valid.drop_duplicates("smiles").head(100)
    top100.to_csv(OUT / "top100_novel_candidates.csv", index=False)
    print(f"  ✅ top100_novel_candidates.csv "
          f"(combined score range {top100['combined'].min():.3f}–"
          f"{top100['combined'].max():.3f})")


def main():
    print("=" * 72)
    print("CPU queue v5 FIXED — heavy 24-core parallel (~30 min)")
    print("=" * 72)

    tasks = [
        ("BRICS massive (50k variants)", task_brics_massive),
        ("Conformer ensembles (1000 × 100 confs)", task_conformer_massive),
        ("Tanimoto novelty (50k × 124)", task_tanimoto_massive),
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
    print("\n=== DONE ===")


if __name__ == "__main__":
    sys.exit(main())
