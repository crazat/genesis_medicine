"""TxGNN Top 후보 → Boltz-2 + ADMET-AI 통합 결정 테이블.

종합 점수
-----------
combined = affinity_prob_binary × BBB × QED × (1-hERG) × (1-DILI)
→ "AD-druggable repurposing candidate" 우선순위
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RESULT = Path(__file__).parent / "results"


def main() -> int:
    smi = pd.read_csv(RESULT / "top20_smiles.csv")
    aff = pd.read_csv(RESULT / "boltz2_bace1_affinity.csv")

    # SMILES + affinity 병합
    merged = smi.merge(aff, on="drug_name", how="inner")
    valid_smiles = merged[merged["smiles"].notna()].copy()
    print(f"=== ADMET-AI v2 ({len(valid_smiles)} 화합물) ===")

    from admet_ai import ADMETModel
    model = ADMETModel(num_workers=2)
    preds = model.predict(smiles=valid_smiles["smiles"].tolist())

    # admet_ai DataFrame: index=SMILES
    smi_to_admet = {smi_str: row for smi_str, row in preds.iterrows()}

    rows = []
    for _, r in valid_smiles.iterrows():
        ap = smi_to_admet.get(r["smiles"])
        if ap is None:
            continue
        herg = float(ap.get("hERG", 1.0))
        dili = float(ap.get("DILI", 1.0))
        bbb = float(ap.get("BBB_Martins", 0.0))
        qed = float(ap.get("QED", 0.0))
        lipinski = float(ap.get("Lipinski", 0.0))
        prob = float(r["affinity_probability_binary"])

        # 종합 스코어
        combined = prob * bbb * qed * (1 - herg) * (1 - dili)
        rows.append({
            "txgnn_rank": int(r["txgnn_rank"]),
            "drug_name": r["drug_name"],
            "pIC50_approx": round(r["pIC50_approx"], 2),
            "BACE1_prob": round(prob, 3),
            "BBB": round(bbb, 3),
            "QED": round(qed, 3),
            "hERG": round(herg, 3),
            "DILI": round(dili, 3),
            "combined_score": round(combined, 5),
            "safety_gate": (herg < 0.5) and (dili < 0.5) and (bbb >= 0.5) and (qed >= 0.4),
        })

    out = pd.DataFrame(rows).sort_values("combined_score", ascending=False)
    csv = RESULT / "repurposing_full_report.csv"
    out.to_csv(csv, index=False)
    print(f"\n{'=' * 110}")
    print("TxGNN Top 재창출 후보 × BACE1 affinity × ADMET 통합 결정 테이블")
    print("=" * 110)
    print(out.to_string(index=False))
    print("=" * 110)

    n = len(out)
    pass_gate = out["safety_gate"].sum()
    print(f"\n안전 게이트 (hERG<0.5 & DILI<0.5 & BBB≥0.5 & QED≥0.4): {pass_gate}/{n}")
    best = out.iloc[0]
    print(f"\n최상위 combined_score: {best['drug_name']} ({best['combined_score']})")
    print(f"  TxGNN rank: {best['txgnn_rank']}")
    print(f"  BACE1 prob: {best['BACE1_prob']}, BBB: {best['BBB']}, QED: {best['QED']}, hERG: {best['hERG']}")
    print(f"\n✅ 저장: {csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
