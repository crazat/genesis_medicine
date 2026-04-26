"""BATCHIE-style Bayesian Optimization for SAR cycle.

Genesis_Medicine v3의 SAR 반복 (round 1 → 2 → 3) 효율화. 102 화합물 + scaffold-hop
변형 데이터를 활용해 다음 SAR 라운드 합성 후보 자동 추천.

알고리즘:
  1. 각 후보 분자 → RDKit descriptor + Morgan FP 특징
  2. Gaussian Process regression on (features → target metric)
  3. Expected Improvement (EI) acquisition으로 다음 합성 추천
  4. Multi-fidelity: ABFE 정량 (저비용) + in vitro IC50 (고비용) 결합

용도:
  - EMB-3 next-gen lead 자동 추천
  - Embelin scaffold 변형 재탐색
  - 외용 logKp + hERG + skin_reaction multi-objective

라이선스: gpytorch (MIT), botorch (MIT) — commercial OK.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski

RDLogger.DisableLog("rdApp.*")


def featurize(smiles: str, fp_bits: int = 512) -> np.ndarray | None:
    """RDKit descriptor + Morgan FP."""
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
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=fp_bits)
    return np.concatenate([np.array(desc), np.array(fp)])


def expected_improvement(mu: np.ndarray, sigma: np.ndarray,
                         best: float, xi: float = 0.01) -> np.ndarray:
    """EI acquisition function (maximization)."""
    from scipy.stats import norm
    # avoid div-by-zero
    sigma = np.maximum(sigma, 1e-6)
    z = (mu - best - xi) / sigma
    return (mu - best - xi) * norm.cdf(z) + sigma * norm.pdf(z)


def upper_confidence_bound(mu: np.ndarray, sigma: np.ndarray,
                            beta: float = 2.0) -> np.ndarray:
    """UCB acquisition (maximization)."""
    return mu + beta * sigma


def gp_regression(X_train: np.ndarray, y_train: np.ndarray,
                   X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Gaussian Process regression — sklearn 기반 간이.

    botorch/gpytorch 비호환 시 fallback. botorch 더 강력한 case는 위 함수 호출.
    """
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel

    # Kernel: Matern 2.5 + white noise
    kernel = Matern(nu=2.5, length_scale=1.0) + WhiteKernel(noise_level=0.1)
    gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                    n_restarts_optimizer=3, random_state=42)
    gp.fit(X_train, y_train)
    mu, sigma = gp.predict(X_test, return_std=True)
    return mu, sigma


def suggest_next_batch(
    df_known: pd.DataFrame,
    df_candidates: pd.DataFrame,
    target_metric: str,
    smiles_col: str = "smiles",
    batch_size: int = 5,
    acquisition: str = "EI",
    minimize: bool = False,
) -> pd.DataFrame:
    """다음 SAR 라운드 합성 후보 batch_size개 추천.

    Args:
        df_known: 이미 측정된 화합물 (smiles + target_metric column 필수)
        df_candidates: 후보 (smiles만 필요)
        target_metric: 최적화할 컬럼 (예: "affinity_probability_binary")
        batch_size: 추천 수
        acquisition: "EI" | "UCB"
        minimize: True면 -metric으로 변환 (예: hERG, IC50)

    Returns:
        df_candidates 부분집합 (top batch_size, acquisition score 추가).
    """
    # Featurize known
    X_known, y_known = [], []
    for _, r in df_known.iterrows():
        f = featurize(r[smiles_col])
        if f is not None and pd.notna(r.get(target_metric)):
            X_known.append(f)
            y_known.append(r[target_metric])
    if not X_known:
        raise ValueError(f"X_known 0개 — {target_metric} 또는 SMILES 확인")
    X_known = np.array(X_known)
    y_known = np.array(y_known)
    if minimize:
        y_known = -y_known

    # Featurize candidates
    cand_idx, X_cand = [], []
    for i, r in df_candidates.iterrows():
        f = featurize(r[smiles_col])
        if f is not None:
            cand_idx.append(i)
            X_cand.append(f)
    X_cand = np.array(X_cand)

    # GP fit + predict
    mu, sigma = gp_regression(X_known, y_known, X_cand)
    best = float(y_known.max())

    if acquisition == "EI":
        score = expected_improvement(mu, sigma, best)
    elif acquisition == "UCB":
        score = upper_confidence_bound(mu, sigma)
    else:
        raise ValueError(f"unknown acquisition: {acquisition}")

    # Top batch
    top_idx_local = np.argsort(score)[-batch_size:][::-1]
    selected = []
    for i in top_idx_local:
        c_idx = cand_idx[i]
        row = df_candidates.loc[c_idx].to_dict()
        row["gp_mean"] = float(mu[i]) if not minimize else -float(mu[i])
        row["gp_std"] = float(sigma[i])
        row["acquisition_score"] = float(score[i])
        selected.append(row)
    return pd.DataFrame(selected)


def multi_fidelity_score(
    df: pd.DataFrame,
    boltz2_col: str = "affinity_probability_binary",
    abfe_col: str | None = None,
    in_vitro_col: str | None = None,
) -> pd.Series:
    """다중 fidelity 종합 score.

    weight: in_vitro (5) > ABFE (3) > Boltz-2 (1).
    in_vitro/ABFE 미측정이면 Boltz-2만.
    """
    score = df[boltz2_col].astype(float)
    weight = pd.Series(1.0, index=df.index)
    if abfe_col and abfe_col in df.columns:
        abfe = df[abfe_col]
        # ABFE는 ΔG (kcal/mol) — 작을수록 좋음. -ΔG/10으로 normalize
        score = score + 3.0 * (-abfe.fillna(0) / 10.0)
        weight = weight + 3.0 * abfe.notna()
    if in_vitro_col and in_vitro_col in df.columns:
        ic50 = df[in_vitro_col]
        # IC50 nM — log10 변환, 작을수록 좋음
        ic50_score = -np.log10(ic50.replace(0, 1e-6)) / 6  # nM → -log10/6 ~ pIC50/6
        score = score + 5.0 * ic50_score.fillna(0)
        weight = weight + 5.0 * ic50.notna()
    return (score / weight).round(4)
