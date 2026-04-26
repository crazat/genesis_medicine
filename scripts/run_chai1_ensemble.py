"""Chai-1 ensemble cofold for top compounds × targets.

Chai-1 is fully open-source under Apache-2.0 (Chai Discovery 2024-2026,
released completely open-source 2025-Q4). Performance ~AlphaFold-3 level
(77% PoseBusters, 68.5% DockQ — comparable to AF3 76% / 72.9%).

This runner:
    1. Loads top-K compound list from each disease screen + EMB-3
    2. Runs Chai-1 cofold for each (compound, target) pair
    3. Aggregates with Boltz-2 results into 2-way ensemble consensus
    4. Outputs per-target affinity ranking with consensus scoring

Output: pilot/chai1_ensemble/ensemble_consensus.csv
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/chai1_ensemble"
OUT.mkdir(parents=True, exist_ok=True)

# Top compounds × top targets selected for ensemble validation
ENSEMBLE_PAIRS = [
    # Skin scar / fibrosis (EMB-3 lead)
    ("EMB-3", "TGFB1", "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
     "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS"),
    ("EMB-3", "MMP1", "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
     "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"),
    # Pigmentation top: Oxyresveratrol × TYR
    ("Oxyresveratrol", "TYR", "Oc1ccc(/C=C/c2cc(O)c(O)cc2O)cc1",
     ""),    # full TYR seq from registry — leave blank, agent will fetch
    # Acne top: Baicalein × AR
    ("Baicalein", "AR", "Oc1cc2oc(-c3ccccc3)cc(=O)c2c(O)c1O",
     ""),
    # Photoaging top: EMB-3 × SIRT1 (already in pair 1+2 for TGFB1/MMP1)
    ("EMB-3", "SIRT1", "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",
     ""),
    # Alopecia top: Emodin × AR
    ("Emodin", "AR", "Cc1cc(O)c2C(=O)c3cc(O)cc(O)c3C(=O)c2c1",
     ""),
]


def load_target_seq(target: str) -> str:
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_disease_screen import TARGET_REGISTRY
    if target in TARGET_REGISTRY:
        return TARGET_REGISTRY[target]["sequence"]
    return ""


def run_chai1_one(compound: str, target: str, smiles: str,
                   sequence: str, out_dir: Path) -> dict:
    """Run Chai-1 cofold for a single (compound, target) pair.

    Chai-1 expects FASTA + SMILES format input. We write a temporary
    FASTA file and call chai_lab.chai1.run_inference.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    if not sequence:
        sequence = load_target_seq(target)
    if not sequence:
        return {"status": "no_sequence",
                "compound": compound, "target": target}

    fasta_path = out_dir / f"{target}__{compound}.fasta"
    fasta_content = (
        f">protein|{target}\n{sequence}\n"
        f">ligand|{compound}\n{smiles}\n"
    )
    fasta_path.write_text(fasta_content)

    try:
        from chai_lab.chai1 import run_inference
        import torch

        out_path = out_dir / f"{target}__{compound}_chai1"
        out_path.mkdir(exist_ok=True)
        candidates = run_inference(
            fasta_file=fasta_path,
            output_dir=out_path,
            num_trunk_recycles=3,
            num_diffn_timesteps=200,
            seed=42,
            device=torch.device("cuda:0"),
            use_esm_embeddings=True,
        )
        # candidates is a StructureCandidates object
        # Extract aggregate scores
        if hasattr(candidates, "aggregate_score") and candidates.aggregate_score is not None:
            top_score = float(candidates.aggregate_score[0])
        else:
            top_score = None
        return {
            "status": "ok",
            "compound": compound, "target": target,
            "chai1_aggregate_score": top_score,
            "out_path": str(out_path),
        }
    except Exception as e:
        return {
            "status": "error",
            "compound": compound, "target": target,
            "error": str(e)[:300],
        }


def aggregate_with_boltz2():
    """Combine Chai-1 results with existing Boltz-2 affinity_probability_binary.

    Reads from pilot/screen/*/screen_results.csv and pilot/scaffold_hop/.../affinity_*.json.
    """
    boltz_data = {}
    # Disease screens
    for disease in ["pigmentation", "alopecia", "acne", "photoaging"]:
        csv = ROOT / f"pilot/screen/{disease}/screen_results.csv"
        if not csv.exists(): continue
        df = pd.read_csv(csv)
        for _, r in df.iterrows():
            for tgt_col in ["TYR", "TYRP1", "DCT", "AR", "SRD5A2", "CTNNB1",
                             "MMP1", "SIRT1"]:
                if tgt_col in df.columns and not pd.isna(r.get(tgt_col, np.nan)):
                    key = (r["compound"], tgt_col)
                    boltz_data[key] = float(r[tgt_col])
    # Scaffold-hop EMB-3 known affinities (Round 1)
    boltz_data[("EMB-3", "TGFB1")] = 0.749
    boltz_data[("EMB-3", "MMP1")] = 0.674
    boltz_data[("EMB-3", "SIRT1")] = 0.632   # from photoaging screen (EMB-3 was top there)
    return boltz_data


def main():
    print("=" * 72)
    print("Chai-1 ensemble cofold + 2-way Boltz-2 consensus")
    print("=" * 72)

    boltz_known = aggregate_with_boltz2()
    print(f"  Loaded {len(boltz_known)} Boltz-2 baseline affinities\n")

    results = []
    for i, (compound, target, smiles, seq) in enumerate(ENSEMBLE_PAIRS, 1):
        print(f"[{i}/{len(ENSEMBLE_PAIRS)}] {compound:18s} × {target:8s}")
        res = run_chai1_one(compound, target, smiles, seq, OUT / "chai1_runs")
        boltz_score = boltz_known.get((compound, target))
        res["boltz2_affinity_prob_binary"] = boltz_score
        if res["status"] == "ok" and boltz_score is not None:
            # Consensus: Boltz-2 prob ≥ 0.55 + Chai-1 high aggregate = strong evidence
            res["consensus_call"] = (
                "strong" if (boltz_score >= 0.55 and
                              res.get("chai1_aggregate_score") is not None and
                              res["chai1_aggregate_score"] >= 0.55) else
                "moderate" if boltz_score >= 0.55 else
                "weak"
            )
        results.append(res)

    df = pd.DataFrame(results)
    df.to_csv(OUT / "ensemble_consensus.csv", index=False)
    print(f"\n✅ {OUT}/ensemble_consensus.csv")
    print("\n=== ENSEMBLE CONSENSUS ===")
    print(df[["compound", "target", "boltz2_affinity_prob_binary",
              "chai1_aggregate_score" if "chai1_aggregate_score" in df.columns else "status"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
