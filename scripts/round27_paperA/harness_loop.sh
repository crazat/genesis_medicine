#!/usr/bin/env bash
# harness_loop.sh (R15) — the daemon that runs the opportunity harness: SCAN -> TRIAGE -> PURSUE.
#
# WHAT IT ADDS THAT THE OTHER FIVE DAEMONS DO NOT
# The existing stack can allocate compute optimally within a FIXED set of claims, and cannot produce a new
# one. This loop is the explore arm in hypothesis space: every SCAN_PERIOD it sweeps the live artifacts for
# structure no current claim covers, and every LOOP_S it advances exactly one confirmation step of the one
# committed pursuit. One step per tick is deliberate -- it bounds the runtime of any single invocation, so
# the daemon can never wedge, and it keeps the pursuit alive across ticks, which is the whole point (no
# other layer in this stack can hold a thread of inquiry longer than its own timer).
#
# RESOURCE CONTRACT: pure CPU, EXPLORE cores only, nice 15, OMP_NUM_THREADS=1, CUDA hidden. It reads the
# core split from tier_state/core_split.active rather than hardcoding 19-23, so it composes with phase15's
# actuator instead of fighting it. It never kills a process, never queues GPU work, never touches the
# exploit floor, never writes to an existing CSV. `touch tier_state/harness/HARNESS_OFF` stops all of it.
#
# LAUNCH: MUST be `bash harness_loop.sh` from $SD -- `./harness_loop.sh` or an absolute path breaks the
# watcher's pc() prefix match and reads as a dead daemon (the 2026-08-02 canonical-cmdline rule).
set -u
SD=/home/crazat/genesis_medicine/scripts/round27_paperA
TS=$SD/tier_state
HS=$TS/harness
PY=/home/crazat/genesis_medicine/.venv/bin/python
LOG=$SD/harness_loop.log
HB=$HS/heartbeat
LOCK=$HS/loop.lock
LOOP_S=${LOOP_S:-900}
SCAN_PERIOD=${SCAN_PERIOD:-3600}
mkdir -p "$HS"

export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES=""

log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }

# single-flight: a stale lock from a killed loop must not block the relaunch forever, so the lock carries a
# PID and is only honoured while that PID is alive and is actually a harness_loop.
if [ -f "$LOCK" ]; then
  old=$(cat "$LOCK" 2>/dev/null)
  if [ -n "$old" ] && [ -d "/proc/$old" ] && tr '\0' ' ' < "/proc/$old/cmdline" 2>/dev/null | grep -q 'harness_loop.sh'; then
    log "another harness_loop is alive (pid $old) -> exiting, refusing to duplicate"
    exit 0
  fi
  log "stale lock from pid ${old:-?} cleared"
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

cores(){ sed -n 's/.*EXPLORE=\([0-9-]*\).*/\1/p' "$TS/core_split.active" 2>/dev/null | head -1; }

log "harness_loop START (loop ${LOOP_S}s, scan ${SCAN_PERIOD}s, explore cores $(cores))"
last_scan=0
while true; do
  if [ -f "$HS/HARNESS_OFF" ]; then
    echo "$(date +%s) OFF" > "$HB"
    sleep "$LOOP_S"; continue
  fi
  C=$(cores); C=${C:-19-23}
  now=$(date +%s)

  if [ $((now - last_scan)) -ge "$SCAN_PERIOD" ]; then
    if out=$(nice -n 15 taskset -c "$C" "$PY" "$SD/harness/harness_scan.py" 2>&1); then
      log "SCAN ok :: $(echo "$out" | head -1)"
      last_scan=$now
    else
      # a failed scan is LOUD: the heartbeat records it and the watcher's harness trip fires if it persists,
      # because a silently empty scan reads exactly like "there is nothing to find" (this is the 35-day
      # stale-aggregator failure mode, and it must not be reproduced in the new layer).
      log "SCAN FAILED :: $(echo "$out" | tail -3 | tr '\n' ' ')"
      echo "$(date +%s) SCAN_FAILED" > "$HB"
    fi
  fi

  if out=$(nice -n 15 taskset -c "$C" "$PY" "$SD/harness/harness_ledger.py" 2>&1); then
    log "LEDGER :: $(echo "$out" | head -1)"
    echo "$(date +%s) OK $(echo "$out" | head -1)" > "$HB"
  else
    log "LEDGER FAILED :: $(echo "$out" | tail -3 | tr '\n' ' ')"
    echo "$(date +%s) LEDGER_FAILED" > "$HB"
  fi

  sleep "$LOOP_S"
done
