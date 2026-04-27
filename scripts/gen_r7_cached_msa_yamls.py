"""Generate R7 cofold yamls using LOCAL CACHED MSA — RATELIMIT-free GPU saturation.

Tier A path: 30 R7 candidates × 14 cached-MSA targets = 420 cofold.
"""
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


def get_seq_from_fasta(uniprot_id: str):
    fp = MSA_DIR / f"{uniprot_id}.fasta"
    if not fp.exists():
        return None
    lines = fp.read_text().splitlines()
    seq = "".join(l for l in lines if not l.startswith(">"))
    return seq if seq else None


def get_seq_from_msa(msa_path: Path):
    """Fallback: query sequence is first sequence (after >query) in a3m."""
    if not msa_path.exists():
        return None
    text = msa_path.read_text()
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.startswith(">"):
            if i + 1 < len(lines):
                return lines[i + 1].strip().replace("-", "")
    return None


def main() -> int:
    candidates = pd.read_csv(OUT / "bayesian_v3_round7_candidates.csv").head(30)
    print(f"R7 candidates: {len(candidates)}")

    n_yaml = 0
    failed = []
    for target_key, uniprot, msa_fname in TARGETS:
        msa_path = MSA_DIR / msa_fname
        seq = get_seq_from_fasta(uniprot)
        if seq is None:
            seq = get_seq_from_msa(msa_path)
        if seq is None:
            failed.append((target_key, "no fasta or msa first-seq"))
            continue
        if not msa_path.exists():
            failed.append((target_key, "msa missing"))
            continue
        in_dir = OUT / f"inputs_r7_{target_key}"
        in_dir.mkdir(exist_ok=True)
        for i, row in candidates.iterrows():
            smi = row["smiles"]
            cid = f"r7_{target_key}_{i}"
            cfg = {
                "version": 1,
                "sequences": [{"protein": {
                    "id": "A",
                    "sequence": seq,
                    "msa": str(msa_path),
                }}, {"ligand": {"id": "L", "smiles": smi}}],
                "properties": [{"affinity": {"binder": "L"}}],
            }
            (in_dir / f"{cid}.yaml").write_text(yaml.safe_dump(cfg))
            n_yaml += 1
        print(f"  ✅ {target_key} ({len(seq)} aa, MSA: {msa_fname}): 30 yamls")

    if failed:
        print(f"\n⚠️  {len(failed)} targets skipped:")
        for t, why in failed:
            print(f"    {t}: {why}")

    print(f"\n✅ R7 cached-MSA yamls: {n_yaml} (= {len(TARGETS) - len(failed)} targets × 30)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
