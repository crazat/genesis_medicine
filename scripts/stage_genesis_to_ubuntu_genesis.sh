#!/usr/bin/env bash
set -euo pipefail

TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"
LOG_DIR="/home/crazat/genesis_medicine/pilot"
WSL_EXE="${WSL_EXE:-wsl.exe}"
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$LOG_DIR"

run_wsl() {
  if "$WSL_EXE" --status >/dev/null 2>&1; then
    "$WSL_EXE" "$@"
  else
    /init /mnt/c/WINDOWS/system32/wsl.exe -- "$@"
  fi
}

log() {
  printf '[%s] %s\n' "$(date '+%F %T %Z')" "$*"
}

log "Starting C: Ubuntu -> D: ${TARGET_DISTRO} native migration"
log "Source disk:"
df -hT / /mnt/d || true
log "Target disk:"
run_wsl -d "$TARGET_DISTRO" -u crazat -- df -hT / /home/crazat/genesis_medicine || true

log "Copying Genesis project and execution environments"
cd /home/crazat
nice -n 19 ionice -c2 -n7 \
  tar --one-file-system --xattrs --acls \
    --warning=no-file-changed --ignore-failed-read \
    --exclude='genesis_medicine/pilot/cpu_xtb_npass_top5000_hetero6_36conf_d_native.log' \
    --exclude='genesis_medicine/pilot/cpu_meaningful/xtb_npass_top5000_hetero6_refine_36conf.csv' \
    -cpf - genesis_medicine miniforge3 miniconda3 .local .cache \
    2> "$LOG_DIR/d_wsl_full_migration_project_tar_${RUN_ID}.log" \
  | run_wsl -d "$TARGET_DISTRO" -u crazat -- \
      tar --xattrs --acls -xpf - -C /home/crazat

if [ -d /mnt/d/genesis_archive ]; then
  log "Copying existing /mnt/d/genesis_archive into ${TARGET_DISTRO} native ext4"
  cd /mnt/d
  nice -n 19 ionice -c2 -n7 \
    tar --warning=no-file-changed --ignore-failed-read \
      -cpf - genesis_archive \
      2> "$LOG_DIR/d_wsl_full_migration_archive_tar_${RUN_ID}.log" \
    | run_wsl -d "$TARGET_DISTRO" -u crazat -- \
        tar -xpf - -C /home/crazat
else
  log "No /mnt/d/genesis_archive directory found; archive-native copy skipped"
fi

log "Recording migration completion marker in target"
run_wsl -d "$TARGET_DISTRO" -u crazat -- bash -lc \
  "cd /home/crazat/genesis_medicine && { echo \"completed_at_kst=\$(date '+%F %T %Z')\"; echo 'source=C Ubuntu /home/crazat + /mnt/d/genesis_archive'; echo 'target=Ubuntu-Genesis /home/crazat native ext4'; } > pilot/D_NATIVE_FULL_MIGRATION_${RUN_ID}.txt"

log "Target post-copy summary"
run_wsl -d "$TARGET_DISTRO" -u crazat -- bash -lc \
  "df -hT / /home/crazat/genesis_medicine; du -sh /home/crazat/genesis_medicine /home/crazat/miniforge3 /home/crazat/miniconda3 /home/crazat/.local /home/crazat/genesis_archive 2>/dev/null || true; cd /home/crazat/genesis_medicine && git rev-parse --short HEAD && git status --short | head -80"

log "Migration script finished"
