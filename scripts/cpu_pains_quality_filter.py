"""PAINS + REOS + Brenk + structural alert filter on 2336 pool + R4 candidates.

Removes pan-assay interference compounds (PAINS, Baell 2010), reactive groups
(Brenk filter), and non-drug-like structures (REOS).
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import FilterCatalog, Descriptors

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

PAINS_PARAMS = FilterCatalog.FilterCatalogParams()
PAINS_PARAMS.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
PAINS_CATALOG = FilterCatalog.FilterCatalog(PAINS_PARAMS)

BRENK_PARAMS = FilterCatalog.FilterCatalogParams()
BRENK_PARAMS.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.BRENK)
BRENK_CATALOG = FilterCatalog.FilterCatalog(BRENK_PARAMS)

NIH_PARAMS = FilterCatalog.FilterCatalogParams()
NIH_PARAMS.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.NIH)
NIH_CATALOG = FilterCatalog.FilterCatalog(NIH_PARAMS)


def reos_check(m):
    """Rapid Elimination Of Swill (Hann + Walters)."""
    mw = Descriptors.MolWt(m)
    logp = Descriptors.MolLogP(m)
    hbd = Descriptors.NumHDonors(m)
    hba = Descriptors.NumHAcceptors(m)
    rotb = Descriptors.NumRotatableBonds(m)
    fc = sum(a.GetFormalCharge() for a in m.GetAtoms())
    heavy = m.GetNumHeavyAtoms()

    fail = []
    if not (200 <= mw <= 500):
        fail.append("mw")
    if not (-5 <= logp <= 5):
        fail.append("logp")
    if hbd > 5:
        fail.append("hbd")
    if hba > 10:
        fail.append("hba")
    if rotb > 8:
        fail.append("rotb")
    if abs(fc) > 2:
        fail.append("charge")
    if heavy > 50:
        fail.append("heavy")
    return fail


def quality_check(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        # PAINS
        pains_match = PAINS_CATALOG.HasMatch(m)
        # Brenk reactive groups
        brenk_match = BRENK_CATALOG.HasMatch(m)
        # NIH MLSMR rejection rules
        nih_match = NIH_CATALOG.HasMatch(m)
        # REOS
        reos_fail = reos_check(m)
        all_pass = (not pains_match) and (not brenk_match) and (
            not nih_match) and len(reos_fail) == 0

        return {
            "smiles": smi,
            "pains_alert": pains_match,
            "brenk_alert": brenk_match,
            "nih_alert": nih_match,
            "reos_fails": ",".join(reos_fail) if reos_fail else "",
            "n_reos_fail": len(reos_fail),
            "all_filters_pass": all_pass,
        }
    except Exception:
        return None


def main():
    print("=" * 72)
    print("PAINS + REOS + Brenk + NIH structural alerts")
    print("=" * 72)

    # Combine 2336 pool + R4 candidates
    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    smiles = drug["smiles"].dropna().unique().tolist()

    try:
        r4 = pd.read_csv(OUT / "round4_top100.csv")
        smiles += r4["smiles"].dropna().tolist()
    except Exception:
        pass

    smiles = list(set(smiles))
    print(f"Total unique mol: {len(smiles)}")

    with Pool(processes=12) as p:
        results = p.map(quality_check, smiles)
    valid = [r for r in results if r]
    df = pd.DataFrame(valid)
    df.to_csv(OUT / "quality_filter_full.csv", index=False)
    print(f"\nValid: {len(df)}")

    print(f"\n[Filter-fail breakdown]")
    print(f"  PAINS alerts: {df['pains_alert'].sum()}/{len(df)}")
    print(f"  Brenk alerts: {df['brenk_alert'].sum()}/{len(df)}")
    print(f"  NIH alerts: {df['nih_alert'].sum()}/{len(df)}")
    print(f"  REOS fails (any): {(df['n_reos_fail'] > 0).sum()}/{len(df)}")

    clean = df[df["all_filters_pass"]]
    clean.to_csv(OUT / "quality_filtered_clean.csv", index=False)
    print(f"\n[Clean (all 4 filters pass): {len(clean)}/{len(df)} = {100*len(clean)/len(df):.1f}%]")

    # PAINS-flagged subset for review
    pains = df[df["pains_alert"]]
    pains.to_csv(OUT / "quality_pains_flagged.csv", index=False)
    print(f"  PAINS-flagged: {len(pains)} mol — manual review recommended")

    return 0


if __name__ == "__main__":
    sys.exit(main())
