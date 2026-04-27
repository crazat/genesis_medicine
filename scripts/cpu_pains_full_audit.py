"""Full PAINS audit on 2530 mol pool (2336 ADMET + 194 R4) for paper #3 v0.3 evidence."""
import sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import FilterCatalog, Descriptors

RDLogger.DisableLog("rdApp.*")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"

# Initialize all relevant filter catalogs
PARAMS_PAINS_A = FilterCatalog.FilterCatalogParams()
PARAMS_PAINS_A.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A)
PARAMS_PAINS_B = FilterCatalog.FilterCatalogParams()
PARAMS_PAINS_B.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B)
PARAMS_PAINS_C = FilterCatalog.FilterCatalogParams()
PARAMS_PAINS_C.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C)
PARAMS_BRENK = FilterCatalog.FilterCatalogParams()
PARAMS_BRENK.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.BRENK)
PARAMS_NIH = FilterCatalog.FilterCatalogParams()
PARAMS_NIH.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.NIH)
PARAMS_ZINC = FilterCatalog.FilterCatalogParams()
PARAMS_ZINC.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.ZINC)

CAT_A = FilterCatalog.FilterCatalog(PARAMS_PAINS_A)
CAT_B = FilterCatalog.FilterCatalog(PARAMS_PAINS_B)
CAT_C = FilterCatalog.FilterCatalog(PARAMS_PAINS_C)
CAT_BRENK = FilterCatalog.FilterCatalog(PARAMS_BRENK)
CAT_NIH = FilterCatalog.FilterCatalog(PARAMS_NIH)
CAT_ZINC = FilterCatalog.FilterCatalog(PARAMS_ZINC)


def audit(smi):
    try:
        m = Chem.MolFromSmiles(smi)
        if not m:
            return None
        result = {
            "smiles": smi,
            "PAINS_A_match": CAT_A.HasMatch(m),
            "PAINS_B_match": CAT_B.HasMatch(m),
            "PAINS_C_match": CAT_C.HasMatch(m),
            "Brenk_match": CAT_BRENK.HasMatch(m),
            "NIH_match": CAT_NIH.HasMatch(m),
            "ZINC_match": CAT_ZINC.HasMatch(m),
        }
        # Get specific PAINS hit names (most informative)
        for cat_name, cat_obj in [("PAINS_A", CAT_A), ("PAINS_B", CAT_B), ("PAINS_C", CAT_C)]:
            entries = cat_obj.GetMatches(m)
            if entries:
                result[f"{cat_name}_filter"] = ",".join(
                    [e.GetDescription()[:30] for e in entries[:2]])
        # 1,4-benzoquinone substructure check (our embelin scaffold)
        bq_pattern = Chem.MolFromSmarts("O=C1C(=O)C=CC=C1")
        bq_hyd = Chem.MolFromSmarts("OC1=CC(=O)C(O)=CC1=O")  # 2,5-OH benzoquinone
        result["is_benzoquinone"] = m.HasSubstructMatch(bq_pattern) if bq_pattern else False
        result["is_2_5_dihydroxy_bq"] = m.HasSubstructMatch(bq_hyd) if bq_hyd else False
        # Total flags
        result["n_pains_flags"] = (result["PAINS_A_match"]
                                     + result["PAINS_B_match"]
                                     + result["PAINS_C_match"])
        result["all_filters_clean"] = not any([
            result["PAINS_A_match"], result["PAINS_B_match"], result["PAINS_C_match"],
            result["Brenk_match"], result["NIH_match"]])
        return result
    except Exception:
        return None


def main():
    drug = pd.read_csv(OUT / "druglikeness_full.csv")
    smiles = drug["smiles"].dropna().unique().tolist()
    try:
        r4 = pd.read_csv(OUT / "round4_expanded.csv")
        smiles += r4["smiles"].dropna().tolist()
    except Exception:
        pass
    smiles = list(set(smiles))
    print(f"Total mol for full PAINS audit: {len(smiles)}")

    with Pool(processes=12) as p:
        results = p.map(audit, smiles)
    valid = [r for r in results if r]
    df = pd.DataFrame(valid)
    df.to_csv(OUT / "pains_full_audit.csv", index=False)
    print(f"\n✅ pains_full_audit.csv ({len(df)})")

    print("\n[Filter-fail rates]")
    for f in ["PAINS_A_match", "PAINS_B_match", "PAINS_C_match",
                "Brenk_match", "NIH_match", "is_benzoquinone", "is_2_5_dihydroxy_bq"]:
        n = df[f].sum()
        print(f"  {f}: {n}/{len(df)} ({100*n/len(df):.1f}%)")

    print(f"\n[Pool composition by 1,4-benzoquinone scaffold]")
    bq = df[df["is_benzoquinone"]]
    bq25 = df[df["is_2_5_dihydroxy_bq"]]
    print(f"  All 1,4-benzoquinones: {len(bq)} ({100*len(bq)/len(df):.1f}%)")
    print(f"  2,5-dihydroxy-1,4-benzoquinones (embelin class): {len(bq25)} ({100*len(bq25)/len(df):.1f}%)")

    # Embelin-class but PAINS-clean (rare gem)
    safe = df[(df["is_benzoquinone"]) & (df["all_filters_clean"])]
    print(f"\n[1,4-benzoquinones passing ALL PAINS+Brenk+NIH: {len(safe)}]")
    if len(safe) > 0:
        print(safe.head(5)["smiles"].tolist())

    return 0


if __name__ == "__main__":
    sys.exit(main())
