#!/usr/bin/env python
"""audit_section45_de_relax.py — do paper_A §4.5's ΔE_relax values reproduce? (2026-07-16)

§4.5 carries the paper's headline repositioning claim, and it is in both abstracts:
    "Indapamide ΔE_relax = 6.42 kcal/mol (gas) / 7.48 kcal/mol (water-ALPB) places it within the
     predictable-conformer regime (NOT a σ-outlier), supporting its repositioning candidacy"
and §4.5 argues it explicitly by ordering: "Indapamide's ΔE_relax (6.42-7.48 kcal/mol) is well below the
σ outlier threshold and the CHEMBL94487 paper_B reference (9.36) — Indapamide is NOT a σ outlier".

NO SOURCE FILE HOLDS THOSE NUMBERS. Not one of CHEMBL98 / CHEMBL406 / CHEMBL94487 / CHEMBL57058 has a
dE_relax record in any xtb JSON under pilot/round28_retroval/ (a 9.36 does exist there, but it belongs to
CHEMBL294088 — a coincidence, not the cited value).

What DOES survive is the xtb optimisation trajectory left in pilot/round28_retroval/top_hit_work/<cmpd>/
from 2026-05-16, one day before manuscript_v0.1. This script reads ΔE_relax straight out of those
trajectories: first frame = input geometry, last frame = converged, ΔE = (E_first - E_last) * 627.509.
Nothing is recomputed and nothing is assumed.

TWO INDEPENDENT CHECKS THAT THE READING IS SOUND:
  1. Re-running `xtb in.xyz --gfn 2 --sp --alpb h2o` reproduces each trajectory's FIRST-frame energy to
     8-9 decimal places -> the stored runs were ALPB(water), and in.xyz is genuinely their input.
  2. Vorinostat comes out at 3.91 against the manuscript's 3.89 -- i.e. the method reproduces the one
     value that is right, exactly as §4.7's BertzCT number validated the §4.6 audit.

RESULT — the ordering the claim rests on is REVERSED:
    Vorinostat   manuscript 3.89   trajectory  3.91   match
    Indapamide   manuscript 7.48   trajectory 12.27   MISMATCH (1.6x)
    CHEMBL94487  manuscript 9.36   trajectory  5.69   MISMATCH
  The manuscript asserts Indapamide (7.48) < CHEMBL94487 (9.36), concluding indapamide is the safe one.
  The surviving data says Indapamide (12.27) > CHEMBL94487 (5.69) -- the opposite ordering.

HONEST LIMIT ON THIS CONCLUSION. ΔE_relax is the strain of ONE starting pose, so a different starting
cofold pose legitimately gives a different value; the original run may have used a pose that no longer
exists on disk (the scratch dir holds a single run, while §4.5 claims three solvent modes -- so it was
overwritten at least twice). We therefore cannot prove the published numbers were never computed. We can
only state what is checkable: no artifact holds them, and the only artifact that survives contradicts them
and inverts the comparison the repositioning claim is built on. Either way the values are unpublishable as
they stand -- they must be recomputed from a recorded, named pose before submission.
"""
import os
import re

AU2KCAL = 627.5094740631
W = "/home/crazat/genesis_medicine/pilot/round28_retroval/top_hit_work"
CLAIMED = {"Vorinostat": 3.89, "Indapamide": 7.48, "CHEMBL94487": 9.36}   # §4.5, ALPB column


def de_relax(cmpd):
    p = f"{W}/{cmpd}/xtbopt.log"
    if not os.path.exists(p):
        return None
    e = [float(m) for m in re.findall(r"energy:\s*(-?\d+\.\d+)", open(p).read())]
    if len(e) < 2:
        return None
    return e[0], e[-1], (e[0] - e[-1]) * AU2KCAL, len(e)


def main():
    print("=" * 84)
    print("paper_A §4.5 AUDIT — ΔE_relax read from the 2026-05-16 xtb trajectories (ALPB/water)")
    print("=" * 84)
    print(f"{'compound':<14}{'E_start(Eh)':>17}{'E_final(Eh)':>17}{'ΔE(kcal)':>10}{'frames':>8}"
          f"{'claimed':>9}  verdict")
    for c in ["Vorinostat", "Indapamide", "CHEMBL94487", "CHEMBL57058"]:
        got = de_relax(c)
        if not got:
            print(f"{c:<14} no trajectory")
            continue
        e0, e1, de, n = got
        cl = CLAIMED.get(c)
        v = "-" if cl is None else ("match" if abs(de - cl) < 0.15 else "MISMATCH")
        cls = "-" if cl is None else f"{cl:.2f}"
        print(f"{c:<14}{e0:>17.9f}{e1:>17.9f}{de:>10.2f}{n:>8}{cls:>9}  {v}")

    ind = de_relax("Indapamide")
    ref = de_relax("CHEMBL94487")
    if ind and ref:
        print(f"\nTHE CLAIM: manuscript orders Indapamide {CLAIMED['Indapamide']:.2f} < "
              f"CHEMBL94487 {CLAIMED['CHEMBL94487']:.2f}  => 'indapamide is NOT a σ outlier'")
        print(f"THE DATA : trajectories order Indapamide {ind[2]:.2f} > CHEMBL94487 {ref[2]:.2f}"
              f"  => the comparison inverts")


if __name__ == "__main__":
    main()
