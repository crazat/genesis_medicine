"""REINVENT 4 mol2mol scaffold hopping for skin scar pilot.

Embelin · Curcumin → 100 변형 SMILES (medium similarity prior).
이후 ADMET filter + Boltz-2 affinity (별도 스크립트)로 top-N 선별.

전제: external/REINVENT4/priors/mol2mol_medium_similarity.prior 존재.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "external/REINVENT4/priors/mol2mol_medium_similarity.prior"
OUT_BASE = ROOT / "pilot/scaffold_hop"

SEEDS = [
    {
        "name": "embelin",
        "smiles": "CCCCCCCCCCCC1=C(C(=O)C=C(C1=O)O)O",
        "rationale": "1,4-benzoquinone with C11 alkyl — anti-fibrotic on TGF-β1, but hERG risk.",
    },
    {
        "name": "curcumin",
        "smiles": "COC1=C(C=CC(=C1)/C=C/C(=O)CC(=O)/C=C/C2=CC(=C(C=C2)O)OC)O",
        "rationale": "diferuloylmethane — anti-inflammatory, but very low oral bioavailability.",
    },
]


def write_inputs(seed: dict) -> tuple[Path, Path, Path]:
    out_dir = OUT_BASE / seed["name"]
    smi = out_dir / "inputs" / "seed.smi"
    smi.write_text(seed["smiles"] + "\n")

    out_csv = out_dir / "outputs" / "sampled.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    toml = out_dir / "inputs" / "sampling.toml"
    toml.write_text(textwrap.dedent(f'''\
        run_type = "sampling"
        device = "cuda:0"

        [parameters]
        model_file = "{PRIOR}"
        smiles_file = "{smi}"
        sample_strategy = "multinomial"
        temperature = 1.0
        output_file = "{out_csv}"
        num_smiles = 100
        unique_molecules = true
        randomize_smiles = true
    '''))
    return toml, out_csv, out_dir


def run(seed: dict) -> int:
    print(f"\n=== {seed['name'].upper()} ===")
    print(f"   SMILES: {seed['smiles']}")
    print(f"   합리화: {seed['rationale']}")

    toml, out_csv, out_dir = write_inputs(seed)
    log = out_dir / "outputs" / "reinvent.log"

    cmd = [str(Path(sys.executable).parent / "reinvent"), "-l", str(log), str(toml)]
    print(f"   $ {' '.join(cmd)}")
    rc = subprocess.run(cmd, cwd=out_dir).returncode

    if rc != 0:
        print(f"   ❌ exit {rc} (log: {log})")
        return rc
    if out_csv.exists():
        n = sum(1 for _ in out_csv.open()) - 1
        print(f"   ✅ {n} SMILES → {out_csv}")
    return rc


def main() -> int:
    if not PRIOR.exists():
        print(f"❌ prior 없음: {PRIOR}", file=sys.stderr)
        return 1
    if not shutil.which(str(Path(sys.executable).parent / "reinvent")):
        print("❌ reinvent CLI 없음 — uv pip install reinvent4", file=sys.stderr)
        return 1

    for seed in SEEDS:
        if run(seed) != 0:
            return 2
    print("\n다음 단계: scripts/analyze_scaffold_hop.py 로 ADMET 필터링.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
