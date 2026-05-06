"""SA score + drug-likeness on full 2336 ADMET pool. Heavy 24-core."""
import sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, Crippen, QED

# SA score from RDKit Contrib (located in venv site-packages)
import rdkit
SA_PATH = Path(rdkit.__file__).parent / "Contrib" / "SA_Score"
sys.path.insert(0, str(SA_PATH))
import sascorer

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"


def analyze(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        mw = Descriptors.MolWt(m)
        logp = Crippen.MolLogP(m)
        hbd = Descriptors.NumHDonors(m)
        hba = Descriptors.NumHAcceptors(m)
        return {
            "smiles": smi,
            "sa_score": sascorer.calculateScore(m),
            "qed": QED.qed(m),
            "mw": mw,
            "logp": logp,
            "hbd": hbd,
            "hba": hba,
            "tpsa": Descriptors.TPSA(m),
            "rotbonds": Descriptors.NumRotatableBonds(m),
            "aromatic_rings": Descriptors.NumAromaticRings(m),
            "heavy_atoms": Descriptors.HeavyAtomCount(m),
            "lipinski_violations": int(mw > 500) + int(logp > 5)
                                    + int(hbd > 5) + int(hba > 10),
            "veber_violations": int(Descriptors.NumRotatableBonds(m) > 10)
                                  + int(Descriptors.TPSA(m) > 140),
        }
    except Exception:
        return None


def main():
    df = pd.read_csv(OUT / "admet_screen_combined.csv")
    smiles = df["smiles"].dropna().tolist()
    print(f"SA score + drug-likeness on {len(smiles)} mol")

    with Pool(24) as p:
        results = p.map(analyze, smiles)
    valid = [r for r in results if r]
    out = pd.DataFrame(valid)
    out.to_csv(OUT / "druglikeness_full.csv", index=False)

    print(f"  valid: {len(out)}")
    print(f"  SA range: {out['sa_score'].min():.2f}-{out['sa_score'].max():.2f}, "
          f"mean {out['sa_score'].mean():.2f}")
    print(f"  QED range: {out['qed'].min():.3f}-{out['qed'].max():.3f}, "
          f"mean {out['qed'].mean():.3f}")
    print(f"  Lipinski-pass (0 viol): "
          f"{(out['lipinski_violations'] == 0).sum()}/{len(out)}")
    print(f"  Veber-pass: {(out['veber_violations'] == 0).sum()}/{len(out)}")
    drug_like = ((out['lipinski_violations'] == 0)
                  & (out['veber_violations'] == 0))
    print(f"  Drug-like (both pass): {drug_like.sum()}/{len(out)}")


if __name__ == "__main__":
    sys.exit(main())
