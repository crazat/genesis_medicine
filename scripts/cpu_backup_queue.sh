#!/bin/bash
# CPU backup queue — conformer Pool=8 종료 시 자동으로 다음 작업 시작 (CPU saturation 유지)
cd /home/crazat/genesis_medicine
source .venv/bin/activate
LOG=pilot/cpu_backup_queue.log
log() { echo "[$(date)] $*" | tee -a $LOG; }

log "=== CPU backup queue start ==="

# conformer Pool=8 종료 대기 (max 8h)
for i in {1..480}; do
    if ! pgrep -f cpu_5000_conf > /dev/null; then
        log "conformer Pool=8 ended."
        break
    fi
    sleep 60
done

# 백업 작업 1: xtb top500 extended (CPU intensive, ~3-4h)
log "Backup 1: xtb_npass_top500_extended"
if [ -f scripts/cpu_xtb_npass_top500_extended.py ]; then
    nohup python scripts/cpu_xtb_npass_top500_extended.py > pilot/cpu_xtb_top500.log 2>&1 &
    echo $! > pilot/cpu_backup_pid.txt
    log "xtb top500 started PID=$(cat pilot/cpu_backup_pid.txt)"
fi

log "=== CPU backup queue handed off ==="
