"""R15 BRICS triple-safe candidate (chromanol fragment) × 14 skin targets.

Top-priority candidate: OCC1COc2cc(O)ccc2C1 (R12_4 chromanol, only triple-safe in ADMET filter).
Boltz-2 cofold YAML 생성 (cached MSA 사용).

Output: pilot/cpu_meaningful/inputs_r15_chromanol/r15_chrom_<target>.yaml × 14
"""
from __future__ import annotations
import sys
from pathlib import Path
import yaml

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

CHROMANOL_SMILES = "OCC1COc2cc(O)ccc2C1"  # R12_4 chromanol fragment, triple-safe ADMET


def get_seq(uniprot, msa_path):
    fp = MSA_DIR / f"{uniprot}.fasta"
    if fp.exists():
        return "".join(l for l in fp.read_text().splitlines() if not l.startswith(">"))
    if msa_path.exists():
        lines = msa_path.read_text().splitlines()
        for i, l in enumerate(lines):
            if l.startswith(">") and i + 1 < len(lines):
                return lines[i + 1].strip().replace("-", "")
    return None


def main():
    in_dir = OUT / "inputs_r15_chromanol"
    in_dir.mkdir(exist_ok=True)
    n = 0
    skipped = []
    for tk, up, mn in TARGETS:
        msa = MSA_DIR / mn
        seq = get_seq(up, msa)
        if not seq or not msa.exists():
            skipped.append((tk, "no MSA"))
            continue
        cfg = {
            "version": 1,
            "sequences": [
                {"protein": {"id": "A", "sequence": seq, "msa": str(msa)}},
                {"ligand": {"id": "L", "smiles": CHROMANOL_SMILES}}
            ],
            "properties": [{"affinity": {"binder": "L"}}]
        }
        (in_dir / f"r15_chrom_{tk}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1
    print(f"✅ R15 chromanol × 14 targets: {n} YAMLs in {in_dir}")
    if skipped:
        print(f"⚠️  skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
