#!/usr/bin/env bash
# sweetspot_ledger_loop.sh (R8) — continuously compute the EXPLOIT/EXPLORE sweet spot.
# Runs phase8_sweetspot_controller.py every ~25 min so the shadow price lambda, cost-cooling alpha, and
# the over-greed flag accumulate a time series (phase8_sweetspot.log) instead of being a one-shot check.
# ADVISORY ONLY: it logs the recommendation; it never moves cores or kills anything. If this daemon dies,
# ZERO compute is lost (the real exploit/explore work runs in the sigma-matrix + gpu_roi_supervisor
# daemons). Pure-CPU, cores 19-23, nice 15 -> never touches exploit cores 0-18 or the GPU.
PY=/home/crazat/genesis_medicine/.venv/bin/python
CTRL=/home/crazat/genesis_medicine/scripts/round27_paperA/phase8_sweetspot_controller.py
while true; do
  taskset -c 19-23 nice -n 15 "$PY" "$CTRL" >/dev/null 2>&1
  sleep 1500
done
