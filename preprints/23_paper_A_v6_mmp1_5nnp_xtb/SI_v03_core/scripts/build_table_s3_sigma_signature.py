#!/usr/bin/env python
"""build_table_s3_sigma_signature.py — generate paper_A Supplementary Table S3 from the real data.

CONTEXT (2026-07-16). Both paper_A manuscripts cite "Supplementary Table S3" (the full top-30 descriptor
correlation table backing §4.6) but no such file existed, and §4.6's own top-10 does not reproduce -- see
audit_section46_sigma_signature.py, which shows all ten named descriptors sit at r ~ 0 (p up to 0.91)
against the claimed r < -0.97, while §4.7's BertzCT number reproduces to 4 decimals from the same file and
DV, proving the setup is the manuscript's own. This script produces the table §4.6 should have had.

METHOD AND WHY. Rank (Spearman) correlation is the primary statistic, not Pearson. dE_relax carries three
extreme values (599.5 / 504.4 / 494.8 kcal/mol against a median of 11.65 and an IQR of 4.29); on the
Pearson scale those three points alone drag size descriptors (Diameter, Radius, WPath) to r ~ +0.99 while
their rank correlation is only ~ +0.26. Reporting that as a "signature" would repeat at n=140 the exact
small-n deterministic-fit error §4.7 warns about at n=4. The rank statistic is immune to it, and the
signature it finds survives deletion of all three outliers (reported per row as rho_no_outliers).

Emits SI/Table_S3_sigma_signature_mordred_top30.csv with, per descriptor: Spearman rho + p, the
outlier-deleted rho, the Pearson r for transparency, and the descriptor family.
"""
import numpy as np
import pandas as pd
from scipy import stats

SAR = "/home/crazat/genesis_medicine/pilot/round28_retroval/paper_a_sar_dataset.csv"
OUT = ("/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/SI/"
       "Table_S3_sigma_signature_mordred_top30.csv")
DV = "dE_relax"
NON_DESC = {"cid", "ic50_nm", "dE_relax", "smiles"}
TOPN = 30


def family(c):
    """Mordred descriptor family, for the interpretation column."""
    if c.startswith("ATS") or c.startswith("AATS"):
        return "Moreau-Broto autocorrelation"
    if "TopoPSA" in c:
        return "topological polar surface area"
    if c.startswith("nHetero") or c.startswith("nN") or c.startswith("nO") or c.startswith("nX"):
        return "heteroatom count"
    if c.startswith("SM1_Dz") or c.startswith("SM_"):
        return "Barysz matrix spectral moment"
    if c.startswith("Sp") and c.endswith("_A"):
        return "adjacency matrix spectrum"
    if c.startswith("BCUT"):
        return "BCUT eigenvalue"
    if "ETA" in c:
        return "ETA"
    if c.startswith("MID") or c.startswith("AMID"):
        return "information content"
    return "other"


def main():
    df = pd.read_csv(SAR)
    y = df[DV]
    outliers = set(y.nlargest(3).index)          # 599.5 / 504.4 / 494.8 vs median 11.65

    rows = []
    for c in df.columns:
        if c in NON_DESC:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        m = x.notna() & y.notna()
        if m.sum() < 100 or x[m].nunique() < 3:
            continue
        rho, p = stats.spearmanr(x[m], y[m])
        if not np.isfinite(rho):
            continue
        r_p, p_p = stats.pearsonr(x[m], y[m])
        m2 = m & ~df.index.isin(outliers)
        rho2, p2 = (stats.spearmanr(x[m2], y[m2]) if m2.sum() > 10 and x[m2].nunique() > 2
                    else (np.nan, np.nan))
        rows.append({
            "descriptor": c, "family": family(c), "n": int(m.sum()),
            "spearman_rho": round(float(rho), 4), "spearman_p": float(f"{p:.3g}"),
            "rho_no_outliers": round(float(rho2), 4) if np.isfinite(rho2) else "",
            "pearson_r": round(float(r_p), 4), "pearson_p": float(f"{p_p:.3g}"),
        })

    rows.sort(key=lambda d: -abs(d["spearman_rho"]))
    top = rows[:TOPN]
    for i, d in enumerate(top, 1):
        d["rank"] = i
    cols = ["rank", "descriptor", "family", "n", "spearman_rho", "spearman_p",
            "rho_no_outliers", "pearson_r", "pearson_p"]
    pd.DataFrame(top)[cols].to_csv(OUT, index=False)

    print(f"wrote {OUT}  ({len(top)} rows of {len(rows)} valid descriptors, n={top[0]['n']} ligands)")
    print(f"{'#':<3}{'descriptor':<16}{'rho':>8}{'p':>11}{'rho(-3out)':>12}{'pearson':>9}  family")
    for d in top[:12]:
        print(f"{d['rank']:<3}{d['descriptor']:<16}{d['spearman_rho']:>+8.3f}{d['spearman_p']:>11.2g}"
              f"{d['rho_no_outliers']:>+12.3f}{d['pearson_r']:>+9.3f}  {d['family']}")
    fams = pd.Series([d["family"] for d in top]).value_counts()
    print("\nfamily composition of the top-30:")
    for f, n in fams.items():
        print(f"  {n:>2}  {f}")
    pos = sum(1 for d in top if d["spearman_rho"] > 0)
    print(f"\ndirection: {pos}/{TOPN} POSITIVE  (manuscript §4.6 claims all NEGATIVE)")
    print(f"BCUT descriptors in the top-30: {sum(1 for d in top if d['family']=='BCUT eigenvalue')}"
          f"  (manuscript §4.6 claims 6 of its top-10)")


if __name__ == "__main__":
    main()
