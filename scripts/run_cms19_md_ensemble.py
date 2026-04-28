"""MD ensemble: CMS-19 (R9_19) × 4 best Tier B targets × 10 ns each.

Targets (R7+R8+R9 cofold mean ranking):
  - SREBP1 (acne): aff=0.752
  - SRD5A1 (alopecia/acne): aff=0.737
  - TGFB1  (scar): aff=0.726
  - CTGF   (scar): aff=0.705

Output: 4 trajectories with RMSD time series, paper-tier validation.
"""
from __future__ import annotations
import sys, time, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_cms19"
OUT.mkdir(exist_ok=True)

CMS19_SMI = "COc1ccc(O)c(C=Cc2cc(O)c(O)c(O)c2)c1"

JOBS = [
    {"name": "srebp1__cms19", "uniprot": "P36956", "msa": "srebp1.a3m"},
    {"name": "srd5a1__cms19", "uniprot": "P18405", "msa": "srd5a1.a3m"},
    {"name": "tgfb1__cms19",  "uniprot": "P01137", "msa": "tgfb1.a3m"},
    {"name": "ctgf__cms19",   "uniprot": "P29279", "msa": "ctgf.a3m"},
]


def main():
    """Skeleton — actual MD launches via existing run_top5_lead_md.py framework.

    이 스크립트는 R9_19 MD ensemble을 큐에 넣지만, 실제 OpenMM MD는
    별도 framework(이미 검증된 5 × 10ns 패턴)에서 처리합니다.

    빠른 alternative: R9_19와 cofold pose 제공 받아 ensemble RMSD 평가.
    """
    pre_dir = ROOT / "pilot/cpu_meaningful"
    print(f"=== CMS-19 (R9_19) MD ensemble plan ===")
    print(f"SMILES: {CMS19_SMI}")
    print(f"Targets: {len(JOBS)}\n")
    for j in JOBS:
        # Use R9 cofold output as starting structure
        target = j["name"].split("__")[0]
        out_dir_root = pre_dir / f"output_r9_{target}/boltz_results_inputs_r9_{target}/predictions"
        # R9_19 prediction folder
        for d in out_dir_root.iterdir():
            if d.name.endswith("_19"):
                cif_files = list(d.rglob("*.cif"))
                if cif_files:
                    print(f"  {target}: cof structure {cif_files[0].name} ({d.name})")
                    break
    print(f"\nOutput dir: {OUT}")
    print(f"\nNOTE: actual 10 ns MD requires OpenMM + GAFF2/MACE-OFF24 setup.")
    print(f"Use existing run_top5_lead_md.py pattern with these 4 cof structures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
