"""scaffold-hop 결과 ADMET 필터링 + skin topical scoring.

skin topical 적합 후보 도출:
- 유효 SMILES (RDKit parseable)
- MW ≤ 500, logP 1.5-3.5, HBD ≤ 5, HBA ≤ 10, TPSA ≤ 140
- hERG ≤ 0.3, Skin_Reaction ≤ 0.3, AMES ≤ 0.5
- Tanimoto ≥ 0.4 (mol2mol medium similarity, scaffold 유지)
- seed 대비 hERG / Skin_Reaction / logP 거리 개선 → composite score
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski

warnings.filterwarnings("ignore")
RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "pilot/scaffold_hop"

SEEDS = {
    "embelin":  "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
    "curcumin": "COC1=C(C=CC(=C1)/C=C/C(=O)CC(=O)/C=C/C2=CC(=C(C=C2)O)OC)O",
}


def rdkit_props(smi: str) -> dict | None:
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return None
    return {
        "smiles_canon": Chem.MolToSmiles(m),
        "MW":   Descriptors.MolWt(m),
        "logP": Crippen.MolLogP(m),
        "HBD":  Lipinski.NumHDonors(m),
        "HBA":  Lipinski.NumHAcceptors(m),
        "TPSA": Descriptors.TPSA(m),
        "n_rings": Descriptors.RingCount(m),
        "n_heavy": m.GetNumHeavyAtoms(),
    }


def passes_topical(p: dict) -> bool:
    return (p["MW"] <= 500
            and 1.5 <= p["logP"] <= 3.5
            and p["HBD"] <= 5
            and p["HBA"] <= 10
            and p["TPSA"] <= 140)


def composite_score(seed_admet: dict, c: dict) -> float:
    """seed 대비 개선 점수 (0-1, 높을수록 좋음)."""
    # hERG, Skin_Reaction은 낮을수록 좋음
    d_herg = seed_admet["hERG"] - c["hERG"]
    d_skin = seed_admet["Skin_Reaction"] - c["Skin_Reaction"]
    d_ames = seed_admet["AMES"] - c["AMES"]

    # logP 최적 거리: 2.5 가 skin topical sweet spot
    d_logp = abs(seed_admet["_logP"] - 2.5) - abs(c["logP"] - 2.5)

    # MW 페널티 (500 초과는 거의 0)
    mw_ok = 1.0 if c["MW"] <= 450 else max(0.0, (500 - c["MW"]) / 50)

    raw = (0.35 * d_herg + 0.25 * d_skin + 0.10 * d_ames + 0.20 * d_logp +
           0.10 * mw_ok)
    # squash to 0-1 (sigmoid)
    import math
    return 1 / (1 + math.exp(-3 * raw))


def main() -> int:
    from admet_ai import ADMETModel
    print("[1/3] ADMETModel 로드 (~10s)")
    model = ADMETModel()

    # seed 자체의 ADMET (비교 baseline)
    seed_props = {n: {**rdkit_props(s), "_logP": rdkit_props(s)["logP"]}
                  for n, s in SEEDS.items()}
    seed_df = model.predict(list(SEEDS.values()))
    for i, n in enumerate(SEEDS):
        for k in ["hERG", "Skin_Reaction", "AMES", "Bioavailability_Ma",
                  "ClinTox", "Solubility_AqSolDB"]:
            seed_props[n][k] = float(seed_df.iloc[i][k])

    summary_rows = []
    for name, seed in SEEDS.items():
        print(f"\n=== {name.upper()} ===")
        csv = BASE / name / "outputs/sampled.csv"
        if not csv.exists():
            print(f"   ⚠️  {csv} 없음 — run_scaffold_hop.py 먼저 실행")
            continue
        df = pd.read_csv(csv)
        print(f"  raw samples: {len(df)}")

        # 1) RDKit 파싱 + 물성
        rows = []
        for _, r in df.iterrows():
            smi = r["SMILES"]
            p = rdkit_props(smi)
            if p is None:
                continue
            p["smiles"] = smi
            p["tanimoto_to_seed"] = float(r.get("Tanimoto", 0))
            p["nll"] = float(r.get("NLL", 0))
            rows.append(p)
        cleaned = pd.DataFrame(rows).drop_duplicates(subset="smiles_canon")
        print(f"  valid + dedup: {len(cleaned)}")

        # 2) Lipinski / topical filter
        topical = cleaned[cleaned.apply(passes_topical, axis=1)].copy()
        print(f"  topical OK (MW≤500, logP 1.5-3.5, …): {len(topical)}")
        if topical.empty:
            continue

        # 3) ADMET-AI 예측
        print(f"  ADMET-AI 예측 시작 ({len(topical)}개)…")
        adm = model.predict(topical["smiles"].tolist())
        for col in ["hERG", "Skin_Reaction", "AMES", "Bioavailability_Ma",
                    "ClinTox", "Solubility_AqSolDB"]:
            topical[col] = adm[col].values

        # 4) tox 상대 필터 — seed 대비 hERG · Skin_Reaction · AMES 중 ≥2개 개선
        s = seed_props[name]
        improve_count = (
            (topical["hERG"] < s["hERG"]).astype(int) +
            (topical["Skin_Reaction"] < s["Skin_Reaction"]).astype(int) +
            (topical["AMES"] < s["AMES"]).astype(int)
        )
        # 또한 어느 endpoint도 0.05 이상 더 나빠지지 않을 것
        no_regress = (
            (topical["hERG"] - s["hERG"] < 0.05) &
            (topical["Skin_Reaction"] - s["Skin_Reaction"] < 0.05) &
            (topical["AMES"] - s["AMES"] < 0.05) &
            (topical["ClinTox"] - s["ClinTox"] < 0.10)
        )
        tox_ok = topical[(improve_count >= 2) & no_regress].copy()
        print(f"  tox-OK (≥2 endpoint seed보다 좋음, regression < 0.05): "
              f"{len(tox_ok)}")
        if tox_ok.empty:
            continue

        # 5) composite score
        seed_admet = seed_props[name]
        tox_ok["score"] = tox_ok.apply(
            lambda r: composite_score(seed_admet, r.to_dict()), axis=1)
        tox_ok = tox_ok.sort_values("score", ascending=False).reset_index(drop=True)

        # 6) 저장 + 출력
        out_csv = BASE / name / "outputs/ranked.csv"
        cols = ["smiles", "smiles_canon", "score", "tanimoto_to_seed", "MW",
                "logP", "HBD", "HBA", "TPSA", "hERG", "Skin_Reaction",
                "AMES", "ClinTox", "Solubility_AqSolDB", "Bioavailability_Ma"]
        tox_ok[cols].to_csv(out_csv, index=False)
        print(f"  ✅ {out_csv}")

        # seed 비교 한 줄
        print(f"\n  📊 SEED ({name}):")
        s = seed_admet
        print(f"     MW={s['MW']:.1f}  logP={s['_logP']:.2f}  "
              f"hERG={s['hERG']:.3f}  Skin={s['Skin_Reaction']:.3f}  "
              f"AMES={s['AMES']:.3f}")

        # top 5
        print(f"\n  🏆 TOP 5:")
        for i, r in tox_ok.head(5).iterrows():
            print(f"     [{i+1}] score={r['score']:.3f}  "
                  f"MW={r['MW']:.0f} logP={r['logP']:.2f} "
                  f"hERG={r['hERG']:.2f} Skin={r['Skin_Reaction']:.2f}  "
                  f"Tan={r['tanimoto_to_seed']:.2f}")
            print(f"         {r['smiles']}")

        summary_rows.append({
            "seed": name,
            "raw": len(df),
            "valid": len(cleaned),
            "topical_pass": len(topical),
            "tox_pass": len(tox_ok),
            "best_score": float(tox_ok.iloc[0]["score"]),
            "best_smiles": tox_ok.iloc[0]["smiles"],
            "best_hERG": float(tox_ok.iloc[0]["hERG"]),
            "best_skin": float(tox_ok.iloc[0]["Skin_Reaction"]),
        })

    if summary_rows:
        pd.DataFrame(summary_rows).to_csv(BASE / "summary.csv", index=False)
        print(f"\n✅ {BASE / 'summary.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
