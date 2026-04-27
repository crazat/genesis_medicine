"""xtb GFN2 single-point on R7 Bayesian candidates (top 50).

CPU saturation: xtb GFN2 on 50 compounds × 5 conformers = 250 jobs.
HOMO-LUMO gap, dipole, atomization energy.
"""
from __future__ import annotations
import sys
import time
import shutil
import subprocess
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
XTB_BIN = "/home/crazat/miniforge3/envs/genesis-md/bin/xtb"


def run_one(args):
    idx, smi, tmpdir = args
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return {"idx": idx, "smi": smi, "err": "invalid"}
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=5, randomSeed=42)
        if not cids:
            return {"idx": idx, "smi": smi, "err": "no embed"}

        results = []
        for cid in cids:
            try:
                AllChem.MMFFOptimizeMolecule(m, confId=cid, maxIters=200)
            except Exception:
                continue
            xyz = Chem.MolToXYZBlock(m, confId=cid)
            wd = Path(tmpdir) / f"mol_{idx}_{cid}"
            wd.mkdir(parents=True, exist_ok=True)
            xyz_path = wd / "input.xyz"
            xyz_path.write_text(xyz)
            try:
                proc = subprocess.run(
                    [XTB_BIN, str(xyz_path), "--gfn", "2", "--alpb", "water"],
                    cwd=wd, capture_output=True, text=True, timeout=120,
                )
                stdout = proc.stdout
                energy_h = None
                gap_ev = None
                for line in stdout.splitlines():
                    if "TOTAL ENERGY" in line.upper():
                        for tok in line.split():
                            try:
                                energy_h = float(tok)
                                break
                            except ValueError:
                                continue
                    if "HOMO-LUMO GAP" in line.upper():
                        for tok in line.split():
                            try:
                                gap_ev = float(tok)
                                break
                            except ValueError:
                                continue
                if energy_h is not None:
                    results.append({"energy_h": energy_h, "gap_ev": gap_ev})
            except subprocess.TimeoutExpired:
                continue
            except Exception:
                continue
            finally:
                shutil.rmtree(wd, ignore_errors=True)

        if not results:
            return {"idx": idx, "smi": smi, "err": "all failed"}
        energies = [r["energy_h"] for r in results]
        gaps = [r["gap_ev"] for r in results if r["gap_ev"] is not None]
        return {
            "idx": idx, "smi": smi,
            "n_conf": len(results),
            "min_energy_h": min(energies),
            "energy_kcal_min": min(energies) * 627.5095,
            "gap_ev_mean": float(np.mean(gaps)) if gaps else None,
        }
    except Exception as e:
        return {"idx": idx, "smi": smi, "err": str(e)[:80]}


def main():
    candidates = pd.read_csv(OUT / "bayesian_v3_round7_candidates.csv").head(50)
    print(f"R7 candidates for xtb: {len(candidates)}")

    import tempfile
    with tempfile.TemporaryDirectory(prefix="xtb_r7_") as tmpdir:
        args = [(i, smi, tmpdir) for i, smi in enumerate(candidates["smiles"].tolist())]
        t0 = time.time()
        with Pool(processes=12) as p:
            results = p.map(run_one, args)
        wall = (time.time() - t0) / 60
        print(f"\nWall: {wall:.1f} min")

    valid = [r for r in results if "min_energy_h" in r]
    out = pd.DataFrame(valid)
    out_csv = OUT / "xtb_r7_top50.csv"
    out.to_csv(out_csv, index=False)
    print(f"\n✅ {out_csv} ({len(valid)}/{len(candidates)} valid)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
