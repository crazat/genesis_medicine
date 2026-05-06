#!/usr/bin/env bash
# OpenFold3 minimal smoke (ubiquitin) — establishes RTX 5090 baseline.
#
# Drain-mode aware: refuses to run on D Ubuntu-Genesis when
# pilot/QUEUE_DRAIN_MODE exists, unless GENESIS_OF3_DRAIN_OVERRIDE=1.
#
# Outputs:
#   pilot/openfold3_smoke/<RUN_ID>/output/...
#   pilot/openfold3_smoke/<RUN_ID>/baseline.json  (wall, peak VRAM, pLDDT)
#   pilot/openfold3_smoke/baseline_latest.json    (symlink to last success)
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/crazat/genesis_medicine}"
OPENFOLD3_ROOT="${OPENFOLD3_ROOT:-$PROJECT_ROOT/external_tools/openfold-3}"
PIXI_BIN="${PIXI_BIN:-/home/crazat/.pixi/bin/pixi}"
OPENFOLD_CACHE="${OPENFOLD_CACHE:-$PROJECT_ROOT/.cache/openfold3}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SMOKE_DIR="$PROJECT_ROOT/pilot/openfold3_smoke"
OUTPUT_DIR="$SMOKE_DIR/$RUN_ID"
DRAIN="$PROJECT_ROOT/pilot/QUEUE_DRAIN_MODE"
QUERY_JSON="${QUERY_JSON:-$OPENFOLD3_ROOT/examples/example_inference_inputs/query_ubiquitin.json}"
RUNNER_YAML="${RUNNER_YAML:-$OPENFOLD3_ROOT/examples/example_runner_yamls/low_mem.yml}"
CKPT="${CKPT:-$OPENFOLD_CACHE/of3-p2-155k.pt}"
LOG="$SMOKE_DIR/openfold3_smoke_latest.log"

mkdir -p "$OUTPUT_DIR"
exec > >(tee -a "$LOG") 2>&1

if [[ -f "$DRAIN" && "${GENESIS_OF3_DRAIN_OVERRIDE:-0}" != "1" ]]; then
  echo "[$(date -Is)] skip: pilot/QUEUE_DRAIN_MODE present"
  exit 0
fi
if [[ ! -x "$PIXI_BIN" ]]; then
  echo "[$(date -Is)] missing pixi at $PIXI_BIN — install pixi or override PIXI_BIN"
  exit 2
fi
if [[ ! -f "$CKPT" ]]; then
  echo "[$(date -Is)] missing OpenFold3 checkpoint at $CKPT"
  exit 2
fi
if [[ ! -f "$QUERY_JSON" ]]; then
  echo "[$(date -Is)] missing query JSON at $QUERY_JSON"
  exit 2
fi

cd "$OPENFOLD3_ROOT"

export OPENFOLD_CACHE
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$PROJECT_ROOT/.cache/xdg}"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.8}"
export CONDA_OVERRIDE_CUDA="${CONDA_OVERRIDE_CUDA:-12.8}"
export PATH="/usr/lib/wsl/lib:${PATH}"
export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${CUDA_HOME}/targets/x86_64-linux/lib:${CUDA_HOME}/lib64:${LD_LIBRARY_PATH:-}"

start_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
start_s=$(date +%s)

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader > "$OUTPUT_DIR/gpu_pre.csv" || true
fi

set +e
"$PIXI_BIN" run -e openfold3-cuda12 run_openfold predict \
  --query-json "$QUERY_JSON" \
  --inference-ckpt-path "$CKPT" \
  --use-msa-server=False \
  --use-templates=False \
  --num-diffusion-samples=1 \
  --num-model-seeds=1 \
  --runner-yaml "$RUNNER_YAML" \
  --output-dir "$OUTPUT_DIR"
rc=$?
set -e

end_s=$(date +%s)
end_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
wall=$((end_s - start_s))

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader > "$OUTPUT_DIR/gpu_post.csv" || true
fi

cif=$(find "$OUTPUT_DIR" -type f -name '*.cif' | head -1 || true)
plddt=""
agg=$(find "$OUTPUT_DIR" -type f -name '*confidences_aggregated.json' | head -1 || true)
if [[ -n "$agg" ]]; then
  plddt=$("$PROJECT_ROOT/.venv/bin/python" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d.get('avg_plddt') or d.get('plddt_mean') or '')" "$agg" 2>/dev/null || true)
fi

baseline="$OUTPUT_DIR/baseline.json"
"$PROJECT_ROOT/.venv/bin/python" - <<PY > "$baseline"
import json, os
print(json.dumps({
    "run_id": "${RUN_ID}",
    "started": "${start_iso}",
    "finished": "${end_iso}",
    "wall_seconds": ${wall},
    "rc": ${rc},
    "query": "$(basename "$QUERY_JSON")",
    "cif": "${cif}",
    "plddt_mean": "${plddt}",
    "checkpoint": "$(basename "$CKPT")",
    "runner_yaml": "$(basename "$RUNNER_YAML")",
}, indent=2))
PY

if [[ "$rc" -eq 0 ]]; then
  ln -sfn "$baseline" "$SMOKE_DIR/baseline_latest.json"
  echo "[$(date -Is)] SUCCESS rc=0 wall=${wall}s plddt=${plddt:-?} cif=${cif:-?}"
else
  echo "[$(date -Is)] FAIL rc=$rc wall=${wall}s — see $OUTPUT_DIR"
fi

exit $rc
