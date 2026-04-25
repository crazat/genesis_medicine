"""logKp (skin permeability coefficient) 자체 ML head 학습.

Genesis_Medicine v3 stack의 가장 큰 약점 — ADMET-AI는 skin_reaction 있지만
정량 logKp (cm/h) 예측 모델이 없음. 외용제 개발의 핵심 지표.

데이터: FDA 2326 dermal absorption (n≈2326 화합물의 logKp 측정값) — 공개.
       PLOS Digital Health 2024 (DOI 10.1371/journal.pdig.0000483)에서 LGBM SOTA.

모델: LGBM Regressor on RDKit descriptors + Morgan fingerprint.

출력: pickle 모델 → src/genesis_medicine/admet/logkp_model.pkl
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "logkp_train"
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR = ROOT / "src/genesis_medicine/admet"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def featurize(smiles: str) -> np.ndarray | None:
    """RDKit descriptors + Morgan FP 2048 bits."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    desc = [
        Descriptors.MolWt(mol),
        Crippen.MolLogP(mol),
        Lipinski.NumHDonors(mol),
        Lipinski.NumHAcceptors(mol),
        Descriptors.TPSA(mol),
        Descriptors.NumRotatableBonds(mol),
        Descriptors.NumAromaticRings(mol),
        Descriptors.HeavyAtomCount(mol),
    ]
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    return np.concatenate([np.array(desc), np.array(fp)])


def load_or_synthesize_data(data_path: Path) -> pd.DataFrame:
    """학습 데이터 로드 또는 합성.

    실제 FDA 2326 dataset은 PLOS Digital Health 2024 supplementary에 있음 —
    URL: https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000483

    여기서는 dataset 미다운로드 시 sklearn datasets 형식 placeholder 생성.
    """
    if data_path.exists():
        df = pd.read_csv(data_path)
        print(f"  loaded: {len(df)} rows from {data_path}")
        return df

    print(f"  ⚠️  {data_path} 없음 — placeholder 생성 (skin_compounds_curated.csv 기반)")
    print(f"     실제 학습은 FDA 2326 dataset 다운로드 후 진행:")
    print(f"     URL: https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000483")
    print(f"     supplementary 다운로드 → {data_path}")

    # placeholder: skin_compounds_curated.csv를 logKp prediction 으로 사용
    # logKp는 logP + MW에서 대략 추정 가능 (Potts-Guy equation):
    # log Kp (cm/h) = -2.7 + 0.71 logP - 0.0061 MW
    skin = pd.read_csv(ROOT / "data/skin_compounds_curated.csv")
    skin = skin[skin["smiles"].notna()].copy()
    skin["logkp_potts_guy"] = (-2.7 + 0.71 * skin["logp"].astype(float)
                                 - 0.0061 * skin["mw"].astype(float))
    placeholder = skin[["smiles", "logkp_potts_guy"]].rename(
        columns={"logkp_potts_guy": "log_kp"})
    placeholder.to_csv(data_path, index=False)
    print(f"  ✅ placeholder ({len(placeholder)} rows) → {data_path}")
    print(f"     ⚠️  Potts-Guy 추정값. 실제 측정 데이터로 교체 권장.")
    return placeholder


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",
                        default=str(DATA_DIR / "logkp_dataset.csv"),
                        help="logKp training data (CSV: smiles, log_kp)")
    parser.add_argument("--out",
                        default=str(MODEL_DIR / "logkp_model.pkl"),
                        help="output pickle path")
    parser.add_argument("--no-train", action="store_true",
                        help="data prep만, 학습 skip")
    args = parser.parse_args()

    print("=== logKp ML head 학습 ===")
    df = load_or_synthesize_data(Path(args.data))

    # featurize
    print("\n[1/3] featurization")
    feats = []
    targets = []
    for _, row in df.iterrows():
        f = featurize(row["smiles"])
        if f is None:
            continue
        feats.append(f)
        targets.append(row["log_kp"])
    X = np.array(feats)
    y = np.array(targets)
    print(f"  X: {X.shape}, y: {y.shape}, y range: [{y.min():.2f}, {y.max():.2f}]")

    if args.no_train:
        return 0

    # train
    print("\n[2/3] LGBM training")
    try:
        import lightgbm as lgb
        from sklearn.model_selection import KFold, cross_val_score
        from sklearn.metrics import mean_absolute_error, r2_score
    except ImportError:
        print(f"  ❌ lightgbm 또는 sklearn 미설치")
        print(f"     uv pip install --python {sys.executable} lightgbm scikit-learn")
        return 1

    model = lgb.LGBMRegressor(
        n_estimators=500, learning_rate=0.05, num_leaves=31,
        min_child_samples=5, random_state=42, verbose=-1,
    )

    if len(X) < 50:
        print(f"  ⚠️  데이터 너무 적음 ({len(X)}) — 5-fold CV 대신 train all")
        model.fit(X, y)
        y_pred = model.predict(X)
        print(f"  train MAE: {mean_absolute_error(y, y_pred):.3f}")
        print(f"  train R²:  {r2_score(y, y_pred):.3f}")
    else:
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        mae_scores = -cross_val_score(model, X, y, scoring="neg_mean_absolute_error",
                                        cv=kf)
        r2_scores = cross_val_score(model, X, y, scoring="r2", cv=kf)
        print(f"  5-fold CV MAE: {mae_scores.mean():.3f} ± {mae_scores.std():.3f}")
        print(f"  5-fold CV R²:  {r2_scores.mean():.3f} ± {r2_scores.std():.3f}")
        model.fit(X, y)

    # save
    print("\n[3/3] save")
    out_path = Path(args.out)
    with out_path.open("wb") as f:
        pickle.dump({
            "model": model,
            "feature_dim": X.shape[1],
            "n_train": len(X),
            "training_data": str(args.data),
            "version": "0.1.0_potts_guy_placeholder" if "potts_guy" in str(args.data)
                       else "0.1.0",
        }, f)
    print(f"  ✅ {out_path} ({out_path.stat().st_size // 1024} KB)")

    # quick test on EMB-3 + Embelin
    print("\n=== EMB-3 / Embelin / EGCG 예측 ===")
    test = {
        "Embelin": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        "EMB-3":   "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
        "EGCG":    "C1[C@H]([C@H](OC2=CC(=CC(=C21)O)O)C3=CC(=C(C(=C3)O)O)O)OC(=O)C4=CC(=C(C(=C4)O)O)O",
        "Asiaticoside": "C[C@@H]1CC[C@@]2(CC[C@@]3(C(=CC[C@H]4[C@]3(C[C@H]([C@@H]5[C@@]4(C[C@H]([C@@H]([C@@]5(C)CO)O)O)C)O)C)[C@@H]2[C@H]1C)C)C(=O)O",
    }
    for name, smi in test.items():
        f = featurize(smi)
        if f is None:
            continue
        pred = model.predict(f.reshape(1, -1))[0]
        print(f"  {name:15s} log Kp = {pred:.2f} (cm/h, log scale)")

    print("\n=== 해석 ===")
    print("log Kp ≥ -2: 좋은 외용 흡수")
    print("log Kp -2 ~ -4: 중간")
    print("log Kp < -4: 나쁜 흡수 (외용 적합 X)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
