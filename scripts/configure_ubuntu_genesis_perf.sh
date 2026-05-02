#!/usr/bin/env bash
set -euo pipefail

TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"
GENESIS_USER="${GENESIS_USER:-crazat}"
COPY_CUDA_TOOLKIT="${COPY_CUDA_TOOLKIT:-auto}"
WSL_EXE="${WSL_EXE:-wsl.exe}"

log() {
  printf '[ubuntu-genesis-perf] %s\n' "$*"
}

run_wsl() {
  if "$WSL_EXE" --status >/dev/null 2>&1; then
    "$WSL_EXE" "$@"
  else
    /init /mnt/c/WINDOWS/system32/wsl.exe -- "$@"
  fi
}

require_wsl_target() {
  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- true
}

copy_user_dotfiles() {
  local files=()
  local f
  for f in .bashrc .profile .gitconfig .condarc; do
    if [ -e "/home/${GENESIS_USER}/${f}" ]; then
      files+=("$f")
    fi
  done

  if [ "${#files[@]}" -eq 0 ]; then
    log "no source dotfiles to copy"
    return 0
  fi

  log "copying selected user dotfiles: ${files[*]}"
  (
    cd "/home/${GENESIS_USER}"
    tar --xattrs --acls -cpf - "${files[@]}"
  ) | run_wsl -d "$TARGET_DISTRO" -u "$GENESIS_USER" --cd "/home/${GENESIS_USER}" -- \
        tar --xattrs --acls -xpf - -C "/home/${GENESIS_USER}"
}

configure_system_files() {
  log "configuring /etc/wsl.conf, limits, and Genesis profile defaults"

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- tee /etc/wsl.conf >/dev/null <<EOF
[boot]
systemd=true

[user]
default=${GENESIS_USER}

[automount]
options=metadata,umask=22,fmask=11
EOF

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- tee /etc/security/limits.d/99-genesis.conf >/dev/null <<'EOF'
* soft nofile 1048576
* hard nofile 1048576
root soft nofile 1048576
root hard nofile 1048576
EOF

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- mkdir -p \
    /etc/systemd/system.conf.d /etc/systemd/user.conf.d

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- tee /etc/systemd/system.conf.d/99-genesis-limits.conf >/dev/null <<'EOF'
[Manager]
DefaultLimitNOFILE=1048576
EOF

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- tee /etc/systemd/user.conf.d/99-genesis-limits.conf >/dev/null <<'EOF'
[Manager]
DefaultLimitNOFILE=1048576
EOF

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- tee /etc/profile.d/genesis-performance.sh >/dev/null <<'EOF'
# Genesis_Medicine defaults for the dedicated Ubuntu-Genesis WSL distro.
ulimit -n 1048576 2>/dev/null || true

if [ -z "${HOME:-}" ]; then
  HOME="$(getent passwd "$(id -u)" | cut -d: -f6)"
  export HOME
fi

if [ -d "${HOME:-/home/crazat}/genesis_medicine" ]; then
  export GENESIS_ROOT="${GENESIS_ROOT:-${HOME:-/home/crazat}/genesis_medicine}"
  export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$GENESIS_ROOT/.cache}"
  export HF_HOME="${HF_HOME:-$GENESIS_ROOT/.cache/huggingface}"
  export TORCH_HOME="${TORCH_HOME:-$GENESIS_ROOT/.cache/torch}"
fi

if [ -d /usr/local/cuda-12.8/bin ]; then
  case ":$PATH:" in
    *:/usr/local/cuda-12.8/bin:*) ;;
    *) export PATH="/usr/local/cuda-12.8/bin:$PATH" ;;
  esac
fi

if [ -d /usr/local/cuda-12.8/lib64 ]; then
  case ":${LD_LIBRARY_PATH:-}:" in
    *:/usr/local/cuda-12.8/lib64:*) ;;
    *) export LD_LIBRARY_PATH="/usr/local/cuda-12.8/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
  esac
fi
EOF

  run_wsl -d "$TARGET_DISTRO" -u "$GENESIS_USER" --cd "/home/${GENESIS_USER}" -- bash -s <<'EOF'
    set -e
    marker="# Genesis performance defaults"
    block='

# Genesis performance defaults
if [ -f /etc/profile.d/genesis-performance.sh ]; then
  . /etc/profile.d/genesis-performance.sh
fi'
    for target_file in "$HOME/.profile" "$HOME/.bashrc"; do
      touch "$target_file"
      if ! grep -Fq "$marker" "$target_file"; then
        printf "%s\n" "$block" >> "$target_file"
      fi
    done
EOF
}

copy_cuda_toolkit_if_needed() {
  if [ ! -d /usr/local/cuda-12.8 ]; then
    log "source /usr/local/cuda-12.8 absent; skipping CUDA toolkit copy"
    return 0
  fi

  if run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- test -d /usr/local/cuda-12.8; then
    log "target CUDA toolkit already present"
  elif [ "$COPY_CUDA_TOOLKIT" = "0" ] || [ "$COPY_CUDA_TOOLKIT" = "false" ]; then
    log "COPY_CUDA_TOOLKIT disabled; skipping CUDA toolkit copy"
  else
    log "copying CUDA 12.8 toolkit to target distro"
    (
      cd /usr/local
      nice -n 19 ionice -c2 -n7 tar --xattrs --acls -cpf - cuda-12.8
    ) | run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- \
          tar --xattrs --acls -xpf - -C /usr/local
  fi

  run_wsl -d "$TARGET_DISTRO" -u root --cd /root -- bash -s <<'EOF'
    if [ -d /usr/local/cuda-12.8 ]; then
      ln -sfn /usr/local/cuda-12.8 /usr/local/cuda
      ln -sfn /usr/local/cuda-12.8 /usr/local/cuda-12
    fi
EOF
}

quick_check() {
  log "quick check"
  run_wsl -d "$TARGET_DISTRO" -u "$GENESIS_USER" --cd "/home/${GENESIS_USER}/genesis_medicine" -- bash -s <<'EOF'
    set -e
    . /etc/profile.d/genesis-performance.sh
    echo "root=$(df -hT / | tail -1)"
    echo "nofile soft=$(ulimit -Sn) hard=$(ulimit -Hn)"
    echo "GENESIS_ROOT=${GENESIS_ROOT:-unset}"
    command -v git
    command -v nvidia-smi
    .venv/bin/python -c "import rdkit; print(\"rdkit ok\")"
    /home/crazat/miniforge3/envs/genesis-md/bin/python -c "import openmm; print(\"openmm ok\")"
EOF
}

require_wsl_target
copy_user_dotfiles
configure_system_files
copy_cuda_toolkit_if_needed
quick_check

log "done; systemd activation and VHD resize still require a future WSL shutdown window"
