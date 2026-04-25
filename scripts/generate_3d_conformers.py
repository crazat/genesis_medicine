"""천연물 라이브러리 3D conformer 사전생성 (RDKit ETKDGv3).

용도: docking/MD를 위한 sane initial 3D 좌표.
출력: data/skin_compounds_3d/<name>.sdf (single conformer, force-field optimised)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "skin_compounds_3d"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    csv = DATA / "skin_compounds_curated.csv"
    if not csv.exists():
        print("❌ skin_compounds_curated.csv 없음 — fetch_skin_compound_smiles.py 먼저 실행")
        return 1

    df = pd.read_csv(csv)
    valid = df[df["smiles"].notna()]
    print(f"=== {len(valid)}개 천연물 → 3D ETKDG conformer ===")

    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError:
        print("❌ RDKit 미설치")
        return 1

    n_ok, n_fail = 0, 0
    for _, r in valid.iterrows():
        try:
            mol = Chem.MolFromSmiles(r["smiles"])
            if mol is None:
                n_fail += 1
                continue
            mol = Chem.AddHs(mol)
            params = AllChem.ETKDGv3()
            params.randomSeed = 42
            cid = AllChem.EmbedMolecule(mol, params)
            if cid != 0:
                # MMFF94 fallback
                AllChem.MMFFOptimizeMolecule(mol)
            else:
                AllChem.MMFFOptimizeMolecule(mol)

            safe = (r["name"]
                    .replace(" ", "_")
                    .replace("/", "_")
                    .replace("(", "")
                    .replace(")", "")
                    .replace(",", "")
                    .replace("-", "_"))
            sdf = OUT / f"{safe}.sdf"
            with Chem.SDWriter(str(sdf)) as w:
                # 메타데이터 기록
                mol.SetProp("_Name", r["name"])
                mol.SetProp("source", str(r.get("source_botanical", "")))
                mol.SetProp("source_korean", str(r.get("source_korean", "")))
                mol.SetProp("category", str(r.get("category", "")))
                mol.SetProp("CID", str(r.get("cid", "")))
                w.write(mol)
            n_ok += 1
        except Exception as e:
            print(f"  ❌ {r['name']}: {e}")
            n_fail += 1

    print(f"\n✅ {n_ok}개 SDF 생성 → {OUT}")
    print(f"   실패: {n_fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
