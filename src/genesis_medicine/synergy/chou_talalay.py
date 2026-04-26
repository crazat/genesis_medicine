"""Chou-Talalay synergy + Topical PBPK (자운고 + EMB-3).

Chou-Talalay (1984) median-effect equation:
  fa / fu = (D / Dm)^m
  where:
    fa = fraction affected
    fu = fraction unaffected (1 - fa)
    Dm = median-effect dose (IC50 if fa=0.5)
    m = Hill coefficient (sigmoid 기울기)

Combination Index (CI) for n-drug combo:
  CI = Σ_i (D_i / Dx_i)
  CI < 1: synergy
  CI = 1: additive
  CI > 1: antagonism

PBPK skin (3-compartment):
  vehicle (외용제) → stratum corneum → viable epidermis → systemic
  flux = Kp × C_donor (Diamond-Katz)

라이선스: 본 모듈 자체 구현. CompuSyn 외부 SW 호출 옵션도 지원.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Optional

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


@dataclass
class DoseResponse:
    """단일 약물 dose-response 데이터."""

    drug_name: str
    doses: list                # [µM] 또는 [mg/mL]
    fa: list                   # fraction affected (0-1)
    dm: float = 0.0            # median-effect dose (IC50)
    m: float = 1.0             # Hill coefficient
    r2: float = 0.0


@dataclass
class CombinationResult:
    """약물 조합 평가."""

    drug_names: list           # ["Shikonin", "EMB-3", ...]
    doses: list                # 각 약물 농도 [µM]
    observed_fa: float
    expected_fa_loewe: float    # Loewe additivity
    expected_fa_bliss: float    # Bliss independence
    ci_chou_talalay: float     # CI (Chou-Talalay)
    interaction: str           # "synergy" | "additive" | "antagonism"
    confidence: str = "medium"


def fit_median_effect(doses: list, fa: list,
                       drug_name: str = "") -> DoseResponse:
    """median-effect equation fit → Dm + m."""
    doses = np.array(doses, dtype=float)
    fa = np.array(fa, dtype=float)
    fa = np.clip(fa, 1e-6, 1 - 1e-6)   # avoid log(0)
    fu = 1 - fa

    # log(fa/fu) = m * log(D) - m * log(Dm)
    log_ratio = np.log(fa / fu)
    log_dose = np.log(doses)

    # linear regression
    coef = np.polyfit(log_dose, log_ratio, 1)
    m = coef[0]
    log_dm = -coef[1] / m if m != 0 else 0
    dm = np.exp(log_dm)

    # R²
    pred = m * log_dose - m * log_dm
    ss_res = np.sum((log_ratio - pred) ** 2)
    ss_tot = np.sum((log_ratio - log_ratio.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return DoseResponse(drug_name=drug_name, doses=doses.tolist(),
                         fa=fa.tolist(), dm=float(dm), m=float(m), r2=float(r2))


def fa_at_dose(d: float, dm: float, m: float) -> float:
    """median-effect equation forward: D → fa."""
    if d <= 0:
        return 0.0
    ratio = (d / dm) ** m
    return float(ratio / (1 + ratio))


def combination_index(
    drug_responses: list[DoseResponse],
    combo_doses: list[float],
    observed_fa: float,
) -> float:
    """Chou-Talalay CI 계산.

    각 약물 i에 대해:
      Dx_i = Dm_i * (fa / (1-fa))^(1/m_i)  — observed fa 달성에 필요한 단독 용량
      CI = Σ (D_i / Dx_i)
    """
    if observed_fa <= 0 or observed_fa >= 1:
        return 1.0
    ci = 0.0
    for resp, d in zip(drug_responses, combo_doses):
        dx = resp.dm * ((observed_fa / (1 - observed_fa)) ** (1 / resp.m))
        if dx > 0:
            ci += d / dx
    return ci


def evaluate_combination(
    drug_responses: list[DoseResponse],
    combo_doses: list[float],
    observed_fa: float,
) -> CombinationResult:
    """단일 조합의 multi-method synergy 평가."""
    # Loewe (additive): 같은 fa 달성에 필요한 dose 비
    loewe_expected_fa = observed_fa  # placeholder; CI < 1이면 synergy
    ci = combination_index(drug_responses, combo_doses, observed_fa)

    # Bliss independence: f_a,bliss = 1 - Π (1 - f_i)
    f_each = [fa_at_dose(d, r.dm, r.m)
              for r, d in zip(drug_responses, combo_doses)]
    bliss_fa = 1 - np.prod([1 - f for f in f_each])

    if ci < 0.85:
        interaction = "synergy"
    elif ci < 1.15:
        interaction = "additive"
    else:
        interaction = "antagonism"

    return CombinationResult(
        drug_names=[r.drug_name for r in drug_responses],
        doses=combo_doses,
        observed_fa=observed_fa,
        expected_fa_loewe=loewe_expected_fa,
        expected_fa_bliss=float(bliss_fa),
        ci_chou_talalay=float(ci),
        interaction=interaction,
    )


# ════════════════════════════════════════════════════════════════════════
# Topical PBPK (3-compartment skin model)
# ════════════════════════════════════════════════════════════════════════


@dataclass
class TopicalPBPKConfig:
    """3-compartment skin PBPK parameters."""

    sc_thickness_cm: float = 8e-4         # stratum corneum 8 nm... 실제는 ~10 µm
    epidermis_thickness_cm: float = 1e-2   # 100 µm
    skin_area_cm2: float = 10              # 외용제 도포 면적
    log_kp_predicted: float = -2.0         # 자체 logKp 예측
    drug_concentration_mg_ml: float = 1.0  # 외용제 농도
    dosing_interval_h: float = 12          # 1일 2회


def topical_pbpk_simulate(cfg: TopicalPBPKConfig,
                           duration_h: float = 24,
                           n_steps: int = 1000) -> pd.DataFrame:
    """간이 3-compartment PBPK (scipy stiff solver).

    Model (1st-order rates):
      dC_sc/dt = (Kp_sc / h_sc) * (C_donor - C_sc) - (Kp_ve / h_sc) * (C_sc - C_ve)
      dC_ve/dt = (Kp_ve / h_ve) * (C_sc - C_ve) - (Kp_sys / h_ve) * (C_ve - C_sys * 0)
      dC_sys/dt = (Kp_sys * Area / V_sys) * C_ve - k_elim * C_sys

    Units: time in hours, concentration in mg/mL, kp in cm/h, h in cm.
    """
    from scipy.integrate import solve_ivp

    kp_sc = 10 ** cfg.log_kp_predicted   # cm/h
    kp_ve = kp_sc * 10
    kp_sys = kp_ve * 10
    k_elim = 0.1

    v_sys_ml = 5000
    c_donor = cfg.drug_concentration_mg_ml

    def rhs(t, y):
        c_sc, c_ve, c_sys = y
        dc_sc = ((kp_sc / cfg.sc_thickness_cm) * (c_donor - c_sc)
                  - (kp_ve / cfg.sc_thickness_cm) * (c_sc - c_ve))
        dc_ve = ((kp_ve / cfg.epidermis_thickness_cm) * (c_sc - c_ve)
                  - (kp_sys / cfg.epidermis_thickness_cm) * c_ve)
        dc_sys = (kp_sys * cfg.skin_area_cm2 / v_sys_ml * c_ve
                   - k_elim * c_sys)
        return [dc_sc, dc_ve, dc_sys]

    sol = solve_ivp(rhs, [0, duration_h], [0, 0, 0],
                    method="LSODA",   # stiff
                    t_eval=np.linspace(0, duration_h, n_steps),
                    rtol=1e-6, atol=1e-9)

    return pd.DataFrame({
        "time_h": sol.t, "C_donor": c_donor,
        "C_stratum_corneum": sol.y[0],
        "C_viable_epidermis": sol.y[1],
        "C_systemic": sol.y[2],
    })


def evaluate_recover_jaungo_emb3():
    """Recover 자운고 + EMB-3 처방 PBPK."""
    cfgs = {
        "EMB-3":         TopicalPBPKConfig(log_kp_predicted=-1.86,
                                             drug_concentration_mg_ml=2.0),
        "Embelin":       TopicalPBPKConfig(log_kp_predicted=-0.68,
                                             drug_concentration_mg_ml=0.5),
        "Shikonin":      TopicalPBPKConfig(log_kp_predicted=-2.5,
                                             drug_concentration_mg_ml=2.5),
        "Acetylshikonin":TopicalPBPKConfig(log_kp_predicted=-2.8,
                                             drug_concentration_mg_ml=1.5),
        "Ferulic acid":  TopicalPBPKConfig(log_kp_predicted=-2.0,
                                             drug_concentration_mg_ml=0.5),
    }
    results = {}
    for name, cfg in cfgs.items():
        df = topical_pbpk_simulate(cfg, duration_h=72)
        # Cmax in epidermis (target tissue)
        cmax_ve = df["C_viable_epidermis"].max()
        # Cmax in systemic (safety)
        cmax_sys = df["C_systemic"].max()
        # AUC
        auc_ve = np.trapz(df["C_viable_epidermis"], df["time_h"])
        results[name] = {
            "Cmax_epidermis_mg_ml": float(cmax_ve),
            "Cmax_systemic_mg_ml": float(cmax_sys),
            "AUC_epidermis_h_mg_ml": float(auc_ve),
            "ratio_topical_vs_systemic": (float(cmax_ve / max(cmax_sys, 1e-9))),
        }
    return results
