#!/bin/bash
# R6 GPU chain — Tier B 신규 4 타겟 (PIEZO1 + MYLK + F2RL1 + NR3C1)
# R5 LOX/MITF 종료 대기 후 자동 시작.

set -e
cd /home/crazat/genesis_medicine
source .venv/bin/activate

OUT=pilot/cpu_meaningful

# Wait for R5 LOX/MITF to complete (poll predictions count)
echo "[$(date)] Waiting for R5 LOX + MITF to finish..."
while true; do
    LOX_DONE=$(ls $OUT/output_r5_lox/boltz_results_inputs_r5_lox/predictions/ 2>/dev/null | wc -l)
    LOX_INPUTS=$(ls $OUT/inputs_r5_lox/ 2>/dev/null | wc -l)
    MITF_DONE=$(ls $OUT/output_r5_mitf/boltz_results_inputs_r5_mitf/predictions/ 2>/dev/null | wc -l)
    MITF_INPUTS=$(ls $OUT/inputs_r5_mitf/ 2>/dev/null | wc -l)
    if [ "$LOX_DONE" -ge "$LOX_INPUTS" ] && [ "$MITF_DONE" -ge "$MITF_INPUTS" ]; then
        echo "[$(date)] R5 LOX ($LOX_DONE/$LOX_INPUTS) + MITF ($MITF_DONE/$MITF_INPUTS) complete"
        break
    fi
    echo "[$(date)] LOX $LOX_DONE/$LOX_INPUTS · MITF $MITF_DONE/$MITF_INPUTS — waiting 60s"
    sleep 60
done

for tgt in piezo1 mylk f2rl1 nr3c1; do
    INDIR=$OUT/inputs_r6_$tgt
    OUTDIR=$OUT/output_r6_$tgt
    if [ ! -d "$INDIR" ]; then
        echo "  ⏭️  $tgt inputs missing, skipping"
        continue
    fi
    rm -rf $OUTDIR
    NIN=$(ls $INDIR | wc -l)
    echo "[$(date)] R6 $tgt cofold start ($NIN inputs, --use_msa_server enabled)"
    boltz predict $INDIR --out_dir $OUTDIR \
        --sampling_steps 25 --diffusion_samples 1 --recycling_steps 3 \
        --sampling_steps_affinity 200 --diffusion_samples_affinity 1 \
        --affinity_mw_correction --devices 1 \
        --use_msa_server \
        2>&1 | tee -a pilot/r6_$tgt.log | tail -5
    echo "[$(date)] R6 $tgt done"
done

echo "[$(date)] ✅ R6 chain complete (4 new Tier B targets × 30 R6 candidates = 120 cofolds)"
