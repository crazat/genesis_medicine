"""Generate R16 topical chromanol analog Boltz-2 YAMLs.

Uses the top R15 chromanol topical analogs from:
  pilot/cpu_meaningful/r15_chromanol_analog_scan.csv

Targets:
  TGFB1, TYR, DCT (top-3 R15 chromanol cofold targets)

Output:
  pilot/cpu_meaningful/inputs_r16_chromanol_topical/*.yaml
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
MSA_DIR = ROOT / "data/msa"
INPUT_DIR = OUT / "inputs_r16_chromanol_topical"

TARGETS = [
    ("tgfb1", "P01137", "tgfb1.a3m"),
    ("tyr", "P14679", "tyr.a3m"),
    ("dct", "P40126", "dct.a3m"),
]


def get_seq(uniprot: str, msa_path: Path) -> str | None:
    fasta = MSA_DIR / f"{uniprot}.fasta"
    if fasta.exists():
        return "".join(line for line in fasta.read_text().splitlines() if not line.startswith(">"))
    if msa_path.exists():
        lines = msa_path.read_text().splitlines()
        for idx, line in enumerate(lines):
            if line.startswith(">") and idx + 1 < len(lines):
                return lines[idx + 1].strip().replace("-", "")
    return None


def main() -> int:
    analogs = pd.read_csv(OUT / "r15_chromanol_analog_scan.csv")
    top = analogs.sort_values("topical_followup_score", ascending=False).head(6)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = []
    n = 0
    for analog_rank, row in enumerate(top.itertuples(index=False), start=1):
        analog_id = getattr(row, "analog_id")
        smiles = getattr(row, "smiles")
        for target, uniprot, msa_name in TARGETS:
            msa = MSA_DIR / msa_name
            seq = get_seq(uniprot, msa)
            if not seq or not msa.exists():
                print(f"skip {target}: missing sequence/MSA")
                continue
            job_id = f"r16_{analog_rank:02d}_{target}"
            cfg = {
                "version": 1,
                "sequences": [
                    {"protein": {"id": "A", "sequence": seq, "msa": str(msa)}},
                    {"ligand": {"id": "L", "smiles": smiles}},
                ],
                "properties": [{"affinity": {"binder": "L"}}],
            }
            (INPUT_DIR / f"{job_id}.yaml").write_text(yaml.safe_dump(cfg))
            manifest.append({
                "job_id": job_id,
                "analog_rank": analog_rank,
                "analog_id": analog_id,
                "target": target,
                "smiles": smiles,
                "topical_followup_score": getattr(row, "topical_followup_score"),
                "logP": getattr(row, "logP"),
                "QED": getattr(row, "QED"),
                "gap_eV": getattr(row, "gap_eV"),
            })
            n += 1

    pd.DataFrame(manifest).to_csv(OUT / "r16_chromanol_topical_manifest.csv", index=False)
    print(f"Generated {n} YAMLs in {INPUT_DIR}")
    print(f"Manifest: {OUT / 'r16_chromanol_topical_manifest.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
