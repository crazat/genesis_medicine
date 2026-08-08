#!/usr/bin/env bash
# roi_report.sh — the OUTCOME report: what the electricity actually bought.
#
# WHY THIS EXISTS (2026-07-15): reporting "GPU 95%, boltz=2, daemons up" is a dashboard reading, not a
# result. Utilisation is a proxy, and on 2026-07-15 the proxy read perfect while 93% of GPU tiers were
# re-cofolding molecules already at 9x their sample target and every ROI layer was judging from a 35-day
# stale snapshot. A busy machine is not evidence of progress -- it is most expensive precisely when it is
# busy with worthless work. So the standing report is claim value (P(accept) x impact), and utilisation is
# demoted to an appendix.
#
# Pure CPU, read-only, instant. Run before every status report to the user.
set -u
SD=/home/crazat/genesis_medicine/scripts/round27_paperA
EXP=/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1
TS=$SD/tier_state
PY=/home/crazat/genesis_medicine/.venv/bin/python
SNAP=$SD/roi_report_last.json          # previous snapshot -> deltas ("what moved since last report")

"$PY" - "$SNAP" <<'PY'
import json, os, sys, glob, csv, time, subprocess

SD  = "/home/crazat/genesis_medicine/scripts/round27_paperA"
EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
SNAP = sys.argv[1]

def jload(p, d=None):
    try:
        return json.load(open(p))
    except Exception:
        return d

def age_h(p):
    try:
        return (time.time() - os.path.getmtime(p)) / 3600.0
    except Exception:
        return None

def nrows(p):
    try:
        return max(sum(1 for _ in open(p)) - 1, 0)
    except Exception:
        return 0

led = jload(os.path.join(SD, "paper_claim_ledger_state.json"), {})
prev = jload(SNAP, {})
prev_mv = {c["id"]: c for c in prev.get("ranked", [])}

ranked = led.get("ranked", [])
print("=" * 78)
print("CLAIM VALUE  (objective = sum P(accept) x impact -- what the compute is buying)")
print("=" * 78)
if not ranked:
    print("  !! ledger state unreadable -- the value layer is DOWN, fix before trusting anything below")
for c in ranked:
    p = prev_mv.get(c["id"])
    dmv = c["MV"] - p["MV"] if p else None
    dsu = c["sufficiency"] - p["sufficiency"] if p else None
    arrow = "" if dmv is None else (f"  [MV {dmv:+.3f}, suff {dsu:+.3f}]" if abs(dmv) > 1e-9 or abs(dsu) > 1e-9
                                    else "  [unchanged]")
    print(f"  {c['id']:3s} p{str(c['paper']):2s} MV={c['MV']:6.3f}  suff={c['sufficiency']:.2f}  "
          f"{c['cost']:10s}{arrow}")
    print(f"        {c['statement'][:88]}")
top = next((c for c in ranked if c["id"] == led.get("top")), None)
if top:
    print(f"\n  >>> TOP CLAIM: {top['id']} (MV {top['MV']:.3f}) -> {top['decisive_artifact'][:96]}")
if led.get("floor_is_low_mv"):
    print(f"  [!] MISALLOCATION: floor serves MV={led.get('floor_serves_mv')} vs top {top['MV'] if top else '?'}")

# ---- R14 deliverable axis: the single NEXT ACTION across compute / write-up / idle ----
acts = led.get("actions", [])
if acts:
    print("\n  NEXT ACTIONS  (value realized on PUBLICATION, not compute-completion):")
    for a in acts[:5]:
        print(f"    {a['MV']:6.3f}  {a['kind']:<7} {a['claim']:3s}  {a['what'][:60]}")
    ba = led.get("best_action")
    if ba and ba.get("MV", 0) >= 0.12:
        print(f"  >>> DO NEXT: {ba['kind']} {ba['claim']} (MV {ba['MV']:.3f}) -- {ba['what'][:60]}")
    else:
        print("  >>> DO NEXT: nothing above the value floor -> SUBMISSION (author decision) is the binding step")
    if led.get("floor_should_idle"):
        print("  [VOC-STOP] no compute worth a core-hour -> the exploit floor IDLEs make-work; the binding "
              "constraint is WRITE-UP / SUBMISSION, not compute.")

# ---- R15 opportunity harness: explore in HYPOTHESIS space, and the one committed pursuit ----
# The block above ranks actions within a FIXED claim set. This one reports the layer that can add to it.
h = jload(os.path.join(SD, "tier_state", "harness", "harness_state.json"), {})
if h:
    print("\n" + "=" * 78)
    print("OPPORTUNITY HARNESS  (explore in hypothesis space -- the claim set is no longer fixed)")
    print("=" * 78)
    print(f"  explore share {h.get('explore_share', 0):.2f}   V_explore {h.get('v_explore', 0):.3f} vs "
          f"V_exploit {h.get('v_exploit', 0):.3f}   (clamped to [0.10, 0.40] on both sides by design)")
    print("  registry: " + (", ".join(f"{k}={v}" for k, v in sorted(h.get("counts", {}).items())) or "empty"))
    for o in h.get("top", [])[:4]:
        print(f"    OV={o['OV']:.3f} [{o['state']:<19s}] {o['statement'][:88]}")
    ap = h.get("active_pursuit")
    if ap:
        print(f"  >>> PURSUING {ap['key']}  step {ap['steps_done']}/{ap['steps_total']}, "
              f"{ap['spend_min']:.1f} core-min spent")
        print(f"      {ap['statement'][:88]}")
    else:
        print("  >>> no committed pursuit right now (nothing above the commit floor, or one just concluded)")
    for c in h.get("concluded", [])[-3:]:
        print(f"    {c['state']:<21s} {c['statement'][:76]}")
    if h.get("promotion_pending"):
        print("  [!] PROMOTION PENDING: a pursuit passed every confirmation step and is waiting to be "
              "promoted into paper_claim_ledger.py (an LLM/author decision, not a mechanical one)")
else:
    print("\n  (opportunity harness has no state yet -- check that harness_loop.sh is running)")

# ---- evidence freshness: if this is stale, EVERY number above is a stale snapshot ----
print("\n" + "=" * 78)
print("EVIDENCE FRESHNESS  (stale => every ROI layer above is judging from an old snapshot)")
print("=" * 78)
for label, path in (("sigma_iptm (phase2_reliability_ranked)", os.path.join(EXP, "phase2_reliability_ranked.csv")),
                    ("labels    (phase3_labels)", os.path.join(EXP, "phase3_labels.csv")),
                    ("ledger    (paper_claim_ledger_state)", os.path.join(SD, "paper_claim_ledger_state.json"))):
    a = age_h(path)
    flag = "  <<< STALE" if (a is None or a > 3) else ""
    print(f"  {label:42s} {nrows(path):6d} rows   age {('?' if a is None else f'{a:5.1f}h')}{flag}")

# ---- production since last report ----
print("\n" + "=" * 78)
print("PRODUCTION SINCE LAST REPORT")
print("=" * 78)
labels = os.path.join(EXP, "phase3_labels.csv")
nlab = nrows(labels)
gen = 0
try:
    with open(labels) as fh:
        gen = sum(1 for r in csv.DictReader(fh) if "auto" in r.get("cand_id", ""))
except Exception:
    pass
mols = len(glob.glob(os.path.join(EXP, "denovo_t*_output", "**", "confidence_*_model_0.json"), recursive=True))
cells = len(glob.glob(os.path.join(EXP, "phase2_denovo_sigmaE_*.shard0.csv")))
cur = {"labels": nlab, "generated_labelled": gen, "cofold_mols": mols, "sigma_cells": cells}
for k, v in cur.items():
    d = v - prev.get("production", {}).get(k, v)
    print(f"  {k:22s} {v:7d}   ({d:+d} since last report)")

# ---- what the slots are actually doing right now ----
print("\n" + "=" * 78)
print("WHAT THE COMPUTE IS DOING (appendix -- utilisation is NOT a result)")
print("=" * 78)
def sh(c):
    try:
        return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return "?"
for slot in ("E", "F"):
    t = open(os.path.join(SD, "tier_state", f"slot_{slot}.current")).read().strip() if \
        os.path.exists(os.path.join(SD, "tier_state", f"slot_{slot}.current")) else "?"
    kind = sh(f"grep -oE 'built [A-Z]+ tier {t} ' {SD}/tier_planner.log | tail -1 | awk '{{print $2}}'") or "?"
    print(f"  slot-{slot}: tier {t} (type {kind})")
n_boltz = sh("fuser /dev/dxg 2>/dev/null | tr ' ' '\\n' | grep -c '[0-9]'")
n_xtb = sh("pgrep -fc '[/]bin/xtb '")
gpu = sh("nvidia-smi --query-gpu=utilization.gpu,power.draw --format=csv,noheader")
load = sh("cut -d' ' -f1 /proc/loadavg")
print(f"  boltz={n_boltz}  xtb={n_xtb}  gpu={gpu}  load={load}")
if os.path.exists(os.path.join(SD, "tier_state", "IDLE_BY_DESIGN")):
    print("  NOTE: IDLE_BY_DESIGN set -> GPU idle is intentional (no precision-buying work available)")

json.dump({"ts": time.time(), "ranked": ranked, "production": cur}, open(SNAP, "w"), indent=2)
print("\n(snapshot saved -> next report shows deltas against this point)")
PY
