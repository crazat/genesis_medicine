"""Prep Boltz-2 cofold YAMLs for top 100 BRICS × LOX/AR/MITF.

NOT a re-run of gpu_queue_worker (which already does this for those targets);
instead this generates ADMET-pre-filtered subsets so subsequent batches focus
on top-quality candidates only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]


TARGETS = {
    "tyr": "MLLAVLYCLLWSFQTSAGHFPRACVSSKNLMEKECCPPWSGDRSPCGQLSGRGSCQNILLSNAPLGPQFPFTGVDDRESWPSVFYNRTCQCSGNFMGFNCGNCKFGFWGPNCTERRLLVRRNIFDLSAPEKDKFFAYLTLAKHTISSDYVIPIGTYGQMKNGSTPMFNDINIYDLFVWMHYYVSMDALLGGSEIWRDIDFAHEAPAFLPWHRLFLLRWEQEIQKLTGDENFTIPYWDWRDAEKCDICTDEYMGGQHPTNPNLLSPASFFSSWQIVCSRLEEYNSHQSLCNGTPEGPLRRNPGNHDKSRTPRLPSSADVEFCLSLTQYESGSMDKAANFSFRNTLEGFASPLTGIADASQSSMHNALHIYMNGTMSQVQGSANDPIFLLHHAFVDSIFEQWLRRHRPLQEVYPEANAPIGHNRESYMVPFIPLYRNGDFFISSKDLGYDYSYLQDSDPDSFQDYIKSYLEQASRIWSWLLGAAMVGAVLTALLAGLVSLLCRHKRKQLPEEKQPLLMEKEDYHSLYQSHL",
    # AR + MITF + LOX already in gpu_queue_worker — skipping
}


def prep(target_name: str, target_seq: str, df: pd.DataFrame, out_dir: Path,
         n: int = 100):
    out_dir.mkdir(parents=True, exist_ok=True)
    msa_path = ROOT / f"data/msa/{target_name}.a3m"
    msa_param = str(msa_path) if msa_path.exists() else None

    seq = "".join(target_seq.split())
    n_written = 0
    for i, r in df.head(n).reset_index(drop=True).iterrows():
        protein_block = {"id": "A", "sequence": seq}
        if msa_param:
            protein_block["msa"] = msa_param
        yaml_data = {
            "version": 1,
            "sequences": [
                {"protein": protein_block},
                {"ligand": {"id": "B", "smiles": r["smiles"]}},
            ],
            "properties": [{"affinity": {"binder": "B"}}],
        }
        (out_dir / f"{target_name}__top{i:03d}.yaml").write_text(
            yaml.safe_dump(yaml_data, sort_keys=False)
        )
        n_written += 1
    print(f"  {target_name}: {n_written} yamls (msa cached={msa_param is not None})")


def main():
    df = pd.read_csv(ROOT / "pilot/cpu_queue_v5/top100_novel_candidates.csv")
    print(f"Top 100 novel BRICS: {len(df)}")
    for tname, tseq in TARGETS.items():
        out_dir = ROOT / f"pilot/cpu_meaningful/inputs_{tname}"
        prep(tname, tseq, df, out_dir, n=100)


if __name__ == "__main__":
    sys.exit(main())
