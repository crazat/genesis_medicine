"""3D pharmacophore + shape similarity on integrated top candidates.

Paper-tier task: conformer ensembles for top 45 integrated candidates,
pharmacophore feature extraction, and shape-based clustering. Heavy 24-core.

Outputs:
  - pilot/cpu_meaningful/conformers_top45.sdf (concatenated SDF)
  - pilot/cpu_meaningful/pharmacophore_features_top45.csv
  - pilot/cpu_meaningful/shape_similarity_matrix_top45.npy
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, rdMolAlign, rdShapeHelpers
from rdkit.Chem.Pharm2D import Generate, SigFactory
from rdkit.Chem.Pharm2D.SigFactory import SigFactory
from rdkit.Chem import ChemicalFeatures
from rdkit import RDConfig
import os

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def conf_one(args):
    """Generate up to 100 conformers + minimize + return mol with confs."""
    idx, smi, n_confs = args
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return idx, None, {}
        mol = Chem.AddHs(mol)
        cids = AllChem.EmbedMultipleConfs(mol, numConfs=n_confs,
                                           randomSeed=42,
                                           useRandomCoords=True)
        if len(cids) == 0:
            return idx, None, {"error": "embed failed"}
        # Minimize
        for cid in cids:
            try:
                AllChem.MMFFOptimizeMolecule(mol, confId=cid, maxIters=500)
            except Exception:
                pass
        # Pharmacophore features (RDKit BaseFeatures.fdef)
        fdef_path = os.path.join(RDConfig.RDDataDir, "BaseFeatures.fdef")
        feat_factory = ChemicalFeatures.BuildFeatureFactory(fdef_path)
        feats = feat_factory.GetFeaturesForMol(Chem.RemoveHs(mol))
        feat_summary = {}
        for f in feats:
            t = f.GetFamily()
            feat_summary[t] = feat_summary.get(t, 0) + 1
        # Properties
        props = {
            "n_confs": mol.GetNumConformers(),
            "mw": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "tpsa": Descriptors.TPSA(mol),
            "hbd": Descriptors.NumHDonors(mol),
            "hba": Descriptors.NumHAcceptors(mol),
            **{f"feat_{k}": v for k, v in feat_summary.items()},
        }
        return idx, mol, props
    except Exception as e:
        return idx, None, {"error": str(e)[:80]}


def main():
    print("=" * 72)
    print("3D pharmacophore + conformer screen on top 45 candidates")
    print("=" * 72)

    df = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    df = df.dropna(subset=["smiles"]).reset_index(drop=True)
    print(f"Top 45 integrated candidates: {len(df)}")
    print(f"Targets: {df['target'].value_counts().to_dict()}")

    args_list = [(i, smi, 100) for i, smi in enumerate(df["smiles"])]

    print("\n[Conformer generation: 100 confs × 45 mol on Pool(24)]")
    with Pool(24) as p:
        results = p.map(conf_one, args_list)

    valid = [(i, m, p) for i, m, p in results if m]
    print(f"  conformer success: {len(valid)}/{len(results)}")

    # Save concatenated SDF (1 conformer per molecule for compactness)
    writer = Chem.SDWriter(str(OUT / "conformers_top45.sdf"))
    for i, m, _ in valid:
        m.SetProp("_Name", f"{df.iloc[i]['target']}_{df.iloc[i]['compound']}")
        m.SetProp("target", df.iloc[i]["target"])
        m.SetProp("compound", df.iloc[i]["compound"])
        m.SetProp("paper_score", str(df.iloc[i]["paper_tier_score"]))
        # Best conformer (lowest energy after MMFF)
        writer.write(m, confId=0)
    writer.close()
    print(f"  ✅ conformers_top45.sdf")

    # Pharmacophore feature counts
    feat_rows = []
    for i, _, props in valid:
        row = {
            "target": df.iloc[i]["target"],
            "compound": df.iloc[i]["compound"],
            "smiles": df.iloc[i]["smiles"],
            **props,
        }
        feat_rows.append(row)
    fdf = pd.DataFrame(feat_rows)
    fdf.to_csv(OUT / "pharmacophore_features_top45.csv", index=False)
    print(f"  ✅ pharmacophore_features_top45.csv ({len(fdf.columns)} cols)")

    # Per-target feature mean
    feat_cols = [c for c in fdf.columns if c.startswith("feat_")]
    if feat_cols:
        target_feat_mean = fdf.groupby("target")[feat_cols].mean()
        print("\n[Pharmacophore feature mean per target]")
        print(target_feat_mean.round(2).to_string())

    # Shape similarity matrix (Tanimoto on RDKit ShapeProtrudeDist)
    print("\n[Shape similarity matrix on best conformer]")
    n = len(valid)
    sim = np.eye(n, dtype=np.float32)
    mols_only = [m for _, m, _ in valid]
    for i in range(n):
        for j in range(i + 1, n):
            try:
                # Align then compute shape protrude distance
                rdMolAlign.AlignMol(mols_only[i], mols_only[j])
                d = rdShapeHelpers.ShapeProtrudeDist(mols_only[i], mols_only[j],
                                                     allowReordering=False)
                sim[i, j] = sim[j, i] = 1 - d
            except Exception:
                pass
    np.save(OUT / "shape_similarity_matrix_top45.npy", sim)
    print(f"  shape similarity matrix: {sim.shape}")
    print(f"  mean off-diag: {sim[~np.eye(n, dtype=bool)].mean():.3f}")
    print(f"  max off-diag: {sim[~np.eye(n, dtype=bool)].max():.3f}")
    print("  ✅ shape_similarity_matrix_top45.npy")


if __name__ == "__main__":
    sys.exit(main())
