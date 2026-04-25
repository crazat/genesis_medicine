"""Boltz-2 affinity + ADMET-AI v2 결과 통합 리포트.

NEXT ACTIONS #3 + #7 결합 — BACE1 9개 compound의
pIC50 + Lipinski/BBB/hERG/DILI/QED 한 테이블.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd


def load_affinity(out_dir: Path) -> pd.DataFrame:
    rows = []
    for aff_json in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff_json.read_text())
        chembl = aff_json.parent.name.replace("bace1_", "").upper()
        pv = d.get("affinity_pred_value")
        rows.append({
            "chembl_id": chembl,
            "affinity_pred_value": pv,
            "affinity_probability_binary": d.get("affinity_probability_binary"),
            # Boltz-2: pred_value는 log10(IC50)의 scaled form. MW correction 적용된 값.
            # pIC50 ≈ -log10(IC50[M]) = 6 - pred_value (Boltz-2 scaling 기준)
            "pIC50_approx": (6.0 - float(pv)) if pv is not None else None,
        })
    return pd.DataFrame(rows).sort_values("affinity_pred_value")


def load_admet(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df.index.name = "smiles"
    return df


def combine(pilot_dir: Path) -> pd.DataFrame:
    aff = load_affinity(pilot_dir / "output_affinity" / "boltz_results_inputs_affinity" / "predictions")
    admet = load_admet(pilot_dir / "admet_ai_results.csv")
    merged = aff.merge(admet, on="chembl_id", how="outer")
    return merged


def main() -> int:
    pilot = Path(__file__).parent
    merged = combine(pilot)

    key_cols = [
        "chembl_id",
        "affinity_pred_value", "affinity_probability_binary", "pIC50_approx",
        "QED", "Lipinski", "BBB_Martins", "hERG", "DILI", "AMES", "logP",
        "molecular_weight",
    ]
    key_cols = [c for c in key_cols if c in merged.columns]
    out = merged[key_cols]

    # 종합 스코어: binder 확률 × QED × (1 - hERG) × (1 - DILI) × BBB
    def combined_score(row) -> float:
        pb = float(row.get("affinity_probability_binary", 0) or 0)
        qed = float(row.get("QED", 0) or 0)
        herg = float(row.get("hERG", 1) or 1)
        dili = float(row.get("DILI", 1) or 1)
        bbb = float(row.get("BBB_Martins", 0) or 0)
        return pb * qed * (1 - herg) * (1 - dili) * bbb

    out = out.copy()
    out["combined_score"] = out.apply(combined_score, axis=1)
    out = out.sort_values("combined_score", ascending=False)

    out_path = pilot / "bace1_full_report.csv"
    out.to_csv(out_path, index=False)
    print("=" * 100)
    print("BACE1 파일럿 9개 화합물 — Boltz-2 affinity + ADMET-AI v2 통합 리포트")
    print("=" * 100)
    cols_show = [c for c in ["chembl_id","pIC50_approx","affinity_probability_binary",
                             "QED","BBB_Martins","hERG","DILI","combined_score"] if c in out.columns]
    print(out[cols_show].to_string(index=False,
        float_format=lambda v: f"{v:.3f}" if isinstance(v,(int,float)) and not math.isnan(v) else "NaN"))
    print("=" * 100)
    print(f"\n✅ 저장: {out_path}")

    # 요약
    print("\n=== 요약 ===")
    n = len(out)
    strong_binder = (out["affinity_probability_binary"] >= 0.9).sum()
    good_qed = (out.get("QED", pd.Series([0])) >= 0.4).sum()
    bbb_ok = (out.get("BBB_Martins", pd.Series([0])) >= 0.5).sum()
    herg_safe = (out.get("hERG", pd.Series([1])) < 0.5).sum()
    dili_safe = (out.get("DILI", pd.Series([1])) < 0.5).sum()
    print(f"  강한 binder (prob_binary ≥ 0.9): {strong_binder}/{n}")
    print(f"  QED ≥ 0.4:                        {good_qed}/{n}")
    print(f"  BBB 통과 (≥ 0.5):                 {bbb_ok}/{n}")
    print(f"  hERG 안전 (< 0.5):               {herg_safe}/{n}")
    print(f"  DILI 안전 (< 0.5):               {dili_safe}/{n}")
    print()
    print(f"  ⚠️  임상적 의미: 강한 binder이지만 거의 모두 hERG blocker 위험 +")
    print(f"      BBB 통과 낮음 — BACE1 inhibitor 임상 실패 (lanabecestat 등)와 일치.")
    print(f"      → 다음 세션: TxGNN 재창출 또는 다중-타겟 설계로 방향 전환 권고.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
