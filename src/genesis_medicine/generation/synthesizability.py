"""합성 가능성 평가 모듈.

SATURN (MIT, Mamba, PubChem 사전학습) + AiZynthFinder (MIT, AstraZeneca) 통합.
생성 분자의 합성 가능성을 즉시 평가하고, 합성 경로를 자동 계획.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger


@dataclass
class SynthesisRoute:
    """역합성 경로."""

    smiles: str
    is_synthesizable: bool
    sa_score: float  # 1=쉬움, 10=어려움
    num_steps: int = 0
    route_score: float = 0.0
    building_blocks: list[str] = field(default_factory=list)
    reactions: list[str] = field(default_factory=list)
    engine: str = ""


class SynthesizabilityChecker:
    """SATURN + AiZynthFinder 합성 가능성 평가기."""

    def __init__(
        self,
        *,
        sa_threshold: float = 5.0,
        use_aizynthfinder: bool = True,
        aizynthfinder_config: Path | None = None,
    ) -> None:
        self.sa_threshold = sa_threshold
        self.use_aizynthfinder = use_aizynthfinder
        self.aizynthfinder_config = aizynthfinder_config

    def check_batch(self, smiles_list: list[str]) -> list[SynthesisRoute]:
        """배치 합성 가능성 평가."""
        results: list[SynthesisRoute] = []

        # 1단계: RDKit SA Score (항상 사용 가능)
        sa_scores = self._rdkit_sa_scores(smiles_list)

        # 2단계: SATURN 정밀 평가 (설치 시)
        saturn_scores = self._saturn_scores(smiles_list)

        # 3단계: AiZynthFinder 역합성 (설치 시 + 플래그 활성)
        routes = self._aizynthfinder_routes(smiles_list) if self.use_aizynthfinder else {}

        for smi, rdkit_sa in zip(smiles_list, sa_scores):
            sa = saturn_scores.get(smi, rdkit_sa)
            route = routes.get(smi, {})
            results.append(
                SynthesisRoute(
                    smiles=smi,
                    is_synthesizable=sa <= self.sa_threshold,
                    sa_score=sa,
                    num_steps=route.get("num_steps", 0),
                    route_score=route.get("route_score", 0.0),
                    building_blocks=route.get("building_blocks", []),
                    reactions=route.get("reactions", []),
                    engine="saturn+aizynthfinder" if route else "rdkit_sa",
                )
            )

        n_synth = sum(1 for r in results if r.is_synthesizable)
        logger.info(
            "합성 가능성: {}/{} 통과 (SA ≤ {:.1f})",
            n_synth, len(results), self.sa_threshold,
        )
        return results

    def _rdkit_sa_scores(self, smiles_list: list[str]) -> list[float]:
        """RDKit SA Score (Ertl & Schuffenhauer 2009)."""
        try:
            from rdkit import Chem
            from rdkit.Chem import RDConfig
            import sys
            import os

            sa_module_path = os.path.join(RDConfig.RDContribDir, "SA_Score")
            if sa_module_path not in sys.path:
                sys.path.insert(0, sa_module_path)
            import sascorer  # type: ignore[import-untyped]

            scores: list[float] = []
            for smi in smiles_list:
                mol = Chem.MolFromSmiles(smi)
                if mol is None:
                    scores.append(10.0)
                else:
                    scores.append(float(sascorer.calculateScore(mol)))
            return scores
        except (ImportError, ModuleNotFoundError):
            logger.warning("RDKit SA_Score 모듈 로드 실패, 기본값 5.0 반환")
            return [5.0] * len(smiles_list)

    def _saturn_scores(self, smiles_list: list[str]) -> dict[str, float]:
        """SATURN Mamba 기반 합성 가능성 (MIT)."""
        try:
            from saturn import SATURNModel  # type: ignore[import-untyped]

            model = SATURNModel.from_pretrained("saturn-base")
            scores = model.predict_sa(smiles_list)
            return {smi: float(s) for smi, s in zip(smiles_list, scores)}
        except ImportError:
            logger.debug("SATURN 미설치 — RDKit SA Score로 대체")
            return {}

    def _aizynthfinder_routes(self, smiles_list: list[str]) -> dict[str, dict]:
        """AiZynthFinder 역합성 경로 계획 (MIT, AstraZeneca)."""
        try:
            from aizynthfinder.aizynthfinder import AiZynthFinder  # type: ignore[import-untyped]

            finder = AiZynthFinder()
            if self.aizynthfinder_config:
                finder.config.update(str(self.aizynthfinder_config))

            routes: dict[str, dict] = {}
            for smi in smiles_list:
                try:
                    finder.target_smiles = smi
                    finder.tree_search()
                    finder.build_routes()
                    stats = finder.routes.compute_scores()
                    if finder.routes:
                        best = finder.routes[0]
                        routes[smi] = {
                            "num_steps": len(best.get("reactions", [])),
                            "route_score": float(stats[0].get("state score", 0.0)),
                            "building_blocks": best.get("in_stock", []),
                            "reactions": [r.get("template", "") for r in best.get("reactions", [])],
                        }
                except Exception as e:
                    logger.debug("AiZynthFinder 실패: {} — {}", smi[:30], e)
            return routes
        except ImportError:
            logger.debug("AiZynthFinder 미설치 — 역합성 경로 생략")
            return {}
