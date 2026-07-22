#!/usr/bin/env python
"""audit_section46_sigma_signature.py — does paper_A §4.6's "sigma outlier signature" table reproduce?

WHY THIS EXISTS (2026-07-16). paper_A manuscript_v0.2.md §4.6 and manuscript_JCIM_v0.1.md §4.6 report a
top-10 Pearson correlation table between Mordred descriptors and dE_relax on the n=140 SAR cohort, headed
"all p ~ 0, NEGATIVE direction", with every |r| > 0.97 and a BCUT/ETA/spectral family interpretation. That
claim is load-bearing: it appears in both abstracts, drives the §4.8 "complexity-aware mandatory xtb-OPT
rescue" workflow, and is plotted as Figure 4 panel B. Both manuscripts are marked submission-ready.

It does not reproduce. Run this script to see for yourself.

THE DISCRIMINATING TEST. A failure to reproduce could just mean this audit uses the wrong dataset or the
wrong dependent variable. It does not: §4.7 of the same manuscript reports BertzCT r=-0.1246, p=0.142 on
the same cohort, and that number reproduces to 4 decimal places here. Same file, same DV (dE_relax), same
method (Pearson) => the setup is the manuscript's own, and §4.6's table is what is wrong.

WHAT IS ACTUALLY TRUE IN THE DATA (all printed below, nothing asserted from prose):
  1. The 10 descriptors §4.6 names are all present, and all have r ~ 0 (p up to 0.91). Not one is near -0.97.
  2. No alternative DV rescues them (ic50_nm, log10(dE_relax) tested).
  3. The genuine Pearson top-10 is a LEVERAGE ARTIFACT: dE_relax has 3 extreme values (599/504/495 kcal/mol
     vs median 11.65, IQR 4.29), which drag Diameter/Radius/WPath to r ~ +0.99 while their rank correlation
     is only ~ +0.26. Reporting those as a "signature" would repeat, at n=140, exactly the small-n
     deterministic-fit error that §4.7 warns about at n=4.
  4. The defensible signature is the RANK correlation: ATS6s rho=+0.64, TopoPSA(NO) +0.60, nHetero +0.58
     (p < 1e-13) -- real, modest, and pointing at polarity/heteroatom content rather than BCUT eigenvalues.

DO NOT "fix" §4.6 by pasting this script's Spearman table in and calling it the same claim: the direction
(positive), the family (polar-surface/autocorrelation, not BCUT/ETA/spectral), and the strength (0.6, not
0.99) all differ, so the interpretation in §4.6/§4.8 and both abstracts changes with it. That is an author
decision, not a find-and-replace.
"""
import sys

import numpy as np
import pandas as pd
from scipy import stats

SAR = "/home/crazat/genesis_medicine/pilot/round28_retroval/paper_a_sar_dataset.csv"
DV = "dE_relax"
NON_DESC = {"cid", "ic50_nm", "dE_relax", "smiles"}

# the table as printed in manuscript_v0.2.md §4.6 / manuscript_JCIM_v0.1.md §4.6
MANUSCRIPT_TOP10 = [
    ("BCUTse-1h", -0.9883), ("AETA_alpha", -0.9858), ("BCUTv-1l", -0.9847),
    ("BCUTi-1l", -0.9838), ("AXp-0d", -0.9829), ("SpMAD_A", -0.9827),
    ("SpMax_A", -0.9788), ("SpDiam_A", -0.9785), ("BCUTpe-1h", -0.9754),
    ("BCUTare-1h", -0.9702),
]


def corr(df, col, y, method="pearson"):
    x = pd.to_numeric(df[col], errors="coerce")
    m = x.notna() & y.notna()
    if m.sum() < 100 or x[m].nunique() < 3:
        return None
    f = stats.pearsonr if method == "pearson" else stats.spearmanr
    r, p = f(x[m], y[m])
    return (r, p, int(m.sum())) if np.isfinite(r) else None


def main():
    df = pd.read_csv(SAR)
    y = df[DV]
    print("=" * 82)
    print(f"paper_A §4.6 AUDIT   {SAR.split('/')[-1]}   n={len(df)}   DV={DV}")
    print("=" * 82)

    print("\n[1] DISCRIMINATING TEST — does §4.7's BertzCT number reproduce here?")
    r, p, n = corr(df, "BertzCT", y)
    print(f"    this audit : BertzCT r={r:+.4f}, p={p:.4f} (n={n})")
    print(f"    manuscript : BertzCT r=-0.1246, p=0.142")
    same = abs(r + 0.1246) < 0.002 and abs(p - 0.142) < 0.005
    print(f"    => {'REPRODUCES: dataset/DV/method are the manuscript' + chr(39) + 's own.' if same else 'DOES NOT reproduce -- audit setup differs; stop here.'}")
    if not same:
        sys.exit(1)

    print("\n[2] The 10 descriptors §4.6 names — their ACTUAL correlation with dE_relax")
    print(f"    {'descriptor':<13}{'actual r':>10}{'actual p':>11}{'claimed r':>11}")
    for c, claimed in MANUSCRIPT_TOP10:
        if c not in df.columns:
            print(f"    {c:<13}{'ABSENT':>10}{'-':>11}{claimed:>+11.4f}")
            continue
        got = corr(df, c, y)
        if not got:
            print(f"    {c:<13}{'const/NaN':>10}{'-':>11}{claimed:>+11.4f}")
            continue
        r, p, _ = got
        print(f"    {c:<13}{r:>+10.4f}{p:>11.3g}{claimed:>+11.4f}   {'match' if abs(r - claimed) < 0.01 else '<- MISMATCH'}")

    print("\n[3] Does any other dependent variable rescue the claim?")
    alts = {"ic50_nm": pd.to_numeric(df.get("ic50_nm"), errors="coerce"),
            "log10(dE_relax)": np.log10(y)}
    for lab, yy in alts.items():
        if yy is None:
            continue
        out = []
        for c, _ in MANUSCRIPT_TOP10[:4]:
            x = pd.to_numeric(df[c], errors="coerce")
            m = x.notna() & yy.notna()
            rr, _ = stats.pearsonr(x[m], yy[m])
            out.append(f"{c}={rr:+.3f}")
        print(f"    DV={lab:<16}{'  '.join(out)}")
    print("    (claimed: all between -0.97 and -0.99)")

    print("\n[4] Why the naive Pearson top-10 is ALSO not a signature — leverage check")
    s = y.sort_values(ascending=False)
    print(f"    dE_relax: top5 = {[round(v,1) for v in s.head(5)]}, median={y.median():.2f}, IQR={y.quantile(.75)-y.quantile(.25):.2f}")
    print(f"    {'descriptor':<15}{'Pearson':>9}{'Spearman':>10}   verdict")
    for c in ["Diameter", "Radius", "ECIndex", "WPath"]:
        if c not in df.columns:
            continue
        rp_, _, _ = corr(df, c, y)
        rs_, ps_, _ = corr(df, c, y, "spearman")
        print(f"    {c:<15}{rp_:>+9.4f}{rs_:>+10.4f}   {'leverage artifact (3 outliers drive it)' if abs(rp_) - abs(rs_) > 0.4 else 'stable'}")

    print("\n[5] The defensible signature — RANK correlation top-10 (outlier-robust)")
    res = []
    for c in df.columns:
        if c in NON_DESC:
            continue
        got = corr(df, c, y, "spearman")
        if got:
            res.append((c, got[0], got[1]))
    res.sort(key=lambda t: -abs(t[1]))
    for c, rho, p in res[:10]:
        print(f"    {c:<18} rho={rho:+.4f}  p={p:.3g}")
    print("\n    NOTE: positive direction, polarity/heteroatom family, |rho| ~ 0.6 -- none of which is what")
    print("    §4.6/§4.8/the abstracts currently say. Changing the table changes the claim: author decision.")


if __name__ == "__main__":
    main()
