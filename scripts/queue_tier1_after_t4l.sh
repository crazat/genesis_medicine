#!/bin/bash
# Queue Tier 1 GPU work to start AFTER T4L calibration completes.
# - Boltz-2 ChEMBL calibration (~3h GPU)
# - PoseBusters validation (~30min CPU+GPU peeks)
# - Chai-1 ensemble (~1-2h GPU)
# Sequential to avoid GPU contention.

set +e   # tolerate errors per stage
cd /home/crazat/genesis_medicine
source .venv/bin/activate

T4L_RESULT="pilot/calibration/t4l_benzene/result_corrected.json"

echo "[queue] waiting for T4L calibration completion..."
while [ ! -f "$T4L_RESULT" ] && kill -0 112376 2>/dev/null; do
    sleep 300
done
echo "[queue] T4L state at $(date +%H:%M:%S)"
[ -f "$T4L_RESULT" ] && echo "[queue] T4L COMPLETE: $(cat $T4L_RESULT | head -20)"

# 1. PoseBusters first (light, ~30min)
echo ""
echo "[queue 1/3] PoseBusters validation $(date +%H:%M:%S)"
python -u scripts/run_posebusters_validation.py 2>&1 | tail -40

# 2. Boltz-2 ChEMBL calibration (~3h GPU)
echo ""
echo "[queue 2/3] Boltz-2 MMP-1 ChEMBL calibration $(date +%H:%M:%S)"
python -u scripts/boltz2_calibration_mmp1.py 2>&1 | tail -40

# 3. Chai-1 ensemble (top 6 pairs, ~1-2h GPU)
echo ""
echo "[queue 3/3] Chai-1 ensemble cofold $(date +%H:%M:%S)"
python -u scripts/run_chai1_ensemble.py 2>&1 | tail -40

touch pilot/TIER1_QUEUE_DONE
echo ""
echo "=== TIER 1 GPU QUEUE DONE at $(date +%H:%M:%S) ==="
