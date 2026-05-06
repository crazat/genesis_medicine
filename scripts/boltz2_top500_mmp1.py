"""
Boltz-2 affinity prediction on xtb top500 NPC compounds vs MMP-1.

Cross-validates the xtb topical_refine_score ranking (cohort #1, hetero>=2,
192-conf refine) with ML-based protein-ligand affinity prediction. Output
correlation feeds into:
  - #08 abfe_methodology Section "ranking robustness across fidelity layers"
  - #15 universal_scaffold v1.1 Methods (multi-fidelity confirmation)
  - #18 active_learning_multifidelity (Boltz-2 as a fidelity tier)

Inputs:
  pilot/cpu_meaningful/xtb_npass_top500_hetero2_refine_192conf.csv
  data/msa/mmp1.a3m  (MMP-1 catalytic-domain MSA)

Outputs:
  pilot/boltz2_top500_mmp1/inputs/*.yaml  (one per compound)
  pilot/boltz2_top500_mmp1/boltz_results_inputs/
  pilot/boltz2_top500_mmp1/affinity_consolidated.csv
  pilot/boltz2_top500_mmp1/summary.json
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/crazat/genesis_medicine")
TOP_CSV = ROOT / "pilot/cpu_meaningful/xtb_npass_top500_hetero2_refine_192conf.csv"
MSA_PATH = ROOT / "data/msa/mmp1.a3m"
OUT = ROOT / "pilot/boltz2_top500_mmp1"
INPUTS = OUT / "inputs"
OUT.mkdir(parents=True, exist_ok=True)
INPUTS.mkdir(parents=True, exist_ok=True)

BOLTZ_BIN = ROOT / ".venv/bin/boltz"

# Same MMP-1 catalytic-domain sequence as boltz2_calibration_mmp1.py uses.
MMP1_SEQ = (
    "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADIL"
    "VVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGH"
    "SLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"
)

YAML_TEMPLATE = """version: 1
sequences:
- protein:
    id: A
    sequence: {seq}
    msa: {msa}
- ligand:
    id: B
    smiles: {smiles}
properties:
- affinity:
    binder: B
"""


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", s)


def write_yaml_inputs() -> int:
    """Build one YAML per top500 compound. Returns count written."""
    if not TOP_CSV.exists():
        print(f"FAIL: missing {TOP_CSV}")
        return -1
    if not MSA_PATH.exists():
        print(f"FAIL: missing MSA {MSA_PATH}")
        return -1

    n = 0
    with TOP_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            np_id = row.get("np_id") or row.get("compound_id") or f"row_{n}"
            smiles = row["smiles"]
            yaml_path = INPUTS / f"mmp1__{safe_id(np_id)}.yaml"
            yaml_path.write_text(
                YAML_TEMPLATE.format(seq=MMP1_SEQ, msa=str(MSA_PATH), smiles=smiles)
            )
            n += 1
    print(f"[B] wrote {n} YAML inputs -> {INPUTS}")
    return n


def run_boltz() -> int:
    """Run boltz predict on the inputs dir. Returns rc."""
    cmd = [
        str(BOLTZ_BIN),
        "predict",
        str(INPUTS),
        "--out_dir", str(OUT),
        "--accelerator", "gpu",
        "--devices", "1",
        "--num_workers", "1",
        "--diffusion_samples", "1",
        "--sampling_steps", "200",
        "--recycling_steps", "3",
        "--output_format", "mmcif",
    ]
    print(f"[B] running: {' '.join(cmd)}")
    log = OUT / "boltz_run.log"
    with log.open("w") as f:
        f.write(f"# {' '.join(cmd)}\n# started {time.strftime('%Y-%m-%dT%H:%M:%S')}\n\n")
        proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    print(f"[B] boltz rc={proc.returncode}, log={log}")
    return proc.returncode


def consolidate() -> None:
    """Walk boltz_results dir, pull out affinity scores, write consolidated csv."""
    results_dir = OUT / "boltz_results_inputs"
    if not results_dir.exists():
        print(f"WARN: no results dir {results_dir}")
        return

    rows = []
    for affinity_json in sorted(results_dir.rglob("affinity_*.json")):
        try:
            data = json.loads(affinity_json.read_text())
            comp_dir = affinity_json.parent.name
            np_id = comp_dir.replace("mmp1__", "")
            rows.append({
                "np_id": np_id,
                "affinity_pred": data.get("affinity_pred_value"),
                "affinity_prob_binary": data.get("affinity_probability_binary"),
                "json_file": str(affinity_json.relative_to(ROOT)),
            })
        except Exception as e:
            print(f"  skip {affinity_json}: {e}")

    csv_path = OUT / "affinity_consolidated.csv"
    with csv_path.open("w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f"[B] consolidated {len(rows)} affinity rows -> {csv_path}")


def main() -> int:
    start = time.time()
    n = write_yaml_inputs()
    if n <= 0:
        return 1

    rc = run_boltz()

    consolidate()

    summary = {
        "phase": "Boltz-2 affinity batch on xtb top500 vs MMP-1",
        "n_inputs": n,
        "boltz_rc": rc,
        "wallclock_minutes": round((time.time() - start) / 60.0, 2),
        "outputs": {
            "inputs_dir": "pilot/boltz2_top500_mmp1/inputs/",
            "results_dir": "pilot/boltz2_top500_mmp1/boltz_results_inputs/",
            "affinity_csv": "pilot/boltz2_top500_mmp1/affinity_consolidated.csv",
            "boltz_log": "pilot/boltz2_top500_mmp1/boltz_run.log",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUT / ("BOLTZ_OK" if rc == 0 else "BOLTZ_FAIL")).touch()
    return 0 if rc == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
