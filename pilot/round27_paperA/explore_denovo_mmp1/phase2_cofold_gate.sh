#!/usr/bin/env bash
# Phase2 GPU cofold gate — de novo MMP-1 candidate screening by sigma_iptm.
# Runs Boltz cofold on the top-80 de novo YAMLs at SCREEN_SAMPLES diffusion poses each.
# This COMPETES with the reliability cascade for the GPU, so it is slot-deferred:
# launch it explicitly in a GPU gap (e.g. between cascade cycles), NOT auto-fired here.
#
# 25 samples x 80 cand = 2000 poses (~1.3 reliability-cycle equiv) -> enough for a
# sigma_iptm screen estimate, far cheaper than the 100-sample full reliability runs.
# Affinity daemon (boltz_affinity_pin_19_23_daemon.sh) pins boltz to cores 19-23.
# No kill/pkill. Resumable: completed candidate dirs are skipped.
set -u
EXP=/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1
BOLTZ=/home/crazat/miniforge3/envs/genesis-md/bin/boltz
IN=$EXP/denovo_cofold_input
OUT=$EXP/denovo_cofold_output
LOG=$EXP/phase2_cofold.log
SCREEN_SAMPLES=${SCREEN_SAMPLES:-25}
mkdir -p "$OUT"

log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }
log "PHASE2 COFOLD START (screen_samples=$SCREEN_SAMPLES, cores 19-23 via affinity daemon)"

n=0
for y in "$IN"/denovo_mmp1_*.yaml; do
  cid=$(basename "$y" .yaml)
  odir=$OUT/$cid
  done_n=$(find "$odir" -name "confidence_*.json" 2>/dev/null | wc -l)
  if [ "$done_n" -ge "$SCREEN_SAMPLES" ]; then
    continue   # resumable skip
  fi
  [ -d "$odir" ] && rm -rf "$odir"
  cd "$IN"
  nohup $BOLTZ predict "$y" \
    --out_dir "$odir" \
    --diffusion_samples "$SCREEN_SAMPLES" \
    --use_potentials \
    --output_format pdb \
    --seed 2026 \
    >> "$LOG" 2>&1
  cnt=$(find "$odir" -name "confidence_*.json" 2>/dev/null | wc -l)
  n=$((n+1))
  log "cofold $cid done (confidence jsons=$cnt)"
done
log "PHASE2 COFOLD END (processed $n candidates)"
echo "PHASE2_COFOLD_DONE n=$n"
