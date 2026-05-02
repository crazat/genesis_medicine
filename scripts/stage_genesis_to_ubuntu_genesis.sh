#!/usr/bin/env bash
set -euo pipefail

TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"
LOG_DIR="/home/crazat/genesis_medicine/pilot"
mkdir -p "$LOG_DIR"

cd /home/crazat
nice -n 19 ionice -c2 -n7 \
  tar --one-file-system --xattrs --acls \
    --warning=no-file-changed --ignore-failed-read \
    -cpf - genesis_medicine miniforge3 miniconda3 .local .cache \
    2> "$LOG_DIR/d_wsl_initial_copy_tar.log" \
  | wsl.exe -d "$TARGET_DISTRO" -u crazat -- \
      tar --xattrs --acls -xpf - -C /home/crazat
