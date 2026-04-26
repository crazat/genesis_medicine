"""KCID (Korean Cosmetic Ingredient Dictionary) + KFDA gating adapter.

21,130 entries (Sept 2025). Required for Recover product label legality —
only KCID-listed ingredient names are usable on Korean cosmetic products.

License: kcia.or.kr free; programmatic via 공공데이터포털 (data.go.kr 15020628).
URL    : https://kcia.or.kr/cid/main/

Why this matters:
    Hard regulatory gate before any Recover formulation goes to consumer.
    Without this, lead-compound triage saves 6-12 months downstream rework.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class IngredientStatus:
    name_input: str
    inci_name: Optional[str] = None
    kcid_listed: bool = False
    kfda_status: str = "unknown"    # "approved" | "restricted" | "banned" | "unknown"
    eu_cosing_status: str = "unknown"
    eu_annex_restriction: Optional[str] = None
    note: str = ""


# Curated subset for our 124 compounds + common Korean cosmetic ingredients
KCID_LITERATURE = {
    # Korean herbs (KCID-listed via 천연유래 channel)
    "embelin": IngredientStatus(
        name_input="embelin", inci_name="Embelia Ribes Fruit Extract",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved",
        note="Available as Embelia Ribes extract; isolated embelin = active raw material"),
    "asiaticoside": IngredientStatus(
        name_input="asiaticoside", inci_name="Asiaticoside",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved",
        note="Established cosmetic active; no concentration limit in standard products"),
    "madecassoside": IngredientStatus(
        name_input="madecassoside", inci_name="Madecassoside",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved",
        note="Centella active; widely used in K-beauty 진정/재생 products"),
    "EGCG": IngredientStatus(
        name_input="EGCG", inci_name="Epigallocatechin Gallate",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved",
        note="Camellia Sinensis Leaf Extract is the typical INCI source"),
    "berberine": IngredientStatus(
        name_input="berberine", inci_name="Berberine HCl",
        kcid_listed=True, kfda_status="restricted",
        eu_cosing_status="approved",
        note="KFDA: cosmetic dose-limited due to staining + hERG flag (our 0.977)"),
    "baicalein": IngredientStatus(
        name_input="baicalein", inci_name="Scutellaria Baicalensis Root Extract",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved", note="Standard 황금 extract"),
    "shikonin": IngredientStatus(
        name_input="shikonin", inci_name="Lithospermum Erythrorhizon Root Extract",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved", note="자초 extract — well-established"),
    "curcumin": IngredientStatus(
        name_input="curcumin", inci_name="Curcuma Longa (Turmeric) Root Extract",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved", note=""),
    "licochalcone_a": IngredientStatus(
        name_input="licochalcone A", inci_name="Glycyrrhiza Inflata Root Extract",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved", note="감초 extract"),
    "glabridin": IngredientStatus(
        name_input="glabridin", inci_name="Glabridin",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="approved", note="Glycyrrhiza glabra; 미백 기능성 가능"),
    "EMB-3": IngredientStatus(
        name_input="EMB-3", inci_name=None,
        kcid_listed=False, kfda_status="not_listed",
        eu_cosing_status="not_listed",
        note="NEW chemical entity (in silico-derived). Requires Cosmetic "
             "Ingredient Pre-Notification (성분명 공시) under KFDA Article 8 "
             "before product launch. Estimated 6-12 month process."),
    "tretinoin": IngredientStatus(
        name_input="tretinoin", inci_name="Tretinoin",
        kcid_listed=False, kfda_status="banned_in_cosmetics",
        eu_cosing_status="banned_in_cosmetics",
        eu_annex_restriction="Annex II",
        note="PRESCRIPTION ONLY in cosmetic context; Recover would need "
             "의약품 license, not 화장품"),
    "hydroquinone": IngredientStatus(
        name_input="hydroquinone", inci_name="Hydroquinone",
        kcid_listed=False, kfda_status="banned_in_cosmetics",
        eu_cosing_status="banned_in_cosmetics",
        eu_annex_restriction="Annex II 1339",
        note="PRESCRIPTION ONLY since 2010; cosmetic use prohibited"),
    "kojic_acid": IngredientStatus(
        name_input="kojic acid", inci_name="Kojic Acid",
        kcid_listed=True, kfda_status="approved",
        eu_cosing_status="restricted",
        eu_annex_restriction="Annex III max 1.0%",
        note="EU concentration limit; KR allows in 미백 기능성 products"),
}


class KCIDAdapter:
    engine_name = "kcid_v1_2025"

    def __init__(self, *, cache_dir: Path = Path(".cache/kcid")):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def lookup(self, name: str) -> IngredientStatus:
        key = name.lower().replace("-", "_").replace(" ", "_")
        for k, status in KCID_LITERATURE.items():
            if k.lower().replace("-", "_") == key:
                return status
        return IngredientStatus(
            name_input=name, kcid_listed=False, kfda_status="unknown",
            eu_cosing_status="unknown",
            note=("Not in pre-computed KCID subset. Search "
                   "https://kcia.or.kr/cid/main/ for live lookup."),
        )

    def is_recover_safe(self, name: str) -> bool:
        s = self.lookup(name)
        return s.kcid_listed and s.kfda_status not in ("banned_in_cosmetics",
                                                          "prescription_only")
