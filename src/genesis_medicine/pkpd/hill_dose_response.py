"""Hill / sigmoidal dose-response fitting (scipy, BSD-3, commercial-OK).

Standard 4-parameter log-logistic fitting with EDx estimation.
Connects in vitro IC50 → in vivo ED50 species scaling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np


def hill_eq(x: np.ndarray, bottom: float, top: float,
             ic50: float, hill_slope: float) -> np.ndarray:
    """4-parameter log-logistic Hill equation."""
    return bottom + (top - bottom) / (1 + (ic50 / x) ** hill_slope)


@dataclass
class HillFitResult:
    compound: str
    target: str
    bottom: Optional[float]
    top: Optional[float]
    ic50_uM: Optional[float]
    hill_slope: Optional[float]
    r_squared: Optional[float]
    ed50_estimated_uM: Optional[float]
    n_points: int = 0
    method: str = "hill_4parameter"
    note: str = ""


class HillDoseResponseAdapter:
    engine_name = "hill_4parameter"

    def __init__(self, *, cache_dir: Path = Path(".cache/hill_fit")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fit(self, *, compound: str, target: str,
            dose_uM: List[float], response_pct: List[float]) -> HillFitResult:
        try:
            from scipy.optimize import curve_fit
        except ImportError:
            return HillFitResult(
                compound=compound, target=target,
                bottom=None, top=None, ic50_uM=None,
                hill_slope=None, r_squared=None, ed50_estimated_uM=None,
                n_points=len(dose_uM), note="scipy not installed",
            )
        if len(dose_uM) < 4:
            return HillFitResult(
                compound=compound, target=target,
                bottom=None, top=None, ic50_uM=None,
                hill_slope=None, r_squared=None, ed50_estimated_uM=None,
                n_points=len(dose_uM),
                note="Need >= 4 dose points for Hill fit.",
            )
        x = np.asarray(dose_uM, dtype=float)
        y = np.asarray(response_pct, dtype=float)
        try:
            p0 = [min(y), max(y), float(np.median(x)), 1.0]
            popt, _ = curve_fit(hill_eq, x, y, p0=p0, maxfev=10_000)
            y_pred = hill_eq(x, *popt)
            ss_res = float(np.sum((y - y_pred) ** 2))
            ss_tot = float(np.sum((y - np.mean(y)) ** 2))
            r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
            ic50 = float(popt[2])
            ed50 = ic50 / 0.7    # rough species scaling factor
            return HillFitResult(
                compound=compound, target=target,
                bottom=float(popt[0]), top=float(popt[1]),
                ic50_uM=ic50, hill_slope=float(popt[3]),
                r_squared=r2, ed50_estimated_uM=ed50,
                n_points=len(dose_uM),
                note="4-parameter Hill fit converged.",
            )
        except Exception as e:
            return HillFitResult(
                compound=compound, target=target,
                bottom=None, top=None, ic50_uM=None,
                hill_slope=None, r_squared=None, ed50_estimated_uM=None,
                n_points=len(dose_uM), note=f"fit error: {str(e)[:120]}",
            )
