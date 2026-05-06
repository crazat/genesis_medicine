#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/home/crazat/genesis_medicine}"
LOG="$ROOT/pilot/overnight_gpu_backfill_d_native.log"
LOCK="/tmp/genesis_overnight_gpu_backfill_d_native.lock"
END_AT="${GENESIS_OVERNIGHT_END_AT:-2026-05-03T10:00:00+09:00}"
SLEEP_SECONDS="${GENESIS_OVERNIGHT_SLEEP_SECONDS:-120}"

export PATH="/usr/lib/wsl/lib:${PATH}"

PY="${GENESIS_PY:-$ROOT/.venv/bin/python}"
MD_PY="${GENESIS_MD_PY:-/home/crazat/miniforge3/envs/genesis-md/bin/python}"
[[ -x "$MD_PY" ]] || MD_PY="$PY"

mkdir -p "$ROOT/pilot"
cd "$ROOT"

exec 5>"$LOCK"
if ! flock -n 5; then
  printf '[%s] overnight GPU backfill already running; exiting duplicate\n' "$(date -Is)" | tee -a "$LOG"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"
}

deadline_epoch() {
  date -d "$END_AT" +%s
}

now_epoch() {
  date +%s
}

gpu_active_count() {
  local project_count gpu_app_count
  project_count="$(pgrep -fc "run_active_learning_next_cofold|run_r18_chromanol_expanded_backfill_cofold|boltz predict|run_openfold|run_scaffold_hop|run_cryptic_cofold|run_r1[67]_chromanol" || true)"
  gpu_app_count="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | awk '$1 ~ /^[0-9]+$/ {n++} END {print n+0}')"
  if [[ "$project_count" -gt 0 ]]; then
    printf '%s\n' "$project_count"
  else
    printf '%s\n' "$gpu_app_count"
  fi
}

pending_active_learning_mmp1() {
  "$PY" - <<'PY'
import pandas as pd
from scripts.run_active_learning_next_cofold import OUT, SOURCE_CSV, runnable_targets

df = pd.read_csv(SOURCE_CSV)
df["target"] = df["target"].astype(str).str.lower()
df["candidate_id"] = df["candidate_id"].astype(str)
done = set()
for path in sorted(OUT.glob("active_learning_next_cofold_batch*.csv")):
    if path.stem.endswith("_manifest"):
        continue
    try:
        rows = pd.read_csv(path)
    except Exception:
        continue
    for row in rows.itertuples(index=False):
        done.add((str(getattr(row, "candidate_id", "")).strip(), str(getattr(row, "target", "")).strip().lower()))
already_labeled = df["already_labeled_pair"].fillna("").astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})
mask = (
    (df["recommended_next_fidelity"].astype(str) == "Boltz-2 cofold")
    & (~already_labeled)
    & (df["synthesis_gate"].astype(str) != "red")
    & df["target"].isin(runnable_targets())
)
pending = df.loc[mask].copy()
pending = pending[~pending.apply(lambda r: (str(r["candidate_id"]), str(r["target"]).lower()) in done, axis=1)]
print(int((pending["target"] == "mmp1").sum()))
PY
}

r17_green_120ns_complete() {
  "$PY" - <<'PY'
import json
from pathlib import Path

path = Path("pilot/md_r17_chromanol_generative_green_120ns/summary.json")
if not path.exists() or path.stat().st_size == 0:
    print(0)
    raise SystemExit
try:
    data = json.loads(path.read_text())
except Exception:
    print(0)
    raise SystemExit
ok = sum(1 for row in data if isinstance(row, dict) and row.get("status") == "ok") if isinstance(data, list) else 0
print(1 if ok >= 9 else 0)
PY
}

run_task() {
  local name="$1"
  shift
  log "GPU backfill start: $name"
  set +e
  "$@" >> "$LOG" 2>&1
  local rc=$?
  set -e
  log "GPU backfill done: $name rc=$rc"
  return 0
}

log "overnight GPU backfill start end_at=$END_AT"
while [[ "$(now_epoch)" -lt "$(deadline_epoch)" ]]; do
  active="$(gpu_active_count)"
  if [[ "$active" -gt 0 ]]; then
    log "GPU busy active=$active; sleeping ${SLEEP_SECONDS}s"
    sleep "$SLEEP_SECONDS"
    continue
  fi

  pending_mmp1="$(pending_active_learning_mmp1 2>/dev/null || echo 0)"
  if [[ "$pending_mmp1" =~ ^[0-9]+$ && "$pending_mmp1" -gt 0 ]]; then
    run_task "active_learning_include_mmp1 pending=$pending_mmp1" \
      "$PY" -u scripts/run_active_learning_next_cofold.py --include-mmp1
    continue
  fi

  if [[ ! -s "$ROOT/pilot/scaffold_hop/boltz2_validation/validation_full.csv" && -d "$ROOT/pilot/scaffold_hop" ]]; then
    run_task "scaffold_hop_round1_boltz_validation" \
      "$PY" -u scripts/run_scaffold_hop_cofold.py
    continue
  fi

  if [[ ! -s "$ROOT/pilot/scaffold_hop/cryptic_cofold/summary.csv" ]]; then
    run_task "tgfb1_cryptic_pocket_cofold" \
      "$PY" -u scripts/run_cryptic_cofold.py
    continue
  fi

  if [[ ! -s "$ROOT/pilot/scaffold_hop_round3/round3_affinity_full.csv" ]]; then
    run_task "scaffold_hop_round3" \
      "$PY" -u scripts/run_scaffold_hop_round3.py
    continue
  fi

  if [[ "$(r17_green_120ns_complete 2>/dev/null || echo 0)" != "1" ]]; then
    run_task "r17_green_120ns_md" \
      "$MD_PY" -u scripts/run_r17_chromanol_generative_green_120ns.py
    continue
  fi

  run_task "r18_chromanol_expanded_backfill" \
    "$PY" -u scripts/run_r18_chromanol_expanded_backfill_cofold.py --batch-size 32
done

log "overnight GPU backfill stop: deadline reached"
