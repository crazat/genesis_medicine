"""Generate Boltz-2 yaml inputs for Round 4 candidates × MMP-1 + TGFB1 + CTGF.

Round 4 top 30 × 3 targets = 90 cofold inputs (~1h GPU).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

# Receptor sequences (already in repo, copy from existing yamls)
TARGETS = {
    "mmp1": ROOT / "pilot/cpu_meaningful/inputs_tyr",  # use existing for receptor seq
    "tgfb1": ROOT / "pilot/cpu_meaningful/inputs_srd5a2",
    "ctgf": ROOT / "pilot/cpu_meaningful/inputs_ptgs2",
}

RECEPTOR_FALLBACKS = {
    "mmp1": ROOT / "pilot/scaffold_hop_round2/boltz_inputs/mmp1__r2_1.yaml",
    "tgfb1": ROOT / "pilot/scaffold_hop_round2/boltz_inputs/tgfb1__r2_1.yaml",
    "ctgf": ROOT / "pilot/scaffold_hop/boltz2_validation/inputs/ctgf__cur2.yaml",
}


def get_receptor_seq(target):
    """Extract protein sequence from existing yaml."""
    fallback = RECEPTOR_FALLBACKS.get(target)
    if fallback and fallback.exists():
        with open(fallback) as f:
            data = yaml.safe_load(f)
        for s in data.get("sequences", []):
            if "protein" in s:
                return s["protein"]
    return None


def main():
    df = pd.read_csv(OUT / "round4_top100.csv")
    print(f"Round 4 candidates: {len(df)}")

    # Take top 30 by score
    df = df.head(30).reset_index(drop=True)
    print(f"Top 30 by round4_score selected")

    n_yaml = 0
    for target in ["mmp1", "tgfb1", "ctgf"]:
        protein = get_receptor_seq(target)
        if not protein:
            print(f"  ⚠️ {target} receptor sequence not found")
            continue

        target_dir = OUT / f"inputs_round4_{target}"
        target_dir.mkdir(parents=True, exist_ok=True)

        for i, row in df.iterrows():
            smi = row["smiles"]
            cmpd_id = f"r4_{i:03d}"

            yaml_data = {
                "version": 1,
                "sequences": [
                    {"protein": protein},
                    {"ligand": {"id": "L", "smiles": smi}},
                ],
                "properties": [{"affinity": {"binder": "L"}}],
            }

            yaml_path = target_dir / f"{target}__{cmpd_id}.yaml"
            with open(yaml_path, "w") as f:
                yaml.safe_dump(yaml_data, f)
            n_yaml += 1

    print(f"\n✅ Generated {n_yaml} yaml files (top 30 × 3 targets)")
    print("\nRun:")
    print("  for tgt in mmp1 tgfb1 ctgf; do")
    print("    .venv/bin/boltz predict pilot/cpu_meaningful/inputs_round4_$tgt \\")
    print("      --out_dir pilot/cpu_meaningful/output_round4_$tgt \\")
    print("      --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \\")
    print("      --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \\")
    print("      --affinity_mw_correction --devices 1")
    print("  done")


if __name__ == "__main__":
    sys.exit(main())
