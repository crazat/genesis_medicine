"""
ABFE benchmark — Phase 4 prep for 15 ChEMBL MMP-1 reference inhibitors.

Builds complex.parm7/rst7 for each compound using the same protocol as the
EMB-3/embelin runs (GAFF-2.11 + AM1-BCC + ZAFF Zn nonbonded), but with
Vina-docked starting poses instead of MCS alignment.

Pipeline per compound:
  1. RDKit ETKDG 3D embedding from SMILES + formal-charge detection
  2. obabel PDBQT export
  3. AutoDock Vina rigid docking (grid centered on Zn at (40.32, 27.89, 36.94))
  4. Top pose -> SDF (written to {chembl_id}/complex/lig.sdf)
  5. antechamber AM1-BCC -> mol2 (with -nc <formal_charge>; required for
     hydroxamates/carboxylates/sulfonates that are anionic at pH 7)
  6. parmchk2 -> frcmod
  7. tleap merge with mmp1_holo -> complex.parm7/rst7

Output layout (matches what warmup_generic / production_generic /
production_mss expect; in earlier revisions tleap outputs were written flat
in {chembl_id}/, requiring a manual post-prep reorganization):

  pilot/abfe_benchmark_chembl/{chembl_id}/
      lig_pre.sdf, lig.pdbqt, docked.pdbqt, mmp1_holo.pdb, *.log    (intermediates)
      complex/
          lig.sdf, lig.mol2, lig.frcmod, complex.parm7, complex.rst7
          tleap_complex.in, PHASE4_OK
  pilot/abfe_benchmark_chembl/manifest.json
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data/chembl_mmp1_calibration.csv"
OUT_BASE = ROOT / "pilot/abfe_benchmark_chembl"
OUT_BASE.mkdir(parents=True, exist_ok=True)

HOLO_PARM7 = ROOT / "pilot/abfe_mmp1_holo_zn/mmp1_holo.parm7"
HOLO_RST7 = ROOT / "pilot/abfe_mmp1_holo_zn/mmp1_holo.rst7"
RECEPTOR_PDB = ROOT / "pilot/abfe_mmp1_holo_zn/1HFC_chainA_holo.pdb"

# Zn active-site center (from parm7 inspection)
ZN_CENTER = (40.32, 27.89, 36.94)
GRID_SIZE = (25.0, 25.0, 25.0)

CONDA_BIN = "/home/crazat/miniforge3/envs/genesis-md/bin"


def run(cmd: list[str], cwd: Path | None = None, log: Path | None = None, env: dict | None = None) -> tuple[int, str, str]:
    print(f"  $ {' '.join(cmd[:5])}{'...' if len(cmd)>5 else ''}")
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, env=env)
    if log:
        log.write_text(f"# cmd: {' '.join(cmd)}\n# rc: {proc.returncode}\n\n## stdout\n{proc.stdout}\n\n## stderr\n{proc.stderr}")
    return proc.returncode, proc.stdout, proc.stderr


def prepare_receptor_pdbqt(out_dir: Path) -> Path:
    """Convert 1HFC chain A holo to receptor.pdbqt via obabel (meeko CLI is broken in this env)."""
    pdbqt = out_dir / "receptor.pdbqt"
    if pdbqt.exists() and pdbqt.stat().st_size > 1000:
        return pdbqt
    pdb_clean = out_dir / "receptor.pdb"
    src = RECEPTOR_PDB.read_text().splitlines()
    keep = [ln for ln in src if (ln.startswith("ATOM") or (ln.startswith("HETATM") and " ZN " in ln))]
    pdb_clean.write_text("\n".join(keep) + "\nEND\n")
    rc, _, _ = run([f"{CONDA_BIN}/obabel", str(pdb_clean), "-O", str(pdbqt), "-xr"],
                   cwd=out_dir, log=out_dir / "receptor_prep.log")
    return pdbqt if pdbqt.exists() and pdbqt.stat().st_size > 1000 else None


def compute_net_charge(smiles: str) -> int:
    """Estimate the net charge antechamber should use for the inhibitor's
    Zn-binding state.

    antechamber's sqm fails with "number of electrons is odd" when the
    charge it computes from the input SDF doesn't match the implicit electron
    count (9/15 compounds failed this way on 2026-05-04). For MMP-1 hydroxamate
    inhibitors the binding form is the deprotonated anion (Zn²⁺ chelation
    requires the conjugate base regardless of bulk pKa ~9 for hydroxamate).
    Passing -nc -1 to antechamber resolves both the parity error and reflects
    the actual bound-state charge.

    Strategy:
      1. Start from RDKit's formal charge on the parsed SMILES (handles
         already-deprotonated inputs e.g. trailing "[O-]").
      2. If still 0, scan for known anionic functional groups via SMARTS
         (hydroxamate, carboxylate, sulfonate, phosphonate, tetrazole) and
         subtract one per match. Cap at -2 to avoid over-counting on
         pathological inputs.

    Verified 2026-05-06: CHEMBL406 (Prinomastat, hydroxamate) prep succeeded
    with -nc -1; this function returns -1 for that SMILES via the hydroxamate
    SMARTS branch.
    """
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return 0

    formal = Chem.GetFormalCharge(mol)
    if formal != 0:
        return formal

    # SMARTS for groups that are deprotonated in the inhibitor binding form
    # at physiological pH OR when chelating a divalent cation. The patterns
    # match the neutral acid form because that is how SMILES authors usually
    # write these manifests.
    anion_smarts = [
        ("hydroxamate",   "[CX3](=O)[NX3H][OX2H]"),         # R-C(=O)-NH-OH
        ("carboxylate",   "[CX3](=O)[OX2H]"),                # R-COOH
        ("sulfonate",     "[SX4](=O)(=O)[OX2H]"),            # R-SO3H
        ("phosphonate",   "[PX4](=O)([OX2H])[OX2H]"),        # R-PO(OH)2 -> -1 (mono)
        ("tetrazole",     "c1nnn[nH]1"),                     # tetrazole
        # Acyl sulfonamide a.k.a. sulfonyl-acyl-imide R-SO2-NH-C(=O)-R':
        # NH pKa ~5-6 (drug-relevant; e.g. CGS27023A binds MMPs as the anion)
        ("acyl_sulfonamide", "[SX4](=O)(=O)[NX3H][CX3]=O"),
    ]
    n_anions = 0
    for _name, smarts in anion_smarts:
        patt = Chem.MolFromSmarts(smarts)
        if patt is None:
            continue
        matches = mol.GetSubstructMatches(patt)
        n_anions += len(matches)

    return max(-2, -n_anions)


def prepare_ligand(chembl_id: str, smiles: str, out_dir: Path) -> Path | None:
    """RDKit ETKDG embed SMILES -> SDF."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"  FAIL parse SMILES: {smiles}")
        return None
    mol = Chem.AddHs(mol)
    rc = AllChem.EmbedMolecule(mol, randomSeed=42, useRandomCoords=False)
    if rc != 0:
        rc = AllChem.EmbedMolecule(mol, randomSeed=42, useRandomCoords=True)
    AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    mol.SetProp("_Name", chembl_id)
    sdf = out_dir / "lig_pre.sdf"
    Chem.SDWriter(str(sdf)).write(mol)
    return sdf


def vina_dock(lig_sdf: Path, receptor_pdbqt: Path, out_dir: Path) -> Path | None:
    """Convert lig SDF -> PDBQT via obabel, run Vina, save best pose as docked.sdf."""
    lig_pdbqt = out_dir / "lig.pdbqt"
    rc, _, _ = run([f"{CONDA_BIN}/obabel", str(lig_sdf), "-O", str(lig_pdbqt), "-h"],
                   cwd=out_dir, log=out_dir / "ligprep.log")
    if rc != 0 or not lig_pdbqt.exists() or lig_pdbqt.stat().st_size < 200:
        print("  FAIL ligand pdbqt prep")
        return None

    docked_pdbqt = out_dir / "docked.pdbqt"
    rc, _, _ = run([
        f"{CONDA_BIN}/vina",
        "--receptor", str(receptor_pdbqt),
        "--ligand", str(lig_pdbqt),
        "--out", str(docked_pdbqt),
        "--center_x", str(ZN_CENTER[0]),
        "--center_y", str(ZN_CENTER[1]),
        "--center_z", str(ZN_CENTER[2]),
        "--size_x", str(GRID_SIZE[0]),
        "--size_y", str(GRID_SIZE[1]),
        "--size_z", str(GRID_SIZE[2]),
        "--num_modes", "5",
        "--exhaustiveness", "16",
        "--cpu", "2",
        "--seed", "42",
    ], cwd=out_dir, log=out_dir / "vina.log")
    if rc != 0 or not docked_pdbqt.exists():
        print(f"  FAIL Vina dock rc={rc}")
        return None

    # Convert top pose (first model) back to SDF via obabel, adding hydrogens
    # (Vina PDBQT only has polar Hs — antechamber needs all Hs for AM1-BCC)
    cx_dir = out_dir / "complex"
    cx_dir.mkdir(parents=True, exist_ok=True)
    docked_sdf = cx_dir / "lig.sdf"
    rc, _, _ = run([f"{CONDA_BIN}/obabel", str(docked_pdbqt), "-O", str(docked_sdf), "-l", "1", "-h"],
                   cwd=out_dir, log=out_dir / "export.log")
    if not docked_sdf.exists() or docked_sdf.stat().st_size < 100:
        return None
    # Sanity: check heavy + H atom count is reasonable for the SMILES
    try:
        from rdkit import Chem
        m = Chem.SDMolSupplier(str(docked_sdf), removeHs=False)[0]
        if m is None:
            return None
        n_atoms = m.GetNumAtoms()
        # If too few atoms (Hs missing), regenerate via RDKit
        if n_atoms < 20:
            print(f"  WARN: docked SDF has only {n_atoms} atoms — regenerating Hs via RDKit")
            from rdkit.Chem import AllChem
            mh = Chem.AddHs(m, addCoords=True)
            Chem.SDWriter(str(docked_sdf)).write(mh)
    except Exception as e:
        print(f"  RDKit sanity check failed: {e}")
    return docked_sdf


def _run_antechamber(lig_sdf: Path, mol2: Path, cx_dir: Path, log: Path, nc: int) -> int:
    rc, _, _ = run([
        f"{CONDA_BIN}/antechamber",
        "-i", str(lig_sdf), "-fi", "sdf",
        "-o", str(mol2), "-fo", "mol2",
        "-c", "bcc", "-s", "2", "-rn", "LIG", "-pf", "y", "-at", "gaff2",
        "-nc", str(nc),
    ], cwd=cx_dir, log=log)
    return rc


def build_complex(chembl_id: str, lig_sdf: Path, out_dir: Path, net_charge: int) -> tuple[bool, dict]:
    """Run antechamber + parmchk2 + tleap to produce complex/complex.parm7/rst7.

    All artifacts that downstream warmup_generic / production_generic /
    production_mss expect are written into out_dir/complex/. Intermediates
    (logs, mmp1_holo.pdb) stay at out_dir top level.
    """
    cx_dir = out_dir / "complex"
    cx_dir.mkdir(parents=True, exist_ok=True)

    # antechamber — try the SMARTS-detected charge first, then retry with
    # ±1 if sqm reports odd electron count. The Vina+obabel pipeline
    # sometimes preserves the hydroxamate OH proton and sometimes strips
    # it; either parity can hit "odd electrons" at the inferred charge.
    # Worked-example cases: CHEMBL415 succeeded at -nc 0, CHEMBL406 at
    # -nc -1, CHEMBL443684 at -nc 0 (we infer -1 from SMARTS first).
    mol2 = cx_dir / "lig.mol2"
    log_path = out_dir / "antechamber.log"
    candidates = [net_charge, net_charge + 1, net_charge - 1]
    # de-dup while preserving order
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]
    rc = 1
    used_nc = None
    for nc in candidates:
        rc = _run_antechamber(lig_sdf, mol2, cx_dir, log_path, nc)
        if rc == 0 and mol2.exists():
            used_nc = nc
            if nc != net_charge:
                print(f"  antechamber retry succeeded at -nc {nc} (initial guess was {net_charge})")
            break
    if rc != 0 or not mol2.exists():
        return False, {"step": "antechamber", "rc": rc, "net_charge_tried": candidates}
    net_charge = used_nc

    # parmchk2
    frcmod = cx_dir / "lig.frcmod"
    rc, _, _ = run([f"{CONDA_BIN}/parmchk2", "-i", str(mol2), "-f", "mol2", "-o", str(frcmod), "-s", "2"],
                   cwd=cx_dir, log=out_dir / "parmchk2.log")
    if rc != 0 or not frcmod.exists():
        return False, {"step": "parmchk2", "rc": rc}

    # parmed export holo to pdb (inline — avoid python3 PATH resolution issue)
    holo_pdb = out_dir / "mmp1_holo.pdb"
    if not holo_pdb.exists():
        try:
            import parmed as pmd
            p = pmd.load_file(str(HOLO_PARM7), str(HOLO_RST7))
            p.save(str(holo_pdb), overwrite=True)
        except Exception as e:
            print(f"  FAIL parmed export: {e}")
            return False, {"step": "parmed_export", "error": str(e)}
    if not holo_pdb.exists():
        return False, {"step": "parmed_export", "error": "no output"}

    # tleap runs inside complex/; reference the holo PDB via relative path (../)
    leap_in = cx_dir / "tleap_complex.in"
    leap_in.write_text(
        f"source leaprc.protein.ff14SB\n"
        f"source leaprc.water.tip3p\n"
        f"source leaprc.gaff2\n"
        f"loadAmberParams frcmod.ions234lm_126_tip3p\n"
        f"loadAmberParams {frcmod.name}\n"
        f"LIG = loadMol2 {mol2.name}\n"
        f"mol = loadPdb ../{holo_pdb.name}\n"
        f"complex = combine {{ mol LIG }}\n"
        f"solvateBox complex TIP3PBOX 12.0\n"
        f"addIons complex Na+ 0\n"
        f"addIons complex Cl- 0\n"
        f"saveAmberParm complex complex.parm7 complex.rst7\n"
        f"quit\n"
    )
    rc, _, _ = run([f"{CONDA_BIN}/tleap", "-f", str(leap_in.name)], cwd=cx_dir, log=out_dir / "tleap.log")
    if rc != 0 or not (cx_dir / "complex.parm7").exists():
        return False, {"step": "tleap", "rc": rc}

    # Validate
    import parmed as pmd
    cx = pmd.load_file(str(cx_dir / "complex.parm7"), str(cx_dir / "complex.rst7"))
    n_zn = sum(1 for a in cx.atoms if a.element_name == "Zn" or a.name == "ZN")
    n_lig = sum(1 for r in cx.residues if r.name == "LIG")
    return (n_zn >= 1 and n_lig >= 1), {
        "net_charge": net_charge,
        "complex_atoms": len(cx.atoms),
        "complex_residues": len(cx.residues),
        "zn_atoms": n_zn,
        "lig_residues": n_lig,
        "box_A": list(cx.box[:3]),
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=None,
                    help="Restrict to specific ChEMBL IDs (repeatable). Default: all rows in calibration CSV.")
    args = ap.parse_args()

    if not DATA_CSV.exists():
        print(f"FAIL: missing {DATA_CSV}")
        return 1

    if not Path(f"{CONDA_BIN}/vina").exists():
        print(f"FAIL: vina not yet installed at {CONDA_BIN}/vina")
        return 2

    # Read reference compounds (optionally filtered)
    compounds = []
    with DATA_CSV.open() as f:
        for row in csv.DictReader(f):
            if args.only and row["chembl_id"] not in args.only:
                continue
            compounds.append(row)
    print(f"loaded {len(compounds)} reference compounds")

    # Common dir for shared assets
    common_dir = OUT_BASE / "_shared"
    common_dir.mkdir(parents=True, exist_ok=True)

    print(f"preparing receptor pdbqt -> {common_dir}/receptor.pdbqt")
    receptor_pdbqt = prepare_receptor_pdbqt(common_dir)
    if receptor_pdbqt is None:
        print("FAIL: receptor pdbqt prep")
        return 3

    manifest = {"compounds": [], "common": {"receptor_pdbqt": str(receptor_pdbqt.relative_to(ROOT)),
                                            "zn_center": list(ZN_CENTER), "grid_size": list(GRID_SIZE)}}

    for cmp in compounds:
        chembl_id = cmp["chembl_id"]
        smiles = cmp["smiles"]
        ic50_nm = float(cmp["ic50_nm"])
        out_dir = OUT_BASE / chembl_id
        out_dir.mkdir(parents=True, exist_ok=True)
        info = {"chembl_id": chembl_id, "smiles": smiles, "ic50_nm": ic50_nm,
                "reference": cmp.get("reference", ""), "notes": cmp.get("notes", "")}
        print(f"\n=== {chembl_id} ic50={ic50_nm} nM ===")

        # PHASE4_OK lives inside complex/ to match what warmup_generic /
        # production_generic / production_mss expect. Tolerate the legacy
        # top-level marker that earlier prepare runs produced.
        if (out_dir / "complex" / "PHASE4_OK").exists() or (out_dir / "PHASE4_OK").exists():
            print(f"  already prepared, skipping")
            info["status"] = "ok"
            manifest["compounds"].append(info)
            continue

        net_charge = compute_net_charge(smiles)
        if net_charge != 0:
            print(f"  detected formal net charge: {net_charge:+d} (passing -nc to antechamber)")
        info["net_charge"] = net_charge

        t0 = time.time()
        sdf_pre = prepare_ligand(chembl_id, smiles, out_dir)
        if sdf_pre is None:
            info["status"] = "fail_ligand"
            manifest["compounds"].append(info)
            continue

        sdf_docked = vina_dock(sdf_pre, receptor_pdbqt, out_dir)
        if sdf_docked is None:
            info["status"] = "fail_vina"
            manifest["compounds"].append(info)
            continue

        ok, build_info = build_complex(chembl_id, sdf_docked, out_dir, net_charge)
        info.update(build_info)
        info["wall_min"] = round((time.time() - t0) / 60.0, 2)
        if ok:
            (out_dir / "complex" / "PHASE4_OK").touch()
            info["status"] = "ok"
            print(f"  PHASE4_OK in {info['wall_min']} min")
        else:
            info["status"] = f"fail_{build_info.get('step', 'build')}"
            print(f"  FAILED at {info['status']}")
        manifest["compounds"].append(info)

    # When --only restricted the run to a subset, merge into the existing
    # manifest rather than overwriting it (otherwise per-compound smoke tests
    # would erase the rest of the table).
    manifest_path = OUT_BASE / "manifest.json"
    if args.only and manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        new_by_id = {c["chembl_id"]: c for c in manifest["compounds"]}
        merged = []
        for c in existing.get("compounds", []):
            merged.append(new_by_id.pop(c["chembl_id"], c))
        merged.extend(new_by_id.values())
        manifest = {**existing, "compounds": merged}
    manifest_path.write_text(json.dumps(manifest, indent=2))
    n_ok = sum(1 for c in manifest["compounds"] if c.get("status") == "ok")
    print(f"\n=== summary: {n_ok}/{len(manifest['compounds'])} compounds in manifest OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
