"""R15 BRICS bioisostere expansion — 5 universal scaffold leaders × deep BRICS recombination.

Each leader generates 200 derivatives = 1000 R15 candidates total.
Filter: MW 200-500, logP 1-5, Lipinski 0 violations, no PAINS, skin window.

Output: pilot/cpu_meaningful/r15_brics_candidates.csv
"""
from __future__ import annotations

import sys
from itertools import islice
from multiprocessing import Pool
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, BRICS, Descriptors, Lipinski, QED
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
OUT.mkdir(parents=True, exist_ok=True)

LEADERS = [
    ("R12_4",  "OCC1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R12_11", "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1"),
    ("R12_23", "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1"),
    ("R14_5",  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O"),
    ("R13_13", "CC(C)=CCc1cc(O)c(O)c(O)c1C=CC1COc2cc(O)ccc2C1"),
]

N_PER_LEADER = 200
MAX_BUILD = 800  # generate more, filter aggressively


def expand_one(args):
    name, smi = args
    seed = Chem.MolFromSmiles(smi)
    if not seed:
        return []
    fragments = list(BRICS.BRICSDecompose(seed))
    fragments = [f for f in fragments if Chem.MolFromSmiles(f)]
    if len(fragments) < 2:
        return []

    # PAINS catalog
    pains_params = FilterCatalogParams()
    pains_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    pains_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
    pains_cat = FilterCatalog(pains_params)

    builder = BRICS.BRICSBuild(
        [Chem.MolFromSmiles(f) for f in fragments])

    keep = []
    seen = set()
    try:
        for i, mol in enumerate(islice(builder, MAX_BUILD)):
            try:
                Chem.SanitizeMol(mol)
                derivative = Chem.MolToSmiles(mol)
                if not derivative or derivative in seen or len(derivative) > 200:
                    continue
                seen.add(derivative)

                m = Chem.MolFromSmiles(derivative)
                mw = Descriptors.MolWt(m)
                logp = Descriptors.MolLogP(m)
                hbd = Lipinski.NumHDonors(m)
                hba = Lipinski.NumHAcceptors(m)
                tpsa = Descriptors.TPSA(m)
                rotb = Lipinski.NumRotatableBonds(m)
                qed = QED.qed(m)
                lip_viol = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
                if mw < 200 or mw > 500 or logp < 1.0 or logp > 5.0 or lip_viol > 0:
                    continue
                if pains_cat.HasMatch(m):
                    continue
                # Skin window soft filter
                skin_ok = (1.5 <= logp <= 3.5) and (mw <= 500)
                keep.append({
                    "leader_seed": name, "derivative_smiles": derivative,
                    "MW": round(mw, 1), "logP": round(logp, 2),
                    "HBD": hbd, "HBA": hba, "TPSA": round(tpsa, 1),
                    "rotb": rotb, "QED": round(qed, 3),
                    "skin_window": skin_ok,
                })
                if len(keep) >= N_PER_LEADER:
                    break
            except Exception:
                continue
    except Exception:
        pass
    return keep


def main():
    print(f"R15 BRICS expansion on {len(LEADERS)} universal scaffold leaders ({N_PER_LEADER} each)")
    with Pool(min(5, len(LEADERS))) as p:
        all_results = p.map(expand_one, LEADERS)
    flat = [r for batch in all_results for r in batch]
    df = pd.DataFrame(flat)
    df.to_csv(OUT / "r15_brics_candidates.csv", index=False)
    print(f"\nGenerated {len(df)} unique candidates")
    print(df.groupby("leader_seed").size().to_string())
    if "skin_window" in df.columns:
        print(f"\nSkin-window subset: {df['skin_window'].sum()}/{len(df)}")
    print(f"\nSaved {OUT/'r15_brics_candidates.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
