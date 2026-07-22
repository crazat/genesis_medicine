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


LEDGER_STATE = os.path.join(SD, "paper_claim_ledger_state.json")

# Which paper_claim_ledger claim each buildable tier type advances.
#   GENERATION / ACQUISITION -> P1  "de novo generated hits pass DUAL-reliability gating" (fresh hits)
#   REPLICATE                -> B2  "sigma_iptm reproducibility characterized deeper" (already-measured)
# Both GEN and ACQ serve the SAME claim, so choosing between them is a pure resource question and stays
# phase8's job; choosing WHICH CLAIM to serve is the ledger's.
TIER_CLAIM = {"GENERATION": "P1", "ACQUISITION": "P1", "REPLICATE": "B2"}


def claim_mv():
    """{claim_id: marginal value} from the R12 claim ledger (objective = sum P(accept)*impact).

    The ledger is the only layer that models what actually matters (a paper getting accepted); phase8
    only knows marginal-VOI-per-core. Until 2026-07-15 this planner read ONLY phase8's ACQ-vs-GEN
    scalar, so the ledger's standing verdict ("P1 is #1 at MV 0.943") had no path to the GPU at all --
    which is how 93% of tiers (13.7k molecule-slots) became REPLICATE, i.e. claim B2 at MV 0.110, an
    8.6x lower-value claim, at ~440W. Unreadable state -> {} -> caller keeps the phase8 ordering."""
    try:
        d = json.load(open(LEDGER_STATE))
        return {r["id"]: float(r["MV"]) for r in d.get("ranked", []) if "id" in r and "MV" in r}
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


RANKED = os.path.join(EXP, "combined_ranked.csv")
CURSOR = os.path.join(EXP, "replicate_cursor.txt")
CI_CSV = os.path.join(EXP, "phase14_replicate_ci.csv")
IDLE_FLAG = os.path.join(TS, "IDLE_BY_DESIGN")


def replicate_needed():
    """cand_ids whose sigma_iptm has NOT yet reached phase14's precision target (rel halfwidth +-25%).

    Authoritative source is phase14_replicate_ci.csv (refreshed ~25 min by sweetspot_ledger_loop).
    An unreadable/absent file returns [] on purpose: with no precision evidence, the correct action is
    to NOT spend GPU on speculative replicates."""
    try:
        with open(CI_CSV) as fh:
            return [r["cand_id"] for r in csv.DictReader(fh)
                    if str(r.get("precision_reached_stop", "1")).strip() != "1"]
    except Exception:
        return []


LABELS = os.path.join(EXP, "phase3_labels.csv")


def mark_idle(reason):
    """Record that the planner deliberately queued nothing, so an idle GPU is the INTENDED state.

    autonomous_watcher reads this flag and holds its boltz/util counters; without it the watcher's
    liveness trips fire on an idle-by-design slot and false-wake the LLM."""
    try:
        open(IDLE_FLAG, "w").write(f"{time.time()} {reason}\n")
    except Exception:
        pass


def smiles_map(need):
    """{cand_id: smiles} for `need`, searched across EVERY source that carries a SMILES.

    Three sources are required, and each covers a different population:
      * combined_ranked.csv          -- the 1784-molecule seed library only
      * consumed/pending gen manifest -- the GENERATED candidates (auto*/r3_*); this is the ONLY place
                                        their SMILES exist. phase3_labels.csv has a `smiles` column but
                                        it is EMPTY for all 2095 generated rows (phase3_build_labels
                                        pulls metadata from combined_ranked.csv, which does not know
                                        them), so labels alone resolves nothing.
    Looking in the library alone stranded real work: "3 candidate(s) below target but none found in
    combined_ranked.csv" (2026-07-15 00:44) -- all 3 were generated molecules that phase14 says are
    still buying precision."""
    out = {}
    sources = [RANKED, LABELS, os.path.join(EXP, "pending_gen_manifest.csv")]
    sources += sorted(glob.glob(os.path.join(EXP, "consumed_gen_manifest*.csv")))
    for path in sources:
        try:
            with open(path) as fh:
                for r in csv.DictReader(fh):
                    cid = (r.get("cand_id") or "").strip()
                    smi = (r.get("smiles") or "").strip()
                    if cid in need and smi and cid not in out:
                        out[cid] = smi
        except Exception:
            continue
    return out


def in_flight_cands():
    """cand_ids already staged in a tier that is RUNNING or QUEUED -- never build a second tier for them.

    Each tier adds ~32 samples, which is the whole precision target, so a duplicate tier is pure
    oversampling. Without this guard the slot loop builds one tier per slot from the same `need` set
    (t754 and t755 were byte-identical 3-molecule tiers, 2026-07-15 00:55), and every subsequent 10-min
    planner tick rebuilds them again until phase14 next refreshes (~25 min) -- re-creating exactly the
    oversampling this gate exists to stop."""
    tiers = []
    for slot in SLOTS:
        cur = read1(os.path.join(TS, f"slot_{slot}.current"))
        if cur:
            tiers.append(cur)
        tiers += queue_list(slot)
    cands = set()
    for t in tiers:
        for y in glob.glob(os.path.join(EXP, f"denovo_cofold_input_{t}", "*.yaml")):
            cands.add(os.path.splitext(os.path.basename(y))[0])
    return cands


def build_replicate_tier(tnum):
    """Precision-GATED replicates. Replicate only candidates still buying precision; else build nothing.

    Until 2026-07-15 this was an unconditional never-idle filler: it walked the ranked library with a
    cursor and ALWAYS returned a tier. Measured result of that policy — 685 of 733 tiers (93%; 13,700
    molecule-slots) were replicates of candidates whose sigma was already pinned. All 1784 ranked
    candidates sit at >=32 samples (median 288 = 9x the +-25% target; 88% of the 495k samples collected
    are past target) and phase14 reports 565/567 precision-SATURATED "do-not-replicate". That bought no
    claim value at ~440W. Per user decision 2026-07-15 (scale generation; idle rather than re-cofold),
    an empty precision-buying set now yields None -> queue stays empty -> slot idles by design."""
    need = set(replicate_needed()) - in_flight_cands()
    if not need:
        mark_idle("replicate precision-saturated / already in flight")
        logln("REPLICATE skipped: 0 candidates below the phase14 precision target that are not already "
              "in flight (library is ~9x over-sampled) -> slot left IDLE BY DESIGN, no make-work cofold")
        return None
    smi = smiles_map(need)
    seg = sorted(smi.items())[:20]
    if not seg:
        mark_idle("replicate candidates below target but no SMILES resolvable")
        logln(f"REPLICATE skipped: {len(need)} candidate(s) below target but no SMILES found in "
              f"combined_ranked.csv or phase3_labels.csv -> IDLE BY DESIGN")
        return None
    t = f"t{tnum}"
    batch = os.path.join(EXP, f"replicate_batch_{t}.csv")
    with open(batch, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cand_id", "smiles"])
        for cid, s in seg:
            w.writerow([cid, s])
    subprocess.run([PY, os.path.join(EXP, "phase2_build_inputs_generic.py"), batch,
                    os.path.join(EXP, f"denovo_cofold_input_{t}")],
                   cwd=EXP, capture_output=True, text=True, timeout=900)
    if n_inputs(t) > 0:
        logln(f"built REPLICATE tier {t} ({n_inputs(t)} YAML) — precision-buying only "
              f"({len(need)} candidate(s) below phase14 target)")
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
        # R11 GRADUAL ACTUATION (user-approved 2026-06-13, SAFE subset only): honor phase8's VOC-stop /
        # over-greed flags by RAISING THE CEILING (kick a generation round on cores 19-23), never by
        # moving the 0-18 exploit floor (that stays a reviewed step). voc_stop = all tracks below the
        # marginal-VOI floor -> grinding is busy-work, generate instead (Russell-Wefald). over_greedy =
        # EXPLOIT hoarding cores while GENERATION buys more per core -> push explore on 19-23. Gated on
        # NOT gpu_paused (generated mols need a downstream GPU cofold; don't build backlog during a pause)
        # and trigger_generation_round()'s own guards (no double-launch, skip if a manifest is pending).
        if (st.get("voc_stop") or st.get("over_greedy")) and not st.get("gpu_paused"):
            trigger_generation_round()
            logln(f"phase8 ACTUATION: voc_stop={st.get('voc_stop')} over_greedy={st.get('over_greedy')} "
                  f"-> ensured generation round (ceiling-raise, cores 19-23; floor 0-18 untouched)")
        nxt = max(all_tier_numbers()) + 1
        for slot in SLOTS:
            if len(queue_list(slot)) >= MIN_QUEUE:
                continue
            cur = read1(os.path.join(TS, f"slot_{slot}.current"))
            ni, nd = n_inputs(cur), n_done(cur)
            if ni == 0 or nd < LEAD_FRAC * ni:
                continue
            # CLAIM-VALUE ORDERING (R12 ledger drives the GPU as of 2026-07-15). Try tier types in
            # descending order of the MV of the claim each one advances, and take the first that is
            # actually buildable. phase8 only breaks the GENERATION-vs-ACQUISITION tie (same claim P1
            # -> pure resource question). REPLICATE serves B2 (0.110 vs P1 0.943 = 8.6x lower) so it is
            # tried last, and its own phase14 precision gate returns None unless a candidate is genuinely
            # still buying precision -- together that is what retires the old never-idle junk fallback.
            prefer_gen = gen_v > acq_v
            mv = claim_mv()
            kinds = ["GENERATION", "ACQUISITION"] if prefer_gen else ["ACQUISITION", "GENERATION"]
            if mv:
                kinds.sort(key=lambda k: mv.get(TIER_CLAIM[k], 0.0), reverse=True)
            kinds.append("REPLICATE")
            builders = {"GENERATION": build_generation_tier,
                        "ACQUISITION": build_acquisition_tier,
                        "REPLICATE": build_replicate_tier}
            built = kind = None
            for k in kinds:
                built = builders[k](nxt)
                if built:
                    kind = k
                    break
                if k in ("GENERATION", "ACQUISITION"):
                    trigger_generation_round()   # keep the top-claim (P1) pipeline filling
            if built:
                logln(f"slot-{slot} type={kind} -> claim {TIER_CLAIM[kind]} "
                      f"(ledger MV {mv.get(TIER_CLAIM[kind], 0.0):.3f}"
                      f"{', ledger unavailable -> phase8 order' if not mv else ''})")
                with open(os.path.join(TS, f"slot_{slot}.queue"), "a") as fh:
                    fh.write(built + "\n")
                try:
                    os.remove(IDLE_FLAG)   # real work queued -> GPU idle is no longer the intended state
                except OSError:
                    pass
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
