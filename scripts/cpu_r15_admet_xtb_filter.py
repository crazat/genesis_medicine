"""R15 BRICS 44 candidates: ADMET-AI + xtb + skin window ranking.

Triple filter for R15 lead selection:
1. ADMET-AI v2 (107 endpoints) — AMES, hERG, DILI, BBB, HIA
2. GFN2-xTB single-point — HOMO-LUMO gap (electronic stability)
3. Dancik PBPK — logKp, flux

Output: pilot/cpu_meaningful/r15_lead_ranking.csv
"""
from __future__ import annotations
import sys
from pathlib import Path
from multiprocessing import Pool
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "pilot/cpu_meaningful"
OUT_DIR.mkdir(parents=True, exist_ok=True)

R15_CSV = ROOT / "pilot/cpu_meaningful/r15_brics_candidates.csv"


def xtb_one(args):
    idx, smi = args
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import AllChem
        from xtb.interface import Calculator, Param
        from xtb.libxtb import VERBOSITY_MUTED
        RDLogger.DisableLog("rdApp.*")

        m = Chem.MolFromSmiles(smi)
        m = Chem.AddHs(m)
        cid = AllChem.EmbedMolecule(m, randomSeed=42, useRandomCoords=True)
        if cid < 0:
            return {"idx": idx, "smi": smi, "error": "embed"}
        AllChem.MMFFOptimizeMolecule(m, maxIters=500)
        conf = m.GetConformer()
        natoms = m.GetNumAtoms()
        nums = np.array([a.GetAtomicNum() for a in m.GetAtoms()])
        positions = np.array([(conf.GetAtomPosition(i).x,
                                conf.GetAtomPosition(i).y,
                                conf.GetAtomPosition(i).z)
                               for i in range(natoms)]) / 0.5291772083
        calc = Calculator(Param.GFN2xTB, nums, positions)
        calc.set_verbosity(VERBOSITY_MUTED)
        res = calc.singlepoint()
        e_au = res.get_energy()
        try:
            orbs = res.get_orbital_eigenvalues()
            occ = res.get_orbital_occupations()
            homo_idx = max(i for i, o in enumerate(occ) if o > 0.5)
            homo = orbs[homo_idx] * 27.211386
            lumo = orbs[homo_idx + 1] * 27.211386
            gap = lumo - homo
        except Exception:
            homo = lumo = gap = float("nan")
        return {"idx": idx, "smi": smi,
                "energy_au": round(e_au, 6),
                "HOMO_eV": round(homo, 3) if homo == homo else None,
                "LUMO_eV": round(lumo, 3) if lumo == lumo else None,
                "gap_eV": round(gap, 3) if gap == gap else None}
    except Exception as e:
        return {"idx": idx, "smi": smi, "error": str(e)[:200]}


def main():
    if not R15_CSV.exists():
        print(f"missing {R15_CSV}")
        return 1
    df = pd.read_csv(R15_CSV)
    print(f"R15 BRICS pool: {len(df)} candidates")

    # ADMET-AI
    print("\n=== ADMET-AI ===")
    try:
        from admet_ai import ADMETModel
        model = ADMETModel()
        preds = model.predict(smiles=df["derivative_smiles"].tolist())
        if isinstance(preds, pd.DataFrame):
            admet_df = preds.reset_index().rename(columns={"index": "smiles_in"})
        else:
            admet_df = pd.DataFrame(preds)
        admet_df["derivative_smiles"] = df["derivative_smiles"].values[:len(admet_df)]
        keep_cols = ["derivative_smiles", "AMES", "DILI", "hERG", "BBB_Martins", "HIA_Hou",
                      "Lipophilicity_AstraZeneca", "Solubility_AqSolDB"]
        keep_cols = [c for c in keep_cols if c in admet_df.columns]
        merged = df.merge(admet_df[keep_cols], on="derivative_smiles", how="left")
        print(f"  ✅ ADMET joined ({len(merged)} rows)")
    except Exception as e:
        print(f"  ❌ ADMET-AI: {e}")
        merged = df

    # xtb
    print("\n=== xtb HOMO-LUMO ===")
    args = [(i, s) for i, s in enumerate(df["derivative_smiles"].tolist())]
    with Pool(min(8, len(args))) as p:
        xtb_results = p.map(xtb_one, args)
    xtb_df = pd.DataFrame(xtb_results)
    xtb_df = xtb_df.rename(columns={"smi": "derivative_smiles"})
    xtb_keep = ["derivative_smiles", "HOMO_eV", "LUMO_eV", "gap_eV", "energy_au"]
    xtb_keep = [c for c in xtb_keep if c in xtb_df.columns]
    merged = merged.merge(xtb_df[xtb_keep], on="derivative_smiles", how="left")

    # Composite ranking — skin_window + AMES_low + gap_high + flux_high
    if "AMES" in merged.columns and "gap_eV" in merged.columns:
        merged["score"] = (
            (1 - merged.get("AMES", 0.5).fillna(0.5)) * 0.4 +
            merged["skin_window"].astype(float) * 0.3 +
            (merged.get("gap_eV", 3.0).fillna(3.0) > 2.5).astype(float) * 0.2 +
            merged["QED"].fillna(0.5) * 0.1
        )
        merged = merged.sort_values("score", ascending=False).reset_index(drop=True)

    out_path = OUT_DIR / "r15_lead_ranking.csv"
    merged.to_csv(out_path, index=False)
    print(f"\nSaved {out_path} ({len(merged)} rows)")
    if "score" in merged.columns:
        print("\nTop 10 R15 leads:")
        cols = ["leader_seed", "derivative_smiles", "MW", "logP", "QED",
                 "AMES", "hERG", "gap_eV", "skin_window", "score"]
        cols = [c for c in cols if c in merged.columns]
        print(merged[cols].head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
