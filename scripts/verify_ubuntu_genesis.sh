#!/usr/bin/env bash
set -euo pipefail

TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"
WSL_EXE="${WSL_EXE:-wsl.exe}"

run_wsl() {
  if "$WSL_EXE" --status >/dev/null 2>&1; then
    "$WSL_EXE" "$@"
  else
    /init /mnt/c/WINDOWS/system32/wsl.exe -- "$@"
  fi
}

run_wsl -d "$TARGET_DISTRO" --cd /home/crazat/genesis_medicine -- bash -s <<'EOF'
set -e
. /etc/profile.d/genesis-performance.sh 2>/dev/null || true
pwd
df -hT .
git log -1 --oneline --decorate
test ! -d /home/crazat/ComfyUI && echo "ComfyUI_absent_OK"
echo "nofile soft=$(ulimit -Sn) hard=$(ulimit -Hn)"
test -f /etc/profile.d/genesis-performance.sh && echo "genesis_profile_OK"
test -d /usr/local/cuda-12.8 && echo "cuda_toolkit_OK"
.venv/bin/python -c "import rdkit; print(\"rdkit ok\")"
.venv/bin/python -c "import torch; print(\"venv torch cuda\", torch.__version__, torch.cuda.is_available())"
/home/crazat/miniforge3/envs/genesis-md/bin/python -c "import openmm; print(\"openmm ok\")"
nvidia-smi --query-gpu=name,memory.used --format=csv
EOF
