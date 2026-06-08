#!/usr/bin/env python
"""ROI ALLOCATOR — exploit/explore decision engine for the genesis_medicine compute box.

Synthesized from 4 independent literature surveys (2026-06-08) that all converged:
  * Bandits/RL          -> value-of-information (Gittins/KG) as discounted Thompson sampling
  * Bayesian-opt/VoI    -> cost-aware acquisition: fund max(marginal value / GPU-hour); stop arm when EI<=cost
  * Self-driving labs   -> exploit-by-default, diminishing-returns trip-wire, deadline anneal, explore floor
  * Portfolio/Kelly     -> fractional-Kelly sizing (lambda~0.3-0.5), March explore floor, Weitzman timing

Two arms compete for the single GPU (chosen one-at-a-time; long-run fraction emerges):
  A = EXPLOIT : one reliability cycle (15 ligands x 100 Boltz poses) extending sigma stats on KNOWN binders.
                KNOWN, DECAYING value. Marginal value of cycle n  ~  s_sigma / (2*sqrt(2)*(n-1)^1.5)
                (the per-cycle shrinkage of SE(sigma_hat) = sigma/sqrt(2(n-1))).  Publication-closest.
  B = EXPLORE : one de novo discovery batch (cofold + sigma-gating of generated molecules).
                HIGH variance, rare large payoff (a novel reliable binder = a 4th paper). Option value.

Core decision (cost-aware index / Gittins): fund the arm with the higher marginal value PER GPU-HOUR,
subject to a hard March floor on B (never let explore starve) and a deadline anneal on B.

This script is consulted by gpu_roi_supervisor.sh at every GPU-idle event. It is intentionally
transparent: the only subjective inputs are the utility weights LAMBDA_* (documented below).
Pure CPU, instant, read-only except for appending one row to the allocation log.
"""
import os, sys, glob, csv, math, datetime, json

SD    = "/home/crazat/genesis_medicine/scripts/round27_paperA"
PILOT = "/home/crazat/genesis_medicine/pilot/round27_paperA"
EXP   = os.path.join(PILOT, "explore_denovo_mmp1")
LOG   = os.path.join(SD, "roi_allocation_log.csv")

# ---------------- subjective utility inputs (the ONLY knobs; everything else is measured) ----------
# Value units are arbitrary but must be COMMON across arms (the literature's key caveat).
LAMBDA_A   = 1.0     # utility of fully tightening one sigma reliability claim (paper_A/B deliverable)
S_SIGMA    = 0.05    # current sigma effect scale being estimated (sigma_iptm ~0.03-0.06 spread)
LAMBDA_B   = 12.0    # utility of ONE confirmed novel reliable binder (a 4th-paper-worthy hit ~ 12x a sigma claim)
P_HIT_B    = 0.06    # prior prob a de novo deep batch surfaces >=1 new reliable-binder hit (Beta prior mean)
ALPHA_B, BETA_B = 1.0, 15.0   # Beta(a,b) posterior on P_HIT_B (mean ~0.06); updated as batches resolve

T_CYCLE_A_HRS = 1.40   # GPU-hours per reliability cycle (~84 min measured)
T_BATCH_B_HRS = 1.00   # GPU-hours per de novo deep-sigma batch (directory-batched, ~survivors x samples)

KELLY_LAMBDA  = 0.40   # fractional Kelly (robust to noisy estimates; 0.3-0.5 recommended)
B_FLOOR       = 0.15   # March floor: explore never below 15% of recent GPU slots (== "explore=0 방치 금지")
FLOOR_WINDOW  = 8      # look back this many launches to enforce the floor

# deadline anneal: explore value is multiplied by this when a manuscript is near submission.
# Our papers are publish-ready, BUT arm A is ALSO past diminishing returns (n>>28 plateau),
# so the anneal mainly prevents OVER-exploring; set mild (1.0 = off) and revisit at true submission.
DEADLINE_ANNEAL = 1.0

# ---------------- measured state ----------------
def count_reliability_cycles():
    return len(glob.glob(os.path.join(PILOT, "boltz_15_100_v19_v*")))

def next_cycle_index():
    ns = []
    for d in glob.glob(os.path.join(PILOT, "boltz_15_100_v19_v*")):
        try: ns.append(int(d.rsplit("_v", 1)[1]))
        except Exception: pass
    return (max(ns) + 1) if ns else 401

def denovo_triage_done():
    """candidates with a coarse triage result already."""
    out = os.path.join(EXP, "denovo_cofold_output")
    n = 0
    for d in glob.glob(os.path.join(out, "denovo_mmp1_*")):
        if glob.glob(os.path.join(d, "**", "confidence_*.json"), recursive=True):
            n += 1
    return n

def denovo_inputs_total():
    return len(glob.glob(os.path.join(EXP, "denovo_cofold_input", "denovo_mmp1_*.yaml")))

def recent_explore_fraction():
    if not os.path.exists(LOG):
        return 0.0
    rows = list(csv.DictReader(open(LOG)))[-FLOOR_WINDOW:]
    if not rows:
        return 0.0
    return sum(1 for r in rows if r["arm"] == "EXPLORE") / len(rows)

# ---------------- marginal value per GPU-hour ----------------
def mv_a_per_gpuhr(n):
    """EXPLOIT: per-cycle shrinkage of SE(sigma_hat) ~ s/(2*sqrt(2)*(n-1)^1.5), normalized by GPU-hours.
    Decays ~ n^-1.5 -> tiny once n is in the dozens (matches measured sigma_iptm plateau at n~28)."""
    n = max(n, 2)
    marginal = S_SIGMA / (2.0 * math.sqrt(2.0) * (n - 1) ** 1.5)
    return LAMBDA_A * marginal / T_CYCLE_A_HRS

def mv_b_per_gpuhr(triage_done, total):
    """EXPLORE: option value via Thompson draw on P_HIT_B x payoff, per GPU-hour, x deadline anneal.
    Returns (value, p_sampled). Uses posterior mean (deterministic) for the supervisor's stable decision;
    the supervisor may call --sample for a stochastic Thompson variant."""
    # posterior mean of hit prob; option value = P(hit) * payoff
    p = ALPHA_B / (ALPHA_B + BETA_B)
    # if triage incomplete, option value is HIGHER (we know least -> max expected information gain)
    unscreened = max(total - triage_done, 0)
    info_boost = 1.0 + 0.5 * (unscreened / total if total else 0.0)
    val = LAMBDA_B * p * info_boost * DEADLINE_ANNEAL / T_BATCH_B_HRS
    return val, p

def kelly_fraction(mv_b, mv_a):
    """fractional-Kelly explore share from the two marginal values (treat A as ~risk-free leg).
    f* = (mu_B - r)/sigma_B^2 ; here approximated by the normalized value gap, capped, floored."""
    edge = mv_b - mv_a
    denom = mv_b + mv_a + 1e-9
    f = KELLY_LAMBDA * max(edge, 0.0) / denom
    return min(max(f, 0.0), 1.0)

# ---------------- decide ----------------
def decide(sample=False):
    n = count_reliability_cycles()
    triage = denovo_triage_done()
    total = denovo_inputs_total()
    mva = mv_a_per_gpuhr(n)
    mvb, p = mv_b_per_gpuhr(triage, total)
    expl_frac = recent_explore_fraction()
    f_kelly = kelly_fraction(mvb, mva)

    # base rule: fund higher marginal-value-per-GPU-hour (cost-aware Gittins index)
    arm = "EXPLORE" if mvb >= mva else "EXPLOIT"
    reason = f"MV/gpuhr: A={mva:.5g} (n={n}) vs B={mvb:.5g} (p_hit={p:.3f}) -> {arm}"

    # March floor override: if recent explore share below floor, force EXPLORE (anti-atrophy)
    floored = False
    if expl_frac < B_FLOOR and triage >= total and total > 0:
        # only force the *deep* explore once triage is complete; during triage B is already getting GPU
        arm = "EXPLORE"; floored = True
        reason += f" | FLOOR override (recent explore {expl_frac:.0%}<{B_FLOOR:.0%})"

    job = {}
    if arm == "EXPLOIT":
        job = {"arm": "EXPLOIT", "kind": "reliability_cycle", "cycle": next_cycle_index(),
               "seed": next_cycle_index() + 1104}
    else:
        # if triage incomplete, the running gate handles it; supervisor should DEFER (let gate finish).
        # if triage complete, launch deep-sigma on survivors.
        kind = "denovo_deep_sigma" if triage >= total and total > 0 else "denovo_triage_inflight"
        job = {"arm": "EXPLORE", "kind": kind, "triage_done": triage, "total": total}

    out = {"decision": arm, "job": job, "mv_a": mva, "mv_b": mvb, "p_hit": p,
           "kelly_explore_frac": f_kelly, "recent_explore_frac": expl_frac,
           "n_cycles": n, "triage": f"{triage}/{total}", "floored": floored, "reason": reason}
    return out

def log_launch(arm, kind):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as fh:
        w = csv.writer(fh)
        if new: w.writerow(["ts", "arm", "kind"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), arm, kind])

if __name__ == "__main__":
    if "--log" in sys.argv:
        i = sys.argv.index("--log")
        log_launch(sys.argv[i+1], sys.argv[i+2] if len(sys.argv) > i+2 else "")
        sys.exit(0)
    d = decide(sample="--sample" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(d))
    elif "--decide" in sys.argv:
        # one parseable line for the supervisor: ARM|KIND|CYCLE|SEED
        j = d["job"]
        print(f"{j['arm']}|{j['kind']}|{j.get('cycle','')}|{j.get('seed','')}")
    else:
        print(f"DECISION: {d['decision']}  ({d['job']['kind']})")
        print(f"  {d['reason']}")
        print(f"  n_cycles={d['n_cycles']}  triage={d['triage']}  recent_explore={d['recent_explore_frac']:.0%}")
        print(f"  Kelly explore frac target={d['kelly_explore_frac']:.2f}  floored={d['floored']}")
