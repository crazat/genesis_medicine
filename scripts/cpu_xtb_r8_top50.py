"""xtb GFN2 on R8 top 50 — CPU heavy."""
from __future__ import annotations
import sys, time, shutil, subprocess
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
        if m is None: return {"idx": idx, "err": "invalid"}
        m = Chem.AddHs(m)
        cids = AllChem.EmbedMultipleConfs(m, numConfs=5, randomSeed=42)
        if not cids: return {"idx": idx, "err": "no embed"}
        results = []
        for cid in cids:
            try: AllChem.MMFFOptimizeMolecule(m, confId=cid, maxIters=200)
            except Exception: continue
            xyz = Chem.MolToXYZBlock(m, confId=cid)
            wd = Path(tmpdir) / f"mol_{idx}_{cid}"
            wd.mkdir(parents=True, exist_ok=True)
            xyz_path = wd / "input.xyz"
            xyz_path.write_text(xyz)
            try:
                proc = subprocess.run([XTB_BIN, str(xyz_path), "--gfn", "2",
                                          "--alpb", "water"],
                                      cwd=wd, capture_output=True, text=True, timeout=120)
                stdout = proc.stdout
                e_h, g_ev = None, None
                for line in stdout.splitlines():
                    if "TOTAL ENERGY" in line.upper():
                        for tok in line.split():
                            try: e_h = float(tok); break
                            except ValueError: continue
                    if "HOMO-LUMO GAP" in line.upper():
                        for tok in line.split():
                            try: g_ev = float(tok); break
                            except ValueError: continue
                if e_h is not None: results.append({"e": e_h, "g": g_ev})
            except Exception: continue
            finally: shutil.rmtree(wd, ignore_errors=True)
        if not results: return {"idx": idx, "err": "all failed"}
        e = [r["e"] for r in results]
        g = [r["g"] for r in results if r["g"] is not None]
        return {"idx": idx, "smi": smi, "n_conf": len(results),
                "energy_h_min": min(e), "energy_kcal_min": min(e) * 627.5095,
                "gap_ev_mean": float(np.mean(g)) if g else None}
    except Exception as e:
        return {"idx": idx, "err": str(e)[:80]}


def main():
    candidates = pd.read_csv(OUT / "bayesian_v4_round8_candidates.csv").head(50)
    print(f"R8 candidates for xtb: {len(candidates)}")
    import tempfile
    with tempfile.TemporaryDirectory(prefix="xtb_r8_") as tmpdir:
        args = [(i, candidates.iloc[i]["smiles"], tmpdir) for i in range(len(candidates))]
        t0 = time.time()
        with Pool(16) as p:
            results = p.map(run_one, args)
        wall = (time.time() - t0) / 60
        print(f"\nWall: {wall:.1f} min")
    valid = [r for r in results if "energy_h_min" in r]
    out = pd.DataFrame(valid)
    out_csv = OUT / "xtb_r8_top50.csv"
    out.to_csv(out_csv, index=False)
    print(f"\n✅ {out_csv} ({len(valid)}/{len(candidates)} valid)")


if __name__ == "__main__":
    sys.exit(main())
