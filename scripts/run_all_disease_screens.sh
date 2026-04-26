#!/bin/bash
# Sequential disease screens — wait for each to finish before next starts.
# Pigmentation screen runs first (or skipped if already done). Alopecia, acne,
# photoaging follow sequentially. Total expected ~2-3h on shared GPU.

set -e
cd /home/crazat/genesis_medicine
source .venv/bin/activate

if [ -f pilot/screen/pigmentation/screen_results.csv ]; then
    echo "  [skip] pigmentation already done"
else
    echo "[1/4] Pigmentation screen..."
    python -u scripts/run_disease_screen.py \
        --library data/screen_libraries/pigmentation_compounds.csv \
        --targets TYR,TYRP1,DCT \
        --out pilot/screen/pigmentation/
fi

echo "[2/4] Alopecia screen..."
python -u scripts/run_disease_screen.py \
    --library data/screen_libraries/alopecia_compounds.csv \
    --targets SRD5A2,AR,CTNNB1 \
    --out pilot/screen/alopecia/

echo "[3/4] Acne screen..."
python -u scripts/run_disease_screen.py \
    --library data/screen_libraries/acne_compounds.csv \
    --targets SRD5A2,AR \
    --out pilot/screen/acne/

echo "[4/4] Photoaging screen..."
python -u scripts/run_disease_screen.py \
    --library data/screen_libraries/photoaging_compounds.csv \
    --targets MMP1,SIRT1 \
    --out pilot/screen/photoaging/

echo ""
echo "=== ALL DISEASE SCREENS DONE ==="
ls -la pilot/screen/*/screen_results.csv 2>&1
