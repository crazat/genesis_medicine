#!/usr/bin/env bash
# sweetspot_ledger_loop.sh (R8) — continuously compute the EXPLOIT/EXPLORE sweet spot.
# Runs phase8_sweetspot_controller.py every ~25 min so the shadow price lambda, cost-cooling alpha, and
# the over-greed flag accumulate a time series (phase8_sweetspot.log) instead of being a one-shot check.
# ADVISORY ONLY: it logs the recommendation; it never moves cores or kills anything. If this daemon dies,
# ZERO compute is lost (the real exploit/explore work runs in the sigma-matrix + gpu_roi_supervisor
# daemons). Pure-CPU, cores 19-23, nice 15 -> never touches exploit cores 0-18 or the GPU.
PY=/home/crazat/genesis_medicine/.venv/bin/python
SD=/home/crazat/genesis_medicine/scripts/round27_paperA
EXP=/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1
CTRL=$SD/phase8_sweetspot_controller.py            # RESOURCE allocator (lambda/alpha/verdict)
LEDGER=$SD/paper_claim_ledger.py                   # R12 DELIVERABLE-value layer (which CLAIM)
PORTFOLIO=$SD/phase10_portfolio_risk.py            # R13 PORTFOLIO/correlated-failure layer (claim SET)
# R13 ①-④ advisory diagnostics (explore-side; opt-in hooks; default off; never move compute):
ADGATE=$EXP/phase11_admet_ad_gate.py               # ① DyRAMO applicability-domain (must run before IDS)
LFHF=$EXP/phase12_lf_hf_correlation.py             # ② multi-fidelity LF<->HF correlation gate
IDS=$EXP/phase13_ids_toptwo.py                     # ③ Information-Directed Top-Two explore selector
REPLCI=$EXP/phase14_replicate_sigma_ci.py          # ④ REPLICATE sigma-CI relative-precision stop
ACTUATOR=$SD/phase15_actuator.py                   # ⑤ dynamic core re-partition (SHADOW unless ARMED flag)
# FEEDBACK AGGREGATORS (added 2026-07-15) -- these turn raw compute output into the evidence every layer
# below reads. NOTHING ran them: phase3_labels.csv sat at 567 rows / Jun 10 for 35 days while the GPU wrote
# 17,779 confidence JSONs and the floor sigma-gated 3,977 candidates. Every "intelligent" layer was reading
# a Jun-10 snapshot, so P1's sufficiency (= f(n_labels)) was FROZEN at 0.52 no matter how much compute ran
# -- the producers and the decision layers were physically disconnected. One manual run recovered +3,432
# candidates (2,095 of them generated) and moved P1 0.52 -> 0.65. They must run BEFORE the readers.
SCORE=$EXP/phase2_score_sigma.py                   # boltz confidence JSONs -> phase2_reliability_ranked.csv
BUILDLABELS=$EXP/phase3_build_labels.py            # sigma_iptm x sigma_E  -> phase3_labels.csv
while true; do
  # 0) refresh the evidence FIRST (CUDA hidden: pure-CPU, must never touch the GPU explore slots)
  CUDA_VISIBLE_DEVICES="" taskset -c 19-23 nice -n 15 "$PY" "$SCORE"       >/dev/null 2>&1
  CUDA_VISIBLE_DEVICES="" taskset -c 19-23 nice -n 15 "$PY" "$BUILDLABELS" >/dev/null 2>&1
  # advisory layers each tick (all pure-CPU, cores 19-23, nice 15; never move compute):
  #   resource (phase8) -> claim (ledger) -> portfolio (phase10) -> explore diagnostics (11->12->13->14).
  #   phase13(IDS) reads phase11(AD) output, so phase11 runs first. Each guarded; a failure can't block.
  taskset -c 19-23 nice -n 15 "$PY" "$CTRL"      >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$LEDGER"    >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$PORTFOLIO" >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$ADGATE"    >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$LFHF"      >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$IDS"       >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$REPLCI"    >/dev/null 2>&1
  taskset -c 19-23 nice -n 15 "$PY" "$ACTUATOR"  >/dev/null 2>&1   # reads ⑤ inputs above; SHADOW unless armed
  sleep 1500
done
