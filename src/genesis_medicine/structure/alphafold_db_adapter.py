"""AlphaFold Protein Structure Database (EBI) 어댑터.

신규 추론 전에 항상 먼저 조회해서 **이미 있는 구조는 재사용**한다.
214M UniProt 구조 커버.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import StructurePredictionRequest, StructurePredictionResult


class AlphaFoldDBAdapter:
    """AFDB API 래퍼. 실제로는 '예측'이 아니라 '조회'지만 StructurePredictor 인터페이스와 호환."""

    engine_name = "alphafold_db"
    engine_version = "v4-2024"
    _BASE = "https://alphafold.ebi.ac.uk/api/prediction"

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def supports_ligands(self) -> bool:
        return False

    def supports_affinity(self) -> bool:
        return False

    def lookup(self, uniprot: str) -> StructurePredictionResult | None:
        """UniProt 액세션으로 AFDB 조회. 없으면 None."""
        cif_path = self.cache_dir / f"{uniprot}.cif"
        meta_path = self.cache_dir / f"{uniprot}.json"

        if cif_path.exists() and meta_path.exists():
            meta = json.loads(meta_path.read_text())
            logger.info(f"AFDB cache hit: {uniprot}")
            return StructurePredictionResult(
                cif_path=cif_path,
                plddt_mean=meta["plddt_mean"],
                plddt_per_residue=meta.get("plddt_per_residue", []),
                confidence_json=meta_path,
                engine=self.engine_name,
                engine_version=self.engine_version,
                wall_seconds=0.0,
            )

        meta = self._fetch_meta(uniprot)
        if meta is None:
            return None

        cif_url = meta[0].get("cifUrl") or meta[0].get("pdbUrl")
        if not cif_url:
            logger.warning(f"AFDB: no structure URL for {uniprot}")
            return None

        self._download(cif_url, cif_path)
        plddt_mean = float(meta[0].get("confidenceAvgLocalScore", 0.0))
        meta_path.write_text(
            json.dumps({"plddt_mean": plddt_mean, "raw": meta[0]}, default=str)
        )

        return StructurePredictionResult(
            cif_path=cif_path,
            plddt_mean=plddt_mean,
            plddt_per_residue=[],
            confidence_json=meta_path,
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=0.0,
        )

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        raise NotImplementedError(
            "AFDB는 예측이 아닌 조회용. `lookup(uniprot)`을 사용."
        )

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=30))
    def _fetch_meta(self, uniprot: str) -> list[dict] | None:
        url = f"{self._BASE}/{uniprot}"
        r = requests.get(url, timeout=30)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _download(self, url: str, dest: Path) -> None:
        start = time.time()
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        dest.write_bytes(r.content)
        logger.info(f"AFDB downloaded {url} in {time.time() - start:.1f}s")
