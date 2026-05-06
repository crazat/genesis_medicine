#!/usr/bin/env bash
# OpenFold3 metal-cofactor smoke (MMP1 + 2×Zn + 3×Ca + small inhibitor).
#
# Validates that the metal-aware query JSON path (build_openfold3_query_payload
# in src/genesis_medicine/structure/openfold3_adapter.py) actually produces
# a holo prediction on RTX 5090.
#
# Drain-mode aware. Override: GENESIS_OF3_DRAIN_OVERRIDE=1.
#
# Output:
#   pilot/openfold3_smoke/metal_<RUN_ID>/...
#   pilot/openfold3_smoke/metal_baseline_latest.json
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/crazat/genesis_medicine}"
OPENFOLD3_ROOT="${OPENFOLD3_ROOT:-$PROJECT_ROOT/external_tools/openfold-3}"
PIXI_BIN="${PIXI_BIN:-/home/crazat/.pixi/bin/pixi}"
OPENFOLD_CACHE="${OPENFOLD_CACHE:-$PROJECT_ROOT/.cache/openfold3}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SMOKE_DIR="$PROJECT_ROOT/pilot/openfold3_smoke"
OUTPUT_DIR="$SMOKE_DIR/metal_$RUN_ID"
DRAIN="$PROJECT_ROOT/pilot/QUEUE_DRAIN_MODE"
RUNNER_YAML="${RUNNER_YAML:-$OPENFOLD3_ROOT/examples/example_runner_yamls/low_mem.yml}"
CKPT="${CKPT:-$OPENFOLD_CACHE/of3-p2-155k.pt}"
TARGET_KEY="${TARGET_KEY:-MMP1}"
LIG_SMILES="${LIG_SMILES:-O=C(NO)C1(S(=O)(=O)c2ccc(Oc3ccc(Cl)cc3)cc2)CCN(Cc2ccccc2)CC1}"  # CHEMBL79433 — canonical MMP1 inhibitor
LOG="$SMOKE_DIR/openfold3_metal_smoke_latest.log"

mkdir -p "$OUTPUT_DIR"
exec > >(tee -a "$LOG") 2>&1

if [[ -f "$DRAIN" && "${GENESIS_OF3_DRAIN_OVERRIDE:-0}" != "1" ]]; then
  echo "[$(date -Is)] skip: pilot/QUEUE_DRAIN_MODE present"
  exit 0
fi
if [[ ! -f "$CKPT" ]]; then
  echo "[$(date -Is)] missing OpenFold3 checkpoint at $CKPT"
  exit 2
fi

# Build holo query JSON (target sequence + inhibitor + ZN/Ca cofactors).
QUERY_JSON="$OUTPUT_DIR/query.json"
"$PROJECT_ROOT/.venv/bin/python" - <<PY > "$QUERY_JSON"
import json, sys
sys.path.insert(0, "$PROJECT_ROOT/src")
from genesis_medicine.structure import (
    LigandSpec, StructurePredictionRequest, build_openfold3_query_payload
)
from genesis_medicine.structure.cofactor_registry import (
    augment_request_with_cofactors,
)

# MMP1 catalytic domain (PDB 1HFC, residues 100-269 collagenase-1 fragment).
MMP1_CAT = (
    "FVLTEGNPRWEQTHLTYRIENYTPDLPRADVDHAIEKAFQLWSNVTPLTFTKVSEGQADIM"
    "ISFVRGDHRDNSPFDGPGGNLAHAFQPGPGIGGDAHFDEDERWTNNFREYNLHRVAAHEL"
    "GHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"
)
req = StructurePredictionRequest(
    protein_sequences=[MMP1_CAT],
    ligands=[LigandSpec(smiles="$LIG_SMILES", name="MMP1_INHIB_SMOKE")],
)
augment_request_with_cofactors(req, "$TARGET_KEY")
payload = build_openfold3_query_payload(req, query_id="genesis_metal_smoke")
print(json.dumps(payload, indent=2))
PY

cd "$OPENFOLD3_ROOT"

export OPENFOLD_CACHE
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$PROJECT_ROOT/.cache/xdg}"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.8}"
export CONDA_OVERRIDE_CUDA="${CONDA_OVERRIDE_CUDA:-12.8}"
export PATH="/usr/lib/wsl/lib:${PATH}"
export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${CUDA_HOME}/targets/x86_64-linux/lib:${CUDA_HOME}/lib64:${LD_LIBRARY_PATH:-}"

start_s=$(date +%s)
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
wall=$((end_s - start_s))

cif=$(find "$OUTPUT_DIR" -type f -name '*.cif' | head -1 || true)
plddt=""
agg=$(find "$OUTPUT_DIR" -type f -name '*confidences_aggregated.json' | head -1 || true)
if [[ -n "$agg" ]]; then
  plddt=$("$PROJECT_ROOT/.venv/bin/python" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d.get('avg_plddt') or d.get('plddt_mean') or '')" "$agg" 2>/dev/null || true)
fi

baseline="$OUTPUT_DIR/baseline.json"
"$PROJECT_ROOT/.venv/bin/python" - <<PY > "$baseline"
import json, datetime
print(json.dumps({
    "run_id": "${RUN_ID}",
    "target": "${TARGET_KEY}",
    "ligand_smiles": "$LIG_SMILES",
    "wall_seconds": ${wall},
    "rc": ${rc},
    "plddt_mean": "${plddt}",
    "cif": "${cif}",
    "checkpoint": "$(basename "$CKPT")",
    "metal_smoke": True,
    "stamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
}, indent=2))
PY

if [[ "$rc" -eq 0 ]]; then
  ln -sfn "$baseline" "$SMOKE_DIR/metal_baseline_latest.json"
  echo "[$(date -Is)] SUCCESS rc=0 wall=${wall}s plddt=${plddt:-?} target=${TARGET_KEY}"
else
  echo "[$(date -Is)] FAIL rc=$rc wall=${wall}s target=${TARGET_KEY}"
fi
exit $rc
