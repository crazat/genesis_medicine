"""Bayesian Optimization으로 EMB-3 다음 SAR 라운드 후보 추천.

전제:
  - Round 1, 2 결과 데이터: pilot/scaffold_hop/.../ranked.csv, round2_affinity.csv
  - Network 27 cofold: pilot/scaffold_hop/network_validation/network_full.csv
  - 알려진 측정값 + 후보 candidate pool에서 EI 기반 batch_size 추천
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "pilot/scaffold_hop"
OUT = ROOT / "pilot/scaffold_hop/bayesian_sar"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    from genesis_medicine.optimization.bayesian_sar import (
        suggest_next_batch, multi_fidelity_score,
    )

    print("=== Bayesian SAR — 다음 라운드 후보 추천 ===\n")

    # 1. Known 데이터: round 1 ranked.csv (ADMET + Boltz-2 affinity validated)
    round1 = pd.read_csv(SCAFFOLD / "embelin/outputs/ranked.csv")
    valid = pd.read_csv(SCAFFOLD / "boltz2_validation/validation_full.csv")

    # network_full에서 EMB-3 affinity 가져오기
    network = pd.read_csv(SCAFFOLD / "network_validation/network_full.csv")
    # 각 SMILES에 대해 TGFB1 affinity (가장 우리 핵심 metric)
    tgfb1 = network[network["target"] == "TGFB1"][["compound", "affinity_probability_binary"]]
    tgfb1 = tgfb1.rename(columns={"compound": "compound_name"})

    # known dataset: round1 ADMET + 추가 측정값 mapping
    # round1에는 hERG, Skin_Reaction이 있음. valid는 affinity 측정값.
    valid_pivot = valid.pivot_table(index="compound", columns="target",
                                      values="affinity_probability_binary",
                                      aggfunc="first").reset_index()
    valid_pivot.columns.name = None
    print(f"  round 1 ADMET ranked: {len(round1)} compounds")
    print(f"  validated affinity (top 3 ×× 3 targets): {len(valid_pivot)} compounds")

    # round 2 candidates (실패한 라운드 — EMB-3 대비 약함)
    try:
        round2 = pd.read_csv(SCAFFOLD + "_round2/ranked.csv"
                                if False else
                                Path(SCAFFOLD).parent / "scaffold_hop_round2/ranked.csv")
        print(f"  round 2 candidates: {len(round2)} (EMB-3 dataset)")
    except Exception:
        round2 = pd.DataFrame()

    # 2. Known dataset 빌드
    # round 1 ADMET 정보 + valid에서 측정된 TGFB1 affinity 매핑
    known_rows = []
    for _, r in valid_pivot.iterrows():
        comp = r["compound"]
        if "TGFB1" not in r or pd.isna(r["TGFB1"]):
            continue
        # SMILES from round 1 (ADMET ranked)
        match = round1[round1["smiles"].notna()]
        # round1의 'compound_safe' 또는 idx로 mapping
        # 여기서 단순화 — ranked.csv 의 smiles 그대로
        # 첫 row의 SMILES를 valid의 compound 기준으로 lookup
        # 그러나 round1.csv에는 compound_name 없고 smiles만 있음
        # ranking 인덱스로 매핑:
        if comp.startswith("embelin_emb"):
            try:
                idx = int(comp.replace("embelin_emb", "")) - 1
                row = round1.iloc[idx]
                known_rows.append({
                    "smiles": row["smiles"], "compound": comp,
                    "tgfb1_affinity": float(r["TGFB1"]),
                    "hERG": float(row["hERG"]), "skin": float(row["Skin_Reaction"]),
                })
            except Exception:
                continue
    df_known = pd.DataFrame(known_rows)
    if df_known.empty:
        print("\n⚠️ known 데이터 0건 — round 1 매핑 실패")
        return 1
    print(f"  known dataset: {len(df_known)} (TGFB1 affinity 측정됨)")

    # 3. Candidates: round 1 ADMET top 30 (아직 affinity 미측정)
    df_candidates = round1.head(30)[["smiles", "score", "hERG", "Skin_Reaction"]]
    print(f"  candidate pool: {len(df_candidates)}")

    # 4. BO suggest
    print("\n[BO 1] TGFB1 affinity 최대화 (EI acquisition)")
    next_batch = suggest_next_batch(
        df_known=df_known, df_candidates=df_candidates,
        target_metric="tgfb1_affinity", smiles_col="smiles",
        batch_size=5, acquisition="EI",
    )
    print(next_batch[["smiles", "gp_mean", "gp_std", "acquisition_score"]].to_string(index=False))

    print("\n[BO 2] hERG 최소화 (UCB acquisition, minimize)")
    next_safe = suggest_next_batch(
        df_known=df_known, df_candidates=df_candidates,
        target_metric="hERG", smiles_col="smiles",
        batch_size=5, acquisition="UCB", minimize=True,
    )
    print(next_safe[["smiles", "gp_mean", "gp_std", "acquisition_score"]].to_string(index=False))

    # 저장
    next_batch.to_csv(OUT / "tgfb1_max_batch.csv", index=False)
    next_safe.to_csv(OUT / "herg_min_batch.csv", index=False)
    print(f"\n✅ {OUT}/tgfb1_max_batch.csv  +  herg_min_batch.csv")

    print("\n=== 다음 SAR 라운드 권장 ===")
    print(f"  - {len(next_batch)} compounds for TGFB1 affinity validation (~30s × 5 = 2.5분 GPU)")
    print(f"  - {len(next_safe)} compounds for hERG re-validation (~3분 ADMET-AI)")
    print(f"  - 측정 후 known dataset에 추가 → 다음 BO iter (BATCHIE-style)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
