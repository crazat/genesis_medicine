"""
ABFE benchmark — Phase 4 prep for 15 ChEMBL MMP-1 reference inhibitors.

Builds complex.parm7/rst7 for each compound using the same protocol as the
EMB-3/embelin runs (GAFF-2.11 + AM1-BCC + ZAFF Zn nonbonded), but with
Vina-docked starting poses instead of MCS alignment. This ensures each
hydroxamate / sulfonamide inhibitor gets a chemistry-aware initial pose
near the catalytic Zn.

Pipeline per compound:
  1. RDKit ETKDG 3D embedding from SMILES
  2. meeko PDBQT export
  3. AutoDock Vina rigid docking (grid centered on Zn at (40.32, 27.89, 36.94))
  4. Top pose -> SDF
  5. antechamber AM1-BCC -> mol2
  6. parmchk2 -> frcmod
  7. tleap merge with mmp1_holo -> complex.parm7/rst7

Output:
  pilot/abfe_benchmark_chembl/{chembl_id}/{lig.sdf, lig.mol2, lig.frcmod, complex.parm7, complex.rst7, ...}
  pilot/abfe_benchmark_chembl/manifest.json (compound_id -> path mapping + experimental Ki)
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
    docked_sdf = out_dir / "lig.sdf"
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


def build_complex(chembl_id: str, lig_sdf: Path, out_dir: Path) -> tuple[bool, dict]:
    """Run antechamber + parmchk2 + tleap to produce complex.parm7/rst7."""
    # antechamber
    mol2 = out_dir / "lig.mol2"
    rc, _, _ = run([
        f"{CONDA_BIN}/antechamber",
        "-i", str(lig_sdf), "-fi", "sdf",
        "-o", str(mol2), "-fo", "mol2",
        "-c", "bcc", "-s", "2", "-rn", "LIG", "-pf", "y", "-at", "gaff2",
    ], cwd=out_dir, log=out_dir / "antechamber.log")
    if rc != 0 or not mol2.exists():
        return False, {"step": "antechamber", "rc": rc}

    # parmchk2
    frcmod = out_dir / "lig.frcmod"
    rc, _, _ = run([f"{CONDA_BIN}/parmchk2", "-i", str(mol2), "-f", "mol2", "-o", str(frcmod), "-s", "2"],
                   cwd=out_dir, log=out_dir / "parmchk2.log")
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

    # tleap
    leap_in = out_dir / "tleap_complex.in"
    leap_in.write_text(
        f"source leaprc.protein.ff14SB\n"
        f"source leaprc.water.tip3p\n"
        f"source leaprc.gaff2\n"
        f"loadAmberParams frcmod.ions234lm_126_tip3p\n"
        f"loadAmberParams {frcmod.name}\n"
        f"LIG = loadMol2 {mol2.name}\n"
        f"mol = loadPdb {holo_pdb.name}\n"
        f"complex = combine {{ mol LIG }}\n"
        f"solvateBox complex TIP3PBOX 12.0\n"
        f"addIons complex Na+ 0\n"
        f"addIons complex Cl- 0\n"
        f"saveAmberParm complex complex.parm7 complex.rst7\n"
        f"quit\n"
    )
    rc, _, _ = run([f"{CONDA_BIN}/tleap", "-f", str(leap_in.name)], cwd=out_dir, log=out_dir / "tleap.log")
    if rc != 0 or not (out_dir / "complex.parm7").exists():
        return False, {"step": "tleap", "rc": rc}

    # Validate
    import parmed as pmd
    cx = pmd.load_file(str(out_dir / "complex.parm7"), str(out_dir / "complex.rst7"))
    n_zn = sum(1 for a in cx.atoms if a.element_name == "Zn" or a.name == "ZN")
    n_lig = sum(1 for r in cx.residues if r.name == "LIG")
    return (n_zn >= 1 and n_lig >= 1), {
        "complex_atoms": len(cx.atoms),
        "complex_residues": len(cx.residues),
        "zn_atoms": n_zn,
        "lig_residues": n_lig,
        "box_A": list(cx.box[:3]),
    }


def main() -> int:
    if not DATA_CSV.exists():
        print(f"FAIL: missing {DATA_CSV}")
        return 1

    if not Path(f"{CONDA_BIN}/vina").exists():
        print(f"FAIL: vina not yet installed at {CONDA_BIN}/vina")
        return 2

    # Read 15 reference compounds
    compounds = []
    with DATA_CSV.open() as f:
        for row in csv.DictReader(f):
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

        if (out_dir / "PHASE4_OK").exists():
            print(f"  already prepared, skipping")
            info["status"] = "ok"
            manifest["compounds"].append(info)
            continue

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

        ok, build_info = build_complex(chembl_id, sdf_docked, out_dir)
        info.update(build_info)
        info["wall_min"] = round((time.time() - t0) / 60.0, 2)
        if ok:
            (out_dir / "PHASE4_OK").touch()
            info["status"] = "ok"
            print(f"  PHASE4_OK in {info['wall_min']} min")
        else:
            info["status"] = f"fail_{build_info.get('step', 'build')}"
            print(f"  FAILED at {info['status']}")
        manifest["compounds"].append(info)

    (OUT_BASE / "manifest.json").write_text(json.dumps(manifest, indent=2))
    n_ok = sum(1 for c in manifest["compounds"] if c.get("status") == "ok")
    print(f"\n=== summary: {n_ok}/{len(compounds)} compounds prepared OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
