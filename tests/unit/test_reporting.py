"""학술 reporting 모듈 단위 테스트.

목표: 가짜(mock) pilot 결과로부터 manuscript-ready output이 정상 생성되는지 검증.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_mock_pilot(tmp_path: Path) -> dict[str, Path]:
    """가짜 흉터 파일럿 결과 생성."""
    rng = np.random.default_rng(42)
    targets = ["TGFB1", "MMP1", "CTGF"]
    compounds = ["Asiaticoside", "Madecassoside", "Shikonin", "Curcumin", "EGCG",
                 "Baicalin", "Berberine", "Quercetin"]

    # full long-form
    rows = []
    for tgt in targets:
        for comp in compounds:
            prob = float(np.clip(rng.normal(0.55, 0.15), 0, 1))
            rows.append({
                "target": tgt,
                "compound": comp,
                "compound_safe": comp.lower(),
                "affinity_probability_binary": prob,
                "affinity_pred_value": -float(np.clip(prob * 4 - 2, -3, 3)),
                "pIC50_approx": 6.0 + prob * 3,
            })
    full_df = pd.DataFrame(rows)
    full_csv = tmp_path / "scar_full.csv"
    full_df.to_csv(full_csv, index=False)

    # consensus pivot (compound × target)
    pivot = full_df.pivot_table(
        index="compound", columns="target", values="affinity_probability_binary"
    )
    pivot["consensus_score"] = pivot[targets].mean(axis=1)
    pivot = pivot.sort_values("consensus_score", ascending=False)
    consensus_csv = tmp_path / "scar_consensus.csv"
    pivot.to_csv(consensus_csv)

    # compounds metadata
    comp_rows = []
    for c in compounds:
        comp_rows.append({
            "name": c,
            "source_botanical": "Mock Plant",
            "source_korean": "모의식물",
            "smiles": "CCO",
            "mw": float(rng.uniform(200, 500)),
            "logp": float(rng.uniform(1.0, 4.0)),
            "hbd": int(rng.integers(0, 5)),
            "hba": int(rng.integers(0, 8)),
            "tpsa": float(rng.uniform(30, 120)),
            "rotbonds": int(rng.integers(0, 8)),
            "category": "scar",
            "khp_listed": "yes",
        })
    compounds_df = pd.DataFrame(comp_rows)
    compounds_csv = tmp_path / "skin_compounds_curated.csv"
    compounds_df.to_csv(compounds_csv, index=False)

    return {
        "full_csv": full_csv,
        "consensus_csv": consensus_csv,
        "compounds_csv": compounds_csv,
    }


# -- 1. base classes ----------------------------------------------------------
def test_study_context_basic(tmp_path: Path) -> None:
    from genesis_medicine.reporting import StudyContext

    ctx = StudyContext(
        name="test_study",
        title="Test pilot",
        disease="Hypertrophic scar",
        results_dir=tmp_path,
        seed=42,
    )
    assert ctx.name == "test_study"
    assert ctx.seed == 42
    assert ctx.results_dir == tmp_path


# -- 2. citations -------------------------------------------------------------
def test_bibtex_for_components() -> None:
    from genesis_medicine.reporting import bibtex_for_components, bibtex_string

    comps = ["boltz2", "admet_ai", "rdkit"]
    entries = bibtex_for_components(comps)
    assert len(entries) == 3
    assert "Wohlwend" in entries["boltz2"] or "Boltz" in entries["boltz2"]
    bib_str = bibtex_string(comps)
    assert "@article" in bib_str or "@misc" in bib_str
    assert "Boltz" in bib_str


def test_cite_keys() -> None:
    from genesis_medicine.reporting.citations import cite_keys
    keys = cite_keys(["boltz2", "rdkit"])
    assert any("Boltz" in k for k in keys)


# -- 3. methods section -------------------------------------------------------
def test_methods_section_generation(tmp_path: Path) -> None:
    from genesis_medicine.reporting import StudyContext, generate_methods_section

    ctx = StudyContext(
        name="t", title="T",
        disease="Test disease",
        targets=[
            {"key": "TGFB1", "uniprot": "P01137", "display": "TGF-β1", "mode": "antagonist"},
        ],
        components_used=["boltz2", "admet_ai", "coconut_2", "rdkit"],
        seed=42, license_profile="commercial",
    )
    md = generate_methods_section(ctx)
    assert "## Methods" in md
    assert "Boltz-2" in md
    assert "ADMET-AI" in md
    assert "TGFB1" in md or "TGF-β1" in md
    assert "Reproducibility" in md


# -- 4. statistics ------------------------------------------------------------
def test_mann_whitney_basic() -> None:
    from genesis_medicine.reporting import mann_whitney_test

    actives = [0.8, 0.85, 0.9, 0.7, 0.75]
    baseline = [0.2, 0.25, 0.3, 0.15, 0.18]
    r = mann_whitney_test(actives, baseline)
    assert r.n1 == 5 and r.n2 == 5
    # actives 분포가 명확히 더 높으므로 p < 0.05 (scipy 있을 때만)
    if not np.isnan(r.p_value):
        assert r.p_value < 0.05


def test_benjamini_hochberg() -> None:
    from genesis_medicine.reporting import benjamini_hochberg

    pvals = [0.001, 0.01, 0.03, 0.5, 0.6, 0.8]
    out = benjamini_hochberg(pvals, alpha=0.05)
    assert len(out["q_values"]) == 6
    assert out["n_significant"] >= 1


def test_roc_auc() -> None:
    from genesis_medicine.reporting import roc_auc_with_baseline

    actives = [0.9, 0.85, 0.95, 0.8, 0.75]
    baseline = [0.1, 0.2, 0.15, 0.25, 0.18]
    out = roc_auc_with_baseline(actives, baseline)
    assert out["auc"] > 0.95   # 분포가 완전 분리됨


def test_hit_rate() -> None:
    from genesis_medicine.reporting import hit_rate
    r = hit_rate([0.7, 0.8, 0.4, 0.5, 0.9], threshold=0.6)
    assert r["n"] == 5
    assert r["hits"] == 3
    assert r["rate"] == 0.6


# -- 5. checklist -------------------------------------------------------------
def test_tripod_ai_checklist(tmp_path: Path) -> None:
    from genesis_medicine.reporting import StudyContext, tripod_ai_checklist

    mock = _make_mock_pilot(tmp_path)
    ctx = StudyContext(
        name="t", title="Test",
        disease="Test",
        compounds_csv=mock["compounds_csv"],
        seed=42,
    )
    md = tripod_ai_checklist(ctx)
    assert "TRIPOD-AI" in md
    assert "Reproducibility" in md or "computational" in md.lower()


def test_miclaim_checklist() -> None:
    from genesis_medicine.reporting import StudyContext, miclaim_checklist

    ctx = StudyContext(name="t", title="Test", disease="Test")
    md = miclaim_checklist(ctx)
    assert "MI-CLAIM" in md
    assert "Stage" in md


# -- 6. figure factory --------------------------------------------------------
def test_consensus_heatmap_generates_files(tmp_path: Path) -> None:
    from genesis_medicine.reporting import consensus_heatmap

    mock = _make_mock_pilot(tmp_path)
    consensus_df = pd.read_csv(mock["consensus_csv"], index_col=0)
    paths = consensus_heatmap(consensus_df, out_dir=tmp_path / "fig")
    assert len(paths) == 2  # png + pdf
    assert all(p.exists() for p in paths)


def test_lipinski_radar(tmp_path: Path) -> None:
    from genesis_medicine.reporting import lipinski_radar

    mock = _make_mock_pilot(tmp_path)
    compounds_df = pd.read_csv(mock["compounds_csv"])
    paths = lipinski_radar(compounds_df, top_n=4, out_dir=tmp_path / "fig")
    assert len(paths) == 2
    assert all(p.exists() for p in paths)


def test_top_hits_table(tmp_path: Path) -> None:
    from genesis_medicine.reporting import top_hits_table

    mock = _make_mock_pilot(tmp_path)
    consensus_df = pd.read_csv(mock["consensus_csv"], index_col=0)
    paths = top_hits_table(consensus_df, out_dir=tmp_path / "tab", top_n=5)
    assert len(paths) >= 1
    assert (tmp_path / "tab" / "table1_top_hits.csv").exists()


# -- 7. full manuscript build (end-to-end) -----------------------------------
def test_end_to_end_manuscript(tmp_path: Path) -> None:
    from genesis_medicine.reporting import StudyContext, build_manuscript

    mock = _make_mock_pilot(tmp_path)
    ctx = StudyContext(
        name="mock_scar",
        title="Mock skin scar pilot",
        disease="Hypertrophic scar",
        results_dir=tmp_path,
        consensus_csv=mock["consensus_csv"],
        full_csv=mock["full_csv"],
        compounds_csv=mock["compounds_csv"],
        targets=[
            {"key": "TGFB1", "uniprot": "P01137", "display": "TGF-β1", "mode": "antagonist"},
            {"key": "MMP1", "uniprot": "P03956", "display": "MMP-1", "mode": "inhibitor"},
            {"key": "CTGF", "uniprot": "P29279", "display": "CTGF", "mode": "antagonist"},
        ],
        components_used=["boltz2", "admet_ai", "coconut_2", "rdkit"],
        output_dir=tmp_path / "manuscript",
        seed=42, license_profile="commercial",
    )
    result = build_manuscript(ctx)

    # 파일 존재 + 기본 검증
    assert result.manuscript_md.exists()
    assert result.references_bib and result.references_bib.exists()
    assert result.checklist_md and result.checklist_md.exists()
    assert result.methods_md and result.methods_md.exists()
    assert len(result.figures) >= 4   # heatmap, dist, radar, roc
    assert len(result.tables) >= 1
    assert result.word_count > 200

    # manuscript 내용 확인
    md_text = result.manuscript_md.read_text()
    assert "## Abstract" in md_text
    assert "## Methods" in md_text
    assert "## 3. Results" in md_text
    assert "Boltz-2" in md_text
    assert "Hypertrophic scar" in md_text


# -- 8. benchmark baseline ----------------------------------------------------
def test_synthetic_negative_distribution() -> None:
    from genesis_medicine.reporting.benchmark_baseline import synthetic_negative_distribution

    arr = synthetic_negative_distribution(n=100, seed=0)
    assert len(arr) == 100
    assert all(0 <= v <= 1 for v in arr)
    assert 0.05 < float(np.mean(arr)) < 0.30


def test_compare_to_baseline_strong_separation() -> None:
    from genesis_medicine.reporting.benchmark_baseline import compare_to_baseline

    actives = [0.85, 0.9, 0.8, 0.95, 0.78]
    baseline = [0.1, 0.2, 0.15, 0.18, 0.05]
    out = compare_to_baseline(actives, baseline)
    assert out["roc_auc"] > 0.9
    if not np.isnan(out["mann_whitney_p"]):
        assert out["mann_whitney_p"] < 0.05
