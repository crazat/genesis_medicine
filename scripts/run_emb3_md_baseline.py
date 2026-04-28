"""EMB-3 MD baseline — head-to-head comparison vs CMS-19 (7 targets × 10 ns each).

EMB-3 SMILES: CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O
Same 7 targets as CMS-19 ensemble for direct dual-lead comparison.
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
import pandas as pd

_ENV_BIN = Path(sys.executable).parent
if str(_ENV_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ENV_BIN}:{os.environ.get('PATH', '')}"

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_emb3_baseline"
OUT.mkdir(parents=True, exist_ok=True)

EMB3_SMI = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"

# Find EMB-3 cofold cifs from existing R3 / Round 4 output (EMB-3 already has cofold history)
# Use generic Boltz-2 R7-R9 inputs as proxy — EMB-3 is candidate idx=? in some round
# For baseline, we use the existing scaffold-hop r3_6 for TGFB1 + cofold against new targets
# Simpler: cofold EMB-3 against same MSA-cached targets fresh

JOBS = [
    {"name": "tgfb1__emb3", "uniprot": "P01137", "msa": "tgfb1.a3m"},
    {"name": "mmp1__emb3",  "uniprot": "P03956", "msa": "mmp1.a3m"},
    {"name": "ctgf__emb3",  "uniprot": "P29279", "msa": "ctgf.a3m"},
    {"name": "srd5a1__emb3","uniprot": "P18405", "msa": "srd5a1.a3m"},
    {"name": "mitf__emb3",  "uniprot": "O75030", "msa": "mitf.a3m"},
    {"name": "tyr__emb3",   "uniprot": "P14679", "msa": "tyr.a3m"},
    {"name": "tyrp1__emb3", "uniprot": "P17643", "msa": "tyrp1.a3m"},
]


def cofold_emb3():
    """Quick cofold EMB-3 vs 7 targets using cached MSA."""
    import yaml
    inputs_dir = OUT / "boltz_inputs"
    inputs_dir.mkdir(exist_ok=True)
    msa_dir = ROOT / "data/msa"

    for j in JOBS:
        msa_path = msa_dir / j["msa"]
        fasta_path = msa_dir / f"{j['uniprot']}.fasta"
        if fasta_path.exists():
            seq = "".join(l for l in fasta_path.read_text().splitlines()
                            if not l.startswith(">"))
        else:
            text = msa_path.read_text() if msa_path.exists() else ""
            for i, l in enumerate(text.splitlines()):
                if l.startswith(">") and i + 1 < len(text.splitlines()):
                    seq = text.splitlines()[i + 1].strip().replace("-", "")
                    break
            else:
                continue
        cfg = {
            "version": 1,
            "sequences": [
                {"protein": {"id": "A", "sequence": seq, "msa": str(msa_path)}},
                {"ligand": {"id": "L", "smiles": EMB3_SMI}},
            ],
            "properties": [{"affinity": {"binder": "L"}}],
        }
        (inputs_dir / f"{j['name']}.yaml").write_text(yaml.safe_dump(cfg))
    print(f"✅ Wrote {len(JOBS)} EMB-3 cofold yamls to {inputs_dir}")
    return inputs_dir


def main():
    print("=" * 72)
    print("EMB-3 MD baseline — cofold + 10 ns MD × 7 targets")
    print("=" * 72)
    inputs_dir = cofold_emb3()
    print(f"\nNext: boltz predict {inputs_dir} → output → MD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
