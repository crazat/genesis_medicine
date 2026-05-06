#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/crazat/genesis_medicine"
VENV_PY="$ROOT/.venv/bin/python"
GENESIS_MD_PY="/home/crazat/miniforge3/envs/genesis-md/bin/python"
LOG="$ROOT/pilot/auto_queue_cpu_gpu_daemon.log"
LOCK="/tmp/genesis_auto_queue_cpu_gpu_daemon_v3.lock"
TRIGGER="/tmp/genesis_auto_queue_enabled"
DRAIN="$ROOT/pilot/QUEUE_DRAIN_MODE"
CPU_IDLE_FORCE_THRESHOLD="${GENESIS_CPU_IDLE_FORCE_THRESHOLD:-35}"
CPU_IDLE_ALERT_THRESHOLD="${GENESIS_CPU_IDLE_ALERT_THRESHOLD:-55}"
CPU_REFINE_PROCESS_CAP="${GENESIS_CPU_REFINE_PROCESS_CAP:-39}"
CPU_GPU_BUSY_IDLE_FLOOR="${GENESIS_CPU_GPU_BUSY_IDLE_FLOOR:-25}"

export PATH="/usr/lib/wsl/lib:${PATH}"

mkdir -p "$ROOT/pilot"
cd "$ROOT"
if [[ -f "$DRAIN" ]]; then
  printf '[%s] auto queue daemon not started: QUEUE_DRAIN_MODE present\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi
touch "$TRIGGER"

exec 9>"$LOCK"
if ! flock -n 9; then
  printf '[%s] daemon already running; exiting duplicate\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"
}

active_gpu_jobs() {
  local project_count gpu_app_count
  project_count="$(pgrep -fc "run_r16_chromanol_.*\\.py|run_r17_chromanol_.*\\.py|run_extended_30ns|run_r15_chromanol|boltz predict" || true)"
  gpu_app_count="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | awk '$1 ~ /^[0-9]+$/ {n++} END {print n+0}')"
  if [[ "$project_count" -gt 0 ]]; then
    printf '%s\n' "$project_count"
  elif [[ "$gpu_app_count" -gt 0 ]]; then
    printf '%s\n' "$gpu_app_count"
  else
    printf '0\n'
  fi
}

gpu_task_running() {
  local script="$1"
  pgrep -f -- "$script" >/dev/null
}

active_cpu_refines() {
  pgrep -fc "scripts/cpu_xtb_npass_top_refine.py" || true
}

cpu_idle_pct() {
  vmstat 1 2 2>/dev/null | tail -1 | awk '{if (NF >= 15) print int($15); else print 0}'
}

cpu_task_running() {
  local out="$1"
  pgrep -f -- "scripts/cpu_xtb_npass_top_refine.py .*--out $out" >/dev/null
}

summary_all_ok() {
  local path="$1"
  local expected="$2"
  python3 - "$path" "$expected" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected = int(sys.argv[2])
if not path.exists():
    raise SystemExit(1)
try:
    rows = json.loads(path.read_text())
except Exception:
    raise SystemExit(1)
ok = [r for r in rows if r.get("status") == "ok"]
raise SystemExit(0 if len(ok) >= expected else 1)
PY
}

start_gpu_task() {
  local name="$1"
  local script="$2"
  local log_file="$3"
  log "GPU start: $name"
  nohup setsid bash -lc "exec 9>&-; cd '$ROOT' && exec '$GENESIS_MD_PY' -u '$script'" \
    > "$ROOT/$log_file" 2>&1 < /dev/null &
  log "GPU pid=$! name=$name log=$log_file"
}

queue_gpu_if_idle() {
  local active
  active="$(active_gpu_jobs)"
  if [[ "$active" -gt 0 ]]; then
    log "GPU busy by project jobs: $active"
    return 0
  fi

  local task reason script log_file
  task="$("$VENV_PY" scripts/auto_result_planner.py --slot gpu --field task 2>/dev/null || echo none)"
  reason="$("$VENV_PY" scripts/auto_result_planner.py --slot gpu --field reason 2>/dev/null || echo planner unavailable)"
  script="$("$VENV_PY" scripts/auto_result_planner.py --slot gpu --field script 2>/dev/null || echo none)"
  log_file="$("$VENV_PY" scripts/auto_result_planner.py --slot gpu --field log_file 2>/dev/null || echo none)"
  log "GPU planner: task=$task reason=$reason"

  if [[ "$task" != "none" && -n "$script" && "$script" != "none" && -n "$log_file" && "$log_file" != "none" ]]; then
    if [[ ! -f "$ROOT/$script" ]]; then
      log "GPU planner script missing: $script"
      return 0
    fi
    if gpu_task_running "$script"; then
      log "GPU planner task already running: $task script=$script"
      return 0
    fi
    start_gpu_task "$task" "$script" "$log_file"
    return 0
  fi

  log "GPU no pending planner task"
}

start_cpu_refine() {
  local topn="$1"
  local hetero="$2"
  local confs="$3"
  local workers="$4"
  local out="$5"
  local log_file="pilot/${out%.csv}.log"

  if [[ -s "$ROOT/pilot/cpu_meaningful/$out" ]]; then
    return 1
  fi
  if cpu_task_running "$out"; then
    return 1
  fi

  log "CPU start: $out topn=$topn hetero=$hetero confs=$confs workers=$workers"
  nohup setsid bash -lc "exec 9>&-; cd '$ROOT' && exec '$VENV_PY' -u scripts/cpu_xtb_npass_top_refine.py \
    --topn '$topn' \
    --workers '$workers' \
    --num-confs '$confs' \
    --min-hetero-atoms '$hetero' \
    --out '$out'" \
    > "$ROOT/$log_file" 2>&1 < /dev/null &
  log "CPU pid=$! out=$out log=$log_file"
  return 0
}

queue_cpu_if_idle() {
  local active idle gpu_active
  active="$(active_cpu_refines)"
  idle="$(cpu_idle_pct)"
  gpu_active="$(active_gpu_jobs)"
  if ! [[ "$idle" =~ ^[0-9]+$ ]]; then
    idle=0
  fi

  if [[ "$gpu_active" -gt 0 && "$idle" -le "$CPU_GPU_BUSY_IDLE_FLOOR" ]]; then
    log "CPU hold: GPU job active=$gpu_active and CPU idle=${idle}% <= ${CPU_GPU_BUSY_IDLE_FLOOR}%; preserving GPU feeding headroom"
    return 0
  fi

  if [[ "$active" -ge "$CPU_REFINE_PROCESS_CAP" ]]; then
    log "CPU xTB refine process cap reached: active=$active cap=$CPU_REFINE_PROCESS_CAP idle=${idle}%"
    return 0
  fi
  if [[ "$active" -ge 18 ]]; then
    if [[ "$idle" -le "$CPU_IDLE_FORCE_THRESHOLD" ]]; then
      log "CPU xTB refine busy: active=$active idle=${idle}%"
      return 0
    fi
    log "CPU_IDLE_GAP active_refines=$active idle=${idle}% exceeds ${CPU_IDLE_FORCE_THRESHOLD}%; allowing companion task"
  fi
  if [[ "$active" -gt 0 ]]; then
    log "CPU xTB refine partially busy: active=$active idle=${idle}%; checking for companion task"
  fi

  local spec reason topn hetero confs workers out
  spec="$("$VENV_PY" scripts/auto_result_planner.py --slot cpu --field spec 2>/dev/null || echo none)"
  reason="$("$VENV_PY" scripts/auto_result_planner.py --slot cpu --field reason 2>/dev/null || echo planner unavailable)"
  log "CPU planner: spec=$spec reason=$reason idle=${idle}%"
  if [[ "$spec" == "none" || -z "$spec" ]]; then
    if [[ "$idle" -ge "$CPU_IDLE_ALERT_THRESHOLD" ]]; then
      local msg="CPU_IDLE_GAP_UNRESOLVED idle=${idle}% active_refines=$active planner=none"
      log "$msg"
      printf '[%s] %s\n' "$(date -Is)" "$msg" >> "$ROOT/pilot/cpu_idle_gap_alerts.log"
      printf '%s %s\n' "$(date -Is)" "$msg" >> "$ROOT/pilot/codex_curator_actions.log"
    fi
    log "CPU no pending planner task"
    return 0
  fi
  read -r topn hetero confs workers out <<<"$spec"
  if ! start_cpu_refine "$topn" "$hetero" "$confs" "$workers" "$out"; then
    log "CPU planner task could not be started, likely already running or completed: $out"
  fi
}

log "auto queue daemon start"
while [[ -f "$TRIGGER" && ! -f "$DRAIN" ]]; do
  queue_gpu_if_idle
  queue_cpu_if_idle
  (exec 9>&-; sleep 120)
done
if [[ -f "$DRAIN" ]]; then
  log "auto queue daemon stopped: QUEUE_DRAIN_MODE present"
else
  log "auto queue daemon stopped: trigger removed"
fi
