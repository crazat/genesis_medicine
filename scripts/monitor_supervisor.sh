#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
LOG="$ROOT/pilot/monitor_supervisor.log"
STATUS="$ROOT/pilot/monitor_status_latest.txt"
LOCK="/tmp/genesis_monitor_supervisor.lock"
TRIGGER="/tmp/genesis_monitor_enabled"
QUEUE_TRIGGER="/tmp/genesis_auto_queue_enabled"
CURATOR_TRIGGER="/tmp/genesis_codex_curator_enabled"
DRAIN="$ROOT/pilot/QUEUE_DRAIN_MODE"

mkdir -p "$ROOT/pilot"
cd "$ROOT"
if [[ -f "$DRAIN" ]]; then
  printf '[%s] monitor supervisor not started: QUEUE_DRAIN_MODE present\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi
touch "$TRIGGER" "$QUEUE_TRIGGER" "$CURATOR_TRIGGER"

exec 8>"$LOCK"
if ! flock -n 8; then
  printf '[%s] monitor supervisor already running; exiting duplicate\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"
}

queue_daemon_count() {
  pgrep -fc "auto_queue_cpu_gpu_daemon.sh" || true
}

curator_loop_count() {
  pgrep -fc "codex_curator_loop.sh" || true
}

start_queue_daemon() {
  log "queue daemon missing; starting scripts/auto_queue_cpu_gpu_daemon.sh"
  nohup setsid bash -lc "exec 8>&-; cd '$ROOT' && exec scripts/auto_queue_cpu_gpu_daemon.sh" \
    > "$ROOT/pilot/auto_queue_cpu_gpu_daemon.outer.log" 2>&1 < /dev/null &
  log "queue daemon pid=$!"
}

start_curator_loop() {
  log "codex curator missing; starting scripts/codex_curator_loop.sh"
  nohup setsid bash -lc "exec 8>&-; cd '$ROOT' && exec scripts/codex_curator_loop.sh" \
    > "$ROOT/pilot/codex_curator_loop.outer.log" 2>&1 < /dev/null &
  log "codex curator pid=$!"
}

write_status() {
  {
    printf 'timestamp=%s\n' "$(date -Is)"
    printf 'uptime='
    uptime
    printf '\n[gpu]\n'
    nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv || true
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader || true
    printf '\n[cpu]\n'
    vmstat 1 2 || true
    printf '\n[queue]\n'
    pgrep -af "auto_queue_cpu_gpu_daemon|codex_curator_loop|run_r16_chromanol_topical|cpu_xtb_npass_top_refine.py|cpu_5000" || true
    printf '\n[curator]\n'
    ls -l "$ROOT/pilot/codex_curator_decision.md" "$ROOT/pilot/codex_curator_last.md" "$ROOT/pilot/codex_curator_context.md" 2>/dev/null || true
    tail -n 40 "$ROOT/pilot/codex_curator_actions.log" 2>/dev/null || true
    printf '\n[latest-md]\n'
    find pilot -maxdepth 2 -path '*md*' -name 'summary.json' -printf '%TY-%Tm-%Td %TH:%TM %p\n' 2>/dev/null | sort | tail -12 || true
    printf '\n[latest-xtb]\n'
    ls -lt pilot/cpu_meaningful/xtb_npass_top*_refine_*conf.csv 2>/dev/null | head -12 || true
  } > "$STATUS.tmp"
  mv "$STATUS.tmp" "$STATUS"
  python3 "$ROOT/scripts/write_live_status_report.py" \
    > "$ROOT/pilot/live_status_reporter.log" 2>&1 || true
}

log "monitor supervisor start"
while [[ -f "$TRIGGER" && ! -f "$DRAIN" ]]; do
  if [[ "$(queue_daemon_count)" -eq 0 ]]; then
    start_queue_daemon
  fi
  if [[ "$(curator_loop_count)" -eq 0 ]]; then
    start_curator_loop
  fi
  write_status
  (exec 8>&-; sleep 120)
done
if [[ -f "$DRAIN" ]]; then
  log "monitor supervisor stopped: QUEUE_DRAIN_MODE present"
else
  log "monitor supervisor stopped: trigger removed"
fi
