"""Multi-fidelity BO cascade demo — Boltz-2 → ABFE → wet-lab.

Tier B #7 통합 검증 스크립트.
실제 fidelity evaluator는 placeholder (cheap = Boltz-2 prediction column,
mid = ABFE estimate, gold = wet-lab IC50). 첫 round는 cheap 만으로 수십 ~수백
화합물 평가, mid는 top X% 만 ABFE, gold는 top 5-10개만 CRO IC50.

ROI 추정: 동일 hit rate에서 CRO 비용 30-50% 절감.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Dict
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.genesis_medicine.optimization.multi_fidelity_bo import (
    MultiFidelityBO, FidelityLevel,
)


def boltz2_evaluator(smiles_list: List[str]) -> List[float]:
    """Cheap fidelity (~1 unit cost)."""
    return [float(np.tanh(hash(s) % 100 / 50.0)) for s in smiles_list]


def abfe_evaluator(smiles_list: List[str]) -> List[float]:
    """Mid fidelity (~100 unit cost): ABFE in kcal/mol → mapped 0-1."""
    return [float(np.tanh(hash(s) % 100 / 50.0) + 0.05 * np.random.randn())
            for s in smiles_list]


def wetlab_evaluator(smiles_list: List[str]) -> List[float]:
    """Gold fidelity (~10000 unit cost): IC50 measurement."""
    return [float(np.tanh(hash(s) % 100 / 50.0) + 0.02 * np.random.randn())
            for s in smiles_list]


def morgan_features(smiles: str) -> np.ndarray:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return np.zeros(1024, dtype=np.float32)
    fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, 1024)
    return np.array(fp, dtype=np.float32)


def main() -> int:
    print("=" * 72)
    print("Multi-fidelity BO cascade demo — Tier B #7 (ACS Cent Sci 2025)")
    print("=" * 72)

    # Use existing R5 candidate pool
    out = ROOT / "pilot/cpu_meaningful"
    pool_csv = out / "bayesian_v2_pool_predictions.csv"
    if not pool_csv.exists():
        print(f"❌ pool csv 미발견: {pool_csv}")
        return 1

    pool = pd.read_csv(pool_csv).head(200)
    pool_smiles = pool["smiles"].dropna().tolist()
    print(f"Pool size: {len(pool_smiles)}")

    # Build feature dict
    print("Computing Morgan fingerprints...")
    X_by_smiles = {s: morgan_features(s) for s in pool_smiles}

    cheap = FidelityLevel("boltz2", 1.0, 0.15, boltz2_evaluator)
    mid = FidelityLevel("abfe", 100.0, 0.05, abfe_evaluator)
    gold = FidelityLevel("wetlab", 10000.0, 0.02, wetlab_evaluator)

    bo = MultiFidelityBO([cheap, mid, gold], rho=0.85)

    # Bootstrap with 30 cheap evaluations
    print("\n[Bootstrap] 30 Boltz-2 evaluations")
    bootstrap = pool_smiles[:30]
    cheap_vals = boltz2_evaluator(bootstrap)
    for s, v in zip(bootstrap, cheap_vals):
        bo.add_observation(s, "boltz2", v)

    # Round 1: cascade ABFE on top 10
    print("\n[Round 1] Cascade selection under budget=2000")
    res1 = bo.suggest_next_batch(pool_smiles, X_by_smiles,
                                   budget_remaining=2000, batch_size=20)
    print(f"  Selected {len(res1.selected_smiles)} compounds")
    print(f"  Fidelity mix: {dict(pd.Series(res1.selected_fidelity).value_counts())}")
    print(f"  Total cost: {res1.total_cost:.1f}")
    for s, f in zip(res1.selected_smiles[:5], res1.selected_fidelity[:5]):
        v = (boltz2_evaluator if f == "boltz2"
             else abfe_evaluator if f == "abfe" else wetlab_evaluator)([s])[0]
        bo.add_observation(s, f, v)

    # Round 2: with mid-fidelity data, gold-fidelity recommendations emerge
    print("\n[Round 2] After ABFE feedback — gold fidelity recommendations")
    res2 = bo.suggest_next_batch(pool_smiles, X_by_smiles,
                                   budget_remaining=15000, batch_size=10)
    print(f"  Selected {len(res2.selected_smiles)} compounds")
    print(f"  Fidelity mix: {dict(pd.Series(res2.selected_fidelity).value_counts())}")
    print(f"  Total cost: {res2.total_cost:.1f}")

    print(f"\nObservation tally: {bo.cumulative_observations()}")
    out_csv = out / "multi_fidelity_bo_cascade_demo.csv"
    rows = [{"smiles": s, "fidelity": f, "ei": e}
              for s, f, e in zip(res2.selected_smiles, res2.selected_fidelity,
                                 res2.expected_improvements)]
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"\n✅ Wrote {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
