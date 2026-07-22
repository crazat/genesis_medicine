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
PYG=${PYG:-/home/crazat/miniforge3/envs/genesis-md/bin/python3.11}
log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }
# Driver-authoritative free MiB via torch.cuda.mem_get_info. nvidia-smi memory.free is a WSL2 ARTIFACT when
# process-enumeration breaks ("No running processes found") -> it sticks at the kill-loop peak high-water and
# under-reports real free by 20GB+ (2026-06-12: nvidia-smi 9.4GB vs driver 30.2GB with boltz=0). Only called
# to CONFIRM a low nvidia-smi reading right before the destructive SIGKILL (rare path) -> negligible cost.
real_free_mib(){ PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "$PYG" -c "import torch;print(int(torch.cuda.mem_get_info()[0]//1024//1024))" 2>/dev/null; }
log "GPU VRAM watchdog START (FLOOR ${FLOOR}MiB free, poll ${POLL}s; nvidia-smi gate + torch mem_get_info confirm)"
while true; do
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1)
  if [ -n "$free" ] && [ "$free" -lt "$FLOOR" ]; then
    # nvidia-smi tripped low -> CONFIRM with the driver-authoritative torch reading before any kill, because
    # nvidia-smi free is a known WSL2 artifact. Only SIGKILL when the REAL driver free is also below FLOOR.
    rf=$(real_free_mib)
    if [ -n "$rf" ] && [ "$rf" -lt "$FLOOR" ]; then
      bp=$(pgrep -f '[b]oltz predict' | head -1)
      if [ -n "$bp" ]; then
        kill -9 "$bp" 2>/dev/null
        log "REAL VRAM free ${rf}MiB (nvidia-smi ${free}) < ${FLOOR} -> SIGKILL boltz $bp (resume; mem resets)"
        sleep 45   # let the CUDA context free + supervisor relaunch + reload before re-checking
      fi
    else
      log "nvidia-smi free ${free}MiB < ${FLOOR} BUT driver real_free ${rf}MiB >= FLOOR -> WSL2 ARTIFACT, NO kill"
      sleep 60   # don't spam the artifact confirm-probe
    fi
  fi
  sleep "$POLL"
done
