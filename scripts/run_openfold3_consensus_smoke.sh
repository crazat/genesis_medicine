#!/usr/bin/env bash
# Tri-engine consensus smoke: Boltz-2 + Protenix-v2 + OpenFold3 on a single
# (target, ligand) pair. Uses ConsensusPredictor + ligand-aware RMSD cluster.
#
# Drain-mode aware. Override: GENESIS_OF3_DRAIN_OVERRIDE=1.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/crazat/genesis_medicine}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SMOKE_DIR="$PROJECT_ROOT/pilot/openfold3_smoke"
OUTPUT_DIR="$SMOKE_DIR/consensus_$RUN_ID"
DRAIN="$PROJECT_ROOT/pilot/QUEUE_DRAIN_MODE"
TARGET_KEY="${TARGET_KEY:-MMP1}"
LIG_SMILES="${LIG_SMILES:-O=C(NO)C1(S(=O)(=O)c2ccc(Oc3ccc(Cl)cc3)cc2)CCN(Cc2ccccc2)CC1}"
LOG="$SMOKE_DIR/openfold3_consensus_smoke_latest.log"

mkdir -p "$OUTPUT_DIR"
exec > >(tee -a "$LOG") 2>&1

if [[ -f "$DRAIN" && "${GENESIS_OF3_DRAIN_OVERRIDE:-0}" != "1" ]]; then
  echo "[$(date -Is)] skip: pilot/QUEUE_DRAIN_MODE present"
  exit 0
fi

cd "$PROJECT_ROOT"
"$PROJECT_ROOT/.venv/bin/python" - <<PY
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, "$PROJECT_ROOT/src")

from genesis_medicine.structure import (
    Boltz2Adapter,
    ConsensusPredictor,
    ConsensusRequest,
    LigandSpec,
    OpenFold3Adapter,
    ProtenixAdapter,
    StructurePredictionRequest,
    augment_request_with_cofactors,
)

OUT = Path("$OUTPUT_DIR")
OUT.mkdir(parents=True, exist_ok=True)

# Same MMP1 sequence as run_openfold3_metal_smoke.sh
MMP1 = (
    "FVLTEGNPRWEQTHLTYRIENYTPDLPRADVDHAIEKAFQLWSNVTPLTFTKVSEGQADIM"
    "ISFVRGDHRDNSPFDGPGGNLAHAFQPGPGIGGDAHFDEDERWTNNFREYNLHRVAAHEL"
    "GHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"
)
req = StructurePredictionRequest(
    protein_sequences=[MMP1],
    ligands=[LigandSpec(smiles="$LIG_SMILES", name="MMP1_INHIB_CONSENSUS")],
    num_samples=1,
)
augment_request_with_cofactors(req, "$TARGET_KEY")

predictors = {}
try:
    predictors["boltz2"] = Boltz2Adapter(cache_dir=OUT / "boltz2")
except Exception as exc:
    print(f"# boltz2 unavailable: {exc}")
try:
    predictors["protenix"] = ProtenixAdapter(cache_dir=OUT / "protenix")
except Exception as exc:
    print(f"# protenix unavailable: {exc}")
try:
    predictors["openfold3"] = OpenFold3Adapter(cache_dir=OUT / "openfold3")
except Exception as exc:
    print(f"# openfold3 unavailable: {exc}")

if len(predictors) < 2:
    print(json.dumps({"status": "skipped", "reason": "need ≥2 predictors", "available": list(predictors)}, indent=2))
    raise SystemExit(0)

cp = ConsensusPredictor(predictors=predictors)
t0 = time.time()
result = cp.predict_consensus(ConsensusRequest(base_request=req, engines=list(predictors), samples_per_engine=1))
wall = time.time() - t0

summary = {
    "run_id": "$RUN_ID",
    "target": "$TARGET_KEY",
    "engines_used": [e.engine for e in result.all_entries],
    "consensus_plddt": result.consensus_plddt,
    "rmsd_dispersion": result.rmsd_dispersion,
    "wall_seconds": wall,
    "representative_engine": result.representative.engine,
    "metadata": result.metadata,
}
print(json.dumps(summary, indent=2))
(OUT / "consensus_summary.json").write_text(json.dumps(summary, indent=2))
PY
