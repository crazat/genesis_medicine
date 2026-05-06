"""구조 예측 앙상블 합의 점수 (B5 — ultrathink 2026-04-25).

Protenix-v2 + OpenFold3 + Boltz-2 다중 어댑터 합의로 신뢰도 향상.

알고리즘
--------
1. 각 어댑터로 N개 샘플 생성
2. 모든 샘플 간 RMSD 매트릭스
3. 클러스터별 대표 + 합의 점수 (per-residue pLDDT 평균 + 클러스터 일치도)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from loguru import logger
from pydantic import BaseModel, Field

from .base import (
    StructurePredictionRequest,
    StructurePredictionResult,
    StructurePredictor,
)


@dataclass
class ConsensusEntry:
    cif_path: Path
    engine: str
    plddt_mean: float = 0.0
    consensus_score: float = 0.0
    cluster_id: int = -1
    rmsd_to_consensus: float = 0.0


class ConsensusRequest(BaseModel):
    base_request: StructurePredictionRequest
    engines: list[str] = Field(default_factory=lambda: ["boltz2", "protenix", "openfold3"])
    samples_per_engine: int = 3


class ConsensusResult(BaseModel):
    representative: ConsensusEntry
    all_entries: list[ConsensusEntry]
    cluster_assignment: list[int] = Field(default_factory=list)
    consensus_plddt: float = 0.0
    rmsd_dispersion: float = 0.0
    metadata: dict = Field(default_factory=dict)


class ConsensusPredictor:
    """다중 구조 예측 어댑터 합의 — Protocol을 충족하지는 않음 (다중 출력)."""

    def __init__(self, predictors: dict[str, StructurePredictor]) -> None:
        self.predictors = predictors

    def predict_consensus(self, req: ConsensusRequest) -> ConsensusResult:
        all_entries: list[ConsensusEntry] = []
        for engine_name in req.engines:
            if engine_name not in self.predictors:
                logger.warning("합의에 요청된 엔진 '{}' 미등록 — 건너뜀", engine_name)
                continue
            predictor = self.predictors[engine_name]
            sub_req = req.base_request.model_copy(
                update={"num_samples": req.samples_per_engine}
            )
            try:
                result = predictor.predict(sub_req)
            except Exception as e:
                logger.warning("{} 실패: {}", engine_name, e)
                continue
            all_entries.append(ConsensusEntry(
                cif_path=result.cif_path,
                engine=engine_name,
                plddt_mean=result.plddt_mean,
            ))

        if not all_entries:
            raise RuntimeError("합의 어댑터 모두 실패")

        # 클러스터링 — RMSD 기반
        rmsd_matrix = self._pairwise_rmsd([e.cif_path for e in all_entries])
        cluster_ids = self._cluster_by_rmsd(rmsd_matrix, threshold=2.0)
        for entry, cid in zip(all_entries, cluster_ids):
            entry.cluster_id = cid

        # 가장 큰 클러스터의 대표 — pLDDT 최댓값
        from collections import Counter
        biggest_cluster = Counter(cluster_ids).most_common(1)[0][0]
        cluster_members = [e for e in all_entries if e.cluster_id == biggest_cluster]
        representative = max(cluster_members, key=lambda e: e.plddt_mean)

        # 합의 점수 — 대표 클러스터 비율 × 평균 pLDDT
        consensus_ratio = len(cluster_members) / len(all_entries)
        consensus_plddt = float(np.mean([e.plddt_mean for e in cluster_members]))
        for e in all_entries:
            if e.cluster_id == biggest_cluster:
                e.consensus_score = consensus_ratio * e.plddt_mean

        return ConsensusResult(
            representative=representative,
            all_entries=all_entries,
            cluster_assignment=cluster_ids,
            consensus_plddt=consensus_plddt,
            rmsd_dispersion=float(np.mean(rmsd_matrix)),
            metadata={
                "engines_used": [e.engine for e in all_entries],
                "consensus_ratio": consensus_ratio,
                "n_clusters": len(set(cluster_ids)),
            },
        )

    def _pairwise_rmsd(
        self,
        cif_paths: list[Path],
        ligand_weight: float = 0.4,
    ) -> np.ndarray:
        """Compute pairwise distance combining backbone CA RMSD and ligand
        heavy-atom RMSD.

        For pose-quality clustering, ligand heavy atoms must contribute —
        otherwise two predictions that agree on the protein backbone but
        place the ligand in different pockets get clustered together.

        distance = (1 - ligand_weight) * CA_RMSD + ligand_weight * LIG_RMSD

        If a structure has no ligand heavy atoms (apo), the ligand term is
        skipped and distance = CA_RMSD. ``ligand_weight`` is in [0, 1].
        """
        n = len(cif_paths)
        matrix = np.zeros((n, n))
        try:
            from Bio.PDB import MMCIFParser, Superimposer
        except ImportError:
            logger.debug("Biopython 미설치 — RMSD 0 반환")
            return matrix

        parser = MMCIFParser(QUIET=True)
        ca_atoms: list[list] = []
        lig_atoms: list[list] = []
        for p in cif_paths:
            try:
                s = parser.get_structure("s", str(p))
                ca = [a for a in s.get_atoms() if a.get_name() == "CA"]
                # Ligand heavy atoms = HETATM whose residue name is not a
                # standard amino acid / nucleotide / common ion. Approximate
                # via Biopython hetflag and exclude waters + lone metal ions.
                lig = []
                for a in s.get_atoms():
                    res = a.get_parent()
                    hetflag = res.get_id()[0]
                    if hetflag.strip() and hetflag != "W":
                        # Exclude pure metal-ion entries (single-atom CCDs).
                        resname = res.get_resname().strip()
                        if resname in {"ZN", "CU", "FE", "CA", "MG", "MN",
                                       "NI", "CO", "K", "NA", "HOH"}:
                            continue
                        if a.element != "H":
                            lig.append(a)
                ca_atoms.append(ca)
                lig_atoms.append(lig)
            except Exception as e:
                logger.debug("CIF 파싱 실패 {}: {}", p, e)
                ca_atoms.append([])
                lig_atoms.append([])

        for i in range(n):
            for j in range(i + 1, n):
                ca_i, ca_j = ca_atoms[i], ca_atoms[j]
                if not ca_i or not ca_j:
                    matrix[i, j] = matrix[j, i] = 999.0
                    continue
                k = min(len(ca_i), len(ca_j))
                ca_rms = 999.0
                try:
                    sup = Superimposer()
                    sup.set_atoms(ca_i[:k], ca_j[:k])
                    ca_rms = float(sup.rms)
                except Exception:
                    pass

                lig_i, lig_j = lig_atoms[i], lig_atoms[j]
                w = float(ligand_weight)
                if lig_i and lig_j:
                    m = min(len(lig_i), len(lig_j))
                    try:
                        # Apply the same superposition (already fitted on CA)
                        # to ligand atoms by recomputing on CA frame:
                        sup = Superimposer()
                        sup.set_atoms(ca_i[:k], ca_j[:k])
                        rot, tran = sup.rotran
                        # Transform ligand_j onto i's frame
                        diffs = []
                        for a_i, a_j in zip(lig_i[:m], lig_j[:m]):
                            xj = a_j.coord @ rot + tran
                            diffs.append(((a_i.coord - xj) ** 2).sum())
                        if diffs:
                            lig_rms = float(np.sqrt(sum(diffs) / len(diffs)))
                        else:
                            lig_rms = 999.0
                    except Exception:
                        lig_rms = 999.0
                    dist = (1.0 - w) * ca_rms + w * lig_rms
                else:
                    dist = ca_rms

                matrix[i, j] = matrix[j, i] = dist
        return matrix

    def _cluster_by_rmsd(self, matrix: np.ndarray, threshold: float = 2.0) -> list[int]:
        n = matrix.shape[0]
        clusters: list[int] = [-1] * n
        next_id = 0
        for i in range(n):
            if clusters[i] >= 0:
                continue
            clusters[i] = next_id
            for j in range(i + 1, n):
                if clusters[j] < 0 and matrix[i, j] < threshold:
                    clusters[j] = next_id
            next_id += 1
        return clusters
