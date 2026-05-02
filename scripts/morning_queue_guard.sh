#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
LOG="$ROOT/pilot/morning_queue_guard.log"
LOCK="/tmp/genesis_morning_queue_guard.lock"
TRIGGER="/tmp/genesis_morning_queue_guard_enabled"
MONITOR_TRIGGER="/tmp/genesis_monitor_enabled"
QUEUE_TRIGGER="/tmp/genesis_auto_queue_enabled"
CURATOR_TRIGGER="/tmp/genesis_codex_curator_enabled"
DRAIN="$ROOT/pilot/QUEUE_DRAIN_MODE"

mkdir -p "$ROOT/pilot"
cd "$ROOT"
if [[ -f "$DRAIN" ]]; then
  printf '[%s] morning queue guard not started: QUEUE_DRAIN_MODE present\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi
touch "$TRIGGER" "$MONITOR_TRIGGER" "$QUEUE_TRIGGER" "$CURATOR_TRIGGER"

exec 6>"$LOCK"
if ! flock -n 6; then
  printf '[%s] morning guard already running; exiting duplicate\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"
}

deadline_epoch() {
  if [[ -n "${GENESIS_GUARD_UNTIL:-}" ]]; then
    date -d "$GENESIS_GUARD_UNTIL" +%s
    return
  fi

  local today target now
  today="$(date +%F)"
  target="$(date -d "$today 10:30:00" +%s)"
  now="$(date +%s)"
  if [[ "$target" -le "$now" ]]; then
    target="$(date -d "tomorrow 10:30:00" +%s)"
  fi
  printf '%s\n' "$target"
}

monitor_count() {
  pgrep -fc "scripts/monitor_supervisor.sh" || true
}

queue_count() {
  pgrep -fc "scripts/auto_queue_cpu_gpu_daemon.sh" || true
}

curator_count() {
  pgrep -fc "scripts/codex_curator_loop.sh" || true
}

cpu_idle_pct() {
  vmstat 1 2 2>/dev/null | tail -1 | awk '{if (NF >= 15) print int($15); else print 0}'
}

start_monitor() {
  log "monitor supervisor missing; starting"
  nohup setsid bash -lc "exec 6>&-; cd '$ROOT' && exec scripts/monitor_supervisor.sh" \
    > "$ROOT/pilot/monitor_supervisor.outer.log" 2>&1 < /dev/null &
  log "monitor supervisor pid=$!"
}

start_queue() {
  log "auto queue daemon missing; starting"
  nohup setsid bash -lc "exec 6>&-; cd '$ROOT' && exec scripts/auto_queue_cpu_gpu_daemon.sh" \
    > "$ROOT/pilot/auto_queue_cpu_gpu_daemon.outer.log" 2>&1 < /dev/null &
  log "auto queue daemon pid=$!"
}

start_curator() {
  log "codex curator loop missing; starting"
  nohup setsid bash -lc "exec 6>&-; cd '$ROOT' && exec scripts/codex_curator_loop.sh" \
    > "$ROOT/pilot/codex_curator_loop.outer.log" 2>&1 < /dev/null &
  log "codex curator loop pid=$!"
}

heartbeat() {
  local idle cpu_task
  idle="$(cpu_idle_pct)"
  cpu_task="$(python3 scripts/auto_result_planner.py --slot cpu --field task 2>/dev/null || echo unknown)"
  {
    printf '\n[%s] heartbeat deadline=%s\n' "$(date -Is)" "$(date -d "@$DEADLINE" -Is)"
    printf '[gpu]\n'
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv || true
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader || true
    printf '[cpu]\n'
    uptime || true
    ps aux --sort=-%cpu | head -8 || true
    printf '[loops]\n'
    pgrep -af "monitor_supervisor|auto_queue_cpu_gpu_daemon|codex_curator_loop|run_r16|run_r15|cpu_xtb_npass_top_refine|cpu_5000" | head -80 || true
    printf '[planner]\n'
    python3 scripts/auto_result_planner.py --slot all --field json || true
    if [[ "$cpu_task" == "none" && "$idle" =~ ^[0-9]+$ && "$idle" -ge 55 ]]; then
      printf '[cpu-idle-gap]\n'
      printf 'idle=%s%% planner_cpu_task=none\n' "$idle"
    fi
  } >> "$LOG" 2>&1
  python3 "$ROOT/scripts/write_live_status_report.py" \
    > "$ROOT/pilot/live_status_reporter.log" 2>&1 || true
}

DEADLINE="$(deadline_epoch)"
log "morning queue guard start until $(date -d "@$DEADLINE" -Is)"

while [[ -f "$TRIGGER" && ! -f "$DRAIN" && "$(date +%s)" -lt "$DEADLINE" ]]; do
  touch "$MONITOR_TRIGGER" "$QUEUE_TRIGGER" "$CURATOR_TRIGGER"
  if [[ "$(monitor_count)" -eq 0 ]]; then
    start_monitor
  fi
  if [[ "$(queue_count)" -eq 0 ]]; then
    start_queue
  fi
  if [[ "$(curator_count)" -eq 0 ]]; then
    start_curator
  fi
  heartbeat
  (exec 6>&-; sleep 300)
done

if [[ -f "$DRAIN" ]]; then
  log "morning queue guard stopped: QUEUE_DRAIN_MODE present"
else
  log "morning queue guard finished; compute loops left running"
fi
