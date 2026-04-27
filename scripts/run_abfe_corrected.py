"""ABFE corrected — Boresch restraints + dual leg + standard state correction.

Publishable-grade protocol (J Cheminform / RSC Med Chem tier).

References
----------
- Boresch, Tettinger, Leitgeb, Karplus. JPC B 2003, 107, 9535. (eq. 32)
- Mobley & Klimovich. JCP 2012, 137, 230901.
- Wang et al. JACS 2015, 137, 2695-2703. (FEP+ benchmark)
- openmmtools 0.24 alchemical replica exchange

Thermodynamic Cycle (sign convention: ΔG_decouple = G_decoupled - G_coupled,
typically positive for tight binders):

  Coupled state P+L bound (restraint on, λ_complex=1)
       │
       │  ΔG_complex (alchemical decoupling in complex, restraint active)
       v
  Decoupled P + L_ghost in pocket (restraint on, λ_complex=0)
       │
       │  ΔG_release_restraint = analytical Boresch correction
       v          (releases ligand from restrained volume to 1 M std state)
  Decoupled P + L_ghost free (no restraint, std state)
       │
       │  -ΔG_solvent (re-coupling L in pure solvent at 1 M)
       v
  Coupled L in pure solvent at 1 M

Final binding free energy:
  ΔG_bind = ΔG_solvent - ΔG_complex - ΔG_release_restraint

For binders: ΔG_bind < 0.
ΔG_complex typically dominates: ~20-40 kcal/mol for tight binders.
ΔG_solvent typically: 5-25 kcal/mol (smaller magnitude).
ΔG_release_restraint typically: 5-10 kcal/mol with k_r=10 kcal/mol/Å², k_θ=k_φ=100 kcal/mol/rad².

Usage
-----
  python run_abfe_corrected.py \\
      --receptor pilot/.../receptor.pdb \\
      --ligand-smiles "CCCCCC1=C(O)..." \\
      --name EMB3_MMP1 \\
      --out pilot/.../abfe_corrected/

Calibration check
-----------------
T4 lysozyme L99A + benzene benchmark:
  Expected ΔG_bind = -5.2 ± 0.2 kcal/mol (Mobley et al. JCP 2007)
  Run via: scripts/abfe_calibrate_t4l.py
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# Force genesis-md env binaries on PATH (am1bcc, antechamber)
os.environ["PATH"] = (
    "/home/crazat/miniforge3/envs/genesis-md/bin:"
    + os.environ.get("PATH", "")
)


# ─── Physical constants (CODATA 2022) ──────────────────────────────────────
R_KCAL_MOL_K = 1.987204258e-3    # kcal mol⁻¹ K⁻¹
N_AVO = 6.02214076e23
T_KELVIN_DEFAULT = 310.0

# 1 M standard state volume per molecule
V_STD_ANGSTROM3 = 1.0 / (N_AVO * 1e-27)    # = 1660.539 Å³


# ─── Default protocol parameters ───────────────────────────────────────────
N_LAMBDA_WINDOWS_DEFAULT = 16
N_ITERATIONS_DEFAULT = 500          # 5 ns per window @ 10 ps/iteration
STEPS_PER_ITERATION_DEFAULT = 5000  # 10 ps @ 2 fs
EQ_NS_DEFAULT = 0.5
PADDING_NM_DEFAULT = 1.2

# Boresch restraint force constants (Boresch 2003 standard)
K_R_KCAL_MOL_A2 = 10.0
K_THETA_KCAL_MOL_RAD2 = 100.0
K_PHI_KCAL_MOL_RAD2 = 100.0


# ═══════════════════════════════════════════════════════════════════════════
# Boresch restraint — 6-DOF orientational restraint between P+L
# ═══════════════════════════════════════════════════════════════════════════

def select_boresch_atoms(modeller, lig_atom_indices: list[int],
                          rng_seed: int = 42) -> tuple[list[int], list[int]]:
    """Select 3 receptor + 3 ligand anchor atoms for Boresch restraint.

    Heuristic (following Boresch 2003 best practice):
      - Ligand: pick L1 = ligand heavy atom closest to ligand COM
                pick L2, L3 = bonded heavy atoms forming non-collinear triangle
      - Receptor: pick R1 = Cα closest to L1
                  pick R2, R3 = adjacent Cα atoms forming non-collinear triangle

    Returns: (receptor_atoms, ligand_atoms) — each list of 3 atom indices.
    """
    from openmm import unit

    # modeller.positions is Quantity (could wrap list[Vec3] or ndarray)
    pos_q = modeller.positions
    pos = np.asarray(pos_q.value_in_unit(unit.nanometer))    # (N, 3) nm

    # ligand heavy atoms (no H)
    lig_heavy = []
    for i in lig_atom_indices:
        a = list(modeller.topology.atoms())[i]
        if a.element is not None and a.element.symbol != "H":
            lig_heavy.append(i)
    if len(lig_heavy) < 3:
        raise ValueError("ligand has < 3 heavy atoms — Boresch restraint impossible")

    lig_pos = pos[lig_heavy]
    lig_com = lig_pos.mean(axis=0)
    dists = np.linalg.norm(lig_pos - lig_com, axis=1)
    L1 = lig_heavy[int(np.argmin(dists))]

    # find L2: bonded heavy atom to L1
    bond_partners = []
    for bond in modeller.topology.bonds():
        a1, a2 = bond.atom1.index, bond.atom2.index
        if a1 == L1 and a2 in lig_heavy: bond_partners.append(a2)
        if a2 == L1 and a1 in lig_heavy: bond_partners.append(a1)
    if not bond_partners:
        raise ValueError(f"L1={L1} has no bonded heavy ligand neighbor")
    L2 = bond_partners[0]

    # find L3: bonded to L2, distinct from L1, non-collinear
    L3 = None
    for bond in modeller.topology.bonds():
        a1, a2 = bond.atom1.index, bond.atom2.index
        cand = None
        if a1 == L2 and a2 in lig_heavy and a2 != L1: cand = a2
        if a2 == L2 and a1 in lig_heavy and a1 != L1: cand = a1
        if cand is None: continue
        v1 = pos[L2] - pos[L1]
        v2 = pos[cand] - pos[L2]
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
        if abs(cos_angle) < 0.95:
            L3 = cand
            break
    if L3 is None:
        # fallback: nearest heavy atom to L2 not L1
        cands = [i for i in lig_heavy if i not in (L1, L2)]
        if not cands:
            raise ValueError("ligand too small for Boresch")
        d = [np.linalg.norm(pos[c] - pos[L2]) for c in cands]
        L3 = cands[int(np.argmin(d))]

    # Receptor anchors: pick Cα atoms closest to L1
    ca_indices = []
    for atom in modeller.topology.atoms():
        if atom.name == "CA" and atom.residue.chain.id == "A":
            ca_indices.append(atom.index)
    if len(ca_indices) < 3:
        # fallback any backbone
        ca_indices = [a.index for a in modeller.topology.atoms()
                       if a.name in ("CA", "C", "N")]
    ca_pos = pos[ca_indices]
    ca_dists = np.linalg.norm(ca_pos - pos[L1], axis=1)
    sorted_ca = np.argsort(ca_dists)

    R1 = ca_indices[sorted_ca[0]]
    # R2, R3 sequential along chain — get residue indices
    atoms_list = list(modeller.topology.atoms())
    R1_res = atoms_list[R1].residue.index

    # nearest CA on different residue
    R2, R3 = None, None
    for idx in sorted_ca[1:]:
        cand_idx = ca_indices[idx]
        cand_res = atoms_list[cand_idx].residue.index
        if cand_res != R1_res:
            if R2 is None:
                R2 = cand_idx
                R2_res = cand_res
            elif cand_res != R2_res:
                R3 = cand_idx
                # check non-collinearity
                v1 = pos[R2] - pos[R1]
                v2 = pos[R3] - pos[R2]
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2)+1e-9)
                if abs(cos_angle) < 0.95:
                    break
    if R3 is None:
        raise ValueError("could not find non-collinear receptor anchors")

    return [R1, R2, R3], [L1, L2, L3]


def measure_restraint_geometry(positions: np.ndarray,
                                  receptor_anchors: list[int],
                                  ligand_anchors: list[int]) -> dict:
    """Measure equilibrium values of 6 Boresch coordinates from given frame.

    Positions in nanometers; output distances in Å, angles in radians.
    """
    p_a = positions   # Å expected
    P1, P2, P3 = receptor_anchors
    L1, L2, L3 = ligand_anchors

    def _vec(a, b): return p_a[b] - p_a[a]
    def _dist(a, b): return float(np.linalg.norm(_vec(a, b)))
    def _angle(a, b, c):
        v1 = _vec(b, a); v2 = _vec(b, c)
        cos_th = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2)+1e-9)
        return float(np.arccos(np.clip(cos_th, -1, 1)))
    def _dihedral(a, b, c, d):
        b1 = _vec(a, b); b2 = _vec(b, c); b3 = _vec(c, d)
        n1 = np.cross(b1, b2); n2 = np.cross(b2, b3)
        m1 = np.cross(n1, b2 / (np.linalg.norm(b2)+1e-9))
        x = np.dot(n1, n2); y = np.dot(m1, n2)
        return float(np.arctan2(y, x))

    return {
        "r0_A":      _dist(P1, L1),
        "thetaA0":   _angle(P2, P1, L1),
        "thetaB0":   _angle(P1, L1, L2),
        "phiA0":     _dihedral(P3, P2, P1, L1),
        "phiB0":     _dihedral(P2, P1, L1, L2),
        "phiC0":     _dihedral(P1, L1, L2, L3),
    }


def add_flat_bottom_restraint_to_system(system, ligand_atoms: list[int],
                                            receptor_atoms: list[int],
                                            r_max_A: float = 8.0,
                                            k_kcal_mol_A2: float = 10.0) -> dict:
    """Flat-bottom harmonic distance restraint between ligand COM and
    receptor binding-pocket reference atoms COM.

    Energy:  U(r) = 0.5 k (r - r_max)² if r > r_max else 0
    Confines ligand to a sphere of radius r_max around binding site.

    More robust than 6-DOF Boresch for diverse ligands; trades
    rotational/translational restraint for simpler analytical correction.

    References:
      - Hamelberg & McCammon, JACS 2004, 126, 7683 (volume correction)
      - Mobley et al., JCP 2007, 127, 084108

    Returns: {n_lig_atoms, n_rec_atoms, r_max_A, k_kcal_mol_A2, expr}
    """
    from openmm import CustomCentroidBondForce
    # convert kcal/mol/Å² → kJ/mol/nm²
    k_kj_nm2 = k_kcal_mol_A2 * 4.184 * 100
    r_max_nm = r_max_A / 10.0

    expr = (
        "step(r - r_max) * 0.5 * k * (r - r_max)^2; "
        "r = distance(g1, g2)"
    )
    force = CustomCentroidBondForce(2, expr)
    force.addGlobalParameter("k", k_kj_nm2)
    force.addGlobalParameter("r_max", r_max_nm)

    g_lig = force.addGroup(ligand_atoms)
    g_rec = force.addGroup(receptor_atoms)
    force.addBond([g_lig, g_rec], [])
    force.setName("FlatBottomRestraint")
    system.addForce(force)
    return {
        "n_lig_atoms": len(ligand_atoms), "n_rec_atoms": len(receptor_atoms),
        "r_max_A": r_max_A, "k_kcal_mol_A2": k_kcal_mol_A2,
        "type": "flat_bottom_distance_centroid",
    }


def flat_bottom_standard_state_correction(r_max_A: float = 8.0,
                                              T: float = T_KELVIN_DEFAULT) -> dict:
    """Analytical ΔG to release flat-bottom spherical restraint to std 1 M.

    For a flat-bottom restraint with infinite-range zero potential below r_max,
    the restrained volume is V_R = (4/3) π r_max³. The standard state is
    V° = 1660.5 Å³.

    ΔG_R^o = -RT ln(V_R / V°)

    For r_max = 8 Å: V_R = 2145 Å³ → ΔG_R^o = -RT ln(1.292) ≈ -0.16 kcal/mol
    For r_max = 5 Å: V_R = 524 Å³ → ΔG_R^o = -RT ln(0.316) ≈ +0.71 kcal/mol

    Sign: at r_max=8, V_R > V°, releasing slightly favorable (negative).
    Used in cycle: ΔG_bind = ΔG_solvent − ΔG_complex − ΔG_R^o.
    """
    import math
    V_R = (4.0/3.0) * math.pi * (r_max_A ** 3)
    RT = R_KCAL_MOL_K * T
    dG_release = -RT * math.log(V_R / V_STD_ANGSTROM3)
    return {
        "delta_g_release_restraint_kcal_mol": dG_release,
        "V_R_A3": V_R, "V_std_A3": V_STD_ANGSTROM3, "r_max_A": r_max_A,
        "T_kelvin": T,
        "restraint_type": "flat_bottom_spherical",
        "formula": "ΔG_R^o = -RT ln(V_R / V°), V_R = 4/3 π r_max³",
    }


# ═══════════════════════════════════════════════════════════════════════════
# System setup — complex (P+L) and solvent (L only)
# ═══════════════════════════════════════════════════════════════════════════

def setup_complex(receptor_pdb: Path, ligand_smiles: str,
                    padding_nm: float = PADDING_NM_DEFAULT,
                    eq_ns: float = EQ_NS_DEFAULT,
                    ligand_template_pdb: Path | None = None,
                    ligand_template_resname: str = "") -> dict:
    """Build complex P+L system, equilibrate, return simulation state.

    Initial ligand placement priority:
      1. If `ligand_template_pdb` + `ligand_template_resname` given: extract
         heavy-atom centroid of that residue, place ligand there.
      2. Else: place at receptor COM (heuristic, may clash for buried pockets).
    """
    from openff.toolkit import Molecule
    from openff.units import unit as off_unit
    from openmmforcefields.generators import SystemGenerator
    from pdbfixer import PDBFixer
    import openmm as mm
    import openmm.app as app
    from openmm import unit

    print(f"\n[setup_complex] receptor={receptor_pdb}, ligand={ligand_smiles[:40]}...")

    fixer = PDBFixer(filename=str(receptor_pdb))
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(False)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    modeller = app.Modeller(fixer.topology, fixer.positions)

    lig = Molecule.from_smiles(ligand_smiles, allow_undefined_stereo=True)
    lig.generate_conformers(n_conformers=1)
    lig.assign_partial_charges("am1bcc")

    sg = SystemGenerator(
        forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds},
    )

    # Determine binding site center (nm)
    binding_center_nm = None
    if ligand_template_pdb is not None and ligand_template_resname:
        tmpl = app.PDBFile(str(ligand_template_pdb))
        tmpl_pos = []
        for atom, p in zip(tmpl.topology.atoms(), tmpl.positions):
            if atom.residue.name == ligand_template_resname:
                tmpl_pos.append([p.x, p.y, p.z])
        if tmpl_pos:
            binding_center_nm = np.array(tmpl_pos).mean(axis=0)
            print(f"  binding site from template ({ligand_template_resname}): "
                  f"{binding_center_nm} nm ({len(tmpl_pos)} atoms)")
    if binding_center_nm is None:
        rec_pos = np.asarray(modeller.positions.value_in_unit(unit.nanometer))
        binding_center_nm = rec_pos.mean(axis=0)
        print(f"  fallback binding site = receptor COM: {binding_center_nm} nm")

    # add ligand at binding site center
    coords = lig.conformers[0].m_as("nanometer")
    coords += binding_center_nm - coords.mean(axis=0)
    lig._conformers = [coords * off_unit.nanometer]
    modeller.addHydrogens(sg.forcefield, pH=7.4)
    modeller.add(lig.to_topology().to_openmm(),
                 lig.conformers[0].to_openmm())

    modeller.addSolvent(sg.forcefield, padding=padding_nm*unit.nanometer,
                         ionicStrength=0.15*unit.molar)

    system = sg.create_system(modeller.topology)
    system.addForce(mm.MonteCarloBarostat(1*unit.atmosphere,
                                            310*unit.kelvin, 25))

    # ligand atom indices
    lig_atoms = []
    for atom in modeller.topology.atoms():
        if atom.residue.name in ("LIG", "LIG1", "UNL", "UNK"):
            lig_atoms.append(atom.index)
    if not lig_atoms:
        raise ValueError("ligand atoms not found in topology")

    print(f"  system size: {system.getNumParticles()}, ligand: {len(lig_atoms)} atoms")

    # equilibrate
    integ = mm.LangevinMiddleIntegrator(310*unit.kelvin, 1.0/unit.picosecond,
                                          2.0*unit.femtosecond)
    sim = app.Simulation(modeller.topology, system, integ,
                          mm.Platform.getPlatformByName("CUDA"))
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=5000)
    sim.context.setVelocitiesToTemperature(310*unit.kelvin)
    print(f"  equilibrating {eq_ns} ns NPT…")
    sim.step(int(eq_ns * 500_000))
    eq_state = sim.context.getState(getPositions=True, getVelocities=True,
                                      enforcePeriodicBox=True)
    return {
        "modeller": modeller, "system": system, "lig_atoms": lig_atoms,
        "eq_positions": eq_state.getPositions(),
        "eq_box": eq_state.getPeriodicBoxVectors(),
    }


def setup_solvent_only(ligand_smiles: str, padding_nm: float = 1.0,
                         eq_ns: float = 0.5) -> dict:
    """Ligand-only solvent system — for ΔG_solvent_decouple leg."""
    from openff.toolkit import Molecule
    from openmmforcefields.generators import SystemGenerator
    import openmm as mm
    import openmm.app as app
    from openmm import unit

    print(f"\n[setup_solvent] ligand-only, {padding_nm} nm padding")

    lig = Molecule.from_smiles(ligand_smiles, allow_undefined_stereo=True)
    lig.generate_conformers(n_conformers=1)
    lig.assign_partial_charges("am1bcc")

    sg = SystemGenerator(
        forcefields=["amber/tip3p_standard.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds},
    )

    modeller = app.Modeller(lig.to_topology().to_openmm(),
                             lig.conformers[0].to_openmm())
    modeller.addSolvent(sg.forcefield, padding=padding_nm*unit.nanometer,
                         model="tip3p")

    system = sg.create_system(modeller.topology)
    system.addForce(mm.MonteCarloBarostat(1*unit.atmosphere,
                                            310*unit.kelvin, 25))

    lig_atoms = []
    for atom in modeller.topology.atoms():
        if atom.residue.name in ("LIG", "LIG1", "UNL", "UNK"):
            lig_atoms.append(atom.index)

    integ = mm.LangevinMiddleIntegrator(310*unit.kelvin, 1.0/unit.picosecond,
                                          2.0*unit.femtosecond)
    sim = app.Simulation(modeller.topology, system, integ,
                          mm.Platform.getPlatformByName("CUDA"))
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=5000)
    sim.context.setVelocitiesToTemperature(310*unit.kelvin)
    sim.step(int(eq_ns * 500_000))
    eq_state = sim.context.getState(getPositions=True, getVelocities=True,
                                      enforcePeriodicBox=True)
    print(f"  solvent system: {system.getNumParticles()}, ligand: {len(lig_atoms)}")
    return {
        "modeller": modeller, "system": system, "lig_atoms": lig_atoms,
        "eq_positions": eq_state.getPositions(),
        "eq_box": eq_state.getPeriodicBoxVectors(),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Alchemical leg — replica exchange ABFE
# ═══════════════════════════════════════════════════════════════════════════

def run_alchemical_leg(setup: dict, *, leg_name: str, store_dir: Path,
                         n_windows: int = N_LAMBDA_WINDOWS_DEFAULT,
                         n_iterations: int = N_ITERATIONS_DEFAULT,
                         steps_per_iter: int = STEPS_PER_ITERATION_DEFAULT,
                         softcore_alpha: float = 0.5,
                         softcore_a: int = 1) -> dict:
    """Run alchemical decoupling leg (electrostatics → sterics).

    Round 10: softcore_alpha and softcore_a exposed as parameters to mitigate
    NaN at electrostatic-steric transition for polyphenol / charged ligands.
    """
    from openmmtools import alchemy, multistate, mcmc, states
    from openmm import unit

    store_dir.mkdir(parents=True, exist_ok=True)
    storage_path = store_dir / f"replica_exchange_{leg_name}.nc"
    if storage_path.exists():
        print(f"  [warn] removing existing {storage_path}")
        storage_path.unlink()

    print(f"\n[alchemical leg: {leg_name}] {n_windows} windows × "
          f"{n_iterations} iter × {steps_per_iter*0.002:.0f} ps")

    factory = alchemy.AbsoluteAlchemicalFactory(
        consistent_exceptions=False, switch_width=1.0*unit.angstrom,
        alchemical_pme_treatment="exact",
    )
    region = alchemy.AlchemicalRegion(
        alchemical_atoms=setup["lig_atoms"],
        softcore_alpha=softcore_alpha,
        softcore_a=softcore_a,
    )
    alch_system = factory.create_alchemical_system(setup["system"], region)

    # lambda schedule: electrostatics first (1→0), then sterics (1→0)
    n_elec = n_windows // 2 + 1
    n_steric = n_windows - n_elec + 1
    lambdas_elec = np.linspace(1.0, 0.0, n_elec)
    lambdas_steric = np.linspace(1.0, 0.0, n_steric)
    schedule = []
    for le in lambdas_elec:
        schedule.append({"lambda_electrostatics": float(le),
                         "lambda_sterics": 1.0})
    for ls in lambdas_steric[1:]:
        schedule.append({"lambda_electrostatics": 0.0,
                         "lambda_sterics": float(ls)})

    thermo_states = []
    for s in schedule:
        ts = states.ThermodynamicState(system=alch_system,
                                        temperature=310*unit.kelvin,
                                        pressure=1*unit.atmosphere)
        css = states.CompoundThermodynamicState(
            thermodynamic_state=ts,
            composable_states=[alchemy.AlchemicalState.from_system(alch_system)]
        )
        css.lambda_electrostatics = s["lambda_electrostatics"]
        css.lambda_sterics = s["lambda_sterics"]
        thermo_states.append(css)

    sampler_state = states.SamplerState(positions=setup["eq_positions"],
                                          box_vectors=setup["eq_box"])
    sampler_states = [sampler_state] * len(thermo_states)

    move = mcmc.LangevinDynamicsMove(
        timestep=2.0*unit.femtosecond, collision_rate=1.0/unit.picosecond,
        n_steps=steps_per_iter, reassign_velocities=False,
    )
    sampler = multistate.ReplicaExchangeSampler(
        mcmc_moves=move, number_of_iterations=n_iterations,
        online_analysis_interval=20,
    )
    reporter = multistate.MultiStateReporter(str(storage_path),
                                               checkpoint_interval=20)
    sampler.create(thermodynamic_states=thermo_states,
                    sampler_states=sampler_states, storage=reporter)

    t0 = time.time()
    sampler.run(n_iterations)
    wall = time.time() - t0
    print(f"  ✅ {leg_name} done in {wall/3600:.2f}h")

    # MBAR analysis
    analyzer = multistate.MultiStateSamplerAnalyzer(reporter)
    Deltaf_ij, dDeltaf_ij = analyzer.get_free_energy()
    df_kT = Deltaf_ij[0, -1]
    ddf_kT = dDeltaf_ij[0, -1]
    kT_kcal = R_KCAL_MOL_K * 310.0
    df_kcal = df_kT * kT_kcal
    ddf_kcal = ddf_kT * kT_kcal

    # Convergence diagnostic — replica swap acceptance
    try:
        n_accepted = analyzer.reporter.read_mcmc_moves_acceptance_rate()
    except Exception:
        n_accepted = None

    print(f"  ΔG_{leg_name}_decouple = {df_kcal:.3f} ± {ddf_kcal:.3f} kcal/mol")
    return {
        "leg": leg_name,
        "delta_g_decouple_kcal_mol": float(df_kcal),
        "uncertainty_kcal_mol": float(ddf_kcal),
        "n_windows": n_windows,
        "n_iterations": n_iterations,
        "ps_per_iteration": steps_per_iter * 0.002,
        "total_simulation_ns": (n_windows * n_iterations
                                  * steps_per_iter * 0.002 / 1000),
        "wall_hours": wall / 3600,
        "storage": str(storage_path),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Main orchestration
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receptor", required=True, type=Path,
                         help="receptor PDB (already prepped)")
    parser.add_argument("--ligand-smiles", required=True, type=str)
    parser.add_argument("--name", required=True, type=str,
                         help="run name (e.g., 'EMB3_MMP1')")
    parser.add_argument("--out", required=True, type=Path,
                         help="output directory")
    parser.add_argument("--ligand-template-pdb", type=Path,
                         help="PDB containing reference ligand (for initial coords)")
    parser.add_argument("--ligand-template-resname", type=str, default="",
                         help="residue name of reference ligand in template PDB")
    parser.add_argument("--n-windows", type=int, default=N_LAMBDA_WINDOWS_DEFAULT)
    parser.add_argument("--n-iterations", type=int, default=N_ITERATIONS_DEFAULT)
    parser.add_argument("--eq-ns", type=float, default=EQ_NS_DEFAULT)
    parser.add_argument("--padding-nm", type=float, default=PADDING_NM_DEFAULT)
    parser.add_argument("--r-max-A", type=float, default=8.0,
                         help="flat-bottom restraint radius in Å (Round 9: try 5.0 for buried pockets)")
    parser.add_argument("--minimize-tolerance", type=float, default=10.0,
                         help="energy minimization tolerance in kJ/mol (Round 9: try 1.0 for tighter starting state)")
    parser.add_argument("--softcore-alpha", type=float, default=0.5,
                         help="alchemical soft-core alpha (Round 10: try 0.8 for polyphenol/charged ligands)")
    parser.add_argument("--softcore-a", type=int, default=1,
                         help="alchemical soft-core 'a' exponent (default 1)")
    parser.add_argument("--skip-complex", action="store_true",
                         help="skip complex leg (debugging)")
    parser.add_argument("--skip-solvent", action="store_true",
                         help="skip solvent leg (debugging)")
    args = parser.parse_args()

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(f"ABFE corrected — {args.name}")
    print(f"  receptor: {args.receptor}")
    print(f"  ligand:   {args.ligand_smiles[:60]}")
    print(f"  output:   {out}")
    print(f"  protocol: {args.n_windows} windows × {args.n_iterations} iter "
          f"× {STEPS_PER_ITERATION_DEFAULT*0.002:.0f} ps "
          f"= {args.n_windows*args.n_iterations*STEPS_PER_ITERATION_DEFAULT*0.002/1000:.1f} ns")
    print("=" * 72)
    t_start = time.time()

    results = {"name": args.name, "ligand_smiles": args.ligand_smiles,
                "receptor": str(args.receptor), "n_windows": args.n_windows,
                "n_iterations": args.n_iterations,
                "ps_per_iteration": STEPS_PER_ITERATION_DEFAULT*0.002}

    # 1) COMPLEX LEG
    if not args.skip_complex:
        complex_setup = setup_complex(args.receptor, args.ligand_smiles,
                                         padding_nm=args.padding_nm,
                                         eq_ns=args.eq_ns,
                                         ligand_template_pdb=args.ligand_template_pdb,
                                         ligand_template_resname=args.ligand_template_resname)

        # Flat-bottom distance restraint — robust alternative to Boresch.
        # Ligand atoms (COM) restrained within r_max of receptor anchor atoms (COM).
        # Receptor anchors: Cα atoms within 6 Å of ligand COM (binding-site definition).
        from openmm import unit as _u
        eq_pos_nm = np.asarray(
            complex_setup["eq_positions"].value_in_unit(_u.nanometer))
        lig_idx = complex_setup["lig_atoms"]
        lig_com_nm = eq_pos_nm[lig_idx].mean(axis=0)
        # collect Cα atoms within 6 Å of ligand COM
        atoms_list = list(complex_setup["modeller"].topology.atoms())
        rec_anchors = []
        for atom in atoms_list:
            if atom.name == "CA":
                d_nm = np.linalg.norm(eq_pos_nm[atom.index] - lig_com_nm)
                if d_nm < 0.6:    # 6 Å
                    rec_anchors.append(atom.index)
        if len(rec_anchors) < 3:
            # fallback: nearest 5 Cα atoms regardless of distance
            ca_idx = [a.index for a in atoms_list if a.name == "CA"]
            ca_dists = [np.linalg.norm(eq_pos_nm[i] - lig_com_nm) for i in ca_idx]
            rec_anchors = [ca_idx[i] for i in np.argsort(ca_dists)[:5]]
        print(f"\n[restraint] ligand atoms: {len(lig_idx)}, "
              f"receptor binding-site Cα atoms: {len(rec_anchors)}")
        r_max_A = args.r_max_A    # Round 9: configurable (was 8.0)
        rinfo = add_flat_bottom_restraint_to_system(
            complex_setup["system"], lig_idx, rec_anchors,
            r_max_A=r_max_A, k_kcal_mol_A2=10.0,
        )

        # analytical standard state correction
        std_corr = flat_bottom_standard_state_correction(r_max_A=r_max_A)
        std_corr["restraint_info"] = rinfo
        print(f"  ΔG_release_restraint = "
              f"{std_corr['delta_g_release_restraint_kcal_mol']:+.3f} kcal/mol "
              f"(flat-bottom r_max={r_max_A} Å)")

        # alchemical complex leg
        complex_result = run_alchemical_leg(
            complex_setup, leg_name="complex", store_dir=out,
            n_windows=args.n_windows, n_iterations=args.n_iterations,
            softcore_alpha=args.softcore_alpha, softcore_a=args.softcore_a,
        )
        results["complex"] = complex_result
        results["restraint"] = std_corr
        results["restraint_anchors"] = {"receptor_ca": rec_anchors,
                                          "ligand": lig_idx}

    # 2) SOLVENT LEG
    if not args.skip_solvent:
        solvent_setup = setup_solvent_only(args.ligand_smiles, padding_nm=1.5)
        solvent_result = run_alchemical_leg(
            solvent_setup, leg_name="solvent", store_dir=out,
            n_windows=args.n_windows, n_iterations=args.n_iterations,
            softcore_alpha=args.softcore_alpha, softcore_a=args.softcore_a,
        )
        results["solvent"] = solvent_result

    # 3) FINAL ASSEMBLY
    if "complex" in results and "solvent" in results:
        dG_c = results["complex"]["delta_g_decouple_kcal_mol"]
        dG_s = results["solvent"]["delta_g_decouple_kcal_mol"]
        dG_r = results["restraint"]["delta_g_release_restraint_kcal_mol"]
        # ΔG_bind = ΔG_solvent - ΔG_complex - ΔG_release_restraint
        dG_bind = dG_s - dG_c - dG_r
        # propagate uncertainty (independent legs)
        unc_c = results["complex"]["uncertainty_kcal_mol"]
        unc_s = results["solvent"]["uncertainty_kcal_mol"]
        unc_total = math.sqrt(unc_c**2 + unc_s**2)
        results["binding_free_energy"] = {
            "delta_g_bind_kcal_mol": dG_bind,
            "uncertainty_kcal_mol": unc_total,
            "components": {
                "delta_g_complex_decouple_kcal_mol": dG_c,
                "delta_g_solvent_decouple_kcal_mol": dG_s,
                "delta_g_release_restraint_kcal_mol": dG_r,
            },
            "formula": "ΔG_bind = ΔG_solvent - ΔG_complex - ΔG_release",
            "interpretation": (
                "binder" if dG_bind < -2 else
                ("weak/non-binder" if dG_bind > 0 else "borderline")
            ),
            "implied_K_d_M": math.exp(dG_bind / (R_KCAL_MOL_K * 310.0)),
        }
        print("\n" + "=" * 72)
        print(f"FINAL ΔG_bind = {dG_bind:.2f} ± {unc_total:.2f} kcal/mol")
        print(f"  ΔG_complex     = {dG_c:8.2f} ± {unc_c:.2f}")
        print(f"  ΔG_solvent     = {dG_s:8.2f} ± {unc_s:.2f}")
        print(f"  ΔG_release_R   = {dG_r:8.2f}  (analytical)")
        print(f"  implied K_d    = {results['binding_free_energy']['implied_K_d_M']:.2e} M")
        print("=" * 72)

    results["wall_hours_total"] = (time.time() - t_start) / 3600
    (out / "result_corrected.json").write_text(
        json.dumps(results, indent=2, default=str))
    print(f"\n✅ {out}/result_corrected.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
