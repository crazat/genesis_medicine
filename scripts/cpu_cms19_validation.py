"""CMS-19 (R9_19) validation: PAINS + Dancik PBPK + xtb gap + Tanimoto NPASS."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/cpu_meaningful"
sys.path.insert(0, str(ROOT))

CMS19_SMI = "COc1ccc(O)c(C=Cc2cc(O)c(O)c(O)c2)c1"
CMS19_NAME = "CMS-19"


def main():
    print(f"=== {CMS19_NAME} validation ===")
    print(f"SMILES: {CMS19_SMI}")

    from rdkit import Chem
    from rdkit.Chem import FilterCatalog, Descriptors, Crippen, AllChem, DataStructs
    m = Chem.MolFromSmiles(CMS19_SMI)
    print(f"\n[Lipinski + physchem]")
    print(f"  MW: {Descriptors.MolWt(m):.1f}, logP: {Crippen.MolLogP(m):.2f}, "
          f"TPSA: {Descriptors.TPSA(m):.1f}, HBD: {Descriptors.NumHDonors(m)}, "
          f"HBA: {Descriptors.NumHAcceptors(m)}, RotB: {Descriptors.NumRotatableBonds(m)}")

    print(f"\n[1] PAINS / Brenk / NIH / ZINC filter audit")
    catalogs = [
        ("PAINS_A", FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A),
        ("PAINS_B", FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B),
        ("PAINS_C", FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C),
        ("BRENK",   FilterCatalog.FilterCatalogParams.FilterCatalogs.BRENK),
        ("NIH",     FilterCatalog.FilterCatalogParams.FilterCatalogs.NIH),
        ("ZINC",    FilterCatalog.FilterCatalogParams.FilterCatalogs.ZINC),
    ]
    flags = []
    for name, cat in catalogs:
        params = FilterCatalog.FilterCatalogParams()
        params.AddCatalog(cat)
        flt = FilterCatalog.FilterCatalog(params)
        if flt.HasMatch(m):
            for e in flt.GetMatches(m):
                print(f"  ❌ {name}: {e.GetDescription()}")
                flags.append(f"{name}:{e.GetDescription()}")
        else:
            print(f"  ✅ {name}: clean")

    print(f"\n[2] Dancik 4-layer skin PBPK")
    from src.genesis_medicine.dermatology.skin_pbpk_dancik import (
        DancikSkinPBPK, TopicalFormulation)
    pbpk = DancikSkinPBPK()
    for veh, occ in [("ointment", True), ("cream", False), ("aqueous", False)]:
        r = pbpk.predict(TopicalFormulation(
            smiles=CMS19_SMI, dose_ug_per_cm2=100,
            vehicle=veh, occluded=occ))
        print(f"  {veh:10s}: logKp={r.log_kp_cm_s:.2f}, "
                f"flux={r.flux_ss_ug_cm2_h:.0f} μg/cm²/h, "
                f"24h dose={r.cumulative_dose_24h_ug_cm2:.0f}, "
                f"bioavail={r.bioavailability_topical:.2f}")

    print(f"\n[3] xtb GFN2 (R7+R8+R9 통합)")
    xtb = pd.read_csv(OUT / "xtb_r789_combined.csv")
    canon_q = Chem.MolToSmiles(m)
    matched = False
    for _, row in xtb.iterrows():
        try:
            mr = Chem.MolFromSmiles(str(row["smi"]))
            if mr and Chem.MolToSmiles(mr) == canon_q:
                print(f"  ✅ matched idx {row['idx']}: "
                        f"energy_kcal={row['energy_kcal_min']:.1f}, "
                        f"HOMO-LUMO gap={row['gap_ev_mean']:.2f} eV, "
                        f"n_conf={row['n_conf']}")
                matched = True
                break
        except Exception:
            continue
    if not matched:
        print(f"  ⚠️  CMS-19 not found in xtb_r789_combined.csv (canonical mismatch)")

    print(f"\n[4] Tanimoto NPASS top analog (9997 NPASS)")
    fp_q = AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)
    npass = pd.read_csv(OUT / "npass_2026_pottsguy_logkp_10k.csv")
    sims = []
    for _, row in npass.iterrows():
        m2 = Chem.MolFromSmiles(str(row["smiles"]))
        if m2 is None: continue
        fp2 = AllChem.GetMorganFingerprintAsBitVect(m2, 2, 2048)
        s = DataStructs.TanimotoSimilarity(fp_q, fp2)
        sims.append((row["np_id"], s, row["smiles"], row["logp"], row["mw"]))
    sims.sort(key=lambda x: -x[1])
    for np_id, sim, smi, logp, mw in sims[:5]:
        print(f"  {np_id}: Tan={sim:.3f}, MW={mw:.0f}, logP={logp:.1f} | {smi[:50]}")

    print(f"\n[5] R7+R8+R9 cofold mean affinity (per target)")
    pieces = []
    for r in [7, 8, 9]:
        f = OUT / f"r{r}_affinity_consolidated.csv"
        if f.exists():
            pieces.append(pd.read_csv(f))
    cofold = pd.concat(pieces)
    cms19_hits = cofold[cofold["smiles"] == CMS19_SMI]
    if len(cms19_hits):
        per_target = cms19_hits.groupby("target")["affinity_prob_binary"].max().sort_values(ascending=False)
        print(f"  {len(cms19_hits)} hits across {per_target.size} targets")
        print(f"  Mean: {per_target.mean():.3f}, Max: {per_target.max():.3f}, Min: {per_target.min():.3f}")
        for t, v in per_target.items():
            sym = "★" if v >= 0.6 else " "
            print(f"  {sym} {t:8s}: {v:.3f}")

    # Summary verdict
    print(f"\n=== VERDICT ===")
    if not flags:
        print(f"  ✅ CMS-19 PAINS-clean — paper-tier scaffold OK for dual lead")
    else:
        print(f"  ⚠️  CMS-19 flagged in {len(flags)} catalogs — disclosure required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
