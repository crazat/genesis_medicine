#!/bin/bash
# Wait for pigmentation, then chain alopecia → acne → photoaging.
# Drops ALL_DONE flag on completion. Run in background; monitor flag for completion.

set -e
cd /home/crazat/genesis_medicine
source .venv/bin/activate

mkdir -p pilot/screen
echo "[chain] waiting for pigmentation screen completion..."
while [ ! -f pilot/screen/pigmentation/screen_results.csv ]; do
    sleep 60
done
echo "[chain] pigmentation done at $(date +%H:%M:%S)"

if [ ! -f pilot/screen/alopecia/screen_results.csv ]; then
    echo "[chain] starting alopecia at $(date +%H:%M:%S)"
    python -u scripts/run_disease_screen.py \
        --library data/screen_libraries/alopecia_compounds.csv \
        --targets SRD5A2,AR,CTNNB1 \
        --out pilot/screen/alopecia/
fi
echo "[chain] alopecia done at $(date +%H:%M:%S)"

if [ ! -f pilot/screen/acne/screen_results.csv ]; then
    echo "[chain] starting acne at $(date +%H:%M:%S)"
    python -u scripts/run_disease_screen.py \
        --library data/screen_libraries/acne_compounds.csv \
        --targets SRD5A2,AR \
        --out pilot/screen/acne/
fi
echo "[chain] acne done at $(date +%H:%M:%S)"

if [ ! -f pilot/screen/photoaging/screen_results.csv ]; then
    echo "[chain] starting photoaging at $(date +%H:%M:%S)"
    python -u scripts/run_disease_screen.py \
        --library data/screen_libraries/photoaging_compounds.csv \
        --targets MMP1,SIRT1 \
        --out pilot/screen/photoaging/
fi
echo "[chain] photoaging done at $(date +%H:%M:%S)"

touch pilot/screen/ALL_DONE
echo "[chain] ALL DONE at $(date +%H:%M:%S)"
