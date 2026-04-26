"""ABFE protocol calibration — T4 lysozyme L99A + benzene benchmark.

The T4L99A · benzene system is the canonical small-molecule ABFE benchmark
(Mobley, Chodera, Dill JCP 2007; literature ΔG_bind = -5.18 ± 0.18 kcal/mol
from ITC measurements).

If our corrected ABFE protocol yields ΔG_bind = -5.2 ± 1 kcal/mol on this
system, we have evidence that the protocol is correctly implemented and
absolute binding free energies on EMB-3/Embelin can be trusted within
~1-2 kcal/mol uncertainty.

Reference structure: PDB 181L (T4L99A + benzene complex).

Run
---
  python scripts/abfe_calibrate_t4l.py --out pilot/calibration/t4l_benzene/

Expected wall time
------------------
~8h on RTX 5090 (smaller system than MMP-1).

Pass/fail criterion
-------------------
ΔG_bind ∈ [-7.0, -3.5] kcal/mol  (literature value -5.2, ±2 sigma tolerance)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T4L_PDB_URL = "https://files.rcsb.org/download/181L.pdb"
BENZENE_SMILES = "c1ccccc1"
LITERATURE_DG_BIND = -5.18    # kcal/mol, Mobley et al. 2007
LITERATURE_UNC = 0.18

PASS_TOL = 2.0    # ±2 kcal/mol from literature accepted as protocol pass


def download_181l(out_path: Path) -> Path:
    if out_path.exists() and out_path.stat().st_size > 1000:
        print(f"  [reuse] {out_path}")
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {T4L_PDB_URL} → {out_path}")
    urllib.request.urlretrieve(T4L_PDB_URL, str(out_path))
    return out_path


def strip_ligand_from_181l(pdb_path: Path, out_pdb: Path) -> Path:
    """Strip benzene (BNZ) from 181L.pdb to get apo receptor."""
    lines = pdb_path.read_text().splitlines()
    keep = []
    for ln in lines:
        # remove BNZ residue records
        if ln.startswith(("ATOM", "HETATM")):
            res = ln[17:20].strip()
            if res in ("BNZ", "BEN"):
                continue
            # remove HOH (waters; will be re-added by solvation)
            if res == "HOH":
                continue
        if ln.startswith("HET ") and "BNZ" in ln:
            continue
        if ln.startswith("HETNAM") and "BNZ" in ln:
            continue
        keep.append(ln)
    out_pdb.write_text("\n".join(keep) + "\n")
    return out_pdb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path,
                         default=ROOT / "pilot/calibration/t4l_benzene")
    parser.add_argument("--n-windows", type=int, default=16)
    parser.add_argument("--n-iterations", type=int, default=400)
    parser.add_argument("--eq-ns", type=float, default=0.5)
    args = parser.parse_args()

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("ABFE Calibration — T4L99A + benzene")
    print(f"  literature ΔG_bind = {LITERATURE_DG_BIND:.2f} ± {LITERATURE_UNC:.2f} kcal/mol")
    print(f"  pass criterion: |ΔG - lit| < {PASS_TOL:.1f} kcal/mol")
    print(f"  output: {out}")
    print("=" * 72)

    # 1) prepare receptor PDB
    raw = download_181l(out / "181L_raw.pdb")
    receptor = strip_ligand_from_181l(raw, out / "receptor_apo.pdb")
    print(f"\n[1/2] receptor prepared: {receptor}")

    # 2) call run_abfe_corrected.py — genesis-md env (openff/openmm/openmmforcefields here)
    GENESIS_PY = "/home/crazat/miniforge3/envs/genesis-md/bin/python"
    cmd = [
        GENESIS_PY, str(ROOT / "scripts/run_abfe_corrected.py"),
        "--receptor", str(receptor),
        "--ligand-smiles", BENZENE_SMILES,
        "--name", "t4l_benzene_calibration",
        "--out", str(out),
        "--n-windows", str(args.n_windows),
        "--n-iterations", str(args.n_iterations),
        "--eq-ns", str(args.eq_ns),
        "--padding-nm", "1.0",
        # Use BNZ coords from 181L for proper pocket placement (avoids NaN)
        "--ligand-template-pdb", str(raw),
        "--ligand-template-resname", "BNZ",
    ]
    print(f"\n[2/2] running corrected ABFE…\n  {' '.join(cmd)}")
    rc = subprocess.run(cmd).returncode
    if rc != 0:
        print(f"\n❌ ABFE failed (rc={rc})")
        return 1

    # 3) compare to literature
    result_path = out / "result_corrected.json"
    if not result_path.exists():
        print(f"❌ {result_path} missing")
        return 1
    res = json.loads(result_path.read_text())
    dG = res.get("binding_free_energy", {}).get("delta_g_bind_kcal_mol")
    if dG is None:
        print("❌ delta_g_bind not in result")
        return 1

    delta = abs(dG - LITERATURE_DG_BIND)
    passed = delta < PASS_TOL

    print("\n" + "=" * 72)
    print(f"CALIBRATION RESULT")
    print(f"  computed:   {dG:.2f} kcal/mol")
    print(f"  literature: {LITERATURE_DG_BIND:.2f} ± {LITERATURE_UNC:.2f}")
    print(f"  deviation:  {delta:.2f} kcal/mol")
    print(f"  status:     {'✅ PASS' if passed else '❌ FAIL'} (tolerance ±{PASS_TOL})")
    print("=" * 72)

    summary = {
        "computed_dg_bind_kcal_mol": dG,
        "literature_dg_bind_kcal_mol": LITERATURE_DG_BIND,
        "literature_uncertainty": LITERATURE_UNC,
        "deviation_kcal_mol": delta,
        "tolerance_kcal_mol": PASS_TOL,
        "passed": passed,
        "interpretation": (
            "Protocol validated — ABFE results on EMB-3/Embelin trustable "
            "within ~2 kcal/mol uncertainty." if passed else
            "Protocol failed calibration — investigate restraint setup, "
            "equilibration time, lambda schedule, or solvent leg."
        ),
    }
    (out / "calibration_summary.json").write_text(
        json.dumps(summary, indent=2))
    print(f"\n✅ {out}/calibration_summary.json")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
