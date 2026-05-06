"""
OpenFold3 + AQAffinity scoring for Paper #A (Tier-1 ABFE benchmark) and Paper #B
(Boltz-2 cross-validation on xtb top500).

Two modes:
  --mode tier1    : Score 6 PASSED Tier-1 ABFE benchmark compounds (with experimental IC50).
                    Output: pIC50 vs AQAff pKd Pearson + Spearman, used as Section 3.2 of paper #A.
  --mode top500   : Score top500 NPC compounds (matches Boltz-2 batch).
                    Output: cross-engine ensemble rank + high-disagreement signal for paper #B.

Reuses pattern from scripts/run_openfold3_chembl_calibration.py (chunked aqaffinity predict).
- Pixi env: openfold3-cuda12
- Receptor: MMP-1 catalytic domain stub (MMP1_SEQ, same as prior calibration)
- AQAffinity: structure-free, sequence + ligand SMILES → pKd
- 1 ligand chain per query (Zn cofactor cannot be added to AQAff queries; ZAFF stays in ABFE side)

Output:
  pilot/of3_aqaff_tier1/{predictions.csv, summary.json}
  pilot/of3_aqaff_top500/{predictions.csv, summary.json, ensemble_rank.csv}
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/home/crazat/genesis_medicine")
PILOT = ROOT / "pilot"
TIER1_OUT = PILOT / "of3_aqaff_tier1"
TOP500_OUT = PILOT / "of3_aqaff_top500"

PIXI_BIN = "/home/crazat/.pixi/bin/pixi"
OF3_ROOT = ROOT / "external_tools/openfold-3"
AQ_ROOT = ROOT / "external_tools/aqaffinity"
RUNNER_YAML = AQ_ROOT / "examples/inference/L1000/runner.yaml"
OF3_CKPT = ROOT / ".cache/openfold3/of3-p2-155k.pt"
BINDING_CKPT = ROOT / ".cache/openfold3/aqaffinity_binding_head.pt"

# Same MMP1 stub as the existing calibration (matches prior R=-0.292 result domain).
MMP1_SEQ = (
    "FVLTEGNPRWEQTHLTYRIENYTPDLPRADVDHAIEKAFQLWSNVTPLTFTKVSEGQADIM"
    "ISFVRGDHRDNSPFDGPGGNLAHAFQPGPGIGGDAHFDEDERWTNNFREYNLHRVAAHEL"
    "GHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG"
)

TIER1_COMPOUNDS = [
    # (chembl_id, ic50_nM, smiles, name)
    ("CHEMBL415",      4.0,    "CC(C)CC(NC(=O)C(CC1=CC=CC=C1)NC(=O)C(O)CC(C)C)C(=O)NO", "Batimastat"),
    ("CHEMBL94487",    12.0,   "O=C(NO)CC(C(=O)NC(C)c1ccccc1)Cc1ccc(Oc2ccc(F)cc2)cc1",  "RS-130830"),
    ("CHEMBL257077",   15.0,   "CC(C)CC(NC(=O)C(NC(=O)C(O)CC(C)C)C(=O)NC)C(=O)NO",       "prinomastat-like"),
    ("CHEMBL301236",   42.0,   "CC(C)C[C@H](NS(=O)(=O)c1ccc(F)cc1)C(=O)NO",              "fluoro-aryl HX"),
    ("CHEMBL292707",   200.0,  "CC(C)CC(=O)NC(CC(=O)NO)C(=O)N(C)C",                       "Ilomastat"),
    ("CHEMBL2105729",  18000.0,"CCC(=O)NC(CCCNC(=N)N)C(=O)NO",                           "weak HX"),
]


def _sanitize(s: str) -> str:
    return "".join(c if (c.isalnum() or c in "_-") else "_" for c in s)


def _build_query_json(rows: list[dict]) -> dict:
    queries: dict[str, Any] = {}
    for r in rows:
        qid = _sanitize(str(r["id"]))
        queries[qid] = {
            "chains": [
                {"molecule_type": "protein", "chain_ids": ["A"], "sequence": MMP1_SEQ},
                {"molecule_type": "ligand", "chain_ids": "B", "smiles": r["smiles"]},
            ]
        }
    return {"queries": queries}


def _parse_outputs(out_dir: Path, rows: list[dict]) -> tuple[dict[str, float], list[str]]:
    found: dict[str, float] = {}
    missing: list[str] = []
    for r in rows:
        qid = _sanitize(str(r["id"]))
        bh_files = sorted((out_dir / qid).rglob("*binding_head.txt"))
        if not bh_files:
            missing.append(r["id"])
            continue
        vals: list[float] = []
        for p in bh_files:
            try:
                vals.append(float(p.read_text().strip()))
            except Exception:
                continue
        if vals:
            found[r["id"]] = sum(vals) / len(vals)
        else:
            missing.append(r["id"])
    return found, missing


def _run_chunk(chunk: list[dict], chunk_idx: int, work_dir: Path, timeout_s: int) -> tuple[dict[str, float], list[dict]]:
    chunk_dir = work_dir / f"chunk_{chunk_idx:03d}"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    query_json = chunk_dir / "query.json"
    out_dir = chunk_dir / "output"
    out_dir.mkdir(exist_ok=True)
    query_json.write_text(json.dumps(_build_query_json(chunk), indent=2))

    cmd = [
        PIXI_BIN, "run", "-e", "openfold3-cuda12",
        "aqaffinity", "predict",
        "--query_json", str(query_json),
        "--runner_yaml", str(RUNNER_YAML),
        "--inference_ckpt_path", str(OF3_CKPT),
        "--binding_affinity_ckpt_path", str(BINDING_CKPT),
        "--use_msa_server=false",
        "--output_dir", str(out_dir),
    ]
    print(f"[chunk {chunk_idx}] launching aqaffinity on {len(chunk)} compounds", flush=True)
    rc = -1
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(OF3_ROOT), capture_output=True, text=True, timeout=timeout_s)
        rc = proc.returncode
        (chunk_dir / "stdout.log").write_text(proc.stdout)
        (chunk_dir / "stderr.log").write_text(proc.stderr)
    except subprocess.TimeoutExpired as exc:
        (chunk_dir / "stdout.log").write_text(exc.stdout.decode() if exc.stdout else "")
        (chunk_dir / "stderr.log").write_text((exc.stderr.decode() if exc.stderr else "") + f"\n[Timeout {timeout_s}s]")
        rc = 124
    wall = time.time() - t0

    found, missing = _parse_outputs(out_dir, chunk)
    failures = [{"id": cid, "error": f"no binding_head.txt (rc={rc})"} for cid in missing]
    print(f"[chunk {chunk_idx}] rc={rc} predicted={len(found)}/{len(chunk)} missing={len(missing)} wall={wall/60:.1f}min", flush=True)
    return found, failures


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


def _verify_paths() -> list[str]:
    missing = [str(p) for p in (OF3_ROOT, RUNNER_YAML, OF3_CKPT, BINDING_CKPT) if not p.exists()]
    return missing


def run_tier1(chunk_size: int, timeout_s: int) -> int:
    TIER1_OUT.mkdir(parents=True, exist_ok=True)
    rows = [{"id": cid, "smiles": smi, "ic50_nm": ic50, "name": name}
            for (cid, ic50, smi, name) in TIER1_COMPOUNDS]
    chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

    pkd_map: dict[str, float] = {}
    failures: list[dict] = []
    for idx, chunk in enumerate(chunks):
        found, fails = _run_chunk(chunk, idx, TIER1_OUT, timeout_s)
        pkd_map.update(found)
        failures.extend(fails)

    # Build predictions table + correlations
    pred_rows = []
    pIC50_list = []
    pkd_list = []
    for r in rows:
        ic50_M = r["ic50_nm"] * 1e-9
        pIC50 = -math.log10(ic50_M)
        pkd = pkd_map.get(r["id"])
        pred_rows.append({
            "chembl_id": r["id"], "name": r["name"],
            "smiles": r["smiles"], "ic50_nm": r["ic50_nm"],
            "pIC50": pIC50, "aqaff_pkd": pkd,
        })
        if pkd is not None:
            pIC50_list.append(pIC50)
            pkd_list.append(pkd)

    csv_path = TIER1_OUT / "predictions.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["chembl_id", "name", "smiles", "ic50_nm", "pIC50", "aqaff_pkd"])
        w.writeheader()
        w.writerows(pred_rows)

    summary = {
        "phase": "OF3+AQAffinity Tier-1 ABFE benchmark scoring",
        "mode": "tier1",
        "stamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_compounds": len(rows),
        "n_predicted": len(pkd_map),
        "n_failures": len(failures),
        "pearson_pkd_vs_pIC50": _pearson(pkd_list, pIC50_list),
        "spearman_pkd_vs_pIC50": _spearman(pkd_list, pIC50_list),
        "predictions": pred_rows,
        "failures": failures,
        "notes": [
            "AQAffinity is sequence-only (apo MMP-1 catalytic stub), no Zn cofactor.",
            "Higher pKd = stronger predicted binder; should correlate positively with pIC50.",
            "For paper #A Section 3.2 cross-engine table; pair with ABFE dG_bind once Phase 5 finishes.",
        ],
    }
    (TIER1_OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== TIER-1 SUMMARY ===")
    print(f"  n={summary['n_predicted']}/{summary['n_compounds']}")
    if summary["pearson_pkd_vs_pIC50"] is not None:
        print(f"  Pearson(pKd, pIC50)  = {summary['pearson_pkd_vs_pIC50']:.3f}")
        print(f"  Spearman(pKd, pIC50) = {summary['spearman_pkd_vs_pIC50']:.3f}")
    return 0 if len(pkd_map) >= 3 else 2


def run_top500(chunk_size: int, timeout_s: int) -> int:
    TOP500_OUT.mkdir(parents=True, exist_ok=True)
    src = ROOT / "pilot/cpu_meaningful/xtb_npass_top500_hetero2_refine_192conf.csv"
    if not src.exists():
        print(f"FAIL: source CSV missing: {src}")
        return 3

    rows: list[dict] = []
    with src.open() as f:
        for r in csv.DictReader(f):
            smi = r.get("smiles") or r.get("SMILES") or ""
            cid = r.get("np_id") or r.get("npaid") or r.get("npc_id") or r.get("compound_id") or ""
            if smi and cid:
                rows.append({"id": str(cid), "smiles": smi})

    print(f"top500: loaded {len(rows)} compounds from {src.name}")

    chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]
    pkd_map: dict[str, float] = {}
    failures: list[dict] = []
    intermediate = TOP500_OUT / "intermediate.json"
    for idx, chunk in enumerate(chunks):
        found, fails = _run_chunk(chunk, idx, TOP500_OUT, timeout_s)
        pkd_map.update(found)
        failures.extend(fails)
        intermediate.write_text(json.dumps({"pkd_map": pkd_map, "n_done": len(pkd_map)}, indent=2))

    # Predictions table
    pred_rows = []
    for r in rows:
        pred_rows.append({"id": r["id"], "smiles": r["smiles"], "aqaff_pkd": pkd_map.get(r["id"])})
    with (TOP500_OUT / "predictions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "smiles", "aqaff_pkd"])
        w.writeheader()
        w.writerows(pred_rows)

    # Cross-engine ensemble rank with Boltz-2 (if available)
    boltz_csv = ROOT / "pilot/boltz2_top500_mmp1/affinity_consolidated.csv"
    ensemble_rows = []
    cross_pearson = None
    if boltz_csv.exists():
        boltz_map: dict[str, float] = {}
        with boltz_csv.open() as f:
            for r in csv.DictReader(f):
                cid = r.get("compound_id") or r.get("npaid") or r.get("id") or ""
                val = r.get("affinity_pred_value") or r.get("affinity_pkd") or ""
                try:
                    boltz_map[str(cid)] = float(val)
                except Exception:
                    continue
        # Build ranked list of common ids
        common = [cid for cid in pkd_map if cid in boltz_map]
        if len(common) >= 3:
            aq_vals = [pkd_map[c] for c in common]
            bo_vals = [boltz_map[c] for c in common]
            cross_pearson = _pearson(aq_vals, bo_vals)
            # Mean rank ensemble
            aq_rank = sorted(range(len(common)), key=lambda i: -aq_vals[i])  # higher pKd = better
            bo_rank = sorted(range(len(common)), key=lambda i: -bo_vals[i])  # boltz: higher = better
            r_aq = {common[aq_rank[i]]: i for i in range(len(common))}
            r_bo = {common[bo_rank[i]]: i for i in range(len(common))}
            for cid in common:
                ensemble_rows.append({
                    "id": cid,
                    "aqaff_pkd": pkd_map[cid],
                    "boltz_aff": boltz_map[cid],
                    "aqaff_rank": r_aq[cid],
                    "boltz_rank": r_bo[cid],
                    "ensemble_rank": (r_aq[cid] + r_bo[cid]) / 2.0,
                    "rank_disagreement": abs(r_aq[cid] - r_bo[cid]),
                })
            ensemble_rows.sort(key=lambda x: x["ensemble_rank"])
            with (TOP500_OUT / "ensemble_rank.csv").open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["id", "aqaff_pkd", "boltz_aff", "aqaff_rank", "boltz_rank", "ensemble_rank", "rank_disagreement"])
                w.writeheader()
                w.writerows(ensemble_rows)

    summary = {
        "phase": "OF3+AQAffinity top500 cross-validation with Boltz-2",
        "mode": "top500",
        "stamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_compounds": len(rows),
        "n_predicted": len(pkd_map),
        "n_failures": len(failures),
        "boltz_available": boltz_csv.exists(),
        "n_cross_validated": len(ensemble_rows),
        "cross_engine_pearson_aq_vs_boltz": cross_pearson,
        "top10_ensemble_compounds": [r["id"] for r in ensemble_rows[:10]] if ensemble_rows else [],
        "high_disagreement_compounds": sorted(ensemble_rows, key=lambda x: -x["rank_disagreement"])[:10] if ensemble_rows else [],
    }
    (TOP500_OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== TOP500 SUMMARY ===")
    print(f"  n={summary['n_predicted']}/{summary['n_compounds']}")
    print(f"  cross-engine Pearson(AQAff, Boltz) = {cross_pearson}")
    return 0 if len(pkd_map) >= 100 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["tier1", "top500"], required=True)
    ap.add_argument("--chunk-size", type=int, default=20)
    ap.add_argument("--timeout-s", type=int, default=3600)
    args = ap.parse_args()

    missing = _verify_paths()
    if missing:
        print(f"FAIL: missing paths: {missing}")
        return 1

    if args.mode == "tier1":
        return run_tier1(args.chunk_size, args.timeout_s)
    return run_top500(args.chunk_size, args.timeout_s)


if __name__ == "__main__":
    sys.exit(main())
