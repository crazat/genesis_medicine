"""ABFE r3_6 × TGFB1 stability protocol — zinc-free, NaN-mitigated.

8/8 NaN history fix list:
  1. Target: TGFB1 (NO zinc, unlike MMP-1 → ZAFF 무관)
  2. Ligand: r3_6 (round 3 winner, mean Boltz-2 0.650)
  3. ForceField: GAFF2 instead of OpenFF Sage 2.1 (PyPI yanked)
  4. Equilibration: 5 ns (vs prior 1 ns)
  5. Production timestep: 1 fs (vs 2 fs)
  6. Soft-core: shifted Coulomb + LJ (avoid singularities)
  7. Restraint: 300 kJ/mol/nm² (stronger than prior 100)
  8. Replicas: 17 lambda windows + 4 ns each (vs prior 5 ns × 16)
  9. Save trajectory checkpoint every 100 ps for resume

Estimated: 12h on RTX 5090. Uses GPU exclusive — wait until current chain done.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/scaffold_hop/abfe_r3_6_tgfb1_stable"
OUT.mkdir(parents=True, exist_ok=True)


SMILES_R3_6 = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"
TARGET = "TGFB1"
RECEPTOR_PDB_PATH = ROOT / "pilot/scaffold_hop/abfe_emb3_tgfb1_v3/receptor.pdb"


def main():
    print("=" * 72)
    print("ABFE r3_6 × TGFB1 stable protocol (12h GPU)")
    print("=" * 72)
    print(f"Output: {OUT}")
    print(f"Receptor: {RECEPTOR_PDB_PATH}")

    if not RECEPTOR_PDB_PATH.exists():
        print(f"❌ Receptor PDB not found: {RECEPTOR_PDB_PATH}")
        print("   Run scaffold_hop pipeline first to generate cofold pose.")
        return 1

    # Build openff system + GAFF2 fallback
    try:
        import openmm
        from openmm import app, unit
        from openmm import LangevinMiddleIntegrator, MonteCarloBarostat
        import openmmtools
        from openmmtools import alchemy, mcmc, multistate
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except Exception as e:
        print(f"❌ Missing openmm/openmmtools: {e}")
        return 2

    # GAFF2 path (avoid yanked openff-toolkit)
    print("\n[1/8] Parametrize ligand with GAFF2 (avoiding yanked openff)")
    try:
        from openmmforcefields.generators import GAFFTemplateGenerator
        mol = Chem.MolFromSmiles(SMILES_R3_6)
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.UFFOptimizeMolecule(mol)
        sdf = OUT / "ligand_r3_6.sdf"
        writer = Chem.SDWriter(str(sdf))
        writer.write(mol)
        writer.close()

        from openff.toolkit import Molecule as OFFMol
        offmol = OFFMol.from_smiles(SMILES_R3_6, allow_undefined_stereo=True)
        offmol.generate_conformers(n_conformers=1)
        gaff = GAFFTemplateGenerator(molecules=offmol, forcefield="gaff-2.11")
        ff = app.ForceField("amber14/protein.ff14SB.xml",
                              "amber14/tip3p.xml")
        ff.registerTemplateGenerator(gaff.generator)
        print("  ✅ GAFF2 generator registered")

    except Exception as e:
        print(f"❌ GAFF2 setup failed: {e}")
        print("   Hint: pip install openff-toolkit==0.16.7 openmmforcefields==0.14.0")
        return 3

    # Solvate + minimize + equilibrate
    print("\n[2/8] Solvate + minimize")
    pdb = app.PDBFile(str(RECEPTOR_PDB_PATH))
    modeller = app.Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens(ff)

    # Add ligand to system (would normally use openmmforcefields gaff merger)
    # Simplified: this stub script writes the protocol; full impl requires
    # cofold ligand pose merge → openmm system → alchemical leg setup.
    print("  ⚠️ This is the STABLE PROTOCOL TEMPLATE")
    print("     Full implementation requires:")
    print("     1. Boltz-2 pose extraction (cif → ligand pdb)")
    print("     2. ProteinLigandSystem builder (openmmforcefields v0.14.x)")
    print("     3. AlchemicalState + 17-window lambda schedule")
    print("     4. multistate.ReplicaExchangeSampler with 4ns × 17")
    print("     5. multistate.MultiStateReporter for checkpointing")
    print("     6. analyze.ExpandedEnsembleAnalyzer for ΔG estimation")
    print()
    print("     Implementation reference:")
    print("     - openmmtools.tests.test_alchemy")
    print("     - openff-evaluator/protocols/forcefield.py")
    print("     - scripts/run_emb3_abfe_openmmtools.py (existing baseline)")

    # Write the configured protocol parameters as JSON for downstream pickup
    import json
    config = {
        "compound": "r3_6",
        "smiles": SMILES_R3_6,
        "target": TARGET,
        "receptor_pdb": str(RECEPTOR_PDB_PATH),
        "force_field": "GAFF2.11",
        "water_model": "TIP3P",
        "equilibration_ns": 5,
        "production_ns_per_lambda": 4,
        "n_lambda_windows": 17,
        "lambda_schedule_electrostatic": [0.0, 0.25, 0.5, 0.75, 1.0],
        "lambda_schedule_steric": [0.0, 0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95, 1.00],
        "timestep_fs": 1.0,
        "soft_core_alpha": 0.5,
        "soft_core_beta": 12.0,
        "harmonic_restraint_kj_mol_nm2": 300,
        "barostat": "MonteCarloBarostat 1 atm 300K",
        "thermostat": "LangevinMiddle 300K 1/ps",
        "checkpoint_every_ps": 100,
        "expected_runtime_h": 12,
        "target_gpu": "RTX 5090",
        "known_failure_modes": [
            "openff-toolkit PyPI yanked (use GAFF2 fallback)",
            "MMP-1 zinc → ZAFF needed (use TGFB1 instead, no metal)",
            "EMB-3 polyphenol partial charges (use AM1-BCC + ESP fallback)",
            "Replica state 7 NaN (use longer equilibration + softer core)",
        ],
        "note": ("This is the planned stable protocol. Actual launch requires "
                  "GPU free + full implementation merge with run_emb3_abfe_openmmtools.py"),
    }
    config_path = OUT / "stable_protocol_config.json"
    config_path.write_text(json.dumps(config, indent=2))
    print(f"\n[3/8] ✅ Protocol config saved: {config_path}")
    print("\n[4–8] Implementation TBD when GPU free + collaborator review")
    print("         (estimated 1–2 days impl, 12h run, paper #8 v0.3 update)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
