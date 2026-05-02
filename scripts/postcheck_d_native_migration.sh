#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${RUN_ID:?RUN_ID is required}"
MIG_PID="${MIG_PID:?MIG_PID is required}"
TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"
ROOT="/home/crazat/genesis_medicine"
LOG="${LOG:-$ROOT/pilot/d_wsl_full_migration_postcheck_${RUN_ID}.log}"
WSL_EXE="${WSL_EXE:-wsl.exe}"

run_wsl() {
  if "$WSL_EXE" --status >/dev/null 2>&1; then
    "$WSL_EXE" "$@"
  else
    /init /mnt/c/WINDOWS/system32/wsl.exe -- "$@"
  fi
}

log() {
  printf '[postcheck %s] %s\n' "$(date '+%F %T %Z')" "$*"
}

{
  log "waiting for migration PID ${MIG_PID}"
  while ps -p "$MIG_PID" >/dev/null 2>&1; do
    log "migration still running"
    sleep 300
  done

  log "migration PID exited"
  log "last migration log lines"
  tail -120 "$ROOT/pilot/d_wsl_full_migration_${RUN_ID}.log" || true

  log "syncing latest committed docs/git metadata to ${TARGET_DISTRO}"
  cd /home/crazat
  tar --one-file-system --xattrs --acls -cpf - \
    genesis_medicine/.git \
    genesis_medicine/CLAUDE.md \
    genesis_medicine/scripts/stage_genesis_to_ubuntu_genesis.sh \
    genesis_medicine/scripts/postcheck_d_native_migration.sh \
    genesis_medicine/pilot/npass_stop_report_20260502_220806.txt \
    2>> "$LOG" \
    | run_wsl -d "$TARGET_DISTRO" -u crazat -- \
        tar --xattrs --acls -xpf - -C /home/crazat

  log "target verification"
  run_wsl -d "$TARGET_DISTRO" -u crazat -- bash -lc "
    cd /home/crazat/genesis_medicine
    echo HEAD=\$(git rev-parse --short HEAD)
    git status --short CLAUDE.md scripts/stage_genesis_to_ubuntu_genesis.sh scripts/postcheck_d_native_migration.sh pilot/npass_stop_report_20260502_220806.txt
    test -f pilot/D_NATIVE_FULL_MIGRATION_${RUN_ID}.txt
    cat pilot/D_NATIVE_FULL_MIGRATION_${RUN_ID}.txt
    df -hT /
    du -sh /home/crazat/genesis_medicine /home/crazat/miniforge3 /home/crazat/miniconda3 /home/crazat/.local /home/crazat/genesis_archive 2>/dev/null || true
    pgrep -af '[c]pu_xtb_npass_top_refine.py --topn 5000 --workers 8 --num-confs 36|[x]tb /tmp/xtb_refine' | head -20 || true
  "

  log "done"
} >> "$LOG" 2>&1
