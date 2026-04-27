"""Round 5 remainder yaml inputs — AR + SIRT1 + LOX with corrected receptor paths."""
from __future__ import annotations
import sys, yaml
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

RECEPTOR_FALLBACKS = {
    "ar": ROOT / "pilot/gpu_queue/inputs_ar/ar__top076.yaml",
    "sirt1": ROOT / "pilot/gpu_queue/inputs_sirt1/sirt1__top038.yaml",
    "lox": ROOT / "pilot/gpu_queue/inputs_lox/lox__top000.yaml",
    "mitf": ROOT / "pilot/gpu_queue/inputs_mitf/mitf__top000.yaml",
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
    df = pd.read_csv(OUT / "round4_expanded.csv").head(100).reset_index(drop=True)
    print(f"Round 4 expanded top 100")

    n_yaml = 0
    for target in ["ar", "sirt1", "lox", "mitf"]:
        protein = get_receptor_seq(target)
        if not protein:
            print(f"  ⚠️ {target} receptor seq not found")
            continue
        target_dir = OUT / f"inputs_r5_{target}"
        target_dir.mkdir(parents=True, exist_ok=True)
        for i, row in df.iterrows():
            yaml_data = {
                "version": 1,
                "sequences": [
                    {"protein": protein},
                    {"ligand": {"id": "L", "smiles": row["smiles"]}},
                ],
                "properties": [{"affinity": {"binder": "L"}}],
            }
            yaml_path = target_dir / f"{target}__r5_{i:03d}.yaml"
            with open(yaml_path, "w") as f:
                yaml.safe_dump(yaml_data, f)
            n_yaml += 1
        print(f"  ✅ {target}: 100 yamls")

    print(f"\n✅ Generated {n_yaml} yaml files")


if __name__ == "__main__":
    sys.exit(main())
