"""NPASS 2026 update 어댑터 (NAR 2026).

References:
- NPASS 2026 NAR: https://academic.oup.com/nar/article/54/D1/D1519/8324957
- 204k natural products + **+87,507 quantitative composition records
  + 34,975 toxicity + 9,713 ADME records** (vs prior ~33k ADME)

핵심 가치:
- 외용 logKp ground truth 직격 (자체 LGBM 헤드 학습 데이터)
- 천연물 quantitative ADME-Tox — 우리 한약 SMILES 주석 강화
- COCONUT 2.0 + LOTUS 보강

라이선스: NPASS는 free for academic & commercial. Attribution 필수.
URL: https://bidd.group/NPASS/
"""

from __future__ import annotations

import csv
import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger


@dataclass
class NPASSCompound:
    np_id: str
    smiles: Optional[str]
    name: str
    family: Optional[str]
    natural_source: List[str] = field(default_factory=list)
    quantitative_composition: List[Dict[str, float]] = field(default_factory=list)
    toxicity_records: List[Dict[str, str]] = field(default_factory=list)
    adme_records: List[Dict[str, str]] = field(default_factory=list)
    log_kp_observed: Optional[float] = None         # if reported
    skin_permeability_class: Optional[str] = None    # high/medium/low/unknown


class NPASS2026:
    """NPASS 2026 dump 로더 + skin-relevant compound query."""

    engine_name = "npass_2026"

    DEFAULT_DATA = Path(".cache/npass2026")

    def __init__(self, *, data_dir: Path = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else self.DEFAULT_DATA
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._compounds: Optional[List[NPASSCompound]] = None
        self._index_smiles: Dict[str, NPASSCompound] = {}

    @property
    def is_loaded(self) -> bool:
        return self._compounds is not None and len(self._compounds) > 0

    def load(
        self,
        *,
        smiles_file: Optional[Path] = None,
        adme_file: Optional[Path] = None,
        toxicity_file: Optional[Path] = None,
    ) -> bool:
        """NPASS dump TSV/CSV 로드. 파일 미발견 시 False."""
        smiles_file = smiles_file or self.data_dir / "compounds_smiles.tsv"
        adme_file = adme_file or self.data_dir / "adme.tsv"
        toxicity_file = toxicity_file or self.data_dir / "toxicity.tsv"

        if not smiles_file.exists():
            logger.warning("NPASS smiles 미발견: {}", smiles_file)
            return False

        compounds: Dict[str, NPASSCompound] = {}
        with open(smiles_file) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                np_id = row.get("np_id") or row.get("Compound_ID")
                if not np_id:
                    continue
                compounds[np_id] = NPASSCompound(
                    np_id=np_id,
                    smiles=row.get("smiles") or row.get("SMILES"),
                    name=row.get("name") or row.get("Compound_Name", ""),
                    family=row.get("class_id") or row.get("class"),
                )

        if adme_file.exists():
            with open(adme_file) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    np_id = row.get("np_id") or row.get("Compound_ID")
                    if np_id and np_id in compounds:
                        compounds[np_id].adme_records.append(dict(row))
                        # Skin permeability heuristic
                        kp = row.get("logKp_skin") or row.get("log_kp")
                        if kp:
                            try:
                                compounds[np_id].log_kp_observed = float(kp)
                                if compounds[np_id].log_kp_observed > -3.5:
                                    compounds[np_id].skin_permeability_class = "high"
                                elif compounds[np_id].log_kp_observed > -5.5:
                                    compounds[np_id].skin_permeability_class = "medium"
                                else:
                                    compounds[np_id].skin_permeability_class = "low"
                            except ValueError:
                                pass

        if toxicity_file.exists():
            with open(toxicity_file) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    np_id = row.get("np_id") or row.get("Compound_ID")
                    if np_id and np_id in compounds:
                        compounds[np_id].toxicity_records.append(dict(row))

        self._compounds = list(compounds.values())
        for c in self._compounds:
            if c.smiles:
                self._index_smiles[c.smiles] = c
        logger.info("Loaded {} NPASS 2026 compounds", len(self._compounds))
        return True

    def query_skin_permeable(self, max_n: int = 1000) -> List[NPASSCompound]:
        """logKp 측정값이 있는 (외용제 후보) 천연물 반환."""
        if not self.is_loaded:
            self.load()
        return sorted(
            [c for c in (self._compounds or []) if c.log_kp_observed is not None],
            key=lambda c: -(c.log_kp_observed or -10.0),
        )[:max_n]

    def lookup_by_smiles(self, smiles: str) -> Optional[NPASSCompound]:
        if not self.is_loaded:
            self.load()
        return self._index_smiles.get(smiles)

    def export_logkp_training_set(self, output: Path) -> int:
        """자체 LGBM 헤드 학습용 (smiles, logKp) TSV 출력."""
        if not self.is_loaded:
            self.load()
        n = 0
        with open(output, "w") as f:
            f.write("smiles\tlog_kp\n")
            for c in self._compounds or []:
                if c.smiles and c.log_kp_observed is not None:
                    f.write(f"{c.smiles}\t{c.log_kp_observed}\n")
                    n += 1
        logger.info("Exported {} (smiles, logKp) training pairs to {}", n, output)
        return n
