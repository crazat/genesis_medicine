#!/usr/bin/env bash
# GPU VRAM memory-ceiling watchdog (server OOM-절대금지, user 2026-06-09).
# boltz cofold's PyTorch allocator high-water can creep up over a long directory-batch (~2.6GB/mol
# observed: 16GB -> 32GB in ~20min, even at max_parallel_samples=1). This is the HARD guarantee:
# if GPU free drops below FLOOR, SIGKILL the (single) boltz by numeric PID -> gpu_roi_supervisor.sh
# relaunches it, which RESUMES from the out_dir (skips already-predicted molecules, ~0 loss) with a
# fresh low allocator. So usage is capped well below the 32GB ceiling and OOM cannot happen.
# No self-match: pattern is bracketed ([b]oltz); kill uses the numeric PID only. setsid-robust.
set -u
FLOOR=${FLOOR:-6000}        # MiB free below which we recycle boltz
POLL=${POLL:-20}
LOG=/home/crazat/genesis_medicine/scripts/round27_paperA/gpu_vram_watchdog.log
log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }
log "GPU VRAM watchdog START (FLOOR ${FLOOR}MiB free, poll ${POLL}s)"
while true; do
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1)
  if [ -n "$free" ] && [ "$free" -lt "$FLOOR" ]; then
    bp=$(pgrep -f '[b]oltz predict' | head -1)
    if [ -n "$bp" ]; then
      kill -9 "$bp" 2>/dev/null
      log "VRAM free ${free}MiB < ${FLOOR} -> SIGKILL boltz $bp (supervisor relaunches w/ resume; memory resets)"
      sleep 45   # let the CUDA context free + supervisor relaunch + reload before re-checking
    fi
  fi
  sleep "$POLL"
done
