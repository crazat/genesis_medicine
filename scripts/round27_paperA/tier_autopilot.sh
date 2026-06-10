#!/usr/bin/env bash
# tier_autopilot.sh (R10) — runs tier_planner.py on lead-time so each GPU slot's tier queue stays full.
# This is the daemon that makes the queue-driven supervisor self-sustaining: every ~10 min it lets the
# planner (driven by phase8's sweet-spot verdict) build & queue the next ACQUISITION or GENERATION tier
# BEFORE the current one traps, so the supervisor's mechanical rotation always has somewhere to go.
# Pure CPU, cores 19-23 nice 15, CUDA hidden => GPU 2-explore + exploit cores 0-18 untouched. If this
# daemon dies, NO compute is lost (the running boltz tiers continue; only queue-refill pauses) -> not on
# the critical-survival list, but relaunch keeps the loop autonomous.
PY=/home/crazat/genesis_medicine/.venv/bin/python
PLANNER=/home/crazat/genesis_medicine/scripts/round27_paperA/tier_planner.py
export CUDA_VISIBLE_DEVICES=""
while true; do
  nice -n 15 taskset -c 19-23 "$PY" "$PLANNER" >/dev/null 2>&1
  sleep 600
done
