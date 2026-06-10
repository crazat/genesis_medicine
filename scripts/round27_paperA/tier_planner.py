#!/usr/bin/env python
"""tier_planner.py (R10) — the INTELLIGENT layer that keeps the queue-driven supervisor never-idle while
letting phase8's sweet-spot verdict decide WHAT to run next, with NO per-transition human/LLM action.

For each GPU slot: if its tier queue has dropped below MIN_QUEUE and the current tier is >= LEAD_FRAC done,
build & queue the next tier. The TYPE is chosen by phase8's marginal-VOI-per-cost:
  * GENERATION mVOI > ACQUISITION mVOI  -> queue a ready illuminated generation batch if one exists;
    else trigger run_generation_round.sh to prepare one (and queue ACQUISITION this round to stay busy).
  * otherwise -> build an ACQUISITION tier from the un-cofolded pool (always available = never-idle floor).

This is the "greed vs exploration sweet spot, continuously, without my intervention": the supervisor
rotates mechanically; THIS decides the mix; phase8 supplies the number; the LLM autonomous-loop only
handles strategy/exceptions above it. Single-process, lock-guarded, pure CPU. Run from tier_autopilot.sh.
"""
import os, sys, csv, json, glob, subprocess, time, re

SD = "/home/crazat/genesis_medicine/scripts/round27_paperA"
EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
TS = os.path.join(SD, "tier_state")
PHASE8 = os.path.join(SD, "phase8_sweetspot_controller.py")
PHASE8_STATE = os.path.join(SD, "phase8_sweetspot_state.json")
GENROUND = os.path.join(SD, "run_generation_round.sh")
PENDING_GEN = os.path.join(EXP, "pending_gen_manifest.csv")
LOG = os.path.join(SD, "tier_planner.log")
LOCK = os.path.join(SD, "tier_planner.lock")
PY = "/home/crazat/genesis_medicine/.venv/bin/python"
MIN_QUEUE = 1
LEAD_FRAC = 0.70
SLOTS = ["E", "F"]


def logln(m):
    with open(LOG, "a") as fh:
        fh.write(f"[{time.strftime('%F %T')}] {m}\n")
    print(m)


def read1(path, default=""):
    try:
        return open(path).read().strip()
    except Exception:
        return default


def queue_list(slot):
    return [x for x in read1(os.path.join(TS, f"slot_{slot}.queue")).splitlines() if x.strip()]


def n_inputs(t):
    return len(glob.glob(os.path.join(EXP, f"denovo_cofold_input_{t}", "*.yaml")))


def n_done(t):
    return len(glob.glob(os.path.join(EXP, f"denovo_{t}_output", "**", "confidence_*_model_0.json"),
                         recursive=True))


def all_tier_numbers():
    nums = {0}
    for d in glob.glob(os.path.join(EXP, "denovo_cofold_input_t*")):
        m = re.search(r"_t(\d+)$", d)
        if m:
            nums.add(int(m.group(1)))
    for slot in SLOTS:
        cur = read1(os.path.join(TS, f"slot_{slot}.current"), "t0").lstrip("t")
        nums.add(int(cur or 0))
        for q in queue_list(slot):
            nums.add(int(q.lstrip("t") or 0))
    return nums


def refresh_phase8():
    try:
        subprocess.run([PY, PHASE8], cwd=EXP, capture_output=True, timeout=120)
    except Exception as e:
        logln(f"phase8 refresh failed: {e}")
    try:
        return json.load(open(PHASE8_STATE))
    except Exception:
        return {}


def build_acquisition_tier(tnum):
    t = f"t{tnum}"
    batch = os.path.join(EXP, f"phase3_next_batch_{t}.csv")
    outdir = os.path.join(EXP, f"denovo_cofold_input_{t}")
    sel = subprocess.run([PY, os.path.join(EXP, "phase3_acquisition_select.py"),
                          "--stage-dir", f"denovo_cofold_input_{t}", "--out", batch],
                         cwd=EXP, capture_output=True, text=True, timeout=900)
    if not os.path.exists(batch):
        logln(f"acquisition select FAILED {t}: {sel.stderr[-300:]}")
        return None
    subprocess.run([PY, os.path.join(EXP, "phase2_build_inputs_generic.py"), batch, outdir],
                   cwd=EXP, capture_output=True, text=True, timeout=900)
    if n_inputs(t) > 0:
        logln(f"built ACQUISITION tier {t} ({n_inputs(t)} YAML)")
        return t
    logln(f"build_inputs FAILED {t}")
    return None


def build_generation_tier(tnum):
    if not (os.path.exists(PENDING_GEN) and os.path.getsize(PENDING_GEN) > 0):
        return None
    t = f"t{tnum}"
    outdir = os.path.join(EXP, f"denovo_cofold_input_{t}")
    subprocess.run([PY, os.path.join(EXP, "phase2_build_inputs_generic.py"), PENDING_GEN, outdir],
                   cwd=EXP, capture_output=True, text=True, timeout=900)
    if n_inputs(t) > 0:
        os.rename(PENDING_GEN, os.path.join(EXP, f"consumed_gen_manifest_{t}.csv"))
        logln(f"built GENERATION tier {t} ({n_inputs(t)} YAML) from illuminated reseed")
        return t
    return None


def gen_round_running():
    try:
        return bool(subprocess.run(["pgrep", "-f", "[r]un_generation_round"],
                                   capture_output=True, text=True).stdout.strip())
    except Exception:
        return False


def trigger_generation_round():
    if gen_round_running() or (os.path.exists(PENDING_GEN) and os.path.getsize(PENDING_GEN) > 0):
        return
    try:
        subprocess.Popen(["setsid", "bash", GENROUND], cwd=EXP,
                         stdout=open(os.path.join(SD, "run_generation_round.log"), "a"),
                         stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        logln("triggered run_generation_round.sh (GEN favored, no batch ready); ACQ queued this round")
    except Exception as e:
        logln(f"gen trigger failed: {e}")


def main():
    if os.path.exists(LOCK) and (time.time() - os.path.getmtime(LOCK) < 1800):
        return
    open(LOCK, "w").write(str(time.time()))
    try:
        st = refresh_phase8()
        tr = st.get("tracks", {})
        acq_v = float(tr.get("ACQUISITION", 1.0))
        gen_v = float(tr.get("GENERATION", 0.0))
        nxt = max(all_tier_numbers()) + 1
        for slot in SLOTS:
            if len(queue_list(slot)) >= MIN_QUEUE:
                continue
            cur = read1(os.path.join(TS, f"slot_{slot}.current"))
            ni, nd = n_inputs(cur), n_done(cur)
            if ni == 0 or nd < LEAD_FRAC * ni:
                continue
            prefer_gen = gen_v > acq_v
            built = None
            if prefer_gen:
                built = build_generation_tier(nxt)
                if built is None:
                    trigger_generation_round()
            if built is None:
                built = build_acquisition_tier(nxt)
            if built:
                with open(os.path.join(TS, f"slot_{slot}.queue"), "a") as fh:
                    fh.write(built + "\n")
                logln(f"slot-{slot} queue <- {built} (phase8 ACQ {acq_v:.3f} vs GEN {gen_v:.3f} -> "
                      f"{'GEN' if prefer_gen else 'ACQ'}; cur {cur} {nd}/{ni})")
                nxt += 1
    finally:
        try:
            os.remove(LOCK)
        except Exception:
            pass


if __name__ == "__main__":
    main()
