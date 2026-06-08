#!/usr/bin/env bash
# Phase2b GPU-DENSE deep-sigma cofold on the triage survivors.
# Unlike the per-molecule triage (1 boltz call/molecule -> GPU idle between calls),
# this points boltz at a DIRECTORY of survivor YAMLs => ONE invocation, 100 poses each,
# keeping the GPU saturated (the "GPU 최대화" fix). Affinity daemon pins to cores 19-23.
# Resumable, no kill/pkill. Survivors = top-N by triage gate_score.
set -u
EXP=/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1
PY=/home/crazat/genesis_medicine/.venv/bin/python
BOLTZ=/home/crazat/miniforge3/envs/genesis-md/bin/boltz
LOG=$EXP/phase2b_deep.log
TOPN=${TOPN:-20}
DEEP_SAMPLES=${DEEP_SAMPLES:-100}
DEEPIN=$EXP/denovo_deep_input
DEEPOUT=$EXP/denovo_deep_output
log(){ echo "[$(TZ=Asia/Seoul date '+%F %T')] $*" >> "$LOG"; }

cd "$EXP" || exit 1
# 1) score the triage to get survivors
$PY phase2_score_sigma.py >> "$LOG" 2>&1
[ -f phase2_reliability_ranked.csv ] || { log "no triage ranking yet -> abort deep"; exit 2; }

# 2) build survivor directory (top-N cand_ids -> copy their cofold YAMLs)
mkdir -p "$DEEPIN"
$PY - "$TOPN" <<'PYEOF' >> "$LOG" 2>&1
import sys, csv, shutil, os
EXP="/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
topn=int(sys.argv[1])
rows=list(csv.DictReader(open(os.path.join(EXP,"phase2_reliability_ranked.csv"))))
sel=rows[:topn]
src=os.path.join(EXP,"denovo_cofold_input"); dst=os.path.join(EXP,"denovo_deep_input")
n=0
for r in sel:
    cid=r["cand_id"]
    s=os.path.join(src,cid+".yaml")
    if os.path.exists(s):
        shutil.copy(s, os.path.join(dst,cid+".yaml")); n+=1
print(f"deep survivor dir built: {n} YAMLs (top {topn})")
PYEOF

ny=$(ls "$DEEPIN"/*.yaml 2>/dev/null | wc -l)
[ "$ny" -ge 1 ] || { log "0 survivor YAMLs -> abort"; exit 3; }

# 3) ONE GPU-dense boltz invocation over the whole survivor directory
log "PHASE2b DEEP START: $ny survivors x $DEEP_SAMPLES poses (single directory invocation)"
nohup $BOLTZ predict "$DEEPIN" \
  --out_dir "$DEEPOUT" \
  --diffusion_samples "$DEEP_SAMPLES" \
  --use_potentials \
  --output_format pdb \
  --seed 7777 \
  >> "$LOG" 2>&1
rc=$?
pdb=$(find "$DEEPOUT" -name '*.pdb' 2>/dev/null | wc -l)
log "PHASE2b DEEP END rc=$rc pdb=$pdb"

# 4) re-score with deep samples + mark explore round consumed
$PY phase2_score_sigma.py >> "$LOG" 2>&1
touch "$EXP/.deep_round_done"
echo "PHASE2B_DEEP_DONE pdb=$pdb"
