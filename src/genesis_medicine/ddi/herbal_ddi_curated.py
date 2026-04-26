"""Korean herbal compound × Western drug curated DDI table.

Built from PharmGKB + KIDS-KAERS + 의약품안전나라 + literature.
Extends DDInter 2.0 with herbal-specific interactions.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import List

from .ddinter_adapter import KNOWN_DDI, DDIPair


class HerbalDDICurated:
    """Convenience wrapper exporting curated DDI table as DataFrame."""

    @staticmethod
    def to_dataframe() -> pd.DataFrame:
        rows = []
        for p in KNOWN_DDI:
            rows.append({
                "drug_a": p.drug_a,
                "drug_b": p.drug_b,
                "severity": p.severity,
                "mechanism": p.mechanism,
                "cyp_or_transporter": p.cyp_involved or "",
                "description": p.description,
            })
        return pd.DataFrame(rows)

    @staticmethod
    def export_csv(out_path: Path) -> Path:
        df = HerbalDDICurated.to_dataframe()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        return out_path

    @staticmethod
    def filter_recover_relevant() -> pd.DataFrame:
        """Filter to interactions Recover patients are likely to encounter."""
        df = HerbalDDICurated.to_dataframe()
        recover_drugs = {"warfarin", "statins", "isotretinoin", "tacrolimus",
                         "cyclosporine", "anticoagulants", "rosuvastatin",
                         "methotrexate"}
        mask = df["drug_b"].str.lower().str.replace("_", "_").apply(
            lambda x: any(rd in x for rd in recover_drugs))
        return df[mask].sort_values("severity")
