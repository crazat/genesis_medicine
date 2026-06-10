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

pc(){ local n=0 p; for p in $(pgrep -f "$1" 2>/dev/null); do tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | grep -q "^$2" && n=$((n+1)); done; echo $n; }
boltz_n(){ pgrep -f '[b]oltz predict' 2>/dev/null | wc -l; }
xtb_n(){ local n; n=$(pgrep -fc '[/]bin/xtb ' 2>/dev/null); echo "${n:-0}"; }   # capture: pgrep -fc exits 1 at 0 matches but still prints "0"
gpu_util(){ nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | tr -d ' '; }
gpu_free(){ nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | tr -d ' '; }
qlen(){ local n; n=$(grep -c . "$TS/slot_$1.queue" 2>/dev/null); echo "${n:-0}"; }  # grep -c prints 0 on empty/absent; capture ignores exit 1
dfrac_ge(){  # $1=slot $2=percent  -> echo 1 if current tier of slot is >= percent done
  local cur d ni; cur=$(cat "$TS/slot_$1.current" 2>/dev/null)
  [ -z "$cur" ] && { echo 0; return; }
  ni=$(ls "$EXP/denovo_cofold_input_$cur"/*.yaml 2>/dev/null | wc -l)
  d=$(find "$EXP/denovo_${cur}_output" -name 'confidence_*_model_0.json' 2>/dev/null | wc -l)
  { [ "$ni" -gt 0 ] && [ $((d*100)) -ge $(( $2 * ni )) ]; } && echo 1 || echo 0
}

c_sup=0; c_vwd=0; c_boltz=0; c_vram=0; c_idle=0; c_xtb=0
trip(){ echo "WATCHER-WAKE $(TZ=Asia/Seoul date '+%F %T') :: $1"; echo "snapshot: sup=$(pc gpu_roi_supervisor 'bash gpu_roi_supervisor.sh') vwd=$(pc gpu_vram_watchdog 'bash gpu_vram_watchdog.sh') boltz=$(boltz_n) xtb=$(xtb_n) gpu_util=$(gpu_util)% free=$(gpu_free)MiB qE=$(qlen E) qF=$(qlen F)"; exit 0; }

echo "[$(TZ=Asia/Seoul date '+%F %T')] autonomous_watcher START (check ${CHECK_S}s, event-driven; exits-on-anomaly to wake LLM)"
while true; do
  sup=$(pc gpu_roi_supervisor 'bash gpu_roi_supervisor.sh')
  vwd=$(pc gpu_vram_watchdog 'bash gpu_vram_watchdog.sh')
  bz=$(boltz_n); xt=$(xtb_n); gu=$(gpu_util); gf=$(gpu_free)

  [ "$sup" = 1 ] && c_sup=0 || c_sup=$((c_sup+1))
  [ "$vwd" = 1 ] && c_vwd=0 || c_vwd=$((c_vwd+1))
  { [ -n "$bz" ] && [ "$bz" -ge 1 ]; } && c_boltz=0 || c_boltz=$((c_boltz+1))
  { [ -n "$gf" ] && [ "$gf" -lt 6000 ]; } && c_vram=$((c_vram+1)) || c_vram=0
  { [ -n "$gu" ] && [ "$gu" -eq 0 ]; } && c_idle=$((c_idle+1)) || c_idle=0
  { [ -n "$xt" ] && [ "$xt" -ge 1 ]; } && c_xtb=0 || c_xtb=$((c_xtb+1))

  [ $c_sup   -ge 3 ]  && trip "supervisor count=$sup (expected 1) -> queue-rotation stack down/duplicated"
  [ $c_vwd   -ge 3 ]  && trip "vram_watchdog count=$vwd (expected 1) -> OOM hard-backstop GONE"
  [ $c_boltz -ge 6 ]  && trip "boltz<1 sustained (~4.5min) -> GPU explore stalled, supervisor not relaunching"
  [ $c_vram  -ge 4 ]  && trip "VRAM free=${gf}MiB <6000 sustained (~3min) -> kill-loop watchdog not coping; reduce max_parallel"
  [ $c_idle  -ge 8 ]  && trip "GPU util 0% sustained (~6min) -> explore idle"
  [ $c_xtb   -ge 10 ] && trip "xtb=0 sustained (~7.5min) -> exploit CPU floor (de novo sigma_E) died"

  if [ "$(qlen E)" -eq 0 ] && [ "$(qlen F)" -eq 0 ] && [ "$(dfrac_ge E 95)" = 1 ] && [ "$(dfrac_ge F 95)" = 1 ]; then
    trip "both slot queues empty AND both tiers >=95% done -> planner refill failing, double-drain idle imminent"
  fi

  [ $((SECONDS-START)) -ge $SELF_REFRESH_S ] && trip "6h self-refresh heartbeat (healthy; just relaunch me)"
  sleep "$CHECK_S"
done
