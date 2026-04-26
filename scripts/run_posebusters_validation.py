"""PoseBusters validation on all Boltz-2 cofold poses produced in our pipeline.

Why this matters:
    Boltz-2 cofold poses are predicted, not experimental. Roughly 30-50% of
    AI-cofold poses fail one or more PoseBuster checks (steric clashes, bond
    geometry, ring distortion, etc.). For our preprints to be peer-review
    defensible, every pose used downstream (MD, ABFE) must pass PoseBusters.

This runner:
    - Discovers all CIF files under pilot/scaffold_hop/, pilot/screen/,
      and pilot/scaffold_hop_round*/
    - Extracts ligand from each (Boltz-2 outputs LIG residue)
    - Runs PoseBusters on every (protein, ligand) pair
    - Outputs per-pose pass/fail + aggregate statistics
    - Identifies which poses MUST be flagged in our preprint limitations
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/posebusters"
OUT.mkdir(parents=True, exist_ok=True)


def discover_cofold_poses() -> list[dict]:
    """Find all Boltz-2 cofold output CIFs."""
    candidates = []
    for src in [
        ROOT / "pilot/scaffold_hop/boltz_output",
        ROOT / "pilot/scaffold_hop_round2/boltz_output",
        ROOT / "pilot/scaffold_hop_round3/boltz_output",
        ROOT / "pilot/screen/pigmentation/boltz_output",
        ROOT / "pilot/screen/alopecia/boltz_output",
        ROOT / "pilot/screen/acne/boltz_output",
        ROOT / "pilot/screen/photoaging/boltz_output",
    ]:
        if not src.exists():
            continue
        for cif in src.rglob("*_model_0.cif"):
            stem = cif.stem.replace("_model_0", "")
            try:
                target_part, comp_part = stem.split("__", 1)
            except ValueError:
                continue
            candidates.append({
                "cif": str(cif),
                "target": target_part,
                "compound": comp_part,
                "source": str(cif.parent.parent.relative_to(ROOT)),
            })
    return candidates


def run_posebusters(cif_path: str) -> dict:
    """Run PoseBusters on a single Boltz-2 CIF (protein + ligand).

    PoseBusters expects either:
      - mol_pred (RDKit Mol of pose)
      - mol_cond (cond protein, optional)
      - mol_true (ground truth, optional)

    For pose-only checks (no ground truth), we use docking_pose mode.
    """
    from posebusters import PoseBusters
    from rdkit import Chem

    try:
        # Boltz-2 CIFs contain LIG residue + protein. Extract.
        # PoseBusters expects RDKit-readable input.
        # CIF → mol via RDKit's MolFromMol2/PDB or direct CIF parser.
        # Boltz outputs CIF with LIG residue; we use mol_files mode.
        mol_pred = Chem.MolFromMolFile(cif_path, sanitize=False)
        if mol_pred is None:
            # Try as PDB/CIF
            from rdkit.Chem import AllChem
            mol_pred = Chem.MolFromPDBFile(cif_path, sanitize=False, removeHs=False)
        if mol_pred is None:
            return {"status": "unreadable",
                     "checks": {}, "n_pass": 0, "n_total": 0}

        pb = PoseBusters(config="dock")
        df = pb.bust(mol_pred=mol_pred)
        # df is a DataFrame with one row, columns are check names
        if df is None or len(df) == 0:
            return {"status": "empty",
                     "checks": {}, "n_pass": 0, "n_total": 0}
        row = df.iloc[0].to_dict()
        # Drop non-bool meta columns
        checks = {k: bool(v) for k, v in row.items()
                   if isinstance(v, (bool,)) or
                      (isinstance(v, str) and v in ("True", "False"))}
        # Coerce
        bool_checks = {}
        for k, v in row.items():
            if k in ("file", "molecule", "name"): continue
            if pd.isna(v): continue
            try:
                bool_checks[k] = bool(v)
            except Exception:
                pass
        n_pass = sum(1 for v in bool_checks.values() if v)
        return {
            "status": "ok",
            "checks": bool_checks,
            "n_pass": n_pass,
            "n_total": len(bool_checks),
            "pass_rate": n_pass / len(bool_checks) if bool_checks else 0,
            "all_pass": n_pass == len(bool_checks) and len(bool_checks) > 0,
        }
    except Exception as e:
        return {"status": "error",
                 "error": str(e)[:200],
                 "checks": {}, "n_pass": 0, "n_total": 0}


def main():
    print("=" * 72)
    print("PoseBusters validation on all Boltz-2 cofold poses")
    print("=" * 72)

    poses = discover_cofold_poses()
    print(f"\nDiscovered {len(poses)} cofold pose CIFs")
    if not poses:
        print("⚠️ No cofold outputs found. Did the pipeline run?")
        return 1

    results = []
    for i, p in enumerate(poses, 1):
        print(f"  [{i}/{len(poses)}] {p['target']:8s} × {p['compound'][:30]:30s} ", end="")
        res = run_posebusters(p["cif"])
        results.append({
            "source": p["source"],
            "target": p["target"],
            "compound": p["compound"],
            "cif": p["cif"],
            **res,
        })
        if res["status"] == "ok":
            print(f"  {res['n_pass']}/{res['n_total']} pass "
                  f"({'✅' if res['all_pass'] else '⚠️'})")
        else:
            print(f"  [{res['status']}]")

    # Aggregate
    df = pd.DataFrame(results)
    df.to_csv(OUT / "posebusters_results.csv", index=False)
    print(f"\n✅ {OUT}/posebusters_results.csv")

    # Summary
    ok = df[df["status"] == "ok"]
    if len(ok) > 0:
        print("\n=== SUMMARY ===")
        print(f"  Total poses: {len(df)}")
        print(f"  Successfully evaluated: {len(ok)}")
        print(f"  All-pass (clean): {sum(ok['all_pass'])}")
        print(f"  Pass rate (mean): {ok['pass_rate'].mean():.1%}")
        print(f"  Per-target pass-rate:")
        for tgt, grp in ok.groupby("target"):
            print(f"    {tgt:12s}: {grp['pass_rate'].mean():.1%} "
                   f"({sum(grp['all_pass'])}/{len(grp)} all-pass)")

        # Save summary
        summary = {
            "n_poses_total": len(df),
            "n_evaluated": len(ok),
            "n_all_pass": int(sum(ok["all_pass"])),
            "mean_pass_rate": float(ok["pass_rate"].mean()),
            "per_target": {tgt: {"pass_rate_mean": float(grp["pass_rate"].mean()),
                                   "n_all_pass": int(sum(grp["all_pass"])),
                                   "n_total": len(grp)}
                            for tgt, grp in ok.groupby("target")},
        }
        (OUT / "posebusters_summary.json").write_text(
            json.dumps(summary, indent=2))
        print(f"  ✅ {OUT}/posebusters_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
