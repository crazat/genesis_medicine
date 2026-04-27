#!/bin/bash
# Launch ABFE 12h on r3_6 × TGFB1 using genesis-md conda env (has openmmtools 0.26.0)
set -e
cd /home/crazat/genesis_medicine
LOG=pilot/cpu_meaningful/abfe_r3_6_tgfb1_genesis.log

source /home/crazat/miniforge3/etc/profile.d/conda.sh
conda activate genesis-md

echo "[$(date +%H:%M:%S)] Genesis-MD env activated"
python -c "import openmmtools; print(f'openmmtools {openmmtools.__version__}')"
python -c "import openmm; print(f'openmm {openmm.__version__}')"
python -c "import torch; print(f'torch {torch.__version__} cuda={torch.cuda.is_available()}')"

echo "[$(date +%H:%M:%S)] Starting ABFE r3_6 × TGFB1 (12h)"
python scripts/run_emb3_abfe_openmmtools.py \
    --target tgfb1 --compound r3_6 --duration_h 12 \
    2>&1 | tee -a $LOG
