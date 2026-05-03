#!/usr/bin/env python3
"""Cross-engine ChEMBL holdout calibration: Boltz-2 vs OpenFold3 + AQAffinity.

Reads the existing 93-row Boltz-2 calibration:
    pilot/cpu_meaningful/chembl_boltz2_calibration.csv
which contains (chembl_id, smiles, ic50_nm, pIC50, affinity_pred_value,
affinity_prob_binary). For each row we issue an AQAffinity call (sequence
+ SMILES) using the registered MMP1 catalytic domain + Zn/Ca cofactors,
and record the predicted pKd.

The script runs in two modes:

    --mode dryrun (default)
        Writes pilot/calibration/openfold3_aqaffinity_pearson.json with a
        plan + status summary. NO GPU launch. Drain-mode safe.

    --mode execute
        Calls AQAffinityAdapter.predict() per row. Refuses if the
        AQAffinity binding head ckpt or the OpenFold3 inference ckpt is
        missing. Drain-mode aware: skipped unless GENESIS_OF3_DRAIN_OVERRIDE=1.

In both modes, evidence_ledger picks up a new column
``cross_engine_disagreement = abs(z(boltz2) - z(aqaffinity))`` where z is
the holdout-mean-centered, std-scaled Pearson residual. High disagreement
rows become priority signals for the multi-fidelity scheduler.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

PILOT = ROOT / "pilot"
CHEMBL_CSV = PILOT / "cpu_meaningful/chembl_boltz2_calibration.csv"
OUT_DIR = PILOT / "calibration"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "openfold3_aqaffinity_pearson.json"
OUT_CSV = OUT_DIR / "openfold3_aqaffinity_predictions.csv"

# Same MMP1 catalytic-domain stub used by the smoke scripts.
MMP1_SEQ = (
    "FVLTEGNPRWEQTHLTYRIENYTPDLPRADVDHAIEKAFQLWSNVTPLTFTKVSEGQADIM"
    "ISFVRGDHRDNSPFDGPGGNLAHAFQPGPGIGGDAHFDEDERWTNNFREYNLHRVAAHEL"
    "GHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"
)


def _load_chembl() -> list[dict[str, Any]]:
    if not CHEMBL_CSV.exists():
        return []
    with CHEMBL_CSV.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx = sorted(range(len(xs)), key=lambda i: xs[i])
    ry = sorted(range(len(ys)), key=lambda i: ys[i])
    rank_x = [0] * len(xs)
    rank_y = [0] * len(ys)
    for r, i in enumerate(rx):
        rank_x[i] = r
    for r, i in enumerate(ry):
        rank_y[i] = r
    return _pearson([float(v) for v in rank_x], [float(v) for v in rank_y])


def _run_dryrun(rows: list[dict[str, Any]]) -> dict[str, Any]:
    boltz_pic50 = []
    boltz_pred = []
    for r in rows:
        try:
            boltz_pic50.append(float(r.get("pIC50") or 0.0))
            boltz_pred.append(float(r.get("affinity_pred_value") or 0.0))
        except Exception:
            continue
    return {
        "mode": "dryrun",
        "stamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows_in_chembl_csv": len(rows),
        "boltz2_pearson_r": _pearson(boltz_pred, boltz_pic50),
        "boltz2_spearman_rho": _spearman(boltz_pred, boltz_pic50),
        "aqaffinity_pearson_r": None,
        "aqaffinity_spearman_rho": None,
        "openfold3_pearson_r": None,
        "cross_engine_agreement_pearson": None,
        "next_steps": [
            "Install AQAffinity into pixi env openfold3-cuda12 "
            "(pip install aqaffinity || git+https://huggingface.co/SandboxAQ/AQAffinity).",
            "Place binding head ckpt at .cache/openfold3/aqaffinity_binding_head.pt.",
            "Run with --mode execute on D Ubuntu-Genesis (drain mode lifted).",
        ],
        "notes": [
            "MMP1 catalytic domain stub used as the protein context for "
            "all 93 ligands; AQAffinity is structure-free, so the receptor "
            "context is sufficient to score relative pKd.",
            "Cross-engine disagreement column will be appended to "
            "evidence_ledger by the next build_evidence_ledger.py run "
            "after this calibration completes.",
        ],
    }


def _sanitize_query_id(s: str) -> str:
    return "".join(c if (c.isalnum() or c in "_-") else "_" for c in s)


def _build_multi_query_json(chunk: list[dict[str, Any]]) -> dict[str, Any]:
    queries: dict[str, Any] = {}
    for r in chunk:
        qid = _sanitize_query_id(str(r["chembl_id"]))
        queries[qid] = {
            "chains": [
                {
                    "molecule_type": "protein",
                    "chain_ids": ["A"],
                    "sequence": MMP1_SEQ,
                },
                {
                    "molecule_type": "ligand",
                    "chain_ids": "B",
                    "smiles": r["smiles"],
                },
            ]
        }
    return {"queries": queries}


def _parse_chunk_outputs(out_dir: Path, chunk: list[dict[str, Any]]) -> tuple[dict[str, float], list[str]]:
    """Returns (chembl_id -> pkd, list of missing chembl_ids)."""
    found: dict[str, float] = {}
    missing: list[str] = []
    for r in chunk:
        qid = _sanitize_query_id(str(r["chembl_id"]))
        bh_files = sorted((out_dir / qid).rglob("*binding_head.txt"))
        if not bh_files:
            missing.append(r["chembl_id"])
            continue
        vals: list[float] = []
        for p in bh_files:
            try:
                vals.append(float(p.read_text().strip()))
            except Exception:
                continue
        if not vals:
            missing.append(r["chembl_id"])
        else:
            found[r["chembl_id"]] = sum(vals) / len(vals)
    return found, missing


def _run_chunk(
    chunk: list[dict[str, Any]],
    chunk_idx: int,
    cache_dir: Path,
    *,
    pixi_bin: str,
    of3_root: Path,
    runner_yaml: Path,
    inference_ckpt: Path,
    binding_ckpt: Path,
    timeout_s: int,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    import subprocess
    chunk_dir = cache_dir / f"chunk_{chunk_idx:02d}"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    query_json = chunk_dir / "query.json"
    out_dir = chunk_dir / "output"
    out_dir.mkdir(exist_ok=True)
    query_json.write_text(json.dumps(_build_multi_query_json(chunk), indent=2))

    cmd = [
        pixi_bin, "run", "-e", "openfold3-cuda12",
        "aqaffinity", "predict",
        "--query_json", str(query_json),
        "--runner_yaml", str(runner_yaml),
        "--inference_ckpt_path", str(inference_ckpt),
        "--binding_affinity_ckpt_path", str(binding_ckpt),
        "--use_msa_server=false",
        "--output_dir", str(out_dir),
    ]
    rc = -1
    try:
        proc = subprocess.run(
            cmd, cwd=str(of3_root), capture_output=True, text=True, timeout=timeout_s
        )
        rc = proc.returncode
        (chunk_dir / "stdout.log").write_text(proc.stdout)
        (chunk_dir / "stderr.log").write_text(proc.stderr)
    except subprocess.TimeoutExpired as exc:
        (chunk_dir / "stdout.log").write_text(exc.stdout.decode() if exc.stdout else "")
        (chunk_dir / "stderr.log").write_text(
            (exc.stderr.decode() if exc.stderr else "") + f"\n[TimeoutExpired after {timeout_s}s]"
        )
        rc = 124

    found, missing = _parse_chunk_outputs(out_dir, chunk)
    failures = [
        {"chembl_id": cid, "error": f"no binding_head.txt (rc={rc})"} for cid in missing
    ]
    print(f"[chunk {chunk_idx}] rc={rc} predicted={len(found)}/{len(chunk)} missing={len(missing)}", flush=True)
    return found, failures


def _run_execute(rows: list[dict[str, Any]]) -> dict[str, Any]:
    drain = (PILOT / "QUEUE_DRAIN_MODE").exists()
    if drain and os.environ.get("GENESIS_OF3_DRAIN_OVERRIDE") != "1":
        return {
            "mode": "execute",
            "skipped": True,
            "reason": "QUEUE_DRAIN_MODE present (set GENESIS_OF3_DRAIN_OVERRIDE=1 to override)",
        }

    of3_root = Path(os.environ.get("GENESIS_OPENFOLD3_ROOT", str(ROOT / "external_tools/openfold-3")))
    aq_root = Path(os.environ.get("GENESIS_AQAFFINITY_ROOT", str(ROOT / "external_tools/aqaffinity")))
    pixi_bin = os.environ.get("PIXI_BIN", "/home/crazat/.pixi/bin/pixi")
    runner_yaml = Path(os.environ.get(
        "AQAFFINITY_RUNNER_YAML",
        str(aq_root / "examples/inference/L1000/runner.yaml"),
    ))
    inference_ckpt = Path(os.environ.get(
        "OPENFOLD3_INFERENCE_CKPT", str(ROOT / ".cache/openfold3/of3-p2-155k.pt")
    ))
    binding_ckpt = Path(os.environ.get(
        "AQAFFINITY_BINDING_CKPT", str(ROOT / ".cache/openfold3/aqaffinity_binding_head.pt")
    ))

    missing_paths = [
        str(p) for p in (of3_root, runner_yaml, inference_ckpt, binding_ckpt) if not p.exists()
    ]
    if missing_paths:
        return {
            "mode": "execute",
            "skipped": True,
            "reason": f"missing: {missing_paths}",
        }

    chunk_size = int(os.environ.get("AQAFFINITY_CHUNK_SIZE", "20"))
    timeout_s = int(os.environ.get("AQAFFINITY_CHUNK_TIMEOUT", "3600"))
    cache_dir = ROOT / ".cache/aqaffinity_calibration"
    cache_dir.mkdir(parents=True, exist_ok=True)

    valid_rows = [r for r in rows if r.get("smiles")]
    chunks = [valid_rows[i:i + chunk_size] for i in range(0, len(valid_rows), chunk_size)]

    pic50: list[float] = []
    aq_pred: list[float] = []
    boltz: list[float] = []
    out_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for idx, chunk in enumerate(chunks):
        found, chunk_failures = _run_chunk(
            chunk, idx, cache_dir,
            pixi_bin=pixi_bin, of3_root=of3_root, runner_yaml=runner_yaml,
            inference_ckpt=inference_ckpt, binding_ckpt=binding_ckpt,
            timeout_s=timeout_s,
        )
        failures.extend(chunk_failures)
        for r in chunk:
            cid = r["chembl_id"]
            if cid not in found:
                continue
            try:
                pic50.append(float(r.get("pIC50") or 0.0))
                aq_pred.append(float(found[cid]))
                boltz.append(float(r.get("affinity_pred_value") or 0.0))
            except Exception:
                continue
            out_rows.append({
                "chembl_id": cid,
                "smiles": r.get("smiles"),
                "pIC50": r.get("pIC50"),
                "boltz2_aff_value": r.get("affinity_pred_value"),
                "boltz2_aff_prob_binary": r.get("affinity_prob_binary"),
                "aqaffinity_pkd": found[cid],
                "aqaffinity_confidence": None,
            })

    if out_rows:
        with OUT_CSV.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
            writer.writeheader()
            writer.writerows(out_rows)

    return {
        "mode": "execute",
        "stamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows_total": len(rows),
        "rows_predicted": len(out_rows),
        "rows_failed": len(failures),
        "boltz2_pearson_r": _pearson(boltz, pic50),
        "boltz2_spearman_rho": _spearman(boltz, pic50),
        "aqaffinity_pearson_r": _pearson(aq_pred, pic50),
        "aqaffinity_spearman_rho": _spearman(aq_pred, pic50),
        "cross_engine_agreement_pearson": _pearson(boltz, aq_pred),
        "predictions_csv": str(OUT_CSV.relative_to(ROOT)) if out_rows else None,
        "failures_sample": failures[:10],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dryrun", "execute"], default="dryrun")
    args = parser.parse_args()
    rows = _load_chembl()
    if not rows:
        result = {
            "mode": args.mode,
            "skipped": True,
            "reason": f"missing input CSV {CHEMBL_CSV}",
        }
    elif args.mode == "dryrun":
        result = _run_dryrun(rows)
    else:
        result = _run_execute(rows)

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
