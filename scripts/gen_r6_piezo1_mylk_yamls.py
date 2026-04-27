"""Generate R6 cofold yamls for PIEZO1 + MYLK + F2RL1 + NR3C1 (Tier B 신규 4 타겟).

Top 30 from R5 Bayesian Round 6 candidates × 4 new targets = 120 cofold yamls.
PIEZO1은 2521 residues라 chunk 처리 (cap dome 도메인 ~1900-2521 only).
"""
from __future__ import annotations
import sys
from pathlib import Path
import yaml
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
TARGETS_DIR = ROOT / "pilot/skin_targets_2026"

# Pocket / domain trimming
PIEZO1_CAP_DOME_RANGE = (1976, 2547)   # cap + central pore (last 571 residues)
MYLK_CATALYTIC_RANGE = (1465, 1729)    # catalytic kinase domain (CaMK family)


def read_fasta_chunk(fasta_path: Path, start: int = None, end: int = None) -> str:
    """Return sequence (optionally sliced)."""
    lines = fasta_path.read_text().splitlines()
    seq = "".join(l for l in lines if not l.startswith(">"))
    if start is not None and end is not None:
        return seq[start - 1:end]
    return seq


def main() -> int:
    candidates = pd.read_csv(OUT / "bayesian_v2_round6_candidates.csv").head(30)
    print(f"R6 candidates: {len(candidates)}")

    targets = {
        "piezo1": {
            "fasta": TARGETS_DIR / "PIEZO1.fasta",
            "chain_id": "A",
            "chunk": PIEZO1_CAP_DOME_RANGE,
            "rationale": "Cap dome + central pore (last 571 residues, full 2521 too large)",
        },
        "mylk": {
            "fasta": TARGETS_DIR / "MYLK.fasta",
            "chain_id": "A",
            "chunk": MYLK_CATALYTIC_RANGE,
            "rationale": "Catalytic kinase domain (1465-1729)",
        },
        "f2rl1": {
            "fasta": TARGETS_DIR / "F2RL1_PAR2.fasta",
            "chain_id": "A",
            "chunk": None,
            "rationale": "Full GPCR (~395 aa)",
        },
        "nr3c1": {
            "fasta": TARGETS_DIR / "NR3C1_GR.fasta",
            "chain_id": "A",
            "chunk": (502, 777),     # LBD only
            "rationale": "Ligand binding domain (LBD)",
        },
    }

    n_yaml = 0
    for tname, tinfo in targets.items():
        if not tinfo["fasta"].exists():
            print(f"  ⚠️  {tinfo['fasta']} not found, skipping {tname}")
            continue
        seq = read_fasta_chunk(
            tinfo["fasta"],
            tinfo["chunk"][0] if tinfo["chunk"] else None,
            tinfo["chunk"][1] if tinfo["chunk"] else None,
        )
        if not seq:
            print(f"  ⚠️  {tname} sequence empty after slicing, skipping")
            continue
        in_dir = OUT / f"inputs_r6_{tname}"
        in_dir.mkdir(exist_ok=True)
        for i, row in candidates.iterrows():
            smi = row["smiles"]
            cid = f"r6_{tname}_{i}"
            cfg = {
                "version": 1,
                "sequences": [
                    {"protein": {"id": tinfo["chain_id"], "sequence": seq}},
                    {"ligand": {"id": "B", "smiles": smi}},
                ],
                "properties": [
                    {"affinity": {"binder": "B"}},
                ],
            }
            (in_dir / f"{cid}.yaml").write_text(yaml.safe_dump(cfg))
            n_yaml += 1
        print(f"  ✅ {tname} ({len(seq)} aa, {tinfo['rationale']}): {len(candidates)} yamls")

    print(f"\n✅ Generated {n_yaml} R6 cofold yamls (Tier B 신규 4 타겟 × 30 R6 candidates)")
    print(f"\n다음: R5 LOX/MITF 종료 후 다음 chain으로:")
    for tname in targets:
        in_dir = OUT / f"inputs_r6_{tname}"
        out_dir = OUT / f"output_r6_{tname}"
        if in_dir.exists():
            print(f"  boltz predict {in_dir} --out_dir {out_dir} ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
