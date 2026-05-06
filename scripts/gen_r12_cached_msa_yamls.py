"""R12 yamls — cached MSA × 30 R12 candidates (R11_0 family refinement)."""
from __future__ import annotations
import sys
from pathlib import Path
import yaml
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
MSA_DIR = ROOT / "data/msa"

TARGETS = [
    ("tgfb1",  "P01137", "tgfb1.a3m"),
    ("mmp1",   "P03956", "mmp1.a3m"),
    ("ctgf",   "P29279", "ctgf.a3m"),
    ("ar",     "P10275", "ar.a3m"),
    ("mitf",   "O75030", "mitf.a3m"),
    ("lox",    "P28300", "lox.a3m"),
    ("sirt1",  "Q96EB6", "sirt1.a3m"),
    ("tyr",    "P14679", "tyr.a3m"),
    ("tyrp1",  "P17643", "tyrp1.a3m"),
    ("dct",    "P40126", "dct.a3m"),
    ("srd5a1", "P18405", "srd5a1.a3m"),
    ("srd5a2", "P31213", "srd5a2.a3m"),
    ("srebp1", "P36956", "srebp1.a3m"),
    ("ptgs2",  "P35354", "ptgs2.a3m"),
]


def get_seq(uniprot, msa_path):
    fp = MSA_DIR / f"{uniprot}.fasta"
    if fp.exists():
        return "".join(l for l in fp.read_text().splitlines() if not l.startswith(">"))
    if msa_path.exists():
        for i, l in enumerate(msa_path.read_text().splitlines()):
            if l.startswith(">") and i + 1 < len(msa_path.read_text().splitlines()):
                return msa_path.read_text().splitlines()[i + 1].strip().replace("-", "")
    return None


def main():
    cands = pd.read_csv(OUT / "bayesian_v8_round12_candidates.csv").head(30)
    n = 0
    for tk, up, mn in TARGETS:
        msa = MSA_DIR / mn
        seq = get_seq(up, msa)
        if not seq or not msa.exists(): continue
        in_dir = OUT / f"inputs_r12_{tk}"
        in_dir.mkdir(exist_ok=True)
        for i, r in cands.iterrows():
            cfg = {"version": 1, "sequences": [
                {"protein": {"id": "A", "sequence": seq, "msa": str(msa)}},
                {"ligand": {"id": "L", "smiles": r["smiles"]}}
            ], "properties": [{"affinity": {"binder": "L"}}]}
            (in_dir / f"r12_{tk}_{i}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
        print(f"✅ {tk}: 30")
    print(f"\n✅ R12 total: {n}")


if __name__ == "__main__":
    sys.exit(main())
