#!/usr/bin/env python
"""anchor_sigma_ic50_analyze.py — does sigma_iptm actually gate agreement with EXPERIMENT?

This is P1's anchor (ledger MV 0.686, top claim) and the direct answer to the reviewer kill-shot
"no sigma-vs-experiment anchor". It is a pure-CPU read of the anchor cofold outputs; no GPU.

THE TEST. P1 claims de novo hits are trustworthy because they pass a DUAL-reliability gate (sigma_iptm +
sigma_E). A gate is only meaningful if predictions it PASSES agree with reality better than ones it
REJECTS. So: split ligands at the median sigma_iptm and compare Spearman(iptm_mean, pIC50) within each
half. If the low-sigma half correlates with experiment materially better than the high-sigma half, the
gate does what it claims. If both halves are the same, sigma is not buying reliability -- and no wet-lab
assay would change that; it would be a genuine negative result about the method.

WHY NOT A WET LAB (2026-07-15): the planned 17-sulfonamide assay adds ZERO usable points (expected inactive
-> no measurable IC50 -> no rank). 93 ChEMBL ligands that already carry a quantitative IC50 do. Ligands are
the missing ingredient, not measurements.

PILOT NUMBER, CORRECTED 2026-07-16. This docstring previously cited the 15-ligand pilot as rho=+0.383
(p=0.159) and concluded "n~52 for 80% power". That number existed ONLY in prose -- no script computed it and
no CSV held it -- and it does NOT reproduce. Recomputed from the authoritative sources (per-ligand mean
sigma_iptm over the n=161 cycles in preprints/24_.../sigma_iptm_unified_v143_v303_percycle.csv, ligand ids
de-prefixed of "mmp1_", intersected with data/chembl_mmp1_calibration.csv) the pilot is rho=+0.246 (p=0.376),
which needs n~127 for 80% power -- so this n=93 cohort has only ~66% power against it. The n=93 result must
therefore be reported as a BOUND (95% CI on rho=-0.005 is [-0.21,+0.20], which excludes the pilot's +0.246
but not a small positive effect), never as "the effect is zero". pilot_rho() below recomputes it live so the
figure can never again drift into prose-only existence.

Reports secondary diagnostics too (does iptm predict potency at all; is sigma related to potency itself),
because a gate that merely re-discovers "potent compounds are easier to fold" is not a reliability signal.
"""
import csv, glob, json, math, os, re, statistics, sys

GM = "/home/crazat/genesis_medicine"
D = f"{GM}/pilot/round27_paperA/anchor_sigma_ic50"
MANIFEST = f"{D}/anchor_manifest.csv"
OUT = f"{D}/anchor_result.csv"

try:
    from scipy import stats
except ImportError:
    sys.exit("scipy required (use the project .venv python)")


def iptm_samples(cid):
    """every per-sample iptm for one ligand (one confidence_*_model_N.json per diffusion sample)."""
    vals = []
    for p in glob.glob(f"{D}/outputs/**/predictions/{cid}/confidence_{cid}_model_*.json", recursive=True):
        try:
            vals.append(float(json.load(open(p))["iptm"]))
        except Exception:
            pass
    return vals


def fisher_ci(r, n, alpha=0.05):
    """95% CI for a correlation via the Fisher z transform. Reporting rho without this is how a
    bounded null gets mis-stated as 'the effect is zero' (see the 2026-07-16 correction above)."""
    if n <= 3:
        return (float("nan"), float("nan"))
    r = max(min(r, 0.999999), -0.999999)
    zr = 0.5 * math.log((1 + r) / (1 - r))
    se = 1.0 / math.sqrt(n - 3)
    zc = stats.norm.ppf(1 - alpha / 2)
    return math.tanh(zr - zc * se), math.tanh(zr + zc * se)


def n_for_power(r, power=0.80, alpha=0.05):
    """n needed to detect correlation r at the given power (Fisher z)."""
    r = max(min(abs(r), 0.999999), 1e-9)
    zr = 0.5 * math.log((1 + r) / (1 - r))
    return ((stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)) / zr) ** 2 + 3


def power_at(r, n, alpha=0.05):
    if n <= 3:
        return float("nan")
    r = max(min(abs(r), 0.999999), 1e-9)
    zr = 0.5 * math.log((1 + r) / (1 - r))
    return 1 - stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) - zr * math.sqrt(n - 3))


def pilot_rho():
    """Recompute the 15-ligand pilot LIVE from the authoritative CSVs -- never cite it from prose.
    Returns (rho, p, n) or None. Sources: the n=161 per-cycle sigma_iptm table (paper_B) intersected
    with the calibration IC50 set. NOTE the 'mmp1_' prefix on the per-cycle ligand ids: forgetting to
    strip it silently yields a 0-row intersection rather than an error."""
    # NOTE 2026-07-21: reads the WITHDRAWN fabricated panel on purpose — pilot_rho is only the labelled
    # fabricated-potency contrast the real n=93 anchor bound excludes. Whether to keep/drop/restate this
    # comparison is an author decision (it depends on fabricated potency). See the WITHDRAWN README.
    cal_p = f"{GM}/data/chembl_mmp1_calibration.WITHDRAWN.csv"
    per_p = (f"{GM}/preprints/24_paper_B_v1_boltz_xtb_rescue_zn_mmp1/"
             f"sigma_iptm_unified_v143_v303_percycle.csv")
    try:
        cal = {r["chembl_id"]: float(r["ic50_nm"]) for r in csv.DictReader(open(cal_p)) if r.get("ic50_nm")}
        per = {}
        for r in csv.DictReader(open(per_p)):
            lig = r["ligand"].replace("mmp1_", "")
            per.setdefault(lig, {"mean": [], "std": []})
            per[lig]["mean"].append(float(r["mean"]))
            per[lig]["std"].append(float(r["std"]))
    except Exception:
        return None
    rows = [{"iptm": statistics.mean(v["mean"]), "sig": statistics.mean(v["std"]),
             "pic": 9 - math.log10(cal[l])} for l, v in per.items() if l in cal and v["mean"]]
    if len(rows) < 5:
        return None
    ipt = [r["iptm"] for r in rows]; pic = [r["pic"] for r in rows]; sig = [r["sig"] for r in rows]
    ri = {v: i for i, v in enumerate(sorted(ipt))}; rp = {v: i for i, v in enumerate(sorted(pic))}
    err = [abs(ri[r["iptm"]] - rp[r["pic"]]) for r in rows]
    rho, p = stats.spearmanr(sig, err)
    return rho, p, len(rows)


def main():
    man = {r["chembl_id"]: r for r in csv.DictReader(open(MANIFEST))}
    rows = []
    for cid, r in man.items():
        v = iptm_samples(cid)
        if len(v) < 8:            # too few samples to estimate a dispersion
            continue
        rows.append({"chembl_id": cid, "n_samples": len(v),
                     "iptm_mean": statistics.mean(v), "sigma_iptm": statistics.stdev(v),
                     "ic50_nm": float(r["ic50_nm"]), "pIC50": float(r["pIC50"])})
    if len(rows) < 20:
        sys.exit(f"only {len(rows)} ligands have >=8 samples -- cofold still running, rerun when complete")

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    n = len(rows)
    sig = [r["sigma_iptm"] for r in rows]
    ipt = [r["iptm_mean"] for r in rows]
    pic = [r["pIC50"] for r in rows]
    print("=" * 78)
    print(f"SIGMA-vs-EXPERIMENT ANCHOR   n={n} ChEMBL MMP-1 ligands with quantitative IC50")
    print("=" * 78)
    print(f"  sigma_iptm : {min(sig):.4f} – {max(sig):.4f}  ({max(sig)/max(min(sig),1e-9):.1f}x range)")
    print(f"  iptm_mean  : {min(ipt):.4f} – {max(ipt):.4f}   (every ligand confidently folded)")
    print(f"  pIC50      : {min(pic):.2f} – {max(pic):.2f}   (IC50 {min(r['ic50_nm'] for r in rows):.3g}"
          f"–{max(r['ic50_nm'] for r in rows):.4g} nM, {math.log10(max(r['ic50_nm'] for r in rows)/min(r['ic50_nm'] for r in rows)):.2f} log span)")
    print(f"  predictions: {sum(r['n_samples'] for r in rows)}")
    print(f"  samples/ligand median: {statistics.median([r['n_samples'] for r in rows]):.0f}")

    # HEADLINE: does sigma predict the model's own potency-rank error? Reported as a BOUND (CI), because
    # this cohort is not powered to exclude a small effect -- see the 2026-07-16 correction in the docstring.
    ri = {v: i for i, v in enumerate(sorted(ipt))}
    rp = {v: i for i, v in enumerate(sorted(pic))}
    err = [abs(ri[r["iptm_mean"]] - rp[r["pIC50"]]) for r in rows]
    r_err, p_err = stats.spearmanr(sig, err)
    lo_e, hi_e = fisher_ci(r_err, n)
    print(f"\n[HEADLINE] Spearman(sigma_iptm, |potency-rank error|) = {r_err:+.3f} "
          f"(p={p_err:.3f}, 95% CI [{lo_e:+.3f}, {hi_e:+.3f}])")
    pil = pilot_rho()
    if pil:
        pr, pp, pn = pil
        need = n_for_power(pr)
        print(f"  15-ligand pilot (recomputed live, NOT quoted from prose): rho={pr:+.3f} (p={pp:.3f}, n={pn})")
        print(f"  power: detecting the pilot effect at 80% needs n~{need:.0f}; this cohort n={n} has "
              f"~{power_at(pr, n)*100:.0f}% power")
        print(f"  pilot estimate {pr:+.3f} is {'OUTSIDE' if pr > hi_e else 'INSIDE'} the CI -> "
              f"{'excluded' if pr > hi_e else 'NOT excluded'} by this cohort")
    print(f"  >>> honest reading: no evidence of a gating relationship; any true effect is bounded "
          f"above at rho ~ {hi_e:+.2f}. NOT 'the effect is zero'.")

    r_all, p_all = stats.spearmanr(ipt, pic)
    lo_a, hi_a = fisher_ci(r_all, n)
    print(f"\n[baseline] does iptm predict potency at all?  Spearman(iptm_mean, pIC50) = {r_all:+.3f} "
          f"(p={p_all:.3f}, 95% CI [{lo_a:+.3f}, {hi_a:+.3f}])")

    med = statistics.median(sig)
    lo = [r for r in rows if r["sigma_iptm"] <= med]
    hi = [r for r in rows if r["sigma_iptm"] > med]
    r_lo, p_lo = stats.spearmanr([x["iptm_mean"] for x in lo], [x["pIC50"] for x in lo])
    r_hi, p_hi = stats.spearmanr([x["iptm_mean"] for x in hi], [x["pIC50"] for x in hi])
    llo, lhi = fisher_ci(r_lo, len(lo))
    hlo, hhi = fisher_ci(r_hi, len(hi))
    print(f"\n[THE TEST] split at median sigma_iptm={med:.4f}")
    print(f"  LOW-sigma  (gate PASSES, n={len(lo)}):  Spearman(iptm_mean, pIC50) = {r_lo:+.3f} "
          f"(p={p_lo:.3f}, 95% CI [{llo:+.3f}, {lhi:+.3f}])")
    print(f"  HIGH-sigma (gate REJECTS, n={len(hi)}):  Spearman(iptm_mean, pIC50) = {r_hi:+.3f} "
          f"(p={p_hi:.3f}, 95% CI [{hlo:+.3f}, {hhi:+.3f}])")
    print(f"  (each half n~{len(lo)} -> intervals are wide by construction; the load-bearing statement "
          f"is the HEADLINE bound, not this comparison)")

    # Fisher z test for the DIFFERENCE between two independent correlations.
    # NOTE: the dead z() helper and a function-local `import math` used to live here. The local import
    # bound `math` as a main()-local name, so the module-level math was shadowed and any earlier use in
    # main() raised UnboundLocalError. Removed 2026-07-16; math is imported at module scope.
    zl = 0.5 * math.log((1 + max(min(r_lo, .999999), -.999999)) / (1 - max(min(r_lo, .999999), -.999999)))
    zh = 0.5 * math.log((1 + max(min(r_hi, .999999), -.999999)) / (1 - max(min(r_hi, .999999), -.999999)))
    se = math.sqrt(1 / (len(lo) - 3) + 1 / (len(hi) - 3))
    zdiff = (zl - zh) / se
    pdiff = 2 * (1 - stats.norm.cdf(abs(zdiff)))
    print(f"  difference: Fisher z = {zdiff:+.2f}, p = {pdiff:.3f}")
    verdict = ("GATE WORKS: low-sigma predictions agree with experiment significantly better"
               if (pdiff < 0.05 and r_lo > r_hi) else
               "NOT ESTABLISHED: low-sigma predictions are not measurably more trustworthy")
    print(f"  >>> {verdict}")

    r_sp, p_sp = stats.spearmanr(sig, pic)
    print(f"\n[confound check] Spearman(sigma_iptm, pIC50) = {r_sp:+.3f} (p={p_sp:.3f})")
    print("  (if strongly negative, sigma mostly tracks potency itself -- the 'gate' would just be")
    print("   re-discovering that potent binders fold consistently, not measuring reliability)")
    print(f"\nper-ligand table -> {OUT}")


if __name__ == "__main__":
    main()
