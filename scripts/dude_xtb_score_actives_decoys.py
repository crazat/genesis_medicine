"""F3 DUD-E enrichment: xtb GFN2 single-point score for 15 ChEMBL MMP-1 actives + 314 decoys.

CPU-only, multiprocessing.Pool over actives+decoys.
Output:
  pilot/dude_benchmark_mmp1/scored_all.csv (smiles, source, xtb_energy_au, xtb_gap_eV)

Then feed to dude_decoy_benchmark.py --score-csv to get EF/AUC/BEDROC.
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
ROOT = Path("/home/crazat/genesis_medicine")
OUT = ROOT / "pilot/dude_benchmark_mmp1"
ACTIVES_CSV = ROOT / "data/chembl_mmp1_calibration.csv"
DECOYS_CSV = OUT / "decoys.csv"


def xtb_score(args):
    idx, smi, source = args
    try:
        from xtb.libxtb import VERBOSITY_MUTED
        from xtb.interface import Calculator, Param

        m = Chem.MolFromSmiles(str(smi))
        if not m:
            return {"idx": idx, "smiles": smi, "source": source, "xtb_energy_au": None, "xtb_gap_eV": None}
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True) != 0:
            return {"idx": idx, "smiles": smi, "source": source, "xtb_energy_au": None, "xtb_gap_eV": None}
        AllChem.UFFOptimizeMolecule(m, maxIters=500)

        atoms = np.array([a.GetAtomicNum() for a in m.GetAtoms()], dtype=np.int32)
        conf = m.GetConformer()
        xyz = np.array([list(conf.GetAtomPosition(i)) for i in range(m.GetNumAtoms())], dtype=np.float64)
        xyz_bohr = xyz * 1.8897259886

        calc = Calculator(Param.GFN2xTB, atoms, xyz_bohr)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        energy = float(res.get_energy())
        orbital_e = res.get_orbital_eigenvalues()
        n_occ = int(sum(1 for x in res.get_orbital_occupations() if x > 0.5))
        if n_occ < 1 or n_occ >= len(orbital_e):
            gap_eV = None
        else:
            homo = float(orbital_e[n_occ - 1]) * 27.2114
            lumo = float(orbital_e[n_occ]) * 27.2114
            gap_eV = lumo - homo
        return {"idx": idx, "smiles": smi, "source": source, "xtb_energy_au": energy, "xtb_gap_eV": gap_eV}
    except Exception as e:
        return {"idx": idx, "smiles": smi, "source": source, "xtb_energy_au": None, "xtb_gap_eV": None, "err": str(e)[:100]}


def main():
    actives = pd.read_csv(ACTIVES_CSV)
    decoys = pd.read_csv(DECOYS_CSV)
    print(f"actives={len(actives)} decoys={len(decoys)}")

    tasks = []
    for i, row in actives.iterrows():
        tasks.append((f"a{i}", row["smiles"], "active"))
    for i, row in decoys.iterrows():
        tasks.append((f"d{i}", row["smiles"], "decoy"))
    print(f"total tasks: {len(tasks)}")

    t0 = time.time()
    with Pool(processes=22) as pool:
        results = pool.map(xtb_score, tasks, chunksize=4)
    print(f"xtb done {len(results)} mols in {(time.time()-t0)/60:.1f} min")

    df = pd.DataFrame(results)
    df.to_csv(OUT / "scored_all.csv", index=False)
    n_ok = (df["xtb_energy_au"].notna()).sum()
    print(f"saved {OUT/'scored_all.csv'} ({n_ok}/{len(df)} successful)")


if __name__ == "__main__":
    main()
