"""
ABFE benchmark orchestrator — runs warmup + Phase 5 sequentially on each
prepared ChEMBL reference compound, then aggregates Spearman / MAE vs
experimental IC50.

Sequential execution: 1 compound at a time on GPU, 12-18 h each.
Total wall: 5-12 days for full 15-compound benchmark, but designed to be
checkpointed — each compound's PHASE5_OK or PHASE5_INCONCLUSIVE marker
persists, so re-running this script picks up where it left off.

Strategic subset for paper #A submission (run these first; full set later):
  CHEMBL443684 (Marimastat, IC50=5 nM, hydroxamate)
  CHEMBL406    (Prinomastat, IC50=3 nM, sulfonamide-hydroxamate)
  CHEMBL259829 (CGS27023A, IC50=310 nM, non-hydroxamate)
  CHEMBL98     (weak aryl sulfone, IC50=2400 nM)
  CHEMBL2105729 (very weak hydroxamate, IC50=18000 nM)

Output:
  pilot/abfe_benchmark_chembl/{chembl_id}/abfe_production_mss/dG_bind.json
  pilot/abfe_benchmark_chembl/benchmark_summary.json    (Spearman, MAE, table)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH_BASE = ROOT / "pilot/abfe_benchmark_chembl"
# Use the MultiStateSampler variant: smoketest 2026-05-05 confirmed it completes
# all iterations on the ZAFF + Zn restraint system, whereas the original
# ReplicaExchangeSampler (production_generic) deadlocks at swap-all on the
# same input. The 12h overnight benchmark (6 compounds × 2 reps) ran on
# production_mss.py.
PHASE5 = ROOT / "scripts/zaff_phase5_abfe_production_mss.py"
WARMUP_GENERIC = ROOT / "scripts/zaff_phase5_warmup_generic.py"
CONDA_PY = "/home/crazat/miniforge3/envs/genesis-md/bin/python"

# Tier-1 priority subset (revised after 6/15 prep success, IC50 4 nM -> 18 μM, 4500-fold range)
# Original list (Marimastat, Prinomastat, CGS27023A, weak aryl sulfone) failed antechamber
# sqm "odd electrons" — known limitation for some hydroxamate protonation forms.
# Substituted with 5 different but equally diverse PASSED compounds.
TIER1_SUBSET = [
    "CHEMBL415",     # Batimastat 4 nM (hydroxamate)
    "CHEMBL94487",   # RS-130830 12 nM (carboxylate)
    "CHEMBL257077",  # 15 nM (prinomastat-like hydroxamate)
    "CHEMBL301236",  # 42 nM (fluoro-aryl hydroxamate)
    "CHEMBL292707",  # Ilomastat 200 nM (zinc-chelating)
    "CHEMBL2105729", # 18000 nM (very weak hydroxamate)
]


def run(cmd: list[str], cwd: Path | None = None, log_path: Path | None = None) -> int:
    print(f"  $ {' '.join(cmd[:5])}{'...' if len(cmd)>5 else ''}")
    if log_path:
        with log_path.open("a") as f:
            f.write(f"\n# {' '.join(cmd)}\n# started {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
            proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=f, stderr=subprocess.STDOUT)
    else:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    return proc.returncode


def process_compound(chembl_id: str) -> dict:
    work = BENCH_BASE / chembl_id
    # Production scripts (generic / mss) gate on complex/PHASE4_OK; tolerate
    # the legacy top-level marker for compounds prepped before the layout fix.
    if not ((work / "complex" / "PHASE4_OK").exists() or (work / "PHASE4_OK").exists()):
        return {"chembl_id": chembl_id, "status": "no_phase4"}
    # Skip if already done in either production layout (mss = current default,
    # legacy abfe_production = ReplicaExchangeSampler runs from before the
    # 2026-05-05 swap-all deadlock fix).
    for prod_dir_name, status_label in (
        ("abfe_production_mss", "ok"),
        ("abfe_production", "ok"),
    ):
        prod_dir = work / prod_dir_name
        if (prod_dir / "PHASE5_OK").exists():
            try:
                data = json.loads((prod_dir / "dG_bind.json").read_text())
                return {"chembl_id": chembl_id, "status": status_label, **data}
            except Exception:
                pass
        if (prod_dir / "PHASE5_INCONCLUSIVE").exists():
            try:
                data = json.loads((prod_dir / "dG_bind.json").read_text())
                return {"chembl_id": chembl_id, "status": "inconclusive", **data}
            except Exception:
                pass

    # Step A: warmup (writes new complex.rst7 + solvent.rst7 with relaxed clashes)
    print(f"\n=== {chembl_id} warmup ===")
    rc = run([CONDA_PY, str(WARMUP_GENERIC), "--work", str(work), "--leg", "all"],
             log_path=work / "warmup.log")
    if rc != 0:
        return {"chembl_id": chembl_id, "status": "warmup_fail", "rc": rc}

    # Step B: Phase 5 production (complex + solvent + combine, MultiStateSampler)
    print(f"=== {chembl_id} Phase 5 production ===")
    rc = run([CONDA_PY, str(PHASE5), "--work", str(work), "--leg", "all"],
             log_path=work / "phase5.log")
    if rc != 0:
        return {"chembl_id": chembl_id, "status": "phase5_fail", "rc": rc}

    # production_mss writes to abfe_production_mss/; production_generic to
    # abfe_production/. Check both so this orchestrator works against either.
    for prod_dir_name in ("abfe_production_mss", "abfe_production"):
        dG_path = work / prod_dir_name / "dG_bind.json"
        if dG_path.exists():
            data = json.loads(dG_path.read_text())
            return {"chembl_id": chembl_id, "status": "ok", **data}
    return {"chembl_id": chembl_id, "status": "no_dg_json"}


def aggregate_results(results: list[dict], manifest: dict) -> dict:
    """Compute Spearman ρ + MAE between predicted dG_bind and experimental pIC50."""
    import math
    try:
        from scipy.stats import spearmanr, pearsonr
    except ImportError:
        return {"error": "scipy not available", "results": results}

    # Build predicted vs experimental table
    by_id = {r["chembl_id"]: r for r in results if r.get("dG_bind_kcal_mol") is not None}
    exp = {c["chembl_id"]: c for c in manifest["compounds"]}
    paired = []
    for chembl_id, r in by_id.items():
        if chembl_id not in exp:
            continue
        ic50_M = exp[chembl_id]["ic50_nm"] * 1e-9
        pIC50 = -math.log10(ic50_M)
        # Convert IC50 to dG (assuming Ki ~ IC50 for competitive inhibitors)
        # dG = -RT ln(1/Ki) = RT ln(Ki)
        # at 310 K, RT = 0.616 kcal/mol
        dG_exp = 0.616 * math.log(ic50_M)  # negative for binders
        paired.append({
            "chembl_id": chembl_id,
            "ic50_nM": exp[chembl_id]["ic50_nm"],
            "pIC50": pIC50,
            "dG_exp_kcal_mol": dG_exp,
            "dG_pred_kcal_mol": r["dG_bind_kcal_mol"],
            "dG_pred_err": r.get("dG_bind_err_kcal_mol"),
        })

    if len(paired) < 3:
        return {"n": len(paired), "results": results, "paired": paired,
                "note": "need >=3 compounds for correlation"}

    pred = [p["dG_pred_kcal_mol"] for p in paired]
    expv = [p["dG_exp_kcal_mol"] for p in paired]
    rho_s, p_s = spearmanr(pred, expv)
    rho_p, p_p = pearsonr(pred, expv)
    mae = sum(abs(a - b) for a, b in zip(pred, expv)) / len(paired)
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(pred, expv)) / len(paired))

    return {
        "n": len(paired),
        "spearman": {"rho": rho_s, "p_value": p_s},
        "pearson": {"r": rho_p, "p_value": p_p},
        "mae_kcal_mol": mae,
        "rmse_kcal_mol": rmse,
        "paired": paired,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", choices=["tier1", "all"], default="tier1",
                    help="tier1 = 5 strategic compounds; all = full 15")
    ap.add_argument("--summarize-only", action="store_true",
                    help="skip Phase 5 launches, only aggregate existing results")
    args = ap.parse_args()

    if not (BENCH_BASE / "manifest.json").exists():
        print(f"FAIL: missing {BENCH_BASE}/manifest.json — run abfe_benchmark_prepare.py first")
        return 1
    manifest = json.loads((BENCH_BASE / "manifest.json").read_text())
    n_prepared = sum(1 for c in manifest["compounds"] if c.get("status") == "ok")
    print(f"manifest: {n_prepared}/{len(manifest['compounds'])} compounds prepared OK")

    if args.subset == "tier1":
        targets = TIER1_SUBSET
    else:
        targets = [c["chembl_id"] for c in manifest["compounds"] if c.get("status") == "ok"]

    print(f"running ABFE on {len(targets)} compounds: {targets}")

    results = []
    if not args.summarize_only:
        for chembl_id in targets:
            t0 = time.time()
            r = process_compound(chembl_id)
            r["wall_min"] = round((time.time() - t0) / 60.0, 2)
            print(f"  {chembl_id}: {r.get('status')} dG={r.get('dG_bind_kcal_mol', 'n/a')} wall={r['wall_min']}min")
            results.append(r)
            # Save intermediate
            (BENCH_BASE / "benchmark_intermediate.json").write_text(json.dumps(results, indent=2))
    else:
        # Read existing — check both mss (current) and legacy paths
        for chembl_id in targets:
            for prod_dir_name in ("abfe_production_mss", "abfe_production"):
                d = BENCH_BASE / chembl_id / prod_dir_name / "dG_bind.json"
                if d.exists():
                    data = json.loads(d.read_text())
                    results.append({"chembl_id": chembl_id, "status": "ok", **data})
                    break

    summary = {
        "phase": "ABFE benchmark vs ChEMBL MMP-1 IC50",
        "subset": args.subset,
        "compounds_attempted": len(targets),
        "results": results,
        "stats": aggregate_results(results, manifest),
    }
    (BENCH_BASE / "benchmark_summary.json").write_text(json.dumps(summary, indent=2))
    print("\n=== SUMMARY ===")
    if "stats" in summary and "spearman" in summary["stats"]:
        s = summary["stats"]
        print(f"  n={s['n']}  Spearman ρ={s['spearman']['rho']:.3f} (p={s['spearman']['p_value']:.4f})")
        print(f"           Pearson r={s['pearson']['r']:.3f} (p={s['pearson']['p_value']:.4f})")
        print(f"           MAE={s['mae_kcal_mol']:.2f} kcal/mol  RMSE={s['rmse_kcal_mol']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
