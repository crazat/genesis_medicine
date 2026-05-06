"""ADMET-AI v2 batched screen on BRICS 2241 + top100 novel + ChEMBL extended.

Paper-tier task: produces dermal/skin-relevant ADMET profile for downstream
preprint integration (logKp, skin irritation, hERG, BBB penalty, CYP DDI).

Heavy: 24-core multiprocessing for SMILES sanitization + small-batch model
calls. Runs once, finite, produces 3 CSV outputs.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
OUT.mkdir(parents=True, exist_ok=True)


def canonicalize(smi: str):
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return None
        return Chem.MolToSmiles(m)
    except Exception:
        return None


def main():
    print("=" * 72)
    print("ADMET-AI screen: BRICS 2241 + top100 + ChEMBL extended 95")
    print("=" * 72)

    # Sources
    sources = []
    brics = pd.read_csv(ROOT / "pilot/cpu_queue_v5/brics_massive.csv")
    brics["source"] = "brics_massive"
    sources.append(brics[["smiles", "source"]])

    top100 = pd.read_csv(ROOT / "pilot/cpu_queue_v5/top100_novel_candidates.csv")
    top100["source"] = "top100_novel"
    sources.append(top100[["smiles", "source"]])

    chembl = pd.read_csv(ROOT / "pilot/cpu_queue/chembl_mmp1_extended.csv")
    if "smiles" in chembl.columns:
        chembl["source"] = "chembl_extended"
        sources.append(chembl[["smiles", "source"]])

    df = pd.concat(sources, ignore_index=True).drop_duplicates("smiles")
    print(f"Total unique SMILES to screen: {len(df)}")

    # Canonicalize via Pool(24)
    with Pool(processes=24) as pool:
        canon = pool.map(canonicalize, df["smiles"].astype(str).tolist())
    df["canonical"] = canon
    df = df.dropna(subset=["canonical"]).drop_duplicates("canonical")
    print(f"Canonicalized: {len(df)}")

    # ADMET-AI inference (single-pass batched, no Pool — model is GPU-aware
    # but we run CPU mode here to avoid clashing with GPU boltz)
    try:
        import os
        os.environ["CUDA_VISIBLE_DEVICES"] = ""    # force CPU
        from admet_ai import ADMETModel
        print("Loading ADMET-AI v2 (CPU mode — boltz owns GPU)...")
        model = ADMETModel()

        smis = df["canonical"].tolist()
        # Batched in chunks of 200
        BATCH = 200
        all_preds = []
        for i in range(0, len(smis), BATCH):
            chunk = smis[i:i + BATCH]
            preds = model.predict(smiles=chunk)
            preds["smiles"] = chunk
            all_preds.append(preds)
            print(f"  batch {i // BATCH + 1}/{(len(smis) - 1) // BATCH + 1}: {len(chunk)} predicted")

        out = pd.concat(all_preds, ignore_index=True)
        out = out.merge(df[["canonical", "source"]],
                        left_on="smiles", right_on="canonical", how="left")
        out.to_csv(OUT / "admet_screen_combined.csv", index=False)
        print(f"\n✅ admet_screen_combined.csv ({len(out)} rows, {len(out.columns)} endpoints)")

        # Topical-friendly filter
        cols = list(out.columns)
        topical_cols = [c for c in cols if any(k in c.lower()
                        for k in ("logp", "logkp", "skin", "permeab", "herg", "ames"))]
        if topical_cols:
            print(f"\nTopical-relevant endpoints found: {topical_cols}")
            sub = out[["smiles", "source"] + topical_cols]
            sub.to_csv(OUT / "admet_topical_focus.csv", index=False)
            print(f"✅ admet_topical_focus.csv")

    except Exception as e:
        print(f"❌ ADMET-AI failed: {e}")
        import traceback
        traceback.print_exc()
        df.to_csv(OUT / "admet_screen_input_only.csv", index=False)
        print(f"  (input list saved at admet_screen_input_only.csv)")


if __name__ == "__main__":
    sys.exit(main())
