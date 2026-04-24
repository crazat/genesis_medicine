"""스크리닝 모듈 단위 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_medicine.screening.base import (
    DockingPose,
    ScreeningRequest,
    ScreeningResult,
)
from genesis_medicine.screening.consensus import (
    RankedCompound,
    exponential_consensus_ranking,
)


# -- DockingPose / ScreeningRequest 모델 테스트 ---------------------------------

def test_docking_pose_defaults() -> None:
    pose = DockingPose(
        ligand_smiles="CCO",
        protein_id="P56817",
        score=-7.5,
    )
    assert pose.confidence == 0.0
    assert pose.affinity_pkd is None
    assert pose.engine == ""


def test_screening_request_defaults() -> None:
    req = ScreeningRequest(
        protein_id="P56817",
        protein_structure=Path("/tmp/test.pdb"),
        ligand_smiles_list=["CCO", "CC(=O)O"],
    )
    assert req.seed == 42
    assert req.top_n is None
    assert req.top_fraction is None


def test_screening_result_top_smiles() -> None:
    poses = [
        DockingPose(ligand_smiles="B", protein_id="X", score=-5.0),
        DockingPose(ligand_smiles="A", protein_id="X", score=-9.0),
        DockingPose(ligand_smiles="C", protein_id="X", score=-3.0),
    ]
    result = ScreeningResult(engine="test", poses=poses)
    assert result.top_smiles == ["A", "B", "C"]


# -- ECR 합의 스코어링 테스트 ---------------------------------------------------

def test_ecr_empty() -> None:
    ranked = exponential_consensus_ranking({})
    assert ranked == []


def test_ecr_single_stage() -> None:
    stage_results = {
        "stage_a": {"mol1": -9.0, "mol2": -5.0, "mol3": -7.0},
    }
    ranked = exponential_consensus_ranking(stage_results, sigma=0.05)
    assert len(ranked) == 3
    # mol1이 가장 낮은 점수(최고) → 1위
    assert ranked[0].smiles == "mol1"
    assert ranked[0].ecr_score > ranked[1].ecr_score


def test_ecr_multi_stage_consensus() -> None:
    """두 단계에서 모두 상위인 분자가 1위가 되어야 함."""
    stage_results = {
        "docking": {"mol_a": -9.0, "mol_b": -3.0, "mol_c": -6.0},
        "scoring": {"mol_a": -8.0, "mol_b": -7.0, "mol_c": -2.0},
    }
    ranked = exponential_consensus_ranking(stage_results, sigma=0.05)
    # mol_a: docking 1위, scoring 1위 → 합의 1위
    assert ranked[0].smiles == "mol_a"
    assert "docking" in ranked[0].ranks
    assert "scoring" in ranked[0].ranks


def test_ecr_partial_overlap() -> None:
    """일부 단계에만 존재하는 분자는 패널티를 받아야 함."""
    stage_results = {
        "s1": {"mol_a": -9.0, "mol_b": -5.0},
        "s2": {"mol_a": -8.0, "mol_c": -4.0},  # mol_b는 s2에 없음
    }
    ranked = exponential_consensus_ranking(stage_results, sigma=0.05)
    # mol_a: 두 단계 모두 1위 → 확실한 1위
    assert ranked[0].smiles == "mol_a"
    # mol_b는 1단계만, mol_c는 1단계만 → 둘 다 패널티
    incomplete = [r for r in ranked if r.smiles != "mol_a"]
    for r in incomplete:
        assert r.ecr_score < ranked[0].ecr_score


def test_ecr_ranks_stored() -> None:
    stage_results = {
        "stageX": {"a": -10.0, "b": -5.0},
    }
    ranked = exponential_consensus_ranking(stage_results)
    top = ranked[0]
    assert top.smiles == "a"
    assert top.ranks["stageX"] == 0  # 1위 → rank 0
    assert top.scores["stageX"] == -10.0
