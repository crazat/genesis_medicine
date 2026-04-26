"""Round 3 scaffold-hop — Round 2 음성 후속.

Round 2 결과 (2026-04-25): 3 candidates Boltz-2 mean 0.50–0.57 (EMB-3 0.71 미달).
원인: temperature 1.0 + medium similarity prior가 과도한 발산.

Round 3 변경:
  - REINVENT temperature 1.0 → 0.6 (tighter neighborhood)
  - num_smiles 100 → 300 (3× 후보 풀)
  - BRICS 기반 한약 fragment-grafting 보조 채널 (centella, shikonin, EGCG)
  - Boltz-2 affinity 필터를 ADMET 직후로 이동 → affinity-first 선별
  - 통과 기준: mean(TGFB1, MMP1) > 0.71 (EMB-3 baseline) + ADMET non-regression

성공 기준: top-1이 EMB-3 동등 이상 → MD 검증으로 확장.
"""

from __future__ import annotations

import json
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
OUT = ROOT / "pilot/scaffold_hop_round3"
OUT.mkdir(parents=True, exist_ok=True)

PRIOR = ROOT / "external/REINVENT4/priors/mol2mol_medium_similarity.prior"
EMB3_SMILES = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O"

EMB3_BASELINE = {
    "hERG": 0.16, "Skin_Reaction": 0.67, "AMES": 0.181, "ClinTox": 0.05,
    "logP": 2.36, "MW": 224,
    "TGFB1_aff": 0.749, "MMP1_aff": 0.674, "mean_aff": 0.711,
    "MMP1_md_rmsd": 0.79, "TGFB1_md_rmsd": 1.31,
}

TARGETS = ["TGFB1", "MMP1"]
TARGET_SEQS = {
    "TGFB1": "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS",
    "MMP1":  "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG",
}

# 한약 anti-fibrotic 천연물 fragments (BRICS grafting 시드)
HERBAL_FRAGMENTS = {
    "centella_AA":   "OC(=O)C12CCC(C)(C)CC1C1(C)CCC3(C)CCC(O)C(C)(C(O)=O)C3(O)C1CC2",   # asiatic acid
    "shikonin":      "CC(=CCC1=C(O)C(=O)C2=CC=CC(O)=C2C1=O)C",
    "EGCG":          "OC1=CC(O)=CC(C2OC3=C(C(O)=O)C(O)=C(O)C(O)=C3C2)=C1",
    "curcumin":      "COC1=CC(/C=C/C(=O)CC(=O)/C=C/C2=CC=C(O)C(OC)=C2)=CC=C1O",
    "baicalein":     "OC1=C(O)C(O)=C2C(=O)C=C(C3=CC=CC=C3)OC2=C1",
    "honokiol":      "C=CCc1ccc(O)c(-c2cc(CC=C)ccc2O)c1",
    "berberine":     "COc1ccc2cc3[n+](cc2c1OC)CCc1cc2c(cc1-3)OCO2",
    "embelin":       "CCCCCCCCCCCC1=C(O)C(=O)C=C(O)C1=O",
    "EMB3_self":     EMB3_SMILES,
}


# ===========================================================================
def step1_reinvent() -> Path:
    """REINVENT 4 — EMB-3 → 300 variants @ T=0.6 (tighter)."""
    print("\n[1/5] REINVENT 4 mol2mol — EMB-3 seed, T=0.6, 300 samples")
    inp = OUT / "reinvent_inputs"
    inp.mkdir(exist_ok=True)
    out = OUT / "reinvent_outputs"
    out.mkdir(exist_ok=True)
    smi = inp / "seed.smi"
    smi.write_text(EMB3_SMILES + "\n")
    out_csv = out / "sampled.csv"
    toml = inp / "sampling.toml"
    toml.write_text(textwrap.dedent(f"""\
        run_type = "sampling"
        device = "cuda:0"
        [parameters]
        model_file = "{PRIOR}"
        smiles_file = "{smi}"
        sample_strategy = "multinomial"
        temperature = 0.6
        output_file = "{out_csv}"
        num_smiles = 300
        unique_molecules = true
        randomize_smiles = true
    """))
    cmd = [str(Path(sys.executable).parent / "reinvent"),
            "-l", str(out / "reinvent.log"), str(toml)]
    rc = subprocess.run(cmd, cwd=out).returncode
    if rc != 0 or not out_csv.exists():
        print("❌ REINVENT 실패"); sys.exit(1)
    df = pd.read_csv(out_csv)
    print(f"  ✅ REINVENT {len(df)} samples → {out_csv}")
    return out_csv


def step2_brics_graft() -> pd.DataFrame:
    """BRICS 기반 한약 fragment grafting — EMB-3 scaffold + 한약 substituent."""
    print("\n[2/5] BRICS fragment grafting (한약 anti-fibrotic NPs)")
    from rdkit import Chem, RDLogger
    from rdkit.Chem import BRICS, AllChem
    RDLogger.DisableLog("rdApp.*")

    # EMB-3 BRICS 분해 → fragment에 한약 fragment 결합
    emb3 = Chem.MolFromSmiles(EMB3_SMILES)
    emb3_brics = list(BRICS.BRICSDecompose(emb3, returnMols=False))
    print(f"  EMB-3 BRICS fragments: {len(emb3_brics)}")
    for f in emb3_brics:
        print(f"    {f}")

    # 한약 NP들 BRICS fragment + EMB-3 fragment 합성 (BRICS.BRICSBuild)
    seeds = [Chem.MolFromSmiles(s) for s in HERBAL_FRAGMENTS.values()]
    seeds = [m for m in seeds if m is not None]
    all_frags = set()
    for m in seeds + [emb3]:
        try:
            for f in BRICS.BRICSDecompose(m, returnMols=False):
                if f and "*" in f:    # only attachable fragments
                    all_frags.add(f)
        except Exception:
            continue
    print(f"  pooled BRICS fragments (한약 + EMB-3): {len(all_frags)}")

    # BRICS.BRICSBuild — fragment 조합으로 새 분자 생성
    frag_mols = []
    for f in all_frags:
        m = Chem.MolFromSmiles(f)
        if m: frag_mols.append(m)
    builder = BRICS.BRICSBuild(frag_mols, scrambleReagents=True, maxDepth=3)
    built = []
    for i, m in enumerate(builder):
        if i >= 200: break
        if m is None: continue
        try:
            Chem.SanitizeMol(m)
            built.append(Chem.MolToSmiles(m))
        except Exception:
            continue
    built = list(set(built))
    print(f"  BRICS-built unique molecules: {len(built)}")

    return pd.DataFrame({"SMILES": built, "source": "brics_graft"})


def step3_filter(reinvent_csv: Path, brics_df: pd.DataFrame) -> pd.DataFrame:
    """RDKit + ADMET-AI 필터 — REINVENT + BRICS 둘 다 통합."""
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Crippen, Descriptors, Lipinski
    RDLogger.DisableLog("rdApp.*")

    print("\n[3/5] RDKit + ADMET-AI filter (통합 pool)")
    rein = pd.read_csv(reinvent_csv)
    rein["source"] = "reinvent"
    if "SMILES" not in rein.columns and "smiles" in rein.columns:
        rein = rein.rename(columns={"smiles": "SMILES"})
    pool = pd.concat([rein[["SMILES", "source"]],
                      brics_df[["SMILES", "source"]]], ignore_index=True)

    rows = []
    for _, r in pool.iterrows():
        smi = r["SMILES"]
        m = Chem.MolFromSmiles(smi)
        if m is None: continue
        rows.append({
            "smiles": smi, "smiles_canon": Chem.MolToSmiles(m),
            "source": r["source"],
            "MW": Descriptors.MolWt(m), "logP": Crippen.MolLogP(m),
            "HBD": Lipinski.NumHDonors(m), "HBA": Lipinski.NumHAcceptors(m),
            "TPSA": Descriptors.TPSA(m),
        })
    cleaned = pd.DataFrame(rows).drop_duplicates(subset="smiles_canon")

    # 외용제 sweet spot
    topical = cleaned[
        (cleaned["MW"].between(180, 500)) &
        (cleaned["logP"].between(1.5, 3.5)) &
        (cleaned["HBD"] <= 5) & (cleaned["HBA"] <= 10) &
        (cleaned["TPSA"] <= 140)
    ].copy()
    print(f"  pool {len(cleaned)} → topical-OK {len(topical)} "
          f"(reinvent {sum(topical['source']=='reinvent')}, "
          f"brics {sum(topical['source']=='brics_graft')})")

    if topical.empty:
        return topical

    # ADMET-AI
    from admet_ai import ADMETModel
    print("  ADMET-AI 예측...")
    model = ADMETModel()
    adm = model.predict(topical["smiles"].tolist())
    for col in ["hERG", "Skin_Reaction", "AMES", "ClinTox",
                 "Bioavailability_Ma", "Solubility_AqSolDB"]:
        topical[col] = adm[col].values

    # EMB-3 non-regression filter
    s = EMB3_BASELINE
    no_regress = (
        (topical["hERG"] - s["hERG"] < 0.05) &
        (topical["Skin_Reaction"] - s["Skin_Reaction"] < 0.05) &
        (topical["AMES"] - s["AMES"] < 0.10) &
        (topical["ClinTox"] - s["ClinTox"] < 0.10)
    )
    cands = topical[no_regress].copy()
    print(f"  EMB-3 non-regression 통과: {len(cands)}")
    cands.to_csv(OUT / "admet_passed.csv", index=False)
    return cands


def step4_cofold(cands: pd.DataFrame) -> pd.DataFrame:
    """Boltz-2 cofold — top-K (ADMET 통과한 후보) × TGFB1, MMP1."""
    print("\n[4/5] Boltz-2 cofold (affinity-first)")
    import yaml

    # ADMET 점수 합성으로 top-15만 cofold (compute 절약)
    s = EMB3_BASELINE
    cands["admet_score"] = (
        (s["hERG"] - cands["hERG"]) * 0.40 +
        (s["Skin_Reaction"] - cands["Skin_Reaction"]) * 0.30 +
        (s["AMES"] - cands["AMES"]) * 0.10 +
        -abs(cands["logP"] - 2.5) * 0.20
    )
    top = cands.sort_values("admet_score", ascending=False).head(15).reset_index(drop=True)
    top["compound"] = [f"r3_{i+1}" for i in range(len(top))]
    top.to_csv(OUT / "cofold_inputs.csv", index=False)
    print(f"  cofold pool: {len(top)} compounds × 2 targets = {len(top)*2} jobs")

    inputs_dir = OUT / "boltz_inputs"
    inputs_dir.mkdir(exist_ok=True)
    out_dir = OUT / "boltz_output"
    out_dir.mkdir(exist_ok=True)

    for _, r in top.iterrows():
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
            p = inputs_dir / f"{tgt.lower()}__{r['compound']}.yaml"
            p.write_text(yaml.safe_dump(payload, sort_keys=False))

    boltz = str(Path(sys.executable).parent / "boltz")
    cmd = [boltz, "predict", str(inputs_dir),
            "--out_dir", str(out_dir),
            "--sampling_steps", "25",
            "--diffusion_samples", "1",
            "--recycling_steps", "3",
            "--sampling_steps_affinity", "200",
            "--diffusion_samples_affinity", "5",
            "--affinity_mw_correction",
            "--devices", "1"]
    t0 = time.time()
    subprocess.run(cmd)
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
    pivot.to_csv(OUT / "round3_affinity.csv")
    # join smiles
    pivot_with_smi = pivot.reset_index().merge(
        top[["compound", "smiles", "source", "MW", "logP", "hERG",
              "Skin_Reaction", "tanimoto_to_seed" if "tanimoto_to_seed" in top.columns else "MW"]]
            .drop_duplicates(subset="compound"),
        on="compound", how="left")
    pivot_with_smi.to_csv(OUT / "round3_affinity_full.csv", index=False)
    print(f"\n  affinity table:")
    print(pivot.to_string(float_format=lambda v: f"{v:.3f}"))
    return pivot_with_smi


def step5_summarize(aff_full: pd.DataFrame) -> int:
    """EMB-3 baseline 0.711 vs Round 3 best 비교."""
    print("\n[5/5] Round 3 결과 요약")
    if aff_full.empty:
        print("  ⚠️ 결과 없음")
        return 1
    best = aff_full.iloc[0]
    base = EMB3_BASELINE["mean_aff"]
    delta = best["mean"] - base
    print(f"  EMB-3 baseline mean affinity = {base:.3f}")
    print(f"  Round 3 best ({best['compound']}, {best.get('source','?')}) "
          f"mean = {best['mean']:.3f} (Δ {delta:+.3f})")
    print(f"    SMILES: {best['smiles']}")
    print(f"    TGFB1={best.get('TGFB1', 0):.3f} MMP1={best.get('MMP1', 0):.3f}")
    print(f"    hERG={best.get('hERG', 0):.3f} Skin={best.get('Skin_Reaction', 0):.3f}"
          f" logP={best.get('logP', 0):.2f}")

    n_better = (aff_full["mean"] > base).sum()
    print(f"\n  EMB-3 능가 candidate 수: {n_better} / {len(aff_full)}")
    if n_better == 0:
        print("  → Round 3 음성. EMB-3가 여전히 최고 lead.")
        print("  → 권장: SATURN goal-conditioned 또는 NPASS DB curation 후 재시도.")
    elif delta > 0.05:
        print("  ✅ EMB-3 능가 신규 lead 후보 발견 → MD 검증 권장")
    else:
        print("  → 미세 개선만, MD 비용 대비 효익 낮음.")

    return 0


def main() -> int:
    print("=== Round 3 scaffold-hop (EMB-3 tighter + BRICS grafting) ===\n")
    print(f"Seed: EMB-3 = {EMB3_SMILES}")
    print(f"Baseline mean affinity: {EMB3_BASELINE['mean_aff']:.3f}")
    print("Strategy: T=0.6, 300 samples, BRICS herbal grafting")

    sampled = step1_reinvent()
    brics = step2_brics_graft()
    cands = step3_filter(sampled, brics)
    if cands.empty:
        print("\n⚠️ ADMET 통과 0건 — Round 3 종료.")
        return 0
    aff = step4_cofold(cands)
    step5_summarize(aff)
    print(f"\n✅ Round 3 완료. {OUT} 확인.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
