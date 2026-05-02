#!/usr/bin/env bash
set -euo pipefail

TARGET_DISTRO="${TARGET_DISTRO:-Ubuntu-Genesis}"

wsl.exe -d "$TARGET_DISTRO" --cd /home/crazat/genesis_medicine -- bash -lc '
set -e
pwd
df -hT .
git log -1 --oneline --decorate
test ! -d /home/crazat/ComfyUI && echo "ComfyUI_absent_OK"
.venv/bin/python -c "import rdkit; print(\"rdkit ok\")"
.venv/bin/python -c "import torch; print(\"venv torch cuda\", torch.__version__, torch.cuda.is_available())"
/home/crazat/miniforge3/envs/genesis-md/bin/python -c "import openmm; print(\"openmm ok\")"
nvidia-smi --query-gpu=name,memory.used --format=csv
'
