"""한약 천연물 SMILES → fragment library (f-RAG 용).

Genesis_Medicine v3의 `data/skin_compounds_curated.csv` (102 compounds)에서
substructure 추출 → f-RAG의 hard fragment 강제 포함 vocabulary로 사용.

목적: REINVENT 4 mol2mol과 달리 f-RAG는 fragment-level 강제 — 한약 영감 분자가
센텔라 코어, 시코닌 quinone, EGCG gallate ester 등 핵심 pharmacophore를
반드시 포함하도록 generate.

출력: SMILES (.smi) — 하나의 SMILES per line (f-RAG 표준 input).
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, BRICS, Recap

RDLogger.DisableLog("rdApp.*")


def get_brics_fragments(smiles: str) -> list[str]:
    """BRICS 분해 (Breaking Retrosynthetically Interesting Chemical Substructures)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []
    fragments = list(BRICS.BRICSDecompose(mol, returnMols=False))
    # remove dummy atoms
    cleaned = []
    for f in fragments:
        m = Chem.MolFromSmiles(f.replace("*", "[H]"))
        if m and m.GetNumHeavyAtoms() >= 4:
            cleaned.append(Chem.MolToSmiles(m))
    return cleaned


def get_murcko_scaffold(smiles: str) -> str | None:
    """Murcko scaffold — ring + linker (no side chain)."""
    from rdkit.Chem.Scaffolds import MurckoScaffold
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    if scaffold.GetNumHeavyAtoms() < 4:
        return None
    return Chem.MolToSmiles(scaffold)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="data/skin_compounds_curated.csv 경로")
    parser.add_argument("--out", required=True, help="출력 .smi")
    parser.add_argument("--include-categories", default="",
                        help="콤마 분리 카테고리 (예: scar,acne). 빈값=전체")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"❌ 입력 없음: {in_path}", file=sys.stderr)
        return 1

    df = pd.read_csv(in_path)
    if args.include_categories:
        cats = [c.strip().lower() for c in args.include_categories.split(",")]
        mask = df["category"].str.lower().str.contains("|".join(cats), na=False)
        df = df[mask]
    print(f"=== 한약 fragment library 빌드 ===")
    print(f"  입력 화합물: {len(df)}")

    fragments = set()
    scaffolds = set()
    n_brics = 0
    for _, row in df.iterrows():
        smi = row.get("smiles")
        if pd.isna(smi):
            continue
        # BRICS
        for f in get_brics_fragments(smi):
            fragments.add(f)
            n_brics += 1
        # Murcko scaffold
        s = get_murcko_scaffold(smi)
        if s:
            scaffolds.add(s)

    all_frags = fragments | scaffolds
    print(f"  BRICS fragments: {n_brics} (unique: {len(fragments)})")
    print(f"  Murcko scaffolds: {len(scaffolds)}")
    print(f"  총 unique fragments: {len(all_frags)}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(sorted(all_frags)) + "\n")
    print(f"\n✅ {out_path} ({len(all_frags)} fragments)")

    # 핵심 pharmacophore 강조
    key_compounds = {
        "Asiaticoside": "센텔라",
        "Madecassoside": "센텔라",
        "Asiatic acid": "센텔라",
        "Madecassic acid": "센텔라",
        "Shikonin": "자초/자운고",
        "Acetylshikonin": "자초/자운고",
        "EGCG": "녹차",
        "Licochalcone A": "감초",
        "Glabridin": "감초",
        "Berberine": "황련",
        "Curcumin": "울금",
        "Embelin": "Embelia",
        "Baicalein": "황금",
        "Baicalin": "황금",
    }
    print(f"\n=== 핵심 pharmacophore 보유 fragment ===")
    for name, source in key_compounds.items():
        row = df[df["name"] == name]
        if row.empty:
            continue
        smi = row.iloc[0]["smiles"]
        scaf = get_murcko_scaffold(smi) if not pd.isna(smi) else None
        if scaf:
            print(f"  {name:20s} ({source}) Murcko: {scaf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
