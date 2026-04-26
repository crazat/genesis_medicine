"""Dealbreaker safety panel — must check before any topical claim.

7 classes that cause MFDS / KFDA / FDA rejection if hit at p > 0.5:
    hERG / CYP3A4 / AR / GR / ER / PXR / AhR

Built on top of ADMET-AI v2 (already integrated) + SwissTarget polypharmacology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DealbreakerResult:
    compound: str
    smiles: str
    flags: Dict[str, float] = field(default_factory=dict)
    n_dealbreakers: int = 0
    severity: str = "low"     # "low" | "moderate" | "high" | "critical"
    method: str = "dealbreaker_panel_v1"
    note: str = ""


DEALBREAKER_THRESHOLDS = {
    "hERG": 0.5,
    "CYP3A4_inhibition": 0.5,
    "CYP3A4_substrate": 0.5,
    "AR_offtarget": 0.5,        # for non-AGA compounds
    "GR_agonist": 0.4,           # cosmetic GR = illegal in K-cosmetics
    "ER_agonist": 0.4,           # endocrine disruption auto-recall
    "PXR_activation": 0.5,
    "AhR_activation": 0.5,
}


class DealbreakerPanelAdapter:
    engine_name = "dealbreaker_panel_v1"

    def __init__(self, *, cache_dir: Path = Path(".cache/dealbreaker")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def screen(self, *, compound: str, smiles: str,
                admet_predictions: Optional[Dict[str, float]] = None,
                polypharmacology_hits: Optional[List] = None,
                target_disease: str = "") -> DealbreakerResult:
        """Aggregate ADMET-AI + polypharmacology hits → flag dealbreakers."""
        flags = {}
        if admet_predictions:
            for key, threshold in DEALBREAKER_THRESHOLDS.items():
                # ADMET-AI uses lowercase keys like 'hERG', 'CYP3A4_Veith'
                for k_admet, v_admet in admet_predictions.items():
                    if any(part.lower() in k_admet.lower()
                           for part in key.split("_")):
                        if v_admet > threshold:
                            flags[key] = float(v_admet)
                            break
        if polypharmacology_hits:
            for hit in polypharmacology_hits:
                tn = (hit.target_name if hasattr(hit, 'target_name')
                      else str(hit)).lower()
                tp = (hit.probability if hasattr(hit, 'probability') else 0.0)
                # AR is dealbreaker only if NOT the disease target
                is_aga = "alopecia" in target_disease.lower()
                if "ar " in f" {tn} " or tn.startswith("ar"):
                    if not is_aga and tp > DEALBREAKER_THRESHOLDS["AR_offtarget"]:
                        flags["AR_offtarget"] = float(tp)
                for cls in ["GR", "ER", "PXR", "AhR", "CYP3A4", "hERG"]:
                    if cls.lower() in tn and tp > DEALBREAKER_THRESHOLDS.get(
                            f"{cls}_agonist", DEALBREAKER_THRESHOLDS.get(
                                f"{cls}_activation", 0.5)):
                        flags.setdefault(f"{cls}_class", float(tp))

        n = len(flags)
        if n == 0:
            severity = "low"
        elif n == 1:
            severity = "moderate"
        elif n <= 3:
            severity = "high"
        else:
            severity = "critical"

        return DealbreakerResult(
            compound=compound, smiles=smiles, flags=flags,
            n_dealbreakers=n, severity=severity,
            note=(f"{n} dealbreaker(s) flagged. Severity: {severity}. "
                   "Critical = block submission; high = formulation dose limit; "
                   "moderate = explicit disclosure in preprint."),
        )
