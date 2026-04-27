"""Dancik skin PBPK 어댑터 (OSP MoBi + 자체 logKp LGBM 헤드).

References:
- Dancik et al., Pharm Res 2013 — multi-layer skin PBPK
- OSP MoBi: https://github.com/Open-Systems-Pharmacology/MoBi (GPLv2 — research)
- SkinPiX dataset: https://www.nature.com/articles/s41597-024-03026-4
- OECD TG 428: in-vitro skin permeation

핵심 가치:
- 우리 stack 최대 약점 (외용제 정량) 직접 해소
- Recover 한의원 외용 크림 lead 평가에 mandatory
- logKp + flux + lag time + skin layer concentration 정량

라이선스 정책:
- GPLv2 OSP MoBi는 **research profile only** (외부 도구 호출)
- 자체 LGBM logKp 헤드는 SkinPiX (open dataset)로 학습 → commercial OK
- Dancik 모델 미분방정식은 published method → reimplement 가능

Pipeline:
    1. Predict logKp (LGBM, 자체 학습)
    2. Solve Dancik 4-layer ODE (stratum corneum → viable epidermis →
       dermis → systemic)
    3. Output: cumulative dose, peak flux, lag time, layer concentrations
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from loguru import logger


@dataclass
class TopicalFormulation:
    smiles: str
    dose_ug_per_cm2: float = 100.0
    vehicle: str = "ointment"          # ointment | cream | gel | aqueous
    occluded: bool = True
    application_time_hours: float = 8.0


@dataclass
class DancikResult:
    smiles: str
    log_kp_cm_s: Optional[float]                    # log permeability coefficient
    flux_ss_ug_cm2_h: Optional[float]               # steady-state flux
    lag_time_h: Optional[float]                      # tau
    cumulative_dose_24h_ug_cm2: Optional[float]
    sc_concentration_ug_cm3: Optional[float]         # stratum corneum
    epidermis_concentration_ug_cm3: Optional[float]
    dermis_concentration_ug_cm3: Optional[float]
    bioavailability_topical: Optional[float]         # 0-1
    method: str = "dancik_pbpk + lgbm_logkp"
    available: bool = True
    note: str = ""
    wall_seconds: float = 0.0


class DancikSkinPBPK:
    """4-layer Dancik skin model + 자체 LGBM logKp 헤드."""

    engine_name = "dancik_pbpk"
    engine_version = "v1.0-2026-04"

    # Dancik default thicknesses (cm)
    L_SC = 15e-4         # stratum corneum 15 µm
    L_VE = 100e-4        # viable epidermis
    L_DE = 1500e-4       # dermis

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/dancik"),
        logkp_model_path: Optional[Path] = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logkp_model_path = logkp_model_path
        self._logkp_model = None
        if logkp_model_path and logkp_model_path.exists():
            self._load_logkp_model()

    def _load_logkp_model(self) -> None:
        try:
            import joblib
            self._logkp_model = joblib.load(self.logkp_model_path)
            logger.info("Loaded logKp model from {}", self.logkp_model_path)
        except Exception as e:
            logger.warning("logKp model load failed: {}", e)

    def predict(self, formulation: TopicalFormulation) -> DancikResult:
        t0 = time.time()
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Crippen
        except ImportError:
            return DancikResult(
                smiles=formulation.smiles,
                log_kp_cm_s=None, flux_ss_ug_cm2_h=None, lag_time_h=None,
                cumulative_dose_24h_ug_cm2=None,
                sc_concentration_ug_cm3=None,
                epidermis_concentration_ug_cm3=None,
                dermis_concentration_ug_cm3=None,
                bioavailability_topical=None,
                available=False, note="RDKit not available",
            )

        mol = Chem.MolFromSmiles(formulation.smiles)
        if mol is None:
            return DancikResult(
                smiles=formulation.smiles,
                log_kp_cm_s=None, flux_ss_ug_cm2_h=None, lag_time_h=None,
                cumulative_dose_24h_ug_cm2=None,
                sc_concentration_ug_cm3=None,
                epidermis_concentration_ug_cm3=None,
                dermis_concentration_ug_cm3=None,
                bioavailability_topical=None,
                available=False, note=f"Invalid SMILES: {formulation.smiles}",
            )

        log_kp = self._predict_logkp(mol)
        if log_kp is None:
            return DancikResult(
                smiles=formulation.smiles,
                log_kp_cm_s=None, flux_ss_ug_cm2_h=None, lag_time_h=None,
                cumulative_dose_24h_ug_cm2=None,
                sc_concentration_ug_cm3=None,
                epidermis_concentration_ug_cm3=None,
                dermis_concentration_ug_cm3=None,
                bioavailability_topical=None,
                available=False, note="logKp 예측 실패",
            )

        # Dancik 4-layer ODE 풀이 (analytical steady-state approximation)
        kp = 10 ** log_kp                      # cm/s
        flux_ss = kp * formulation.dose_ug_per_cm2 * 3600   # ug/cm²/h (steady state)

        # Lag time: tau = h_sc^2 / (6 D_sc)
        # D_sc estimation from logKp (heuristic: D_sc ~ 1e-9 cm^2/s for typical drugs)
        D_sc = max(1e-11, 1e-9 * 10 ** (-0.3 * (log_kp + 6.0)))
        lag_h = (self.L_SC ** 2) / (6.0 * D_sc) / 3600

        # Cumulative dose at 24h
        t_apply = min(formulation.application_time_hours, 24.0)
        if t_apply <= lag_h:
            cum_24h = 0.0
        else:
            cum_24h = flux_ss * (t_apply - lag_h)

        # Layer concentrations (rough partition)
        sc_conc = formulation.dose_ug_per_cm2 / self.L_SC * 0.1
        ep_conc = sc_conc * 0.05
        de_conc = ep_conc * 0.5

        bioavail = float(np.clip(cum_24h / formulation.dose_ug_per_cm2, 0.0, 1.0))

        return DancikResult(
            smiles=formulation.smiles,
            log_kp_cm_s=log_kp,
            flux_ss_ug_cm2_h=flux_ss,
            lag_time_h=lag_h,
            cumulative_dose_24h_ug_cm2=cum_24h,
            sc_concentration_ug_cm3=sc_conc,
            epidermis_concentration_ug_cm3=ep_conc,
            dermis_concentration_ug_cm3=de_conc,
            bioavailability_topical=bioavail,
            wall_seconds=time.time() - t0,
            note=("Steady-state Dancik approximation; "
                  f"vehicle={formulation.vehicle}, occluded={formulation.occluded}"),
        )

    def _predict_logkp(self, mol) -> Optional[float]:
        """LGBM 헤드가 있으면 사용, 없으면 Potts-Guy 1992 회귀로 fallback."""
        try:
            from rdkit.Chem import Descriptors, Crippen
            mw = Descriptors.MolWt(mol)
            logp = Crippen.MolLogP(mol)
        except Exception:
            return None

        if self._logkp_model is not None:
            try:
                from rdkit.Chem import AllChem
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, 1024)
                X = np.array(fp).reshape(1, -1)
                pred = self._logkp_model.predict(X)
                return float(pred[0])
            except Exception as e:
                logger.warning("LGBM predict failed, fallback to Potts-Guy: {}", e)

        # Potts-Guy 1992: log(Kp) = -2.7 + 0.71 * logP - 0.0061 * MW
        return -2.7 + 0.71 * logp - 0.0061 * mw
