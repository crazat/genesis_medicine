#!/usr/bin/env python
"""harness_ledger.py (R15-B) — the ARBITER and the GREED mechanism.

Three jobs, in one process so they cannot drift out of sync:

  1. REGISTRY   ingest scan observations, deduplicate by stable key, track each one's effect ACROSS scans
                (an effect that flips sign between scans is not a finding, it is noise, and only a
                registry that remembers can tell the difference).
  2. ARBITER    put opportunity value and claim value on ONE scale so explore-vs-exploit is a comparison
                and not a vibe. An opportunity's OV is computed in the same units as the R12 claim
                ledger's MV (impact x headroom x P x multipliers), read straight from
                paper_claim_ledger_state.json, and the explore share is clamped into [0.10, 0.40].
  3. PURSUIT    the greed half. One opportunity at a time may be COMMITTED, and a committed pursuit holds
                a lock that routine rotation cannot preempt. It runs an ordered plan of confirmation
                steps to a CONCLUSION -- positive, bounded, or refuted -- and only then releases.

WHY A LOCK AND A PLAN (the "끝까지 분석해내는" requirement)
--------------------------------------------------------
Every existing decision layer re-decides from scratch on a timer: tier_planner every 600s, the ledger loop
every 1500s. Nothing in the stack can hold a thread of inquiry across ticks, so a promising signal found
at 03:00 is simply gone at 03:10. A pursuit is the missing object: it has an identity, a budget, a plan, a
spend counter, and a stopping rule, and it survives every tick until one of its four stopping rules fires.

WHY THE STOPPING RULES ARE NOT ARBITRARY (the other half of the sweet spot)
--------------------------------------------------------------------------
Unbounded greed is the failure that produced 685 of 733 tiers on a settled claim. A pursuit ends when:
  PRECISION  the CI half-width reaches the target -> the question is ANSWERED, positive or negative alike.
  FUTILITY   P(real) collapses below 0.10 -> stop, and record the BOUND (memory: 음성결과는 bound로).
  BUDGET     spend exceeds the core-hour cap -> stop, record what precision the budget bought.
  VOC        expected remaining gain per core-hour < the same VOC_FLOOR the claim ledger uses.
A REFUTED or BOUNDED conclusion is a real output, written up with its interval, never "found nothing".

CONFIRMATION PLAN = THIS PROJECT'S OWN EVIDENCE STANDARD, ENCODED
-----------------------------------------------------------------
The steps are not generic statistics; they are the exact checks the 2026-07-17/18 discrimination result
had to pass before it was believed: held-out split replication, a permutation null, a partial correlation
against the size/allocation confound, and leave-one-era-out stability. An effect that clears all four is
worth a claim slot; one that does not is worth a recorded bound. Encoding the standard in code is what
stops the harness from lowering it at 04:00 when nobody is watching.

ACTUATION SCOPE (deliberately narrow, follows the R11 precedent the user approved 2026-06-13):
raise the ceiling, never move the floor. This module writes recommendation + registry + pursuit files
under tier_state/harness/, runs its own analysis on the EXPLORE cores, and sets PROMOTION_PENDING to wake
the LLM when a pursuit concludes positive. It never kills a process, never queues GPU work, never touches
the exploit floor, and never edits an existing CSV. tier_state/harness/HARNESS_OFF disables all of it.
"""
import os, sys, json, math, time, glob, random, subprocess
import numpy as np
import pandas as pd
from scipy import stats

SD = "/home/crazat/genesis_medicine/scripts/round27_paperA"
EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
TS = os.path.join(SD, "tier_state")
HS = os.path.join(TS, "harness")
LABELS = os.path.join(EXP, "phase3_labels.csv")
SCAN = os.path.join(HS, "scan_latest.json")
REG = os.path.join(HS, "registry.json")
REGLOG = os.path.join(HS, "registry.jsonl")
PURSUIT = os.path.join(HS, "PURSUIT.active")
ALLOC = os.path.join(HS, "allocation.json")
STATE = os.path.join(HS, "harness_state.json")
PROMO = os.path.join(HS, "PROMOTION_PENDING")
OFF = os.path.join(HS, "HARNESS_OFF")
FINDINGS = os.path.join(HS, "findings")
CLAIM_STATE = os.path.join(SD, "paper_claim_ledger_state.json")
LOG = os.path.join(SD, "harness_ledger.log")

# ---- value constants. VOC_FLOOR is deliberately the SAME number paper_claim_ledger.py uses: one scale. ----
VOC_FLOOR = 0.12
COMMIT_FLOOR = VOC_FLOOR
EXPLORE_MIN = 0.10      # never zero: the 93%-of-tiers-on-a-settled-claim collapse is what a zero floor buys
EXPLORE_MAX = 0.40      # never a takeover: exploitation keeps the majority share by construction
MAX_COMMITTED = 1
BUDGET_CAP_S = 4 * 3600     # core-seconds per pursuit
PRECISION_TARGET = 0.05     # CI half-width on rho at which a question counts as answered
FUTILITY_P = 0.10
MAX_STEP_FAILS = 3
RHO_MIN = 0.15              # same admission floor the scanner uses
SEED = 8107                 # the project's standing seed (used by the discrimination runs)

IMPACT_PRIOR = {"hetero": 3.0, "drift": 3.0, "anomaly": 2.0, "pair": 2.0, "hole": 1.0}
HEADROOM_PRIOR = 0.30       # generic P(accept) headroom a new supported claim adds; a PRIOR, not a measurement

# Territory already claimed by the R12 ledger. A rediscovery of a claimed relation is not an opportunity;
# an ADJACENT one (same variables, different cohort) is a partial one. Value = novelty multiplier.
COVERED = [
    (frozenset(("iptm_mean", "sigma_iptm")), "P1/B2 (the gate's own definition space)", 0.30),
    (frozenset(("sigma_iptm", "sigma_E_med")), "A4 (sigma_E vs sigma_iptm, REAL panel; de novo is adjacent)", 0.55),
    (frozenset(("n_iptm", "sigma_iptm")), "B2/phase14 (precision vs sample count)", 0.25),
    (frozenset(("n_iptm", "kurt_iptm")), "B2/phase14 (precision vs sample count)", 0.25),
    (frozenset(("sigma_iptm", "kurt_iptm")), "B2/phase14 (heavy tails drive sigma)", 0.35),
    (frozenset(("alpb_twin", "gbsa_cell")), "A2 (GBSA/ALPB twin matrix)", 0.40),
]


def logln(m):
    with open(LOG, "a") as fh:
        fh.write(f"[{time.strftime('%F %T')}] {m}\n")


def jload(p, d=None):
    try:
        return json.load(open(p))
    except Exception:
        return d


def jdump(o, p):
    tmp = p + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(o, fh, indent=2, default=str)
    os.replace(tmp, p)          # atomic: a crash mid-write must never leave a half-parsed registry


def novelty_of(obs):
    pair = frozenset((obs.get("a", ""), obs.get("b", "")))
    for k, why, mult in COVERED:
        if k == pair:
            return mult, why
    return 1.0, ""


def stability_of(hist):
    """1.0 = same sign and comparable magnitude every scan; 0 = it flips.

    Two observations are not enough to judge, so an unseen key gets a 0.7 prior rather than a free 1.0."""
    vals = [h for h in hist if h is not None and np.isfinite(h)]
    if len(vals) < 3:
        return 0.7
    signs = np.sign(vals)
    flip = float((signs != signs[0]).mean())
    spread = float(np.std(vals) / (abs(np.mean(vals)) + 1e-9))
    return max(0.0, min(1.0, (1.0 - flip) * math.exp(-spread)))


def p_real(obs, stability):
    """A PRIOR model of P(this effect is real and survives the confirmation plan). Not calibrated.

    Written as an explicit product so every discount is visible and arguable, rather than a single tuned
    number. q enters coarsely on purpose: at n=12,207 the p-value is nearly uninformative, so the effect
    size and the cross-scan stability carry the weight."""
    q = obs.get("q")
    w_q = 1.0 if q is None else (1.0 if q < 1e-6 else 0.8 if q < 1e-3 else 0.6)
    w_eff = float(np.clip(abs(obs.get("rho", 0.0)) / 0.35, 0.3, 1.0))
    w_mech = 1.0
    flags = obs.get("flags", [])
    if "moment_coupled" in flags:
        w_mech *= 0.5      # partly mechanical: the two statistics share a sample
    if "library_only" in flags:
        w_mech *= 0.6      # 1,784 rows and a different population from the 12,207-row panel
    if "deterministic" in flags:
        w_mech = 1.0       # a disk-coverage fact has no sampling uncertainty to discount
    return float(np.clip(w_q * w_eff * stability * w_mech, 0.0, 1.0))


def opportunity_value(obs, stability):
    nov, why = novelty_of(obs)
    pr = p_real(obs, stability)
    ov = IMPACT_PRIOR.get(obs["probe"], 1.0) * HEADROOM_PRIOR * pr * nov
    return round(ov, 4), pr, nov, why


# --------------------------------------------------------------------- registry
def ingest(reg, scan):
    """Fold a scan into the registry. Idempotent per SCAN, not per call.

    The cross-scan history is the only thing that separates a stable effect from a lucky one, so it must
    count DISTINCT scans. The first version appended on every invocation, and running the ledger five
    times against one scan drove a key's history to ['0.312','0.312','0.312','0.312'] and its stability
    from the 0.7 prior to a fully-earned 1.0 -- confidence manufactured by looping, with no new data. A
    scan whose timestamp is already recorded updates the current numbers but does not extend history."""
    now = time.time()
    scan_ts = scan.get("ts")
    fresh = scan_ts != reg.get("last_scan_ts")
    reg["last_scan_ts"] = scan_ts
    seen_now = set()
    for o in scan.get("observations", []):
        k = o["key"]
        seen_now.add(k)
        e = reg["items"].get(k)
        if e is None:
            e = {"key": k, "probe": o["probe"], "scope": o["scope"], "a": o.get("a"), "b": o.get("b"),
                 "statement": o["statement"], "flags": o.get("flags", []),
                 "provenance": {"file": LABELS, "n": o.get("n"), "coverage": o.get("coverage"),
                                "recompute": o.get("recompute")},
                 "extra": o.get("extra", {}),
                 "first_ts": now, "state": "DETECTED", "history": [], "spend_s": 0.0,
                 "steps": [], "fails": 0}
            reg["items"][k] = e
        e["last_ts"] = now
        e["statement"] = o["statement"]          # keep the freshest numbers
        e["rho"], e["ci"], e["q"], e["n"] = o.get("rho"), [o.get("lo"), o.get("hi")], o.get("q"), o.get("n")
        if fresh:
            e["history"] = (e["history"] + [o.get("rho")])[-12:]
        e["seen_count"] = len(e["history"])
        e["stability"] = round(stability_of(e["history"]), 3)
        ov, pr, nov, why = opportunity_value(o, e["stability"])
        e["OV"], e["p_real"], e["novelty"], e["covered_by"] = ov, round(pr, 3), nov, why
        if e["state"] == "DETECTED":
            e["state"] = "TRIAGED"
    for k, e in reg["items"].items():
        if fresh and k not in seen_now and e["state"] in ("DETECTED", "TRIAGED"):
            e["missed"] = e.get("missed", 0) + 1
            if e["missed"] >= 3:
                e["state"] = "ARCHIVED"
                e["archive_reason"] = "not reproduced in 3 consecutive scans"
    return reg


# --------------------------------------------------------------------- pursuit plans
def load_df():
    df = pd.read_csv(LABELS, low_memory=False)
    for c in df.columns:
        if c not in ("cand_id", "smiles", "zbg"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    cid = df["cand_id"].astype(str)
    df["cohort"] = np.where(cid.str.contains("auto"), "generated_auto",
                            np.where(cid.str.contains("r3_"), "generated_r3", "library"))
    df["era"] = cid.str.extract(r"_(auto\d{4})_")[0].fillna("library")
    return df


def scope_rows(df, scope):
    if scope in ("all", "sigmaE_matrix", "per_generation_era", "generated_auto_vs_library"):
        return df
    return df[df["cohort"] == scope]


def _rho_ci(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    n = int(m.sum())
    if n < 20:
        return None
    rho, p = stats.spearmanr(x[m], y[m])
    rho = float(np.clip(rho, -0.999999, 0.999999))
    se = math.sqrt((1 + rho ** 2 / 2) / (n - 3))
    z = np.arctanh(rho)
    return dict(rho=rho, lo=float(np.tanh(z - 1.96 * se)), hi=float(np.tanh(z + 1.96 * se)),
                p=float(p), n=n, half=float((np.tanh(z + 1.96 * se) - np.tanh(z - 1.96 * se)) / 2))


# ---- THE STATISTIC UNDER TEST -------------------------------------------------------------------
# The first version of this file used one generic plan (split-half / permutation / partial / jackknife)
# written against the two VARIABLES rather than against the STATISTIC, and it produced a wrong verdict on
# its very first pursuit: for a DRIFT observation ("the relation is heterogeneous across 23 eras"), the
# leave-one-era-out step returned PASS meaning "stable", which is evidence AGAINST that observation, and the
# generic logic counted it as support. The same run printed "retains 115% of the raw |rho|" because it
# compared a partial correlation against a heterogeneity SPAN -- different units entirely.
# A confirmation step is only meaningful relative to the quantity being confirmed. So each probe declares
# its own statistic and its own null-defining label, and the steps below are written in terms of those.
def _rho(d, a, b):
    x, y = d[a].to_numpy(float), d[b].to_numpy(float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 20:
        return float("nan")
    return float(stats.spearmanr(x[m], y[m]).statistic)


MIN_ERA_N = 200        # same threshold the scanner's drift probe uses; shared so the two cannot disagree


def _i2(d, a, b):
    """Meta-analytic I^2 of the per-era rho: 0 = one common effect, 1 = fully era-dependent."""
    zs, ws = [], []
    for _, g in d.groupby("era"):
        if len(g) < MIN_ERA_N:
            continue
        r = _rho(g, a, b)
        if not np.isfinite(r):
            continue
        r = float(np.clip(r, -0.999, 0.999))
        zs.append(np.arctanh(r))
        ws.append((len(g) - 3) / (1 + r ** 2 / 2))
    if len(zs) < 3:
        return float("nan")
    zs, ws = np.array(zs), np.array(ws)
    zbar = (ws * zs).sum() / ws.sum()
    Q = float((ws * (zs - zbar) ** 2).sum())
    dfree = len(zs) - 1
    return max(0.0, (Q - dfree) / Q) if Q > 0 else 0.0


def _cohort_delta(d, a, b):
    g = d[d["cohort"] == "generated_auto"]
    l = d[d["cohort"] == "library"]
    if len(g) < MIN_ERA_N or len(l) < MIN_ERA_N:
        return float("nan")
    return _rho(g, a, b) - _rho(l, a, b)


STAT = {
    "pair": lambda d, e: _rho(d, e["a"], e["b"]),
    "hetero": lambda d, e: _cohort_delta(d, e["a"], e["b"]),
    "drift": lambda d, e: _i2(d, e["a"], e["b"]),
}
# what a permutation must destroy to build this statistic's null:
PERM_LABEL = {"pair": None, "hetero": "cohort", "drift": "era"}
# a statistic is "still there" if it keeps its sign and at least half its magnitude; for I^2 (which is
# already a 0..1 proportion and has no sign) the floor is absolute.
FLOOR = {"pair": RHO_MIN, "hetero": 0.15, "drift": 0.50}
NPERM = {"pair": 2000, "hetero": 1000, "drift": 400}


def _survives(probe, val, full):
    if not np.isfinite(val):
        return False
    if probe == "drift":
        return val >= FLOOR["drift"]
    return (np.sign(val) == np.sign(full)) and abs(val) >= max(FLOOR[probe], 0.5 * abs(full))


def step_holdout(e, df):
    """Does the SAME statistic reproduce on a seeded held-out half of the same population?"""
    d = scope_rows(df, e["scope"])
    probe = e["probe"]
    full = STAT[probe](d, e)
    idx = np.arange(len(d))
    np.random.default_rng(SEED).shuffle(idx)
    h = len(idx) // 2
    a_val = STAT[probe](d.iloc[idx[:h]], e)
    b_val = STAT[probe](d.iloc[idx[h:]], e)
    if not (np.isfinite(a_val) and np.isfinite(b_val)):
        return {"ok": False, "verdict": "INSUFFICIENT", "detail": "a half was too small for the statistic"}
    ok = _survives(probe, a_val, full) and _survives(probe, b_val, full)
    return {"ok": True, "verdict": "PASS" if ok else "FAIL",
            "detail": (f"{probe} statistic: full {full:+.3f}; held-out halves {a_val:+.3f} and {b_val:+.3f} "
                       f"(n={h}/{len(idx)-h}, seed {SEED})"),
            "stat": {"full": full, "half_a": a_val, "half_b": b_val}}


def step_permutation(e, df):
    """Empirical null for THIS statistic: destroy the structure it claims and see how often chance beats it.

    pair shuffles the second variable; hetero shuffles the cohort label; drift shuffles the era label. The
    era/cohort shuffles matter more than the textbook version: Cochran Q's chi-square approximation is
    unreliable with 23 unequal-n strata, so the permuted null is the honest reference, not the tabulated one."""
    d = scope_rows(df, e["scope"]).copy()
    probe = e["probe"]
    lab = PERM_LABEL[probe]
    full = STAT[probe](d, e)
    if not np.isfinite(full):
        return {"ok": False, "verdict": "INSUFFICIENT", "detail": "statistic undefined on this scope"}
    rng = np.random.default_rng(SEED)
    n = NPERM[probe]
    cnt = 0
    if lab is None:
        x, y = d[e["a"]].to_numpy(float), d[e["b"]].to_numpy(float)
        m = np.isfinite(x) & np.isfinite(y)
        rx, ry = stats.rankdata(x[m]), stats.rankdata(y[m])
        obs = abs(np.corrcoef(rx, ry)[0, 1])
        for _ in range(n):
            if abs(np.corrcoef(rx, rng.permutation(ry))[0, 1]) >= obs:
                cnt += 1
    else:
        obs = abs(full)
        vals = d[lab].to_numpy()
        for _ in range(n):
            d[lab] = rng.permutation(vals)
            v = STAT[probe](d, e)
            if np.isfinite(v) and abs(v) >= obs:
                cnt += 1
    pemp = (cnt + 1) / (n + 1)
    return {"ok": True, "verdict": "PASS" if pemp < 0.01 else "FAIL",
            "detail": (f"observed |{probe} statistic|={obs:.3f}; permutation p={pemp:.4f} over {n} shuffles of "
                       f"{lab or e['b']} (seed {SEED})"),
            "stat": {"p_emp": pemp, "observed": float(obs), "nperm": n, "shuffled": lab or e["b"]}}


def step_confound(e, df):
    """Recompute the statistic after residualizing BOTH variables on the allocation covariates.

    n_iptm and n_sigmaE_cells are set by our own acquisition and floor policies, so any effect could be an
    image of how compute was spent. This is the same size/allocation control the 2026-07-17 discrimination
    result had to pass before it was believed. Residualizing on ranks keeps the statistic non-parametric."""
    d = scope_rows(df, e["scope"]).copy()
    probe = e["probe"]
    ctrl = [c for c in ("n_iptm", "n_sigmaE_cells") if c in d.columns and c not in (e["a"], e["b"])]
    if not ctrl:
        return {"ok": True, "verdict": "N/A", "detail": "no allocation covariate outside the pair"}
    cols = [e["a"], e["b"]] + ctrl
    keep = d[cols].apply(pd.to_numeric, errors="coerce").dropna().index
    if len(keep) < 100:
        return {"ok": False, "verdict": "INSUFFICIENT", "detail": f"n={len(keep)} after dropping nulls"}
    g = d.loc[keep].copy()
    R = g[cols].rank().to_numpy(float)
    C = np.column_stack([np.ones(len(R)), R[:, 2:]])
    for j, name in ((0, e["a"]), (1, e["b"])):
        beta, *_ = np.linalg.lstsq(C, R[:, j], rcond=None)
        g[name] = R[:, j] - C @ beta
    full = STAT[probe](d, e)
    val = STAT[probe](g, e)
    ok = _survives(probe, val, full)
    ret = (abs(val) / (abs(full) + 1e-9)) * 100
    return {"ok": True, "verdict": "PASS" if ok else "FAIL",
            "detail": (f"{probe} statistic {full:+.3f} -> {val:+.3f} after residualizing {e['a']} and "
                       f"{e['b']} on {'+'.join(ctrl)} (retains {ret:.0f}%, n={len(keep)})"),
            "stat": {"full": full, "adjusted": val, "controls": ctrl, "retained_pct": ret}}


def step_era_jackknife(e, df):
    """Is the effect carried by a single generation round? (correlation probes only.)

    Deliberately NOT part of the drift plan: leave-one-out on a pooled estimate is not a test of
    heterogeneity, and reading its "stable" verdict as support for a drift claim is the exact inversion
    this rewrite fixes."""
    d = scope_rows(df, e["scope"])
    vals = []
    for x, g in d.groupby("era"):
        if len(g) < MIN_ERA_N:
            continue
        r = _rho(d[d["era"] != x], e["a"], e["b"])
        if np.isfinite(r):
            vals.append((x, r))
    if len(vals) < 3:
        return {"ok": True, "verdict": "N/A", "detail": f"only {len(vals)} eras with n>={MIN_ERA_N}"}
    rs = [v for _, v in vals]
    same = len({np.sign(v) for v in rs}) == 1
    lo_e, hi_e = min(vals, key=lambda t: t[1]), max(vals, key=lambda t: t[1])
    return {"ok": True, "verdict": "PASS" if (same and (max(rs) - min(rs)) < 0.20) else "FAIL",
            "detail": (f"leave-one-era-out rho spans {min(rs):+.3f} (drop {lo_e[0]}) to {max(rs):+.3f} "
                       f"(drop {hi_e[0]}) over {len(vals)} eras"),
            "stat": {"min": float(min(rs)), "max": float(max(rs)), "n_eras": len(vals)}}


def step_batch_confound(e, df):
    """anomaly probe: are the extreme candidates concentrated in one era (a batch artifact)?"""
    d = df[np.isfinite(df["sigma_iptm"]) & np.isfinite(df["n_iptm"])].copy()
    ids = set(e.get("extra", {}).get("top_ids", []))
    if not ids:
        return {"ok": False, "verdict": "INSUFFICIENT", "detail": "no ids recorded"}
    d["hit"] = d["cand_id"].astype(str).isin(ids)
    tab = pd.crosstab(d["era"], d["hit"])
    if tab.shape[1] < 2 or tab.values.min() < 0:
        return {"ok": True, "verdict": "N/A", "detail": "degenerate table"}
    chi2, p, dof, _ = stats.chi2_contingency(tab)
    return {"ok": True, "verdict": "PASS" if p >= 0.01 else "FAIL",
            "detail": f"anomaly-by-era chi2={chi2:.1f} (df={dof}) p={p:.3g}; "
                      f"{'spread across eras' if p >= 0.01 else 'concentrated in specific eras = batch artifact'}",
            "stat": {"chi2": float(chi2), "p": float(p), "dof": int(dof)}}


def step_quantify_hole(e, df):
    """hole probe: turn a coverage gap into a costed, finite work order."""
    cells = e.get("extra", {}).get("missing_cells", [])
    if not cells:
        return {"ok": False, "verdict": "INSUFFICIENT", "detail": "no missing cells recorded"}
    n_cand = int(df["cand_id"].nunique())
    return {"ok": True, "verdict": "ACTIONABLE",
            "detail": (f"{len(cells)} ALPB twin cells missing over ~{n_cand} candidates; "
                       f"cells: {', '.join(cells[:10])}{' ...' if len(cells) > 10 else ''}"),
            "stat": {"n_cells": len(cells), "cells": cells}}


PLANS = {
    "pair": ["holdout", "permutation", "confound", "era_jackknife"],
    "hetero": ["holdout", "permutation", "confound"],
    "drift": ["holdout", "permutation", "confound"],
    "anomaly": ["batch_confound"],
    "hole": ["quantify_hole"],
}
STEPS = {"holdout": step_holdout, "permutation": step_permutation, "confound": step_confound,
         "era_jackknife": step_era_jackknife, "batch_confound": step_batch_confound,
         "quantify_hole": step_quantify_hole}


# --------------------------------------------------------------------- conclusion
def conclude(e, reg):
    """Turn a finished plan into one of four states. A negative outcome is an OUTPUT, not a non-result:
    it is recorded as a numeric bound, per the standing rule that negative findings are reported as bounds
    rather than as "nothing found"."""
    steps = {s["name"]: s for s in e["steps"]}
    verdicts = [s["verdict"] for s in e["steps"]]
    fails = [s for s in e["steps"] if s["verdict"] == "FAIL"]
    perm, conf = steps.get("permutation"), steps.get("confound")
    if "ACTIONABLE" in verdicts:
        state, why = "CONCLUDED_ACTIONABLE", "coverage gap quantified into a finite work order"
    elif perm and perm["verdict"] == "FAIL":
        # the permuted null is not excluded -> there is nothing here to bound beyond chance
        state = "CONCLUDED_REFUTED"
        why = (f"the permuted null is not excluded (empirical p={perm['stat']['p_emp']:.4f} over "
               f"{perm['stat']['nperm']} shuffles of {perm['stat']['shuffled']}); the observation is "
               f"consistent with chance structure")
    elif fails:
        adj = (conf or {}).get("stat", {})
        if conf and conf["verdict"] == "FAIL" and "adjusted" in adj:
            state = "CONCLUDED_BOUND"
            why = (f"survives the permuted null but not the allocation control: the statistic falls from "
                   f"{adj['full']:+.3f} to {adj['adjusted']:+.3f} once {'+'.join(adj['controls'])} are "
                   f"residualized out, so the effect attributable to chemistry rather than to sampling "
                   f"policy is bounded at |{adj['adjusted']:+.3f}|")
        else:
            state = "CONCLUDED_BOUND"
            why = ("failed " + ", ".join(s["name"] for s in fails) +
                   f" of {len(e['steps'])} steps; the effect is not reproducible at the standard this "
                   f"project applies to its own published results")
    elif any(v == "PASS" for v in verdicts):
        state = "CONCLUDED_POSITIVE"
        why = (f"passed all {sum(1 for v in verdicts if v == 'PASS')} applicable confirmation steps "
               f"({', '.join(s['name'] for s in e['steps'] if s['verdict'] == 'PASS')})")
    else:
        state, why = "CONCLUDED_BOUND", "no step returned a usable verdict"
    e["state"] = state
    e["conclusion"] = why
    e["concluded_ts"] = time.time()
    path = write_finding(e)
    e["finding"] = path
    if state == "CONCLUDED_POSITIVE":
        with open(PROMO, "w") as fh:
            fh.write(f"{time.time()} {e['key']} {path}\n{e['statement']}\n")
    logln(f"PURSUIT CONCLUDED {e['key']} -> {state}: {why}")
    return e


def write_finding(e):
    os.makedirs(FINDINGS, exist_ok=True)
    path = os.path.join(FINDINGS, f"finding_{e['key']}.md")
    L = [f"# Harness finding {e['key']}",
         "",
         f"State: {e['state']}",
         f"Concluded: {time.strftime('%F %T')}",
         f"Probe: {e['probe']}   Scope: {e['scope']}   Variables: {e.get('a')} x {e.get('b')}",
         f"Opportunity value at commit: OV={e.get('OV')} (P_real {e.get('p_real')}, novelty {e.get('novelty')}"
         + (f", overlaps {e['covered_by']}" if e.get("covered_by") else "") + ")",
         "",
         "## Observation",
         "",
         e["statement"],
         "",
         f"Flags: {', '.join(e.get('flags') or []) or 'none'}",
         f"Cross-scan stability: {e.get('stability')} over {e.get('seen_count')} scans; "
         f"effect history {['%.3f' % h for h in e.get('history', []) if h is not None]}",
         "",
         "## Confirmation plan",
         ""]
    for s in e["steps"]:
        L.append(f"- {s['name']}: {s['verdict']} -- {s['detail']}")
    L += ["",
          "## Conclusion",
          "",
          e.get("conclusion", ""),
          "",
          "## Provenance",
          "",
          f"Source file: {e['provenance']['file']} (n={e['provenance'].get('n')}, "
          f"coverage={e['provenance'].get('coverage')})",
          f"Spend: {e.get('spend_s', 0)/60:.1f} core-minutes",
          "",
          "Recompute:",
          "",
          "```",
          str(e["provenance"].get("recompute", "")),
          "```",
          "",
          "This note was produced mechanically by harness_ledger.py. Every number above is recomputed live "
          "from the source file named here; none of it is transcribed from prose. It is a candidate for "
          "promotion into paper_claim_ledger.py, not a claim: promotion is an LLM/author decision.",
          ""]
    with open(path, "w") as fh:
        fh.write("\n".join(L))
    return path


# --------------------------------------------------------------------- main
def main():
    os.makedirs(HS, exist_ok=True)
    if os.path.exists(OFF):
        print("HARNESS_OFF present -> no action")
        return 0
    scan = jload(SCAN)
    if not scan or not scan.get("ok"):
        logln("no usable scan_latest.json -> ledger idle (scanner must run first)")
        print("no usable scan; run harness_scan.py first")
        return 1
    reg = jload(REG, {"items": {}}) or {"items": {}}
    reg = ingest(reg, scan)

    # ---------- ARBITER: one value scale for explore and exploit ----------
    claim = jload(CLAIM_STATE, {}) or {}
    v_exploit = float(claim.get("best_compute_mv", 0.0) or 0.0)
    open_items = [e for e in reg["items"].values() if e["state"] in ("TRIAGED", "COMMITTED")]
    v_explore = max([e["OV"] for e in open_items], default=0.0)
    denom = v_explore + v_exploit
    raw_share = (v_explore / denom) if denom > 0 else EXPLORE_MIN
    share = float(min(EXPLORE_MAX, max(EXPLORE_MIN, raw_share)))
    jdump({"ts": time.time(), "v_explore": v_explore, "v_exploit": v_exploit,
           "explore_share_raw": round(raw_share, 3), "explore_share": round(share, 3),
           "clamp": [EXPLORE_MIN, EXPLORE_MAX],
           "note": ("explore share is CLAMPED on both sides on purpose: the floor is insurance against the "
                    "2026-07-15 collapse (93% of tiers on a settled claim), the ceiling guarantees the "
                    "exploit floor keeps the majority of the machine.")}, ALLOC)

    # ---------- GREED: commit at most one pursuit, and finish what is committed ----------
    committed = [e for e in reg["items"].values() if e["state"] == "COMMITTED"]
    if not committed:
        # deterministic ordering: OV first, then effect size, then n, then key. On the first scan every
        # OV is tied (stability is a flat 0.7 prior until three scans accumulate), so without the
        # tie-breaks the choice of what to spend four core-hours on would fall out of dict insertion order.
        cands = sorted([e for e in reg["items"].values() if e["state"] == "TRIAGED"],
                       key=lambda e: (-e["OV"], -abs(e.get("rho") or 0.0), -(e.get("n") or 0), e["key"]))
        if cands and cands[0]["OV"] >= COMMIT_FLOOR:
            e = cands[0]
            e["state"] = "COMMITTED"
            e["committed_ts"] = time.time()
            e["plan"] = PLANS.get(e["probe"], ["split_half"])
            committed = [e]
            with open(PURSUIT, "w") as fh:
                fh.write(json.dumps({"key": e["key"], "ts": e["committed_ts"], "OV": e["OV"],
                                     "plan": e["plan"], "statement": e["statement"]}) + "\n")
            logln(f"COMMIT {e['key']} OV={e['OV']} plan={e['plan']} :: {e['statement'][:100]}")

    for e in committed:
        done = {s["name"] for s in e["steps"]}
        nxt = next((s for s in e.get("plan", []) if s not in done), None)
        if nxt is None:
            conclude(e, reg)
            for p in (PURSUIT,):
                try:
                    os.remove(p)
                except OSError:
                    pass
            break
        # ---- stopping rules, checked BEFORE spending another step ----
        if e["spend_s"] >= BUDGET_CAP_S:
            e["steps"].append({"name": "budget_stop", "verdict": "FAIL",
                               "detail": f"budget cap {BUDGET_CAP_S/3600:.1f} core-hours reached"})
            conclude(e, reg)
            try:
                os.remove(PURSUIT)
            except OSError:
                pass
            break
        t0 = time.time()
        try:
            df = load_df()
            res = STEPS[nxt](e, df)
        except Exception as ex:
            res = {"ok": False, "verdict": "ERROR", "detail": f"{type(ex).__name__}: {ex}"}
        res["name"] = nxt
        res["elapsed_s"] = round(time.time() - t0, 1)
        e["spend_s"] = round(e.get("spend_s", 0.0) + res["elapsed_s"], 1)
        e["steps"].append(res)
        if res["verdict"] == "ERROR":
            e["fails"] = e.get("fails", 0) + 1
            logln(f"STEP ERROR {e['key']} {nxt}: {res['detail']}")
            if e["fails"] >= MAX_STEP_FAILS:
                e["state"] = "ABORTED"
                e["conclusion"] = f"{MAX_STEP_FAILS} step errors; released so the harness cannot wedge"
                try:
                    os.remove(PURSUIT)
                except OSError:
                    pass
                logln(f"PURSUIT ABORTED {e['key']}")
        else:
            e["fails"] = 0
            logln(f"STEP {e['key']} {nxt} -> {res['verdict']} ({res['elapsed_s']}s): {res['detail'][:120]}")
        # FUTILITY: a failed permutation null means there is nothing here; do not spend the rest of the plan
        if nxt == "permutation" and res.get("verdict") == "FAIL":
            conclude(e, reg)
            try:
                os.remove(PURSUIT)
            except OSError:
                pass
        break   # one step per invocation: bounded runtime, and the daemon stays responsive

    jdump(reg, REG)
    with open(REGLOG, "a") as fh:
        fh.write(json.dumps({"ts": time.time(),
                             "states": {k: sum(1 for e in reg["items"].values() if e["state"] == k)
                                        for k in {e["state"] for e in reg["items"].values()}},
                             "v_explore": v_explore, "v_exploit": v_exploit,
                             "explore_share": round(share, 3)}) + "\n")

    ranked = sorted(reg["items"].values(), key=lambda e: -e["OV"])
    active = next((e for e in reg["items"].values() if e["state"] == "COMMITTED"), None)
    concluded = [e for e in reg["items"].values() if e["state"].startswith("CONCLUDED")]
    jdump({"ts": time.time(), "explore_share": round(share, 3),
           "v_explore": v_explore, "v_exploit": v_exploit,
           "counts": {k: sum(1 for e in reg["items"].values() if e["state"] == k)
                      for k in sorted({e["state"] for e in reg["items"].values()})},
           "top": [{"key": e["key"], "OV": e["OV"], "state": e["state"], "probe": e["probe"],
                    "statement": e["statement"][:150]} for e in ranked[:6]],
           "active_pursuit": (None if not active else
                              {"key": active["key"], "OV": active["OV"],
                               "steps_done": len(active["steps"]), "steps_total": len(active.get("plan", [])),
                               "spend_min": round(active.get("spend_s", 0) / 60, 1),
                               "statement": active["statement"][:150]}),
           "concluded": [{"key": e["key"], "state": e["state"], "finding": e.get("finding"),
                          "statement": e["statement"][:150]} for e in concluded[-6:]],
           "promotion_pending": os.path.exists(PROMO)}, STATE)

    print(f"explore_share={share:.2f} (V_explore {v_explore:.3f} vs V_exploit {v_exploit:.3f}); "
          f"registry {len(reg['items'])} items")
    for e in ranked[:6]:
        print(f"  OV={e['OV']:.3f} [{e['state']:<20s}] {e['statement'][:96]}")
    if active:
        print(f"  ACTIVE PURSUIT {active['key']}: step {len(active['steps'])}/{len(active.get('plan', []))}, "
              f"{active.get('spend_s', 0)/60:.1f} core-min spent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
