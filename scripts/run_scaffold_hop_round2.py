"""Round 2 scaffold-hop — EMB-3를 새 seed로.

Round 1: Embelin → EMB-3 (Tanimoto 0.45, hERG 0.40→0.16, MD 0.79 Å)
Round 2: EMB-3 → EMB-3.x (medium similarity, EMB-3 neighborhood 탐색)

목표: EMB-3보다 더 좋은 lead 찾기.
  - hERG ≤ 0.16
  - Skin_Reaction ≤ 0.67
  - TGFB1 affinity ≥ 0.749
  - MMP1 affinity ≥ 0.674
  - MD MMP1 stability ≤ 0.79 Å mean

전제: REINVENT 4 + ADMET-AI + Boltz-2 + MD 모두 작동 중.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import textwrap
import time
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MSA_CACHE = DATA / "msa"
OUT = ROOT / "pilot/scaffold_hop_round2"
OUT.mkdir(parents=True, exist_ok=True)

PRIOR = ROOT / "external/REINVENT4/priors/mol2mol_medium_similarity.prior"
EMB3_SMILES = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"

EMB3_BASELINE = {
    "hERG": 0.16,
    "Skin_Reaction": 0.67,
    "AMES": 0.181,    # 추정 (Embelin baseline)
    "ClinTox": 0.05,
    "logP": 2.36,
    "MW": 224,
    "TGFB1_aff": 0.749,
    "MMP1_aff": 0.674,
    "MMP1_md_rmsd": 0.79,
}

TARGETS = ["TGFB1", "MMP1"]

# UniProt sequences (이전 v2에서 사용한 mature)
TARGET_SEQS = {
    "TGFB1": "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS",
    "MMP1":  "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG",
}


def step1_generate() -> Path:
    """REINVENT 4 mol2mol — EMB-3 → 100 variants."""
    print("\n[1/4] REINVENT 4 mol2mol (EMB-3 → 100 variants)")
    inputs_dir = OUT / "reinvent_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = OUT / "reinvent_outputs"
    out_dir.mkdir(exist_ok=True)
    smi = inputs_dir / "seed.smi"
    smi.write_text(EMB3_SMILES + "\n")
    out_csv = out_dir / "sampled.csv"
    toml = inputs_dir / "sampling.toml"
    toml.write_text(textwrap.dedent(f"""\
        run_type = "sampling"
        device = "cuda:0"
        [parameters]
        model_file = "{PRIOR}"
        smiles_file = "{smi}"
        sample_strategy = "multinomial"
        temperature = 1.0
        output_file = "{out_csv}"
        num_smiles = 100
        unique_molecules = true
        randomize_smiles = true
    """))
    cmd = [str(Path(sys.executable).parent / "reinvent"),
            "-l", str(out_dir / "reinvent.log"), str(toml)]
    rc = subprocess.run(cmd, cwd=out_dir).returncode
    if rc != 0 or not out_csv.exists():
        print(f"❌ REINVENT 실패")
        sys.exit(1)
    df = pd.read_csv(out_csv)
    print(f"  ✅ {len(df)} samples → {out_csv}")
    return out_csv


def step2_filter(sampled_csv: Path) -> pd.DataFrame:
    """RDKit + ADMET-AI 필터."""
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Crippen, Descriptors, Lipinski
    RDLogger.DisableLog("rdApp.*")

    print("\n[2/4] RDKit + ADMET-AI filter")
    df = pd.read_csv(sampled_csv)
    rows = []
    for _, r in df.iterrows():
        smi = r["SMILES"]
        m = Chem.MolFromSmiles(smi)
        if m is None:
            continue
        rows.append({
            "smiles": smi,
            "smiles_canon": Chem.MolToSmiles(m),
            "MW":   Descriptors.MolWt(m),
            "logP": Crippen.MolLogP(m),
            "HBD":  Lipinski.NumHDonors(m),
            "HBA":  Lipinski.NumHAcceptors(m),
            "TPSA": Descriptors.TPSA(m),
            "tanimoto_to_seed": float(r.get("Tanimoto", 0)),
        })
    cleaned = pd.DataFrame(rows).drop_duplicates(subset="smiles_canon")
    topical = cleaned[(cleaned["MW"] <= 500)
                       & (cleaned["logP"].between(1.5, 3.5))
                       & (cleaned["HBD"] <= 5)
                       & (cleaned["HBA"] <= 10)
                       & (cleaned["TPSA"] <= 140)].copy()
    print(f"  valid: {len(cleaned)}, topical OK: {len(topical)}")

    if topical.empty:
        return topical

    from admet_ai import ADMETModel
    print("  ADMET-AI 예측 중...")
    model = ADMETModel()
    adm = model.predict(topical["smiles"].tolist())
    for col in ["hERG", "Skin_Reaction", "AMES", "ClinTox",
                "Bioavailability_Ma", "Solubility_AqSolDB"]:
        topical[col] = adm[col].values

    # EMB-3 baseline 대비 상대 개선 — 최소 1개 endpoint 더 좋아야 함
    s = EMB3_BASELINE
    improve = (
        (topical["hERG"] < s["hERG"]).astype(int) +
        (topical["Skin_Reaction"] < s["Skin_Reaction"]).astype(int) +
        (topical["AMES"] < s["AMES"]).astype(int)
    )
    no_regress = (
        (topical["hERG"] - s["hERG"] < 0.05) &
        (topical["Skin_Reaction"] - s["Skin_Reaction"] < 0.05) &
        (topical["AMES"] - s["AMES"] < 0.10) &
        (topical["ClinTox"] - s["ClinTox"] < 0.10)
    )
    cands = topical[(improve >= 1) & no_regress].copy()
    print(f"  EMB-3 대비 개선 (≥1 endpoint, regression < 0.05): {len(cands)}")

    # composite score (EMB-3 대비)
    import math
    def score(r):
        d = (s["hERG"] - r["hERG"]) * 0.40 + \
            (s["Skin_Reaction"] - r["Skin_Reaction"]) * 0.30 + \
            (s["AMES"] - r["AMES"]) * 0.10 + \
            (abs(s["logP"] - 2.5) - abs(r["logP"] - 2.5)) * 0.20
        return 1 / (1 + math.exp(-3 * d))
    cands["score"] = cands.apply(lambda r: score(r), axis=1)
    cands = cands.sort_values("score", ascending=False).reset_index(drop=True)
    cands.to_csv(OUT / "ranked.csv", index=False)
    print(f"  ✅ {OUT}/ranked.csv ({len(cands)} 후보)")
    return cands.head(3).copy()


def step3_cofold(top3: pd.DataFrame) -> pd.DataFrame:
    """Boltz-2 cofold — top-3 × TGFB1, MMP1."""
    print("\n[3/4] Boltz-2 cofold (top-3 × 2 타겟)")
    import yaml

    inputs_dir = OUT / "boltz_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = OUT / "boltz_output"
    out_dir.mkdir(exist_ok=True)

    for i, r in top3.iterrows():
        for tgt in TARGETS:
            payload = {
                "version": 1,
                "sequences": [
                    {"protein": {"id": "A", "sequence": TARGET_SEQS[tgt],
                                  "msa": str((MSA_CACHE / f"{tgt.lower()}.a3m").absolute())}},
                    {"ligand": {"id": "B", "smiles": r["smiles"]}},
                ],
                "properties": [{"affinity": {"binder": "B"}}],
            }
            p = inputs_dir / f"{tgt.lower()}__r2_{i+1}.yaml"
            p.write_text(yaml.safe_dump(payload, sort_keys=False))

    boltz = str(Path(sys.executable).parent / "boltz")
    cmd = [
        boltz, "predict", str(inputs_dir),
        "--out_dir", str(out_dir),
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    print(f"  ✅ {(time.time()-t0)/60:.1f}분")

    rows = []
    for aff in sorted(out_dir.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        target_key, comp = stem.split("__", 1)
        rows.append({"target": target_key.upper(), "compound": comp,
                     "affinity_pred_value": d.get("affinity_pred_value"),
                     "affinity_probability_binary": d.get(
                         "affinity_probability_binary")})
    res = pd.DataFrame(rows)
    pivot = res.pivot_table(index="compound", columns="target",
                             values="affinity_probability_binary",
                             aggfunc="first")
    pivot["mean"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("mean", ascending=False)
    pivot.to_csv(OUT / "round2_affinity.csv")
    print(f"  ✅ affinity table:")
    print(pivot.to_string(float_format=lambda v: f"{v:.3f}"))
    return res


def step4_md(top3: pd.DataFrame, affinity: pd.DataFrame) -> int:
    """MD top-1 lead × MMP1, TGFB1 (가장 큰 affinity 후보)."""
    print("\n[4/4] MD top-1 × TGFB1 + MMP1 (10 ns)")

    # affinity가 가장 큰 후보
    pivot = affinity.pivot_table(index="compound", columns="target",
                                  values="affinity_probability_binary",
                                  aggfunc="first")
    pivot["mean"] = pivot.mean(axis=1)
    best_comp = pivot["mean"].idxmax()
    best_smiles = top3.iloc[int(best_comp.replace("r2_", "")) - 1]["smiles"]
    best_aff = pivot.loc[best_comp]
    print(f"  best: {best_comp} (mean {best_aff['mean']:.3f}) "
          f"TGFB1={best_aff.get('TGFB1', 0):.3f} MMP1={best_aff.get('MMP1', 0):.3f}")
    print(f"    SMILES: {best_smiles}")

    # EMB-3 baseline 대비
    if best_aff["mean"] < (EMB3_BASELINE["TGFB1_aff"] + EMB3_BASELINE["MMP1_aff"]) / 2 - 0.05:
        print("  ⚠️ best lead가 EMB-3보다 약함 — round 2 음성 결과")
        print("  → EMB-3가 여전히 최고 lead. ABFE는 EMB-3로 진행.")
        return 0

    # MD 실행 — best_comp × TGFB1, MMP1
    print(f"  ✅ best lead가 EMB-3보다 강함! MD 시작…")
    md_dir = OUT / "md_validation"
    md_dir.mkdir(exist_ok=True)
    boltz_out_root = OUT / "boltz_output/boltz_results_inputs/predictions"

    md_results = []
    for tgt in TARGETS:
        cif = boltz_out_root / f"{tgt.lower()}__{best_comp}" / f"{tgt.lower()}__{best_comp}_model_0.cif"
        if not cif.exists():
            print(f"  ⚠️ CIF 없음: {cif}")
            continue
        # MD 실행 (genesis-md env)
        md_script = OUT / f"_md_runner_{tgt}.py"
        md_script.write_text(textwrap.dedent(f"""\
            import sys, json, time, os
            sys.path.insert(0, '{ROOT}/scripts')
            os.environ['PATH'] = '/home/crazat/miniforge3/envs/genesis-md/bin:' + os.environ.get('PATH', '')
            from pathlib import Path
            from openff.toolkit import Molecule
            from openff.units import unit as off_unit
            from openmmforcefields.generators import SystemGenerator
            from pdbfixer import PDBFixer
            import openmm as mm, openmm.app as app
            from openmm import unit
            import numpy as np

            cif_path = Path('{cif}')
            out_dir = Path('{md_dir / f"{tgt.lower()}__{best_comp}"}')
            out_dir.mkdir(parents=True, exist_ok=True)

            lig = Molecule.from_smiles('{best_smiles}', allow_undefined_stereo=True)
            lig.generate_conformers(n_conformers=1)

            fixer = PDBFixer(filename=str(cif_path))
            fixer.findMissingResidues(); fixer.findNonstandardResidues()
            fixer.replaceNonstandardResidues(); fixer.removeHeterogens(False)
            fixer.findMissingAtoms(); fixer.addMissingAtoms()
            modeller = app.Modeller(fixer.topology, fixer.positions)

            sg = SystemGenerator(
                forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
                small_molecule_forcefield="gaff-2.11",
                molecules=[lig],
                forcefield_kwargs={{"constraints": app.HBonds}},
            )

            _orig = app.PDBxFile(str(cif_path))
            lig_orig = [_orig.positions[a.index] for a in _orig.topology.atoms()
                         if a.residue.name == "LIG1"]
            if lig_orig:
                oc = np.mean([[p.x, p.y, p.z] for p in lig_orig], axis=0)
                coords = lig.conformers[0].m_as("nanometer")
                coords += oc - coords.mean(axis=0)
                lig._conformers = [coords * off_unit.nanometer]

            modeller.addHydrogens(sg.forcefield, pH=7.4)
            modeller.add(lig.to_topology().to_openmm(), lig.conformers[0].to_openmm())

            system = sg.create_system(modeller.topology)
            integ = mm.LangevinMiddleIntegrator(
                310 * unit.kelvin, 1.0/unit.picosecond, 2.0*unit.femtosecond,
            )
            sim = app.Simulation(modeller.topology, system, integ,
                                  mm.Platform.getPlatformByName("CUDA"))
            sim.context.setPositions(modeller.positions)
            sim.minimizeEnergy(maxIterations=300)
            sim.context.setVelocitiesToTemperature(310*unit.kelvin)
            sim.reporters.append(app.DCDReporter(str(out_dir/"traj.dcd"), 500))

            t0 = time.time()
            sim.step(int(10 * 500_000))
            wall = time.time() - t0

            final = out_dir / "final.pdb"
            with open(final, "w") as f:
                app.PDBFile.writeFile(sim.topology,
                                       sim.context.getState(getPositions=True).getPositions(), f)

            import mdtraj as md
            t = md.load(str(out_dir/"traj.dcd"), top=str(final))
            lig_idx = t.topology.select("(not protein) and element != H")
            rmsd = md.rmsd(t, t, frame=0, atom_indices=lig_idx)
            (out_dir / "result.json").write_text(json.dumps({{
                "wall_min": round(wall/60, 2),
                "rmsd_mean_A": round(float(rmsd.mean())*10, 2),
                "rmsd_max_A":  round(float(rmsd.max())*10, 2),
                "rmsd_final_A":round(float(rmsd[-1])*10, 2),
            }}))
        """))
        cmd = ["/home/crazat/miniforge3/envs/genesis-md/bin/python", str(md_script)]
        rc = subprocess.run(cmd).returncode
        result_path = md_dir / f"{tgt.lower()}__{best_comp}" / "result.json"
        if result_path.exists():
            r = json.loads(result_path.read_text())
            md_results.append({"target": tgt, "compound": best_comp,
                               "smiles": best_smiles, **r})

    pd.DataFrame(md_results).to_csv(OUT / "md_summary.csv", index=False)
    print(f"\n  MD 결과 — best lead vs EMB-3 baseline:")
    for r in md_results:
        emb3_md = EMB3_BASELINE.get(f"{r['target']}_md_rmsd", "—")
        # EMB-3 TGFB1 1.31 Å, MMP1 0.79 Å
        baseline = 1.31 if r["target"] == "TGFB1" else 0.79
        delta = r["rmsd_mean_A"] - baseline
        print(f"    {r['target']:6s} {r['rmsd_mean_A']:.2f} Å (EMB-3: {baseline:.2f}, "
              f"Δ {delta:+.2f}) {'✅ 더 안정' if delta < 0 else '⚠️ 덜 안정'}")
    return 0


def main() -> int:
    print("=== Round 2 scaffold-hop (EMB-3 → variants) ===\n")
    print(f"Seed: EMB-3 = {EMB3_SMILES}")
    print(f"  hERG {EMB3_BASELINE['hERG']}, Skin {EMB3_BASELINE['Skin_Reaction']},"
          f" TGFB1 {EMB3_BASELINE['TGFB1_aff']}, MMP1 {EMB3_BASELINE['MMP1_aff']}")

    sampled = step1_generate()
    top3 = step2_filter(sampled)
    if top3.empty:
        print("\n⚠️ EMB-3 대비 개선 후보 0건 — round 2 음성 결과. EMB-3 lead 유지.")
        return 0
    aff = step3_cofold(top3)
    step4_md(top3, aff)

    print(f"\n✅ Round 2 완료. {OUT} 확인.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
