#!/bin/bash
# Boltz autonomous cascade v421-v440. Continues cascade after v420 (user: "ROI높은 순 자율 무중단").
# v380-v420 all complete (1500 PDB each) -> start at N=421, nothing existing is destroyed.
# Each cycle = 15 lig x 100 diffusion poses = 1500 PDB, feeds sigma_E/sigma_iptm reliability n.
# seed pattern: NEXT_SEED = N + 1104 (v421=1525 ... v440=1544).
# Robust launch elsewhere: setsid bash <this> </dev/null >/dev/null 2>&1 & disown.
# Affinity daemon (boltz_affinity_pin_19_23_daemon.sh) pins each new boltz to cores 19-23,
# leaving 0-18 for the xtb sigma_E matrices (80% cap). No kill/pkill anywhere here.

SCRIPT_DIR=/home/crazat/genesis_medicine/scripts/round27_paperA
PILOT_DIR=/home/crazat/genesis_medicine/pilot/round27_paperA
BOLTZ=/home/crazat/miniforge3/envs/genesis-md/bin/boltz
LOG=$SCRIPT_DIR/boltz_cascade_v421_v440_watcher.log

echo "[$(date +%F\ %T)] watcher START v421-v440 autonomous cascade (v380-v420 preserved)" >> $LOG

for N in $(seq 421 440); do
  NEXT_SEED=$((N+1104))

  # only the target N's own (nonexistent / partial) dir is cleared; completed cycles untouched
  [ -d $PILOT_DIR/boltz_15_100_v19_v${N} ] && rm -rf $PILOT_DIR/boltz_15_100_v19_v${N}

  attempt=1
  while [ $attempt -le 3 ]; do
    cd $PILOT_DIR
    nohup $BOLTZ predict boltz_input_v19_msa \
      --out_dir boltz_15_100_v19_v${N} \
      --diffusion_samples 100 \
      --use_potentials \
      --output_format pdb \
      --seed $NEXT_SEED \
      > $SCRIPT_DIR/boltz_v${N}_run.log 2>&1 &
    BPID=$!
    echo "[$(date +%T)] Boltz v${N} launched PID=$BPID seed=$NEXT_SEED attempt=$attempt" >> $LOG
    wait $BPID
    EXIT=$?
    PDB_COUNT=$(find $PILOT_DIR/boltz_15_100_v19_v${N}/boltz_results_boltz_input_v19_msa/predictions -name "*.pdb" 2>/dev/null | wc -l)
    if [ "$EXIT" = "0" ] && [ "$PDB_COUNT" -ge "1500" ]; then
      echo "[$(date +%T)] Boltz v${N} done (PDB=$PDB_COUNT, exit=$EXIT)" >> $LOG
      break
    else
      echo "[$(date +%T)] Boltz v${N} FAIL (PDB=$PDB_COUNT, exit=$EXIT) attempt=$attempt" >> $LOG
      attempt=$((attempt+1))
      [ -d $PILOT_DIR/boltz_15_100_v19_v${N} ] && rm -rf $PILOT_DIR/boltz_15_100_v19_v${N}
    fi
  done
done

echo "[$(date +%F\ %T)] watcher END v421-v440 cascade complete" >> $LOG
