#!/usr/bin/env bash
# GPU ROI SUPERVISOR v3 — MEASURED max-efficiency config. Holds GPU at ~95% (verified) via TWO
# memory-fitted pipelined Boltz slots whose MSA-load gaps cover each other:
#   SLOT-E (EXPLORE) : de novo deep cofold, 100 diffusion samples, cores 19-23  (~19GB VRAM)
#   SLOT-F (FILL)    : reliability cascade,  50 diffusion samples, cores 14-18  (~8GB VRAM)
#   total ~28GB < 32GB  => NO OOM (the v2 over-spawn bug: 2x100=35GB OOM is now impossible here).
#
# STRICT one-boltz-per-slot: a slot is relaunched ONLY when its boltz is absent. Never duplicates.
# Memory ceiling respected by construction (fixed sample counts). xtb sigma_E matrix keeps cores 0-13.
#
# DATA HYGIENE: the 50-sample FILL cascade writes to boltz_15_50_fill_v* (NOT the clean 100-sample
# reliability series boltz_15_100_v19_v*), so paper_B's n-series stays uncontaminated.
#
# HARD RULES: no kill/pkill (launch-only); SIGSTOP/SIGCONT for pause; self-match via brackets;
# setsid-robust; boltz taskset-pinned. PAUSE = kill -STOP this pid.
set -u
SD=/home/crazat/genesis_medicine/scripts/round27_paperA
PILOT=/home/crazat/genesis_medicine/pilot/round27_paperA
EXP=$PILOT/explore_denovo_mmp1
BOLTZ=/home/crazat/miniforge3/envs/genesis-md/bin/boltz
LOG=$SD/gpu_roi_supervisor.log
POLL=${POLL:-30}
log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }

# is a boltz process whose cmdline matches $1 currently alive?
slot_alive(){ for p in $(pgrep -f '[b]oltz predict'); do tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | grep -q "$1" && return 0; done; return 1; }

launch_explore(){   # de novo deep @100, cores 19-23. Rotate round dir so a completed round isn't redone.
  local r=$(( $(for d in $EXP/denovo_deep_output*; do echo "${d##*output}"; done 2>/dev/null | tr -d _r | sort -n | tail -1 ) + 0 ))
  local out="denovo_deep_output"; [ -d "$EXP/$out" ] && out="denovo_deep_output_r$((r+1))"
  cd $EXP
  log "SLOT-E -> de novo deep @100 (cores 19-23) out=$out"
  nohup taskset -c 19-23 $BOLTZ predict denovo_cofold_input \
    --out_dir "$out" --diffusion_samples 100 --use_potentials \
    --output_format pdb --seed 7001 > $EXP/denovo_deep.log 2>&1 &
}

launch_fill(){      # reliability cascade @50 (GPU-fill), cores 14-18, distinct namespace
  local N=$(( $(for d in $PILOT/boltz_15_50_fill_v*; do echo "${d##*_v}"; done 2>/dev/null | sort -n | tail -1) + 1 )); [ "$N" -le 1 ] && N=1
  cd $PILOT
  log "SLOT-F -> cascade @50 fill v${N} (cores 14-18)"
  nohup taskset -c 14-18 $BOLTZ predict boltz_input_v19_msa \
    --out_dir boltz_15_50_fill_v${N} --diffusion_samples 50 --use_potentials \
    --output_format pdb --seed $((N+9000)) > $SD/boltz_fill_v${N}_run.log 2>&1 &
}

log "GPU ROI SUPERVISOR v3 START (SLOT-E de novo@100 19-23 + SLOT-F cascade@50 14-18, ~95% verified, poll ${POLL}s)"
while true; do
  # EXPLORE slot: keep a de novo deep boltz alive (matches denovo_deep_output dirs)
  if ! slot_alive "denovo_deep_output" && ! slot_alive "denovo_cofold_batch_output"; then
     launch_explore; sleep 10
  fi
  # FILL slot: keep a GPU-fill cascade alive (matches either current v421@50 or new fill series)
  if ! slot_alive "boltz_15_100_v19_v" && ! slot_alive "boltz_15_50_fill_v"; then
     launch_fill; sleep 10
  fi
  sleep "$POLL"
done
