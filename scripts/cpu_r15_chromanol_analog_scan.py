"""CPU-only focused analog scan for the R15 chromanol fragment.

Purpose:
  - Use idle CPU while GPU MD is running.
  - Explore topical-path analogs that may lift logP above the skin window
    while preserving the small chromanol core.
  - Avoid TensorFlow/ADMET-AI entirely; this is RDKit + xTB only.

Output:
  pilot/cpu_meaningful/r15_chromanol_analog_scan.csv
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Crippen, Descriptors, QED, rdMolDescriptors
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams


RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
OUT.mkdir(parents=True, exist_ok=True)

XTB_BIN = Path("/home/crazat/miniforge3/envs/genesis-md/bin/xtb")
SEED = "OCC1COc2cc(O)ccc2C1"

SUBSTITUENTS = {
    "F": [("F", None)],
    "Cl": [("Cl", None)],
    "Me": [("C", None)],
    "OH": [("O", None)],
    "OMe": [("O", "C")],
    "CH2OH": [("C", "O")],
    "CN": [("C", "N")],
}

DOUBLE_SUBSTITUENTS = ["F", "Me", "OMe", "OH"]
MAX_XTB = 80
POOL_SIZE = 10


def catalog() -> FilterCatalog:
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_A)
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_B)
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_C)
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
    return FilterCatalog(params)


FILTERS = catalog()


def aromatic_sites(mol: Chem.Mol) -> list[int]:
    return [
        atom.GetIdx()
        for atom in mol.GetAtoms()
        if atom.GetIsAromatic()
        and atom.GetAtomicNum() == 6
        and atom.GetTotalNumHs() > 0
    ]


def attach_substituent(mol: Chem.Mol, site: int, sub_name: str) -> Chem.Mol | None:
    rw = Chem.RWMol(mol)
    atoms = SUBSTITUENTS[sub_name]
    first_idx: int | None = None
    prev_idx: int | None = None
    for symbol, _ in atoms:
        atom_idx = rw.AddAtom(Chem.Atom(symbol))
        if first_idx is None:
            first_idx = atom_idx
        if prev_idx is not None:
            bond = Chem.BondType.TRIPLE if sub_name == "CN" and symbol == "N" else Chem.BondType.SINGLE
            rw.AddBond(prev_idx, atom_idx, bond)
        prev_idx = atom_idx
    assert first_idx is not None
    rw.AddBond(site, first_idx, Chem.BondType.SINGLE)
    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:
        return None
    return out


def enumerate_analogs() -> pd.DataFrame:
    seed = Chem.MolFromSmiles(SEED)
    if seed is None:
        raise RuntimeError("Seed SMILES failed")
    sites = aromatic_sites(seed)

    rows: list[dict[str, object]] = [{
        "analog_id": "R15_chromanol_seed",
        "edit": "seed",
        "smiles": Chem.MolToSmiles(seed),
    }]
    seen = {Chem.MolToSmiles(seed)}

    for site in sites:
        for sub in SUBSTITUENTS:
            mol = attach_substituent(seed, site, sub)
            if mol is None:
                continue
            smi = Chem.MolToSmiles(mol)
            if smi in seen:
                continue
            seen.add(smi)
            rows.append({
                "analog_id": f"R15_chromanol_{sub}_pos{site}",
                "edit": f"{sub}@{site}",
                "smiles": smi,
            })

    # Small double substitutions only; enough to test topical logP lift without
    # exploding the pool or drifting far from the clean chromanol core.
    for site_a, site_b in combinations(sites, 2):
        for sub_a in DOUBLE_SUBSTITUENTS:
            mol_a = attach_substituent(seed, site_a, sub_a)
            if mol_a is None:
                continue
            for sub_b in DOUBLE_SUBSTITUENTS:
                mol_b = attach_substituent(mol_a, site_b, sub_b)
                if mol_b is None:
                    continue
                smi = Chem.MolToSmiles(mol_b)
                if smi in seen:
                    continue
                seen.add(smi)
                rows.append({
                    "analog_id": f"R15_chromanol_{sub_a}{site_a}_{sub_b}{site_b}",
                    "edit": f"{sub_a}@{site_a};{sub_b}@{site_b}",
                    "smiles": smi,
                })

    return pd.DataFrame(rows)


def rdkit_props(row: pd.Series) -> dict[str, object]:
    mol = Chem.MolFromSmiles(str(row["smiles"]))
    if mol is None:
        return {"valid": False}
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    rotb = rdMolDescriptors.CalcNumRotatableBonds(mol)
    qed = QED.qed(mol)
    log_kp = -2.7 + 0.71 * logp - 0.0061 * mw
    skin_window = (1.0 <= logp <= 3.5) and (mw <= 500) and (tpsa <= 120)
    filter_matches = [m.GetDescription() for m in FILTERS.GetMatches(mol)]
    return {
        "valid": True,
        "MW": round(mw, 2),
        "logP": round(logp, 3),
        "TPSA": round(tpsa, 2),
        "HBD": hbd,
        "HBA": hba,
        "rotb": rotb,
        "QED": round(qed, 3),
        "logKp_potts_guy": round(log_kp, 3),
        "skin_window": skin_window,
        "filter_hit_count": len(filter_matches),
        "filter_hits": ";".join(filter_matches[:5]),
        "pre_xtb_score": round(
            (1.0 if skin_window else 0.0) * 0.35
            + min(max((logp - 0.8) / 2.7, 0.0), 1.0) * 0.20
            + qed * 0.20
            + (1.0 if len(filter_matches) == 0 else 0.0) * 0.20
            + (1.0 if tpsa <= 90 else 0.5 if tpsa <= 120 else 0.0) * 0.05,
            4,
        ),
    }


def parse_xtb(stdout: str) -> tuple[float | None, float | None, float | None, float | None]:
    energy = homo = lumo = gap = None
    for line in stdout.splitlines():
        upper = line.upper()
        vals = [float(x) for x in re.findall(r"[-+]?\d+\.\d+(?:[Ee][-+]?\d+)?", line)]
        if "TOTAL ENERGY" in upper and vals:
            energy = vals[-1]
        elif "(HOMO)" in upper and vals:
            homo = vals[-1]
        elif "(LUMO)" in upper and vals:
            lumo = vals[-1]
        elif "HOMO-LUMO GAP" in upper and vals:
            gap = vals[-1]
    return energy, homo, lumo, gap


def run_xtb(args: tuple[int, str, str]) -> dict[str, object]:
    idx, analog_id, smi = args
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return {"idx": idx, "analog_id": analog_id, "xtb_status": "invalid_smiles"}
        mol = Chem.AddHs(mol)
        cids = AllChem.EmbedMultipleConfs(
            mol, numConfs=3, randomSeed=20260430 + idx, pruneRmsThresh=0.35, numThreads=1
        )
        if not cids:
            return {"idx": idx, "analog_id": analog_id, "xtb_status": "no_conformer"}

        records = []
        with tempfile.TemporaryDirectory(prefix=f"r15_chrom_{idx}_") as tmp:
            tmp_path = Path(tmp)
            for cid in cids:
                try:
                    AllChem.MMFFOptimizeMolecule(mol, confId=cid, maxIters=300)
                except Exception:
                    pass
                wd = tmp_path / f"conf_{cid}"
                wd.mkdir()
                xyz = wd / "input.xyz"
                xyz.write_text(Chem.MolToXYZBlock(mol, confId=cid))
                proc = subprocess.run(
                    [str(XTB_BIN), str(xyz), "--gfn", "2", "--alpb", "water"],
                    cwd=wd,
                    capture_output=True,
                    text=True,
                    timeout=180,
                    env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
                )
                if proc.returncode != 0:
                    continue
                energy, homo, lumo, gap = parse_xtb(proc.stdout)
                if energy is not None:
                    records.append({"energy_au": energy, "HOMO_eV": homo, "LUMO_eV": lumo, "gap_eV": gap})
        if not records:
            return {"idx": idx, "analog_id": analog_id, "xtb_status": "all_failed"}

        best = min(records, key=lambda r: r["energy_au"])
        gaps = [r["gap_eV"] for r in records if r["gap_eV"] is not None]
        return {
            "idx": idx,
            "analog_id": analog_id,
            "xtb_status": "ok",
            "xtb_confs": len(records),
            "energy_au_min": best["energy_au"],
            "HOMO_eV": best["HOMO_eV"],
            "LUMO_eV": best["LUMO_eV"],
            "gap_eV": float(np.mean(gaps)) if gaps else None,
        }
    except subprocess.TimeoutExpired:
        return {"idx": idx, "analog_id": analog_id, "xtb_status": "timeout"}
    except Exception as exc:
        return {"idx": idx, "analog_id": analog_id, "xtb_status": f"error:{str(exc)[:80]}"}


def main() -> int:
    t0 = time.time()
    print("R15 chromanol focused analog scan (RDKit + xTB only)")
    print(f"Seed: {SEED}")
    print(f"Pool size: {POOL_SIZE}, MAX_XTB={MAX_XTB}")

    analogs = enumerate_analogs()
    props = pd.DataFrame([rdkit_props(row) for _, row in analogs.iterrows()])
    df = pd.concat([analogs, props], axis=1)
    df = df[df["valid"]].copy()
    df = df.sort_values(["pre_xtb_score", "QED", "logP"], ascending=False).reset_index(drop=True)

    candidates = df.head(MAX_XTB).copy()
    print(f"Generated {len(df)} valid analogs; running xTB on top {len(candidates)}")
    if not XTB_BIN.exists():
        print(f"xTB missing at {XTB_BIN}; writing RDKit-only output")
        df.to_csv(OUT / "r15_chromanol_analog_scan.csv", index=False)
        return 1

    args = [
        (i, row["analog_id"], row["smiles"])
        for i, row in candidates.reset_index(drop=True).iterrows()
    ]
    with Pool(POOL_SIZE) as pool:
        xtb_rows = pool.map(run_xtb, args)

    xtb = pd.DataFrame(xtb_rows).drop(columns=["idx"], errors="ignore")
    merged = df.merge(xtb, on="analog_id", how="left")
    merged["gap_ok"] = merged["gap_eV"].fillna(0) >= 3.0
    merged["topical_followup_score"] = (
        merged["pre_xtb_score"].fillna(0) * 0.65
        + merged["gap_ok"].astype(float) * 0.20
        + (merged["xtb_status"].eq("ok")).astype(float) * 0.15
    )
    merged = merged.sort_values(
        ["topical_followup_score", "pre_xtb_score", "gap_eV"],
        ascending=False,
    )

    out = OUT / "r15_chromanol_analog_scan.csv"
    merged.to_csv(out, index=False)
    print(f"Saved {out} ({len(merged)} rows)")
    print(f"Wall: {(time.time() - t0) / 60:.1f} min")
    print("\nTop 10 topical-path analogs:")
    cols = [
        "analog_id", "edit", "smiles", "MW", "logP", "QED", "skin_window",
        "filter_hit_count", "gap_eV", "xtb_status", "topical_followup_score",
    ]
    print(merged[cols].head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
