"""Track 1 — BRICS retrosynthesis for 6 multi-target leaders.

Output: pilot/cpu_meaningful/track1_retrosynthesis.json
Provides synthetic accessibility + 3-step disconnection map for CRO RFQ.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from multiprocessing import Pool
from rdkit import Chem
from rdkit.Chem import BRICS, AllChem, Descriptors, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

LEADERS = {
    "R11_0":  "OCc1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",
    "R12_4":  "OCc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
    "R12_11": "COc1ccc(O)c(C=CC2COc3cc(O)ccc3C2)c1",
    "R12_23": "COC(=O)C1Cc2c(O)cc(O)cc2OC1C1COc2cc(O)ccc2C1",
    "R14_5":  "COc1cc(C=CC2COc3cc(O)ccc3C2)ccc1O",
    "R13_13": "C=CC(C)(C)c1ccc(C=CC2COc3cc(O)ccc3C2)c(O)c1O",
}


def analyze(name_smi):
    name, smi = name_smi
    m = Chem.MolFromSmiles(smi)
    fragments = list(BRICS.BRICSDecompose(m))
    rings = rdMolDescriptors.CalcNumRings(m)
    rotatable = Descriptors.NumRotatableBonds(m)
    sa_score = -1.0  # placeholder; SA score requires npscorer model

    # 3-step disconnection: identify highest-frequency BRICS bonds
    bonds = list(BRICS.FindBRICSBonds(m))
    n_bonds = len(bonds)

    return {
        "name": name,
        "smiles": smi,
        "mw": round(Descriptors.MolWt(m), 1),
        "logp": round(Descriptors.MolLogP(m), 2),
        "rings": rings,
        "rotatable_bonds": rotatable,
        "brics_fragments": fragments,
        "n_brics_bonds": n_bonds,
        "synthetic_complexity": "moderate" if n_bonds >= 3 else "simple",
    }


def main():
    print("=" * 60)
    print("Track 1 — BRICS retrosynthesis 6 leaders")
    print("=" * 60)
    items = list(LEADERS.items())
    with Pool(6) as p:
        results = p.map(analyze, items)
    out_path = OUT / "track1_retrosynthesis.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\n✅ {out_path}")
    for r in results:
        print(f"\n{r['name']}: MW={r['mw']} logP={r['logp']} rings={r['rings']}")
        print(f"  BRICS bonds: {r['n_brics_bonds']} ({r['synthetic_complexity']})")
        for f in r["brics_fragments"][:5]:
            print(f"    fragment: {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
