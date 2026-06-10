#!/usr/bin/env bash
# GPU ROI SUPERVISOR v4 — QUEUE-DRIVEN autonomous tier rotation.
#
# v3 hardcoded each slot's tier and required a human/LLM to EDIT this file at every resume-skip trap.
# v4 makes tier transition AUTONOMOUS: each slot has a CURRENT tier + a QUEUE of upcoming tiers
# (tier_state/slot_{E,F}.{current,queue}). When the current tier completes (trap = N_done has stalled at
# >= N_inputs, or stalled at >= N_inputs - SKIP_TOL for STALL_SKIP polls), the supervisor SIGKILLs it, pops the
# next tier off the queue, and rotates to it -- no edit, no restart, no idle wait for me.
#
# TWO-LAYER autonomy (the user's "greed/exploration sweet spot without my intervention"):
#   * THIS shell layer = mechanical never-idle rotation (deterministic, robust, runs blind).
#   * tier_planner.py (via tier_autopilot.sh) = the INTELLIGENT layer that REFILLS the queue, using
#     phase8's marginal-VOI-per-cost verdict to choose the next tier's TYPE (ACQUISITION vs GENERATION)
#     and to BUILD it ahead of time. The LLM (autonomous-loop) sits above both for strategy/exceptions.
#
# Convention: tier tN  <->  input denovo_cofold_input_tN, output denovo_tN_output, log denovo_tN.log.
#   SLOT-E: cores 19-23, seed 7041.    SLOT-F: cores 14-18, seed 8107.
# 2-explore @32 max_parallel=2 + expandable_segments => ~21GB used / ~11GB free (OOM-safe; user "OOM
# 절대금지 1순위"). gpu_vram_watchdog.sh backstops at free<6GB. STRICT one-boltz-per-slot.
set -u
SD=/home/crazat/genesis_medicine/scripts/round27_paperA
PILOT=/home/crazat/genesis_medicine/pilot/round27_paperA
EXP=$PILOT/explore_denovo_mmp1
BOLTZ=/home/crazat/miniforge3/envs/genesis-md/bin/boltz
LOG=$SD/gpu_roi_supervisor.log
TS=$SD/tier_state
POLL=${POLL:-30}
SKIP_TOL=2          # a tier is "near-done" at N_inputs - SKIP_TOL (covers silent YAML-escape skips)
STALL_SKIP=16       # near-done-but-not-100%: rotate only after this many no-progress polls (~8 min, LONGER
                    # than the slowest single-candidate cofold so a slow-but-finishing candidate resets the
                    # stall; only a genuinely skipped/stuck candidate trips it). d>=N_inputs rotates at once.
log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }
slot_alive(){ for p in $(pgrep -f '[b]oltz predict'); do tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | grep -q "$1" && return 0; done; return 1; }

n_inputs(){ ls $EXP/denovo_cofold_input_$1/*.yaml 2>/dev/null | wc -l; }
n_done(){ find $EXP/denovo_$1_output -name 'confidence_*_model_0.json' 2>/dev/null | wc -l; }
tier_ready(){ [ "$(n_inputs "$1")" -gt 0 ]; }
kill_tier_boltz(){ for p in $(pgrep -f '[b]oltz predict'); do tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | grep -q "denovo_$1_output" && kill -9 "$p" 2>/dev/null; done; }

launch_tier(){  # $1=tier $2=cores $3=seed $4=slotname
  cd $EXP
  log "SLOT-$4 LAUNCH tier $1 @32 max_parallel=1 (cores $2, seed $3, resume denovo_$1_output)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8 \
  nohup taskset -c $2 $BOLTZ predict denovo_cofold_input_$1 \
    --out_dir denovo_$1_output --diffusion_samples 32 --num_workers 0 --max_parallel_samples 1 --use_potentials \
    --output_format pdb --seed $3 > $EXP/denovo_$1.log 2>&1 &
}

run_slot(){  # $1=slotname(E/F) $2=cores $3=seed
  local cur d ni last stall near trapped nxt
  cur=$(cat $TS/slot_$1.current 2>/dev/null)
  [ -z "$cur" ] && { log "slot-$1: no current tier; skip"; return; }
  d=$(n_done "$cur"); ni=$(n_inputs "$cur")
  # stall tracking: consecutive polls with no new completion
  last=$(cat $TS/slot_$1.lastdone 2>/dev/null || echo 0)
  stall=$(cat $TS/slot_$1.stall 2>/dev/null || echo 0)
  if [ "$d" -gt "$last" ]; then stall=0; else stall=$((stall + 1)); fi
  echo "$d" > $TS/slot_$1.lastdone; echo "$stall" > $TS/slot_$1.stall
  near=0; trapped=0
  if [ "$ni" -gt 0 ]; then
    if [ "$d" -ge "$ni" ]; then
      trapped=1                                          # 100% done -> boltz self-exiting -> rotate now
    elif [ "$d" -ge "$((ni - SKIP_TOL))" ]; then
      near=1
      # near-done AND boltz has EXITED => it self-exited "all processed" with the tail silently skipped
      # (YAML-escape resume-skip). That's a confirmed completion signal -> rotate at once, don't burn
      # ~8 min of half-GPU waiting on a candidate boltz already gave up on. A genuinely-slow last
      # candidate keeps boltz alive, so it falls through to the STALL_SKIP timer instead.
      if ! slot_alive "denovo_${cur}_output"; then trapped=1
      elif [ "$stall" -ge "$STALL_SKIP" ]; then trapped=1; fi
    fi
  fi

  if [ "$trapped" = 1 ]; then
    nxt=$(head -1 $TS/slot_$1.queue 2>/dev/null)
    if [ -n "$nxt" ] && tier_ready "$nxt"; then
      log "AUTO-ROTATE slot-$1: $cur (done $d/$ni, stalled ${stall}p) -> $nxt"
      kill_tier_boltz "$cur"                       # drop the trapped self-exiting boltz (no 3-context)
      echo "$nxt" > $TS/slot_$1.current
      sed -i '1d' $TS/slot_$1.queue
      echo 0 > $TS/slot_$1.lastdone; echo 0 > $TS/slot_$1.stall
      cur=$nxt
    else
      log "slot-$1: tier $cur DONE but queue empty/not-ready -> awaiting tier_planner refill (1-explore until then)"
      return
    fi
  elif [ "$near" = 1 ]; then
    return                                         # near-done: let it finish/self-exit, don't flap-relaunch
  fi
  # ensure current tier is running (resume if it genuinely died mid-run)
  if ! slot_alive "denovo_${cur}_output"; then
    launch_tier "$cur" "$2" "$3" "$1"; sleep 10
  fi
}

log "GPU ROI SUPERVISOR v4 START (QUEUE-DRIVEN auto-rotation; SLOT-E 19-23/7041 + SLOT-F 14-18/8107; poll ${POLL}s, trap: d>=N or near-done+${STALL_SKIP}p stall)"
while true; do
  run_slot E "19-23" 7041
  run_slot F "14-18" 8107
  sleep "$POLL"
done
