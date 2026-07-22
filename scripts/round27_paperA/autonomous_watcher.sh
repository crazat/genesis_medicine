#!/usr/bin/env bash
# autonomous_watcher.sh (R11) — EVENT-DRIVEN incident detector for the de novo MMP-1 autonomous stack.
#
# WHY: a fixed-interval LLM cron (25 min) pays a full uncached context re-read every fire (>5 min cache
# TTL) and is 95%+ "nothing changed" — worst ROI for an expensive model. Meanwhile every TIME-CRITICAL
# fault is already self-healed in SECONDS by mechanical daemons (gpu_vram_watchdog <65s, gpu_roi_supervisor
# rotation, tier_autopilot queue-refill, floor watchdog) — independent of how often the LLM looks. So the
# LLM only needs to wake for faults those daemons CAN'T fix, which are rare & low-frequency.
#
# This watcher runs cheap shell checks every CHECK_S and EXITS (-> the harness re-invokes the LLM via the
# background-task completion hook) ONLY when a real, un-self-healed anomaly is SUSTAINED past its anti-flap
# guard. Healthy steady-state => it never wakes the LLM at all. Net effect vs the old 25-min poll:
#   * cost: LLM fires ~= (incidents + hourly cron heartbeat), NOT ~= wall-clock/interval  (~24 vs ~58/day)
#   * latency: a fault the LLM must handle is caught in ~1 min (CHECK_S*guard), not up to 25 min.
# Pareto-better: cheaper AND faster. The hourly `<<autonomous-loop>>` cron is the backstop that relaunches
# this if it dies (external Gemini co-tenant kill) and does the periodic strategic check.
#
# Pure CPU, nice 15, explore cores 19-23 (exploit 0-18 untouched). Launch via Bash run_in_background:true
# so its EXIT re-invokes the LLM. Self-match-safe process counting (exact cmdline prefix, not pgrep -fc).
set -u
SD=/home/crazat/genesis_medicine/scripts/round27_paperA
TS=$SD/tier_state
EXP=/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1
CHECK_S=${CHECK_S:-45}
SELF_REFRESH_S=${SELF_REFRESH_S:-21600}   # 6h clean exit to avoid a zombie watcher; cron/LLM relaunch
START=$SECONDS

# count only top-level daemons: a match whose PPID is ALSO a match is a same-named subshell child
# (e.g. gpu_vram_watchdog's real_free torch-confirm subshell shows cmdline "bash gpu_vram_watchdog.sh"
# and lingers ~71s under load -> would inflate the count to 2 and false-trip "OOM backstop GONE" 2026-07-13).
# A genuine duplicate daemon has ppid=1/325 (not a match) so it is still counted -> real dup still detected.
pc(){ local n=0 p pp pids; pids=$(pgrep -f "$1" 2>/dev/null); for p in $pids; do tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | grep -q "^$2" || continue; pp=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); printf '%s\n' $pids | grep -qx "$pp" && continue; n=$((n+1)); done; echo $n; }
boltz_n(){ pgrep -f '[b]oltz predict' 2>/dev/null | wc -l; }
xtb_n(){ local n; n=$(pgrep -fc '[/]bin/xtb ' 2>/dev/null); echo "${n:-0}"; }   # capture: pgrep -fc exits 1 at 0 matches but still prints "0"
# numeric-validate: transient WSL2 "Failed to initialize NVML: GPU access blocked by the operating system"
# (dxg hwqueue INSUFFICIENT_RESOURCES under 2-slot load, 2026-07-13) prints an error STRING to stdout; return
# "" for any non-integer so the -n guards at the trip checks reset counters cleanly (no false-trip, no noise).
gpu_util(){ local v; v=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | tr -d ' '); case "$v" in ''|*[!0-9]*) echo "";; *) echo "$v";; esac; }
gpu_free(){ local v; v=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | tr -d ' '); case "$v" in ''|*[!0-9]*) echo "";; *) echo "$v";; esac; }
PYG=${PYG:-/home/crazat/miniforge3/envs/genesis-md/bin/python3.11}
# nvidia-smi memory.free is a WSL2 ARTIFACT under boltz load (process-enum breaks -> stale low high-water,
# under-reports real free by ~13GB: 2026-06-12 nvidia-smi 456MiB vs driver 13585MiB while healthy). Driver-
# authoritative free via torch.cuda.mem_get_info; called only to CONFIRM right before the VRAM trip (~once
# per 3min) so the artifact can't false-wake the LLM, while real OOM still trips.
gpu_free_real(){ PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "$PYG" -c "import torch;print(int(torch.cuda.mem_get_info()[0]//1024//1024))" 2>/dev/null; }
qlen(){ local n; n=$(grep -c . "$TS/slot_$1.queue" 2>/dev/null); echo "${n:-0}"; }  # grep -c prints 0 on empty/absent; capture ignores exit 1
dfrac_ge(){  # $1=slot $2=percent  -> echo 1 if current tier of slot is >= percent done
  local cur d ni; cur=$(cat "$TS/slot_$1.current" 2>/dev/null)
  [ -z "$cur" ] && { echo 0; return; }
  ni=$(ls "$EXP/denovo_cofold_input_$cur"/*.yaml 2>/dev/null | wc -l)
  d=$(find "$EXP/denovo_${cur}_output" -name 'confidence_*_model_0.json' 2>/dev/null | wc -l)
  { [ "$ni" -gt 0 ] && [ $((d*100)) -ge $(( $2 * ni )) ]; } && echo 1 || echo 0
}

# ---- VALUE probes (2026-07-15) --------------------------------------------------------------------
# Every trip above this line is a LIVENESS alarm: daemon dead, GPU idle, VRAM low, queue drained. None of
# them can see "busy doing worthless work". That blind spot is not hypothetical -- for 35 days the whole
# stack looked perfect on every monitored dimension while phase3_labels.csv sat at a Jun-10 snapshot, so
# every ROI layer judged from stale evidence, P1's sufficiency was frozen, and 93% of GPU tiers went to
# already-pinned molecules. Nothing woke the LLM because nothing was DOWN. Unmanned-by-design became
# value-blind. These two probes put the LLM back in the loop on the axis no mechanical layer can judge.
LEDGER_STATE=$SD/paper_claim_ledger_state.json
LABELS=$EXP/phase3_labels.csv
MISACK=$TS/MISALLOC_ACK          # touch to acknowledge a known/accepted misallocation (stops re-waking)
# sweetspot_ledger_loop re-runs the aggregators every ~25 min, so >3h stale means the chain
# (phase2_score_sigma -> phase3_build_labels) is severed. Only meaningful while that loop is RUNNING:
# a paused/SIGSTOPped stack is expected to go stale and must not wake anyone.
sweet_running(){ local p st; for p in $(pgrep -f '[s]weetspot_ledger_loop.sh' 2>/dev/null); do
    st=$(ps -o stat= -p "$p" 2>/dev/null | tr -d ' '); case "$st" in T*|"") ;; *) return 0;; esac; done; return 1; }
evidence_age_h(){ local m n; m=$(stat -c %Y "$LABELS" 2>/dev/null) || { echo 999; return; }
    n=$(date +%s); echo $(( (n - m) / 3600 )); }
misallocated(){ [ ! -f "$MISACK" ] && grep -q '"floor_is_low_mv": true' "$LEDGER_STATE" 2>/dev/null; }
# IDLE_BY_DESIGN silences the liveness trips, and that is correct when there is genuinely nothing worth
# computing -- but it cannot tell "idle because no valuable work exists" from "idle because the thing that
# MAKES valuable work is broken". On 2026-07-15 one malformed seed (a radical `[C]`) aborted every
# generation round; generation is the GPU's only work source now, so the GPU sat idle for hours and the
# watcher stayed silent because idle looked intentional. Starvation = idle-by-design AND no fresh work
# arriving AND no generation round running to produce any. That is a fault, not a resting state.
GENLOG=$SD/run_generation_round.log
gen_running(){ pgrep -f '[r]un_generation_round.sh' >/dev/null 2>&1; }
gen_last_failed(){ tail -5 "$GENLOG" 2>/dev/null | grep -q "produced no manifest"; }
starving(){ [ -f "$TS/IDLE_BY_DESIGN" ] && [ "$(boltz_n)" -eq 0 ] && ! gen_running; }
c_sup=0; c_vwd=0; c_boltz=0; c_vram=0; c_idle=0; c_xtb=0; c_evi=0; c_mis=0; c_starve=0
trip(){ echo "WATCHER-WAKE $(TZ=Asia/Seoul date '+%F %T') :: $1"; echo "snapshot: sup=$(pc gpu_roi_supervisor 'bash gpu_roi_supervisor.sh') vwd=$(pc gpu_vram_watchdog 'bash gpu_vram_watchdog.sh') boltz=$(boltz_n) xtb=$(xtb_n) gpu_util=$(gpu_util)% free=$(gpu_free)MiB qE=$(qlen E) qF=$(qlen F)"; exit 0; }

echo "[$(TZ=Asia/Seoul date '+%F %T')] autonomous_watcher START (check ${CHECK_S}s, event-driven; exits-on-anomaly to wake LLM)"
while true; do
  sup=$(pc gpu_roi_supervisor 'bash gpu_roi_supervisor.sh')
  vwd=$(pc gpu_vram_watchdog 'bash gpu_vram_watchdog.sh')
  bz=$(boltz_n); xt=$(xtb_n); gu=$(gpu_util); gf=$(gpu_free)

  [ "$sup" = 1 ] && c_sup=0 || c_sup=$((c_sup+1))
  [ "$vwd" = 1 ] && c_vwd=0 || c_vwd=$((c_vwd+1))
  if [ -f "$TS/GPU_PAUSED" ]; then
    c_sup=0; c_vwd=0; c_boltz=0; c_vram=0; c_idle=0   # GPU intentionally PAUSED (user directive) -> hold ALL
                                    # GPU-stack counters (supervisor/vram_watchdog/boltz/util/VRAM) so the
                                    # intentionally-absent GPU stack doesn't false-wake the LLM during a pause.
                                    # The exploit FLOOR (c_xtb / feeder, below) is still watched while paused.
  elif [ -f "$TS/IDLE_BY_DESIGN" ]; then
    # tier_planner deliberately queued NOTHING: 0 candidates are below phase14's precision target, so an
    # idle GPU is the CORRECT state (2026-07-15). The old never-idle filler re-cofolded a library already
    # at ~9x the sample target -- ~440W for no claim value. Hold the activity counters; VRAM and daemon
    # liveness stay watched. The planner clears this flag as soon as real (generation) work is queued.
    c_boltz=0; c_idle=0
    { [ -n "$gf" ] && [ "$gf" -lt 6000 ]; } && c_vram=$((c_vram+1)) || c_vram=0
  else
    { [ -n "$bz" ] && [ "$bz" -ge 1 ]; } && c_boltz=0 || c_boltz=$((c_boltz+1))
    { [ -n "$gf" ] && [ "$gf" -lt 6000 ]; } && c_vram=$((c_vram+1)) || c_vram=0
    { [ -n "$gu" ] && [ "$gu" -eq 0 ]; } && c_idle=$((c_idle+1)) || c_idle=0
  fi
  # Floor health = the sigma_E FEEDER daemon is alive. The floor is GPU-rate-limited (gating is faster
  # than cofold), so instantaneous xtb=0 between bursts is NORMAL, not a failure. Wake only if the feeder
  # itself dies (then new cofolded tiers stop getting gated). FLOOR_IDLE_OK remains a manual escape hatch.
  fd=$(pgrep -f '[f]loor_sigma_feeder.sh' | wc -l)
  if [ -f "$TS/FLOOR_IDLE_OK" ]; then
    c_xtb=0
  else
    { [ "$fd" -ge 1 ]; } && c_xtb=0 || c_xtb=$((c_xtb+1))
  fi

  [ $c_sup   -ge 3 ]  && trip "supervisor count=$sup (expected 1) -> queue-rotation stack down/duplicated"
  [ $c_vwd   -ge 3 ]  && trip "vram_watchdog count=$vwd (expected 1) -> OOM hard-backstop GONE"
  [ $c_boltz -ge 6 ]  && trip "boltz<1 sustained (~4.5min) -> GPU explore stalled, supervisor not relaunching"
  if [ $c_vram -ge 4 ]; then
    # nvidia-smi has shown <6000 for ~3min -> CONFIRM with driver real free before waking (WSL2 artifact guard).
    rf=$(gpu_free_real)
    if [ -n "$rf" ] && [ "$rf" -lt 6000 ]; then
      trip "REAL VRAM free=${rf}MiB (nvidia-smi ${gf}) <6000 sustained -> genuine OOM pressure; reduce max_parallel"
    else
      c_vram=0   # WSL2 nvidia-smi artifact (driver real_free ${rf}MiB OK) -> reset, no false wake
    fi
  fi
  [ $c_idle  -ge 8 ]  && trip "GPU util 0% sustained (~6min) -> explore idle"
  [ $c_xtb   -ge 10 ] && trip "sigma_E feeder dead (~7.5min) -> exploit floor no longer self-gating new tiers; relaunch floor_sigma_feeder.sh"

  # VALUE trips: the stack can be 100% healthy and still be producing nothing that moves a claim.
  if sweet_running; then
    { [ "$(evidence_age_h)" -ge 3 ]; } && c_evi=$((c_evi+1)) || c_evi=0
  else
    c_evi=0   # loop paused/stopped -> stale evidence is expected, not a fault
  fi
  misallocated && c_mis=$((c_mis+1)) || c_mis=0
  { [ ! -f "$TS/GPU_PAUSED" ] && starving; } && c_starve=$((c_starve+1)) || c_starve=0
  [ $c_evi -ge 4 ]   && trip "EVIDENCE STALE: phase3_labels.csv is $(evidence_age_h)h old while sweetspot_ledger_loop is running -> the aggregator chain (phase2_score_sigma -> phase3_build_labels) is severed; every ROI layer is deciding from a stale snapshot (this is the 35-day failure of 2026-07-15)"
  [ $c_mis -ge 80 ]  && trip "LEDGER MISALLOCATION sustained (~1h): floor_is_low_mv=true -> compute is serving a claim far below the top-MV claim. Re-allocate, or 'touch tier_state/MISALLOC_ACK' to accept it."
  [ $c_starve -ge 27 ] && trip "GPU STARVED (~20min): idle-by-design AND boltz=0 AND no generation round running -> the work SOURCE is broken, not merely exhausted. $(gen_last_failed && echo 'last gen round logged \"produced no manifest\" -- check run_generation_round.log' || echo 'no gen round was even triggered -- check tier_planner/trigger_generation_round')"

  # Empty queues are EXPECTED under IDLE_BY_DESIGN (planner has no precision-buying work to queue), so
  # this drain trip only means "planner refill FAILING" when idle is not the intended state.
  if [ ! -f "$TS/GPU_PAUSED" ] && [ ! -f "$TS/IDLE_BY_DESIGN" ] && [ "$(qlen E)" -eq 0 ] && [ "$(qlen F)" -eq 0 ] && [ "$(dfrac_ge E 95)" = 1 ] && [ "$(dfrac_ge F 95)" = 1 ]; then
    trip "both slot queues empty AND both tiers >=95% done -> planner refill failing, double-drain idle imminent"
  fi

  [ $((SECONDS-START)) -ge $SELF_REFRESH_S ] && trip "6h self-refresh heartbeat (healthy; just relaunch me)"
  sleep "$CHECK_S"
done
