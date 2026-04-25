"""BACE1 파일럿 10개 ligand ADMET-AI v2 스코어링.

Stage 6 실 런 — ultrathink NEXT ACTIONS #7 부분 실행.
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import pandas as pd
import yaml


def extract_smiles(pilot_dir: Path) -> list[tuple[str, str]]:
    out = []
    for path in sorted(pilot_dir.glob("bace1_*.yaml")):
        d = yaml.safe_load(path.read_text())
        for entry in d.get("sequences", []):
            if "ligand" in entry and "smiles" in entry["ligand"]:
                name = path.stem.replace("bace1_", "").upper()
                out.append((name, entry["ligand"]["smiles"]))
    return out


def main() -> int:
    pilot = Path(__file__).parent / "inputs"
    ligands = extract_smiles(pilot)
    print(f"=== ADMET-AI v2: {len(ligands)} BACE1 ligands ===")

    smiles_list = [s for _, s in ligands]
    names = [n for n, _ in ligands]

    try:
        from admet_ai import ADMETModel
    except ImportError:
        print("admet_ai import 실패")
        return 1

    print("모델 로드 중 (최초 실행 시 ~500MB 체크포인트 다운로드)...")
    model = ADMETModel(num_workers=2)
    print("예측 중...")
    preds = model.predict(smiles=smiles_list)

    # admet_ai가 DataFrame 반환 — index는 유효한 SMILES (invalid drop)
    if isinstance(preds, pd.DataFrame):
        df = preds.copy()
    else:
        df = pd.DataFrame(preds)

    # SMILES → chembl_id 매핑 (invalid 화합물은 드랍됨)
    smi_to_name = dict(zip(smiles_list, names))
    df.insert(0, "chembl_id", [smi_to_name.get(s, "UNKNOWN") for s in df.index])

    out_path = Path(__file__).parent / "admet_ai_results.csv"
    df.to_csv(out_path)
    print(f"\n✅ 저장: {out_path}")

    # 핵심 안전 endpoint 요약
    key_cols = [c for c in df.columns if any(k in c.lower() for k in [
        "herg", "dili", "bbb", "qed", "lipinski", "ames", "logp", "mw"
    ])]
    print(f"\n주요 endpoint 컬럼 ({len(key_cols)}):")
    for c in key_cols[:15]:
        print(f"  {c}")

    # 안전 게이트 적용
    def gate_pass(row) -> bool:
        herg = float(row.get("hERG", 1.0) or 1.0)
        dili = float(row.get("DILI", 1.0) or 1.0)
        bbb = float(row.get("BBB_Martins", 0.0) or 0.0)
        qed = float(row.get("QED", 0.0) or 0.0)
        return herg < 0.5 and dili < 0.5 and bbb >= 0.5 and qed >= 0.4

    df["safety_gate_pass"] = df.apply(gate_pass, axis=1)
    n_pass = int(df["safety_gate_pass"].sum())
    print(f"\n안전 게이트 (hERG<0.5 & DILI<0.5 & BBB>=0.5 & QED>=0.4): {n_pass}/{len(df)}")
    print(df[["chembl_id", "safety_gate_pass"] + [c for c in ["hERG","DILI","BBB_Martins","QED"] if c in df.columns]].to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
