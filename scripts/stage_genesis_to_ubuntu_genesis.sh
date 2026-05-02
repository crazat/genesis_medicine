#!/usr/bin/env bash
set -euo pipefail

TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"
LOG_DIR="/home/crazat/genesis_medicine/pilot"
WSL_EXE="${WSL_EXE:-wsl.exe}"
mkdir -p "$LOG_DIR"

run_wsl() {
  if "$WSL_EXE" --status >/dev/null 2>&1; then
    "$WSL_EXE" "$@"
  else
    /init /mnt/c/WINDOWS/system32/wsl.exe -- "$@"
  fi
}

cd /home/crazat
nice -n 19 ionice -c2 -n7 \
  tar --one-file-system --xattrs --acls \
    --warning=no-file-changed --ignore-failed-read \
    -cpf - genesis_medicine miniforge3 miniconda3 .local .cache \
    2> "$LOG_DIR/d_wsl_initial_copy_tar.log" \
  | run_wsl -d "$TARGET_DISTRO" -u crazat -- \
      tar --xattrs --acls -xpf - -C /home/crazat
