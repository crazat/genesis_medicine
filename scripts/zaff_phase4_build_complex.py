"""ZAFF Phase 4: build holo MMP-1 + EMB-3 complex parm7 for ABFE.

Combines the validated holo MMP-1 (mmp1_holo.parm7 from Phase 2c) with EMB-3
ligand parameters (GAFF-2.11 + AM1-BCC) into a single complex topology suitable
for openmmtools alchemical replica exchange.

Strategy:
  1. Generate EMB-3 3D conformer with RDKit (or use existing apo cofold pose).
  2. Place EMB-3 in the holo MMP-1 active-site cavity. Reuse the apo
     pilot/scaffold_hop/abfe_emb3_mmp1/ligand.sdf if available, aligned to
     the catalytic Zn proximity zone.
  3. Run antechamber + parmchk2 on EMB-3 to produce mol2 + frcmod.
  4. Use tleap to merge holo MMP-1 + EMB-3 + solvent + ions -> complex.parm7.

Inputs:
  pilot/abfe_mmp1_holo_zn/mmp1_holo.parm7 (Phase 2c)
  pilot/abfe_mmp1_holo_zn/sanity_md/PHASE3_PASS (Phase 3 gate)
  pilot/scaffold_hop/abfe_emb3_mmp1/ligand.sdf (existing apo EMB-3 pose)

Outputs:
  pilot/abfe_mmp1_holo_zn/complex/{complex.parm7, complex.rst7, emb3.mol2, emb3.frcmod, PHASE4_OK}

Wallclock: 30-45 min (mostly antechamber AM1-BCC charge fit).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "pilot/abfe_mmp1_holo_zn"
OUT = WORK / "complex"
OUT.mkdir(parents=True, exist_ok=True)

HOLO_PARM7 = WORK / "mmp1_holo.parm7"
HOLO_RST7 = WORK / "mmp1_holo.rst7"
PHASE3_GATE = WORK / "sanity_md" / "PHASE3_PASS"

EMB3_SDF = ROOT / "pilot/scaffold_hop/abfe_emb3_mmp1/ligand.sdf"
EMB3_SMILES = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"


def run(cmd: list[str], cwd: Path | None = None, log: Path | None = None) -> int:
    print("[Phase4]", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    if log:
        log.write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
    if proc.returncode != 0:
        print(proc.stdout[-1500:])
        print("STDERR:", proc.stderr[-1500:])
    return proc.returncode


def main() -> int:
    if not PHASE3_GATE.exists():
        print(f"FAIL: Phase 3 gate not satisfied ({PHASE3_GATE})")
        return 5

    # Step 4.1: prepare EMB-3 ligand
    if EMB3_SDF.exists():
        print(f"[Phase4] reusing EMB-3 sdf: {EMB3_SDF}")
        shutil.copy2(EMB3_SDF, OUT / "emb3.sdf")
    else:
        print("[Phase4] generating EMB-3 conformer from SMILES via RDKit")
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.MolFromSmiles(EMB3_SMILES)
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        Chem.SDWriter(str(OUT / "emb3.sdf")).write(mol)

    # Step 4.2: antechamber AM1-BCC + parmchk2
    sdf_in = OUT / "emb3.sdf"
    mol2_out = OUT / "emb3.mol2"
    rc = run(
        ["antechamber", "-i", str(sdf_in), "-fi", "sdf",
         "-o", str(mol2_out), "-fo", "mol2",
         "-c", "bcc", "-s", "2", "-rn", "LIG", "-pf", "y", "-at", "gaff2"],
        cwd=OUT, log=OUT / "antechamber.log",
    )
    if rc != 0 or not mol2_out.exists():
        print("FAIL: antechamber failed")
        return 6

    frcmod_out = OUT / "emb3.frcmod"
    rc = run(
        ["parmchk2", "-i", str(mol2_out), "-f", "mol2", "-o", str(frcmod_out), "-s", "2"],
        cwd=OUT, log=OUT / "parmchk2.log",
    )
    if rc != 0:
        print("FAIL: parmchk2 failed")
        return 7

    # Step 4.3: tleap to combine holo MMP-1 + EMB-3
    # Convert holo parm7 -> pdb for tleap re-merge
    pdb_holo = OUT / "mmp1_holo.pdb"
    rc = run(
        ["python3", "-c",
         f"import parmed as pmd; "
         f"p=pmd.load_file('{HOLO_PARM7}','{HOLO_RST7}'); "
         f"p.save('{pdb_holo}', overwrite=True)"],
        cwd=OUT, log=OUT / "parmed_export.log",
    )
    if rc != 0 or not pdb_holo.exists():
        print("FAIL: parmed export failed")
        return 8

    # tleap input
    leap_in = OUT / "tleap_complex.in"
    leap_in.write_text(f"""
source leaprc.protein.ff14SB
source leaprc.water.tip3p
source leaprc.gaff2
loadAmberParams frcmod.ions234lm_126_tip3p
loadAmberParams {frcmod_out.name}
LIG = loadMol2 {mol2_out.name}
mol = loadPdb {pdb_holo.name}
complex = combine {{ mol LIG }}
solvateBox complex TIP3PBOX 12.0
addIons complex Na+ 0
addIons complex Cl- 0
saveAmberParm complex complex.parm7 complex.rst7
quit
""".strip())

    rc = run(["tleap", "-f", str(leap_in.name)], cwd=OUT, log=OUT / "tleap_complex.log")
    if rc != 0 or not (OUT / "complex.parm7").exists():
        print("FAIL: tleap complex build failed")
        return 9

    # Step 4.4: validate complex parm7
    import parmed as pmd
    cx = pmd.load_file(str(OUT / "complex.parm7"), str(OUT / "complex.rst7"))
    n_zn = sum(1 for a in cx.atoms if a.element_name == "Zn" or a.name == "ZN")
    n_lig = sum(1 for r in cx.residues if r.name == "LIG")
    summary = {
        "phase": "Phase 4 complex builder",
        "complex_atoms": len(cx.atoms),
        "complex_residues": len(cx.residues),
        "zn_atoms": n_zn,
        "lig_residues": n_lig,
        "box_A": list(cx.box[:3]),
        "outputs": {
            "complex_parm7": str((OUT / "complex.parm7").relative_to(ROOT)),
            "complex_rst7": str((OUT / "complex.rst7").relative_to(ROOT)),
            "emb3_mol2": str((OUT / "emb3.mol2").relative_to(ROOT)),
            "emb3_frcmod": str((OUT / "emb3.frcmod").relative_to(ROOT)),
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

    if n_zn >= 1 and n_lig >= 1 and len(cx.atoms) > 5000:
        (OUT / "PHASE4_OK").touch()
        return 0
    (OUT / "PHASE4_FAIL").touch()
    print("FAIL: missing Zn or LIG residue in complex")
    return 10


if __name__ == "__main__":
    sys.exit(main())
