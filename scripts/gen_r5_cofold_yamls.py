"""Round 5 Boltz-2 yaml inputs — R4 expanded 194 mol × top 5 selective targets.

Targets where R4 integration found strongest selective hits:
  - TGFB1 (r3_6 dual-binder + Pirfenidone class)
  - AR (β-sitosterol sel_idx 0.563 — alopecia hot)
  - CTGF (shikonin 자근 — scar)
  - SIRT1 (chlorogenic_acid — photoaging)
  - LOX (lysyl oxidase, sel_idx 0.78 winners)

194 mol × 5 = 970 cofolds (~10h GPU). Phase by phase.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

RECEPTOR_FALLBACKS = {
    "mmp1": ROOT / "pilot/scaffold_hop_round2/boltz_inputs/mmp1__r2_1.yaml",
    "tgfb1": ROOT / "pilot/scaffold_hop_round2/boltz_inputs/tgfb1__r2_1.yaml",
    "ctgf": ROOT / "pilot/scaffold_hop/boltz2_validation/inputs/ctgf__cur2.yaml",
    "ar": ROOT / "pilot/cpu_queue/inputs_ar/ar__top000.yaml",
    "sirt1": ROOT / "pilot/cpu_queue/inputs_sirt1/sirt1__top000.yaml",
    "lox": ROOT / "pilot/cpu_queue/inputs_lox/lox__top000.yaml",
}


def get_receptor_seq(target):
    fallback = RECEPTOR_FALLBACKS.get(target)
    if fallback and fallback.exists():
        with open(fallback) as f:
            data = yaml.safe_load(f)
        for s in data.get("sequences", []):
            if "protein" in s:
                return s["protein"]
    return None


def main():
    df = pd.read_csv(OUT / "round4_expanded.csv")
    print(f"Round 4 expanded: {len(df)}")

    # Top 100 by score (vs full 194 — first phase)
    df = df.head(100).reset_index(drop=True)
    print(f"Top 100 selected for R5 cofold")

    n_yaml = 0
    for target in ["tgfb1", "ar", "ctgf", "sirt1", "lox"]:
        protein = get_receptor_seq(target)
        if not protein:
            print(f"  ⚠️ {target} receptor seq not found")
            continue

        target_dir = OUT / f"inputs_r5_{target}"
        target_dir.mkdir(parents=True, exist_ok=True)

        for i, row in df.iterrows():
            smi = row["smiles"]
            cmpd_id = f"r5_{i:03d}"
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

    print(f"\n✅ Generated {n_yaml} yaml files (top 100 × 5 targets)")


if __name__ == "__main__":
    sys.exit(main())
