#!/usr/bin/env python
"""harness_scan.py (R15-A) — the EXPLORE arm: turn accumulated data into CANDIDATE CLAIMS.

WHY THIS EXISTS
---------------
R8-R14 built a strong advisory brain (phase8 resource VOI, R12 claim ledger, R13 portfolio/AD/LF-HF/IDS,
R14 deliverable axis). Every one of those layers optimizes *within a fixed set of claims*. The claim set
itself is a hardcoded Python literal in paper_claim_ledger.build_claims(), and its own A4 entry admits the
gap in a comment: "NEW claim, spawned by a result (the evidence->claim loop the static list lacked)".
That loop was me, by hand, in a conversation. With no human/LLM attached, this stack's rate of NEW
hypotheses is exactly zero, no matter how much compute it burns — while 12,207 labelled rows sit
unexamined for structure.

"Explore" in phase13/IDS means explore MOLECULE space (which candidate to cofold next). This module is
explore in HYPOTHESIS space: sweep the live artifacts for structure that no current claim covers, and
emit each hit as a provenance-carrying Observation that the harness ledger can triage, commit to, and
pursue to a conclusion.

HONESTY CONSTRAINTS (these are the hard part, not the statistics)
-----------------------------------------------------------------
A scanner that reports whatever is "significant" is a fabrication machine. At n=12,207 a Spearman rho of
0.03 has p<0.001, so significance carries almost no information here and an unfiltered sweep would bury
the registry in noise that LOOKS like discovery. Four guards, all mandatory:

  1. EFFECT FLOOR, not p. |rho| >= RHO_MIN=0.15 (<2.3% of variance below that) is the admission test;
     the p-value only breaks ties. The floor does the work, significance does not.
  2. FDR over the WHOLE family. Every test from every probe in one scan goes through one
     Benjamini-Hochberg pass, and n_tests is recorded on each observation so the multiplicity is visible
     downstream instead of being laundered away.
  3. DERIVED-PAIR MASK. gate_score = iptm_mean * (1 - min(sigma_iptm/0.10, 1)) * qed
     (phase2_score_sigma.py:78), so those three pairs are arithmetic identities, not findings. Masked.
     Same-sample moment couplings (sigma<->kurt, n<->sigma) are kept but FLAGGED so triage discounts them.
  4. COVERAGE + COHORT TAGGING. qed/composite_score/zbg come from combined_ranked.csv and exist for only
     1,784 of 12,207 rows (14.6%) — the seed library. A pair involving them is a LIBRARY result, never a
     panel result, and is tagged library_only. This is the memory rule about joins silently collapsing to
     an intersection ("join시 prefix 미제거=교집합0 silent"), enforced in code: below MIN_COVERAGE the
     test is not run at all.

Every observation carries file+rows+columns and a literal recompute command, because a number that only
exists in prose is not data (memory: "내 산문 속 숫자는 데이터 아님"). Statements are DESCRIPTIVE only —
the scanner never writes an interpretation or a causal reading; that is the promotion step's job, done by
the LLM against the claim ledger.

Pure CPU, read-only on all data files, writes only under tier_state/harness/. Fails LOUD (non-zero exit +
errors[] in the output) rather than emitting an empty scan that reads as "nothing found".
"""
import os, sys, json, math, time, hashlib, glob, re
import numpy as np
import pandas as pd
from scipy import stats

SD = "/home/crazat/genesis_medicine/scripts/round27_paperA"
EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
TS = os.path.join(SD, "tier_state")
HS = os.path.join(TS, "harness")
LABELS = os.path.join(EXP, "phase3_labels.csv")
OUT = os.path.join(HS, "scan_latest.json")
HIST = os.path.join(HS, "scan_history.jsonl")
LOG = os.path.join(SD, "harness_scan.log")

# ---- admission thresholds (see HONESTY CONSTRAINTS) ----
Q_THRESH = 0.01        # BH-FDR q; strict because the family is large and n is huge
RHO_MIN = 0.15         # |Spearman| effect floor: this, not p, is the real admission test
DELTA_MIN = 0.15       # min |rho_A - rho_B| for a cohort-heterogeneity observation
MIN_N = 200            # a scope below this is not tested (unstable rho, wide CI)
MIN_COVERAGE = 0.05    # a column pair whose joint non-null coverage is below this is not tested
ANOM_Z = 5.0           # robust-z beyond which a candidate counts as a sigma anomaly
ANOM_MIN_K = 20        # a single outlier is noise; a POPULATION of them is an observation

FULL_COLS = ["iptm_mean", "sigma_iptm", "kurt_iptm", "gate_score", "n_iptm",
             "sigma_E_med", "n_sigmaE_cells"]
LIB_COLS = ["qed", "composite_score"]          # present only for the 1,784-molecule seed library
NUMERIC = FULL_COLS + LIB_COLS

# gate_score is an exact arithmetic function of these (phase2_score_sigma.py:78) -> identities, not findings.
# composite_score is the phase1 "QED+ADMET+mild-novelty" composite, i.e. built ON qed
# (phase3_acquisition_select.py:7) -> also an identity, not a discovery.
DERIVED_PAIRS = {frozenset(("gate_score", "iptm_mean")),
                 frozenset(("gate_score", "sigma_iptm")),
                 frozenset(("gate_score", "qed")),
                 frozenset(("qed", "composite_score"))}

# POLICY-INDUCED pairs: how many times a candidate was sampled is DECIDED BY US, not by chemistry.
# phase3_acquisition_select ranks the cofold pool on z(composite_score) and tier_planner.replicate_priority
# orders depth by gate_score, so n_iptm / n_sigmaE_cells correlate with those scores BY CONSTRUCTION -- the
# first raw scan duly "discovered" rho(n_iptm, composite_score)=+0.786 and rho(n_iptm, qed)=+0.693, which is
# the scheduler looking at its own reflection. Masked: a harness that reports its own allocation policy as a
# finding is worse than one that reports nothing.
ALLOC_COLS = ("n_iptm", "n_sigmaE_cells")
SELECT_COLS = ("composite_score", "qed", "gate_score")
POLICY_INDUCED = {frozenset((a, b)) for a in ALLOC_COLS for b in SELECT_COLS}

# NEVER AN ENDPOINT. The masks above were not enough. The first ledger run ranked six allocation-variable
# relations at the top -- "Spearman(iptm_mean, n_iptm) is heterogeneous across 23 generation eras, I^2=0.94"
# -- which is not chemistry, it is OUR OWN POLICY changing over those 23 eras (phase14's precision gate began
# binding 2026-07-26 and the 64-sample convergence cap landed 07-27). n_iptm is assigned by
# tier_planner.replicate_priority() ordering on gate_score, and n_sigmaE_cells by the floor's score-based
# survivor screen, so BOTH are functions of the very variables they would be correlated against. A variable
# the system itself sets by policy can never be an endpoint; it can only be a CONTROL. They stay loaded and
# are used as covariates in the confound step -- they are just not allowed on either side of a finding.
NEVER_ENDPOINT = set(ALLOC_COLS)
# same-sample / same-estimator couplings: real relationships, but partly mechanical -> kept, flagged
MOMENT_COUPLED = {frozenset(("sigma_iptm", "kurt_iptm")),
                  frozenset(("n_iptm", "sigma_iptm")),
                  frozenset(("n_iptm", "kurt_iptm")),
                  frozenset(("n_sigmaE_cells", "sigma_E_med")),
                  # 2026-08-08: the mean and the sd of the SAME bounded sample. Measured in library scope,
                  # median sigma_iptm falls 0.0335 -> 0.0022 monotonically as the mean bin goes 0.860 ->
                  # 0.976: iptm lives on [0,1] and its dispersion has to compress against the ceiling.
                  # rho = -0.920 here and -0.830 in generated_auto, and it is claim P1/B2's own definition
                  # space. It reached CONCLUDED_POSITIVE once because this line was missing.
                  frozenset(("iptm_mean", "sigma_iptm"))}


def logln(m):
    with open(LOG, "a") as fh:
        fh.write(f"[{time.strftime('%F %T')}] {m}\n")


def cohort(cid):
    """generated_auto / generated_r3 / library.

    Substring match, NOT startswith: generated ids are denovo_mmp1_auto0805_2307_133, so a prefix test
    silently classifies all 10,303 generated rows as library (verified against roi_report's own
    `"auto" in cand_id` count = 10,303)."""
    if "auto" in cid:
        return "generated_auto"
    if "r3_" in cid:
        return "generated_r3"
    return "library"


def spearman_ci(x, y):
    """(rho, lo, hi, p, n) with a Bonett-Wright Fisher-z interval.

    SE_z = sqrt((1 + rho^2/2)/(n-3)) is the Spearman-specific standard error; the Pearson 1/sqrt(n-3)
    under-covers for rank correlations. A correlation without an interval is not reportable here
    (memory: 상관은 CI필수)."""
    m = np.isfinite(x) & np.isfinite(y)
    n = int(m.sum())
    if n < 10:
        return None
    rho, p = stats.spearmanr(x[m], y[m])
    if not np.isfinite(rho):
        return None
    rho = float(np.clip(rho, -0.999999, 0.999999))
    z = np.arctanh(rho)
    se = math.sqrt((1.0 + rho * rho / 2.0) / (n - 3)) if n > 3 else float("inf")
    lo, hi = math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)
    return rho, lo, hi, float(p), n


def key_of(*parts):
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def bh_fdr(pvals):
    """Benjamini-Hochberg q-values, order-preserving. One pass over the WHOLE scan family."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    if n == 0:
        return np.array([])
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(q, 0, 1)
    return out


def load_labels(errors):
    if not os.path.exists(LABELS):
        errors.append(f"MISSING {LABELS}")
        return None
    try:
        df = pd.read_csv(LABELS, low_memory=False)
    except Exception as e:
        errors.append(f"UNREADABLE {LABELS}: {e}")
        return None
    if len(df) == 0:
        errors.append(f"EMPTY {LABELS}")
        return None
    for c in NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            errors.append(f"COLUMN ABSENT {c} in phase3_labels.csv")
    df["cohort"] = df["cand_id"].astype(str).map(cohort)
    df["era"] = df["cand_id"].astype(str).map(era_of)
    return df


ERA_RE = re.compile(r"_(auto\d{4})_")


def era_of(cid):
    m = ERA_RE.search(cid)
    if m:
        return m.group(1)
    return "r3" if "r3_" in cid else "library"


# ------------------------------------------------------------------ probes
def probe_pairs(df):
    """Every admissible numeric pair, in every cohort scope. Emits raw tests (FDR applied by the caller)."""
    tests = []
    scopes = {"all": df}
    for c, g in df.groupby("cohort"):
        if len(g) >= MIN_N:
            scopes[c] = g
    for scope, g in scopes.items():
        for i, a in enumerate(NUMERIC):
            for b in NUMERIC[i + 1:]:
                pair = frozenset((a, b))
                if pair in DERIVED_PAIRS or pair in POLICY_INDUCED:
                    continue
                if a in NEVER_ENDPOINT or b in NEVER_ENDPOINT:
                    continue
                if a not in g.columns or b not in g.columns:
                    continue
                # a library-only column has no rows outside the library, so scope=all would be the SAME
                # test reported twice -- double-counted in the FDR family and duplicated in the registry.
                if (a in LIB_COLS or b in LIB_COLS) and scope != "library":
                    continue
                x, y = g[a].to_numpy(float), g[b].to_numpy(float)
                cov = float((np.isfinite(x) & np.isfinite(y)).sum()) / max(len(g), 1)
                if cov < MIN_COVERAGE:
                    continue
                r = spearman_ci(x, y)
                if r is None or r[4] < MIN_N:
                    continue
                rho, lo, hi, p, n = r
                flags = []
                if pair in MOMENT_COUPLED:
                    flags.append("moment_coupled")
                if a in LIB_COLS or b in LIB_COLS:
                    flags.append("library_only")
                tests.append(dict(
                    probe="pair", scope=scope, a=a, b=b, rho=rho, lo=lo, hi=hi, p=p, n=n,
                    coverage=round(cov, 4), flags=flags,
                    key=key_of("pair", scope, *sorted((a, b))),
                    statement=f"Spearman({a}, {b}) = {rho:+.3f} [{lo:+.3f}, {hi:+.3f}], n={n}, scope={scope}",
                    recompute=(f"python -c \"import pandas as pd,scipy.stats as s;"
                               f"d=pd.read_csv('{LABELS}');"
                               f"d=d[d.cand_id.astype(str).str.contains('auto')] if '{scope}'=='generated_auto' else d;"
                               f"print(s.spearmanr(pd.to_numeric(d['{a}'],errors='coerce'),"
                               f"pd.to_numeric(d['{b}'],errors='coerce'),nan_policy='omit'))\""),
                ))
    return tests


def probe_hetero(df, pair_tests):
    """Does an effect DIFFER between the generated and library cohorts?

    This is the probe most likely to produce a genuinely new claim rather than an incremental one: "the
    relation holds for generated molecules but not for the seed library" threatens or extends an existing
    result instead of adding volume to it. Fisher-z difference test on the two cohort rhos."""
    tests = []
    byscope = {}
    for t in pair_tests:
        byscope.setdefault((t["a"], t["b"]), {})[t["scope"]] = t
    for (a, b), d in byscope.items():
        A, B = d.get("generated_auto"), d.get("library")
        if not A or not B or A["n"] < MIN_N or B["n"] < MIN_N:
            continue
        delta = A["rho"] - B["rho"]
        if abs(delta) < DELTA_MIN:
            continue
        za, zb = np.arctanh(A["rho"]), np.arctanh(B["rho"])
        se = math.sqrt((1 + A["rho"] ** 2 / 2) / (A["n"] - 3) + (1 + B["rho"] ** 2 / 2) / (B["n"] - 3))
        zstat = (za - zb) / se
        p = 2 * (1 - stats.norm.cdf(abs(zstat)))
        dlo, dhi = math.tanh(za - zb - 1.96 * se), math.tanh(za - zb + 1.96 * se)
        flags = ["cohort_contrast"]
        if frozenset((a, b)) in MOMENT_COUPLED:
            flags.append("moment_coupled")
        if a in LIB_COLS or b in LIB_COLS:
            flags.append("library_only")
        tests.append(dict(
            probe="hetero", scope="generated_auto_vs_library", a=a, b=b,
            rho=delta, lo=dlo, hi=dhi, p=float(p), n=A["n"] + B["n"], coverage=1.0, flags=flags,
            key=key_of("hetero", *sorted((a, b))),
            statement=(f"Spearman({a}, {b}) differs by cohort: generated {A['rho']:+.3f} (n={A['n']}) vs "
                       f"library {B['rho']:+.3f} (n={B['n']}); difference {delta:+.3f} "
                       f"[{dlo:+.3f}, {dhi:+.3f}] on the Fisher-z scale"),
            recompute=(f"python -c \"import pandas as pd,scipy.stats as s;d=pd.read_csv('{LABELS}');"
                       f"g=d[d.cand_id.astype(str).str.contains('auto')];"
                       f"l=d[~d.cand_id.astype(str).str.contains('auto')];"
                       f"print(s.spearmanr(g['{a}'],g['{b}'],nan_policy='omit'),"
                       f"s.spearmanr(l['{a}'],l['{b}'],nan_policy='omit'))\""),
        ))
    return tests


def probe_drift(df, pair_tests):
    """Is an effect STABLE across generation rounds, or an artifact of one batch?

    Meta-analytic homogeneity (Cochran Q on Fisher-z per era, I^2 reported). A headline relation that is
    heterogeneous across eras is a warning about every claim resting on it — which is exactly the kind of
    thing worth waking a human for, and exactly what nothing in this stack currently looks at."""
    tests = []
    strong = {(t["a"], t["b"]) for t in pair_tests if t["scope"] == "all" and abs(t["rho"]) >= RHO_MIN}
    eras = [(e, g) for e, g in df.groupby("era") if len(g) >= MIN_N]
    if len(eras) < 3:
        return tests
    for a, b in sorted(strong):
        zs, ws, ns = [], [], []
        for e, g in eras:
            r = spearman_ci(g[a].to_numpy(float), g[b].to_numpy(float))
            if r is None or r[4] < MIN_N:
                continue
            rho, _, _, _, n = r
            zs.append(np.arctanh(rho))
            ws.append((n - 3) / (1 + rho ** 2 / 2))
            ns.append(n)
        if len(zs) < 3:
            continue
        zs, ws = np.array(zs), np.array(ws)
        zbar = float((ws * zs).sum() / ws.sum())
        Q = float((ws * (zs - zbar) ** 2).sum())
        dfree = len(zs) - 1
        p = float(1 - stats.chi2.cdf(Q, dfree))
        I2 = max(0.0, (Q - dfree) / Q) if Q > 0 else 0.0
        spread = float(np.tanh(zs.max()) - np.tanh(zs.min()))
        if I2 < 0.5 or abs(spread) < DELTA_MIN:
            continue
        tests.append(dict(
            probe="drift", scope="per_generation_era", a=a, b=b,
            rho=spread, lo=float("nan"), hi=float("nan"), p=p, n=int(sum(ns)), coverage=1.0,
            flags=["heterogeneity"], key=key_of("drift", *sorted((a, b))),
            statement=(f"Spearman({a}, {b}) is heterogeneous across {len(zs)} generation eras: "
                       f"Cochran Q={Q:.1f} (df={dfree}), I^2={I2:.2f}, rho spans "
                       f"{np.tanh(zs.min()):+.3f} to {np.tanh(zs.max()):+.3f} (pooled {np.tanh(zbar):+.3f})"),
            recompute=(f"python -c \"import pandas as pd,scipy.stats as s,re;d=pd.read_csv('{LABELS}');"
                       f"d['era']=d.cand_id.astype(str).str.extract(r'_(auto\\\\d{{4}})_')[0].fillna('lib');"
                       f"print(d.groupby('era').apply(lambda g: s.spearmanr(g['{a}'],g['{b}'],"
                       f"nan_policy='omit').statistic if len(g)>=200 else None))\""),
        ))
    return tests


def probe_anomaly(df):
    """A POPULATION of candidates whose sigma_iptm is extreme given their sample count.

    Robust z within n_iptm bins (median/MAD), so this cannot be explained by sampling depth. A single
    extreme molecule is noise and is deliberately not emitted; a cluster above the normal-theory
    expectation is a phenomenon. Binomial test against the rate expected under normality supplies the
    p-value, so this probe joins the same FDR family as everything else."""
    tests = []
    if "sigma_iptm" not in df.columns or "n_iptm" not in df.columns:
        return tests
    d = df[np.isfinite(df["sigma_iptm"]) & np.isfinite(df["n_iptm"])].copy()
    if len(d) < MIN_N:
        return tests
    d["nbin"] = pd.qcut(d["n_iptm"], q=min(5, d["n_iptm"].nunique()), duplicates="drop")
    zs = []
    for _, g in d.groupby("nbin", observed=True):
        v = g["sigma_iptm"].to_numpy(float)
        med = np.median(v)
        mad = np.median(np.abs(v - med))
        if mad <= 0:
            continue
        zs.append(pd.Series(0.6745 * (v - med) / mad, index=g.index))
    if not zs:
        return tests
    z = pd.concat(zs)
    hits = z[np.abs(z) >= ANOM_Z]
    k, n = int(len(hits)), int(len(z))
    if k < ANOM_MIN_K:
        return tests
    p_exp = 2 * (1 - stats.norm.cdf(ANOM_Z))
    p = float(stats.binomtest(k, n, p_exp, alternative="greater").pvalue)
    lo, hi = stats.beta.ppf([0.025, 0.975], k + 0.5, n - k + 0.5)
    top = d.loc[hits.abs().sort_values(ascending=False).index[:10], "cand_id"].tolist()
    tests.append(dict(
        probe="anomaly", scope="all", a="sigma_iptm", b="n_iptm",
        rho=k / n, lo=float(lo), hi=float(hi), p=p, n=n, coverage=1.0,
        flags=["prevalence"], key=key_of("anomaly", "sigma_iptm_given_n"),
        statement=(f"{k}/{n} candidates ({k/n*100:.2f}% [{lo*100:.2f}, {hi*100:.2f}]) have |robust z| >= "
                   f"{ANOM_Z} for sigma_iptm within their n_iptm stratum, vs {p_exp*100:.4f}% expected "
                   f"under normality; examples {', '.join(top[:5])}"),
        extra={"top_ids": top, "k": k},
        recompute=("see harness/harness_scan.py:probe_anomaly (MAD z within n_iptm quintiles on "
                   f"{LABELS})"),
    ))
    return tests


CELL_RE = re.compile(
    r"phase2_denovo_sigmaE_(opt|ohess)_(?:(gbsa|alpb)_)?gfn(\d)_([a-z0-9]+?)(?:_(gbsa|alpb))?\.shard0\.csv$")


def probe_hole(df):
    """Systematic holes in the sigma_E design matrix — a deterministic coverage fact, not a test.

    Emitted with no p-value (and excluded from the FDR family) because there is no multiplicity here:
    either the twin cell exists on disk or it does not. Cheap, bounded, and it turns the floor's grind
    into an addressable finite list instead of an open-ended matrix."""
    seen = {}
    for f in glob.glob(os.path.join(EXP, "phase2_denovo_sigmaE_*.shard0.csv")):
        m = CELL_RE.match(os.path.basename(f))
        if not m:
            continue
        mode, pre, gfn, solv, post = m.groups()
        seen.setdefault((mode, gfn, solv), set()).add(pre or post or "gbsa")
    gbsa = [k for k, v in seen.items() if "gbsa" in v]
    missing = [k for k in gbsa if "alpb" not in seen[k]]
    if not missing or not gbsa:
        return []
    frac = len(missing) / len(gbsa)
    return [dict(
        probe="hole", scope="sigmaE_matrix", a="alpb_twin", b="gbsa_cell",
        rho=frac, lo=float("nan"), hi=float("nan"), p=float("nan"), n=len(gbsa), coverage=1.0,
        flags=["deterministic", "no_multiplicity"], key=key_of("hole", "alpb_twin"),
        statement=(f"{len(missing)} of {len(gbsa)} GBSA sigma_E cells ({frac*100:.1f}%) still have no ALPB "
                   f"twin: {', '.join('/'.join(k) for k in sorted(missing)[:6])}"
                   f"{' ...' if len(missing) > 6 else ''}"),
        extra={"missing_cells": ["/".join(k) for k in sorted(missing)]},
        recompute=f"ls {EXP}/phase2_denovo_sigmaE_*.shard0.csv | see harness_scan.probe_hole",
    )]


def main():
    errors = []
    t0 = time.time()
    df = load_labels(errors)
    if df is None:
        json.dump({"ts": time.time(), "ok": False, "errors": errors, "observations": []},
                  open(OUT, "w"), indent=2)
        logln("SCAN FAILED: " + "; ".join(errors))
        print("SCAN FAILED: " + "; ".join(errors), file=sys.stderr)
        return 2

    pair_tests = probe_pairs(df)
    tests = pair_tests + probe_hetero(df, pair_tests) + probe_drift(df, pair_tests) + probe_anomaly(df)
    deterministic = probe_hole(df)

    # ONE BH pass over the whole family; n_tests travels with every observation so the multiplicity
    # cannot be laundered out downstream.
    qs = bh_fdr([t["p"] for t in tests]) if tests else []
    for t, q in zip(tests, qs):
        t["q"] = float(q)
    for t in deterministic:
        t["q"] = None

    obs = []
    for t in tests:
        passes = (t["q"] is not None and t["q"] < Q_THRESH and abs(t["rho"]) >= RHO_MIN)
        if t["probe"] == "anomaly":
            passes = t["q"] < Q_THRESH        # prevalence, not a correlation -> effect floor N/A
        if passes:
            obs.append(t)
    obs += deterministic
    obs.sort(key=lambda t: (-abs(t["rho"]),))

    out = {"ts": time.time(), "ok": True, "errors": errors,
           "n_rows": int(len(df)), "n_tests": len(tests), "q_thresh": Q_THRESH, "rho_min": RHO_MIN,
           "elapsed_s": round(time.time() - t0, 1),
           "cohorts": {k: int(v) for k, v in df["cohort"].value_counts().items()},
           "observations": obs}
    json.dump(out, open(OUT, "w"), indent=2, default=str)
    with open(HIST, "a") as fh:
        fh.write(json.dumps({"ts": out["ts"], "n_tests": len(tests), "n_obs": len(obs),
                             "keys": {t["key"]: round(float(t["rho"]), 4) for t in obs}}) + "\n")
    logln(f"scan ok: {len(df)} rows, {len(tests)} tests, {len(obs)} observations pass "
          f"(q<{Q_THRESH}, |rho|>={RHO_MIN}), {out['elapsed_s']}s"
          + (f"; errors: {'; '.join(errors)}" if errors else ""))
    print(f"{len(obs)} observations from {len(tests)} tests over {len(df)} rows "
          f"({out['elapsed_s']}s)")
    for t in obs[:12]:
        qtxt = "n/a" if t["q"] is None else format(t["q"], ".2e")
        print(f"  [{t['probe']:8s}] q={qtxt:>9s}  {t['statement'][:112]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
