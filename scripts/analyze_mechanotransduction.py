"""EMB-3 9-tier mechanotransduction 통합 분석 (paper Discussion 핵심 hook).

기존 5 타겟 (network_full.csv 측정됨):
  Tier 1 receptor:    TGFB1
  Tier 2 signaling:   SMAD3
  Tier 3 myofib act:  PDGFRB
  Tier 4 effector:    CTGF
  Tier 5 ECM:         MMP1
  + JUN, LOX, FGF2, VEGFA

신규 4 타겟 (mechanotransduction prep, ABFE 후 실행):
  Tier 1' receptor:   LPA1, αvβ6 (ITGB6)
  Tier 3' mechano:    YAP1, TAZ (WWTR1)

→ EMB-3 가 9-tier fibrosis network 다층 조절자 (paper grand claim)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NETWORK = ROOT / "pilot/scaffold_hop/network_validation/network_full.csv"
MECH_OUT = ROOT / "pilot/scaffold_hop/mechanotransduction/output"
ANALYSIS_OUT = ROOT / "pilot/scaffold_hop/mechanotransduction_analysis"
ANALYSIS_OUT.mkdir(parents=True, exist_ok=True)


# 9-tier 분류
TIER_DEFINITION = {
    "Tier 1 (receptor)": ["TGFB1", "LPAR1", "ITGB6"],
    "Tier 2 (signaling)": ["SMAD3"],
    "Tier 3 (mechanotrans)": ["YAP1", "WWTR1"],
    "Tier 4 (myofib activation)": ["PDGFRB"],
    "Tier 5 (effector)": ["CTGF"],
    "Tier 6 (ECM)": ["MMP1", "LOX"],
    "Tier 7 (transcription)": ["JUN"],
    "Selectivity (avoid)": ["FGF2", "VEGFA"],
}


def main() -> int:
    print("=== EMB-3 9-tier mechanotransduction 통합 분석 ===\n")

    # 기존 네트워크 결과
    if not NETWORK.exists():
        print(f"❌ {NETWORK} 없음")
        return 1
    df_existing = pd.read_csv(NETWORK)

    # 신규 결과 (ABFE 후 mechanotransduction cofold 실행 후)
    new_targets = ["LPAR1", "ITGB6", "YAP1", "WWTR1"]
    if MECH_OUT.exists():
        # parse 신규 cofold 결과
        import json
        new_rows = []
        for aff in MECH_OUT.rglob("affinity_*.json"):
            d = json.loads(aff.read_text())
            stem = aff.stem.replace("affinity_", "")
            target_key, comp = stem.split("__", 1)
            new_rows.append({
                "target": target_key.upper(), "compound": comp,
                "affinity_pred_value": d.get("affinity_pred_value"),
                "affinity_probability_binary": d.get("affinity_probability_binary"),
            })
        df_new = pd.DataFrame(new_rows) if new_rows else pd.DataFrame()
    else:
        print(f"  ℹ️ 신규 4 타겟 cofold 미실행 (MECH_OUT 없음)")
        print(f"    실행: scripts/run_mechanotransduction_prep.py로 prep → "
              f".venv/bin/boltz predict")
        df_new = pd.DataFrame()

    # 통합
    if not df_new.empty:
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_existing.copy()

    # tier 매핑
    target_to_tier = {}
    for tier, targets in TIER_DEFINITION.items():
        for t in targets:
            target_to_tier[t] = tier
    df["tier"] = df["target"].map(target_to_tier)
    df = df[df["tier"].notna()]

    # tier × compound 평균
    pivot = df.pivot_table(index="tier", columns="compound",
                            values="affinity_probability_binary",
                            aggfunc="mean")
    if "selectivity_score" not in pivot.columns:
        # selectivity = anti_fibrotic - selectivity_avoid
        avoid = pivot.loc["Selectivity (avoid)"] if "Selectivity (avoid)" in pivot.index else None
        anti_tiers = [t for t in pivot.index if t.startswith("Tier")]
        anti = pivot.loc[anti_tiers].mean()
        if avoid is not None:
            pivot.loc["Selectivity score"] = anti - avoid

    pivot.to_csv(ANALYSIS_OUT / "tier_pivot.csv", float_format="%.3f")

    print("=== Tier × Compound (affinity_probability_binary 평균) ===\n")
    print(pivot.to_string(float_format=lambda v: f"{v:.3f}"
                           if pd.notna(v) else "—"))

    # EMB-3 multi-tier coverage
    if "emb3" in pivot.columns:
        emb3 = pivot["emb3"]
        anti_tiers = [t for t in emb3.index if t.startswith("Tier")]
        n_tier_covered = sum(1 for t in anti_tiers if pd.notna(emb3.get(t))
                              and emb3.get(t) >= 0.5)
        print(f"\n=== EMB-3 multi-tier 평가 ===")
        print(f"  Tier 측정됨: {len([t for t in anti_tiers if pd.notna(emb3.get(t))])}")
        print(f"  Tier ≥ 0.5 binding: {n_tier_covered}")
        print(f"  Selectivity (avoid average): "
              f"{pivot.loc['Selectivity (avoid)', 'emb3']:.3f}"
              if 'Selectivity (avoid)' in pivot.index else "  (avoid 미측정)")

    # paper-tier claim 검증
    print(f"\n=== Paper Discussion claim 검증 ===")
    if not df_new.empty and "emb3" in df["compound"].unique():
        new_emb3 = df_new[df_new["compound"] == "emb3"]
        n_new_strong = (new_emb3["affinity_probability_binary"] >= 0.5).sum()
        print(f"  EMB-3 신규 4 타겟 중 ≥ 0.5: {n_new_strong}/4")
        if n_new_strong >= 3:
            print(f"  🚀 EMB-3는 9-tier mechanotransduction 다차원 조절자")
            print(f"     paper Discussion: 'first multi-tier anti-fibrotic'")
        elif n_new_strong >= 1:
            print(f"  🟡 EMB-3는 부분적 multi-tier — 일부 tier만")
        else:
            print(f"  ⚠️ 신규 타겟 binding 약함 — multi-tier 가설 음성")
    else:
        print(f"  ⏳ 신규 4 타겟 cofold 실행 후 재실행 권장")

    print(f"\n✅ {ANALYSIS_OUT}/tier_pivot.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
