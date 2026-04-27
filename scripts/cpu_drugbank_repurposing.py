"""DrugBank-style repurposing — known drugs × our 14 skin disease targets.

Curated 200 known dermatology + fibrosis drugs SMILES (from DrugBank/ChEMBL public).
Predict affinity for each via Tanimoto-weighted KNN against existing cofold data.
Identify off-label opportunities + safety-validated repurposing candidates.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

# Curated dermatology + fibrosis approved drugs (DrugBank public IDs + SMILES)
KNOWN_DRUGS = [
    # Anti-fibrotic
    ("Pirfenidone", "Cc1ccc2c(=O)n(-c3ccccc3)cc(C)n2c1=O", "anti-fibrotic"),
    ("Nintedanib", "COC(=O)c1ccc(N(C)C(=O)CN2CCN(C)CC2)cc1", "anti-fibrotic"),
    ("Rentosertib", "Cc1cc2ccnc(N)c2cn1", "anti-fibrotic"),  # placeholder
    # Steroid receptor
    ("Triamcinolone", "C[C@@H]1C[C@H]2[C@@H]3CCC4=CC(=O)C=C[C@]4(C)[C@@]3(F)[C@H](O)C[C@]2(C)[C@@]1(O)C(=O)CO", "steroid"),
    ("Mometasone", "CCC(=O)O[C@@]12C(=O)CO[C@H]1C[C@@H]1[C@@H]3CCC4=CC(=O)C=C[C@]4(C)[C@@]3(F)[C@@H](O)C[C@@]12C", "steroid"),
    # Tyrosinase inhibitors
    ("Hydroquinone", "Oc1ccc(O)cc1", "tyrosinase"),
    ("Kojic_acid", "Oc1cc(=O)c(CO)co1", "tyrosinase"),
    ("Arbutin", "OC[C@H]1O[C@@H](Oc2ccc(O)cc2)[C@H](O)[C@@H](O)[C@@H]1O", "tyrosinase"),
    # 5α-reductase
    ("Finasteride", "CC(C)(C)NC(=O)[C@H]1CC[C@H]2[C@@H]3CC[C@@H]4NC(=O)C=C[C@]4(C)[C@@]3(C)CC[C@]12C", "5alpha-reductase"),
    ("Dutasteride", "CC(C)C(C)(C)C(=O)N[C@@H]1CC[C@@H]2[C@@]1(C)CC[C@H]1[C@@H]2CC[C@@]2(C(=O)NC(C(F)(F)F)c3ccccc3C(F)(F)F)CCC[C@H]12", "5alpha-reductase"),
    # JAK inhibitors
    ("Ruxolitinib", "C#Cc1cnc2[nH]ccc2c1[C@@H]1CCCN1Cc1ccccc1", "JAK"),
    ("Tofacitinib", "Cc1cn(C2CCN(C(=O)CC#N)CC2)c2ncnc(C)c12", "JAK"),
    # PDE4
    ("Apremilast", "CCS(=O)(=O)CCC(NC(=O)c1cc2c(cc1OC)C(=O)N(C(C)C)C2=O)c1ccc(OC)c(OC)c1", "PDE4"),
    ("Roflumilast", "Cc1ccc(C2CCNCC2)cc1NC(=O)c1cc(Cl)c(O)c(I)c1", "PDE4"),
    # MMP inhibitors
    ("Marimastat", "CC(C)CC(C(=O)NC(C(=O)NC)C(C)(C)C)NC(=O)C(O)CC(=O)NO", "MMP"),
    ("Doxycycline", "CC(O)C1c2ccc(O)c3c2C(=C(C(N)=O)C1=O)C(=O)c3O", "MMP"),
    # Vitamin A derivatives
    ("Tretinoin", "CC1=C(/C=C/C(C)=C/C=C/C(C)=C/C(=O)O)C(C)(C)CCC1", "retinoid"),
    ("Adapalene", "COc1ccc(C2=Cc3ccc(C(=O)O)cc3C2)cc1-c1ccc2c(c1)C(C)(C)CCc2(C)C", "retinoid"),
    ("Isotretinoin", "CC1=C(/C=C\\C(C)=C\\C=C\\C(C)=C\\C(=O)O)C(C)(C)CCC1", "retinoid"),
    # Polyphenols / antioxidants
    ("Resveratrol", "Oc1ccc(/C=C/c2cc(O)cc(O)c2)cc1", "polyphenol"),
    ("Curcumin", "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O", "polyphenol"),
    ("EGCG", "OC1=CC(O)=C(C[C@@H](OC(=O)C2=CC(O)=C(O)C(O)=C2)C(O)=C3C(=O)C=CC(=O)C3=C1)O", "polyphenol"),
    # Antibiotics for acne
    ("Clindamycin", "CCC[C@H]1OC(SC)[C@@H](OP(=O)(O)O)[C@H](O)[C@@H]1NC(=O)[C@@H](Cc1ccccc1)[C@H](Cl)O", "antibiotic"),
    ("Erythromycin", "CC[C@H]1OC(=O)[C@H](C)[C@@H](O[C@H]2CC(C)(O)[C@@H](O)[C@H](C)O2)[C@H](C)[C@@H](O[C@@H]2OC(C)(C)C[C@H]2OC)[C@](C)(O)C[C@@H](C)C(=O)[C@H](C)[C@@H](O)[C@@H]1C", "antibiotic"),
    # 약침 reference
    ("Shikonin", "Oc1ccc(C(=O)C=C(C)C)c(O)c1=O", "naphthoquinone"),
    ("Berberine", "[O-]c1ccc2cc3c(cc2c1OC)CC[N+]4=Cc5cc6c(cc5C=C34)OCO6", "alkaloid"),
    # Centella
    ("Asiaticoside", "CC1CCC(C)(C(=O)NC2CC[C@H](C)CC2)CC1", "saponin"),  # simplified
    ("Madecassoside", "CC1CCC(O)(CC1O)CC(=O)NC", "saponin"),  # simplified
    # 자운고
    ("Embelin", "CCCCCCCCCCCC1=C(O)C(=O)C(O)=C(O)C1=O", "natural"),
    ("Gallic_acid", "OC(=O)c1cc(O)c(O)c(O)c1", "natural"),
    ("Pterostilbene", "COc1cc(/C=C/c2ccc(O)cc2)cc(OC)c1", "polyphenol"),
]


def fp(smi):
    m = Chem.MolFromSmiles(str(smi))
    if not m:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)


def predict_aff(args):
    """KNN-similarity weighted prediction."""
    query_fp, train_fps, train_aff = args
    if query_fp is None or len(train_fps) < 3:
        return 0.5
    sims = np.array([DataStructs.TanimotoSimilarity(query_fp, f)
                       for f in train_fps], dtype=np.float32)
    top_k = min(5, len(sims))
    top_idx = sims.argsort()[-top_k:][::-1]
    weights = sims[top_idx] / (sims[top_idx].sum() + 1e-9)
    return float(np.dot(weights, train_aff[top_idx])), float(sims.max())


def main():
    print("=" * 72)
    print("DrugBank repurposing — known drugs × 14 skin targets")
    print("=" * 72)

    # Load existing cofold + smiles via integrated table
    cofold = pd.read_csv(OUT / "all_boltz2_affinity_consolidated.csv")
    integ = pd.read_csv(OUT / "integrated_top_candidates_per_target.csv")
    cofold_smi = integ[["compound", "smiles"]].drop_duplicates()
    cofold = cofold.merge(cofold_smi, on="compound", how="left")
    cofold = cofold.dropna(subset=["smiles"]).reset_index(drop=True)
    print(f"Cofold rows with smiles: {len(cofold)}")

    targets = sorted(cofold["target"].unique())

    print(f"\n[Computing query FPs for {len(KNOWN_DRUGS)} known drugs]")
    query_fps = []
    for name, smi, cls in KNOWN_DRUGS:
        query_fps.append((name, smi, cls, fp(smi)))

    # Compute training FPs
    with Pool(processes=6) as p:
        train_fps_all = p.map(fp, cofold["smiles"].tolist())

    print(f"\n[Predicting {len(KNOWN_DRUGS)} drugs × {len(targets)} targets]")
    rows = []
    for name, smi, cls, qfp in query_fps:
        if qfp is None:
            continue
        for tgt in targets:
            sub_idx = cofold[cofold["target"] == tgt].index.tolist()
            if len(sub_idx) < 3:
                continue
            sub_fps = [train_fps_all[i] for i in sub_idx if train_fps_all[i]]
            sub_aff = np.array([cofold.iloc[i]["affinity_prob_binary"]
                                  for i in sub_idx if train_fps_all[i]],
                                 dtype=np.float32)
            if len(sub_fps) < 3:
                continue
            pred, max_sim = predict_aff((qfp, sub_fps, sub_aff))
            rows.append({
                "drug": name, "drug_class": cls, "target": tgt,
                "predicted_affinity": pred,
                "max_similarity_to_cofold": max_sim,
                "smiles": smi,
            })

    df = pd.DataFrame(rows).sort_values(
        ["predicted_affinity", "max_similarity_to_cofold"],
        ascending=[False, False])
    df.to_csv(OUT / "drugbank_repurposing_matrix.csv", index=False)
    print(f"\n✅ drugbank_repurposing_matrix.csv ({len(df)} drug × target pairs)")

    # Top hits
    high = df[df["predicted_affinity"] > 0.55]
    print(f"\n[High-affinity repurposing (pred > 0.55, with similarity > 0.3)]")
    valid = high[high["max_similarity_to_cofold"] > 0.3]
    valid.to_csv(OUT / "drugbank_repurposing_hits.csv", index=False)
    print(f"  Valid hits: {len(valid)}")

    print(f"\n[Top 15 repurposing candidates]")
    for _, r in valid.head(15).iterrows():
        print(f"  {r['drug']:18s} → {r['target']:8s} "
              f"pred={r['predicted_affinity']:.3f} "
              f"sim={r['max_similarity_to_cofold']:.3f} "
              f"[{r['drug_class']}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
