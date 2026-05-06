"""R16 topical chromanol anchor triad 200 ns MD.

Extends the best TGFB1, DCT, and TYR R16 pairs to 200 ns after the 100 ns
anchor triad is complete and stable.

Output:
  pilot/md_r16_chromanol_anchor_triad_200ns/summary.json
  pilot/md_r16_chromanol_anchor_triad_200ns/summary.csv
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r16_chromanol_anchor_triad_200ns"
OUT.mkdir(parents=True, exist_ok=True)
COFOLD_CSV = ROOT / "pilot/cpu_meaningful/r16_chromanol_topical_cofold.csv"
RESULT_ROOT = (
    ROOT
    / "pilot/cpu_meaningful/output_r16_chromanol_topical"
    / "boltz_results_inputs_r16_chromanol_topical"
    / "predictions"
)
TARGETS = ["tgfb1", "dct", "tyr"]


def load_runner():
    path = ROOT / "scripts/run_r16_chromanol_topical_top3_md.py"
    spec = importlib.util.spec_from_file_location("r16_top3_md", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    mod.OUT.mkdir(parents=True, exist_ok=True)
    return mod


def existing_ok() -> dict[str, dict[str, object]]:
    path = OUT / "summary.json"
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text())
    except Exception:
        return {}
    return {
        str(row.get("job_id")): row
        for row in rows
        if row.get("status") == "ok" and row.get("job_id")
    }


def build_jobs(runner) -> list[dict[str, object]]:
    df = pd.read_csv(COFOLD_CSV)
    jobs: list[dict[str, object]] = []
    for target in TARGETS:
        subset = df[df["target"].str.lower().eq(target)]
        if subset.empty:
            continue
        row = subset.sort_values("affinity_probability_binary", ascending=False).iloc[0]
        job_id = str(row["job_id"])
        analog_id = str(row["analog_id"])
        cif = RESULT_ROOT / job_id / f"{job_id}_model_0.cif"
        jobs.append(
            {
                "name": f"{job_id}__{runner.clean_name(analog_id)}__200ns",
                "job_id": job_id,
                "analog_id": analog_id,
                "target": target,
                "cif": str(cif.relative_to(ROOT)),
                "smiles": str(row["smiles"]),
                "topical_followup_score": row.get("topical_followup_score"),
                "logP": row.get("logP"),
                "QED": row.get("QED"),
                "gap_eV": row.get("gap_eV"),
                "affinity_probability_binary": row.get("affinity_probability_binary"),
                "affinity_pred_value": row.get("affinity_pred_value"),
            }
        )
    return jobs


def main() -> int:
    runner = load_runner()
    jobs = build_jobs(runner)
    done = existing_ok()
    results: list[dict[str, object]] = list(done.values())

    print("R16 topical chromanol anchor triad 200 ns MD")
    print(
        pd.DataFrame(jobs)[
            ["job_id", "analog_id", "target", "affinity_probability_binary", "cif"]
        ].to_string(index=False)
    )

    for job in jobs:
        if str(job["job_id"]) in done:
            print(f"skip existing ok: {job['job_id']}")
            continue
        try:
            result = runner.run_md(job, ns=200.0)
        except Exception as exc:
            import traceback

            traceback.print_exc()
            result = {
                "name": job["name"],
                "job_id": job["job_id"],
                "analog_id": job["analog_id"],
                "target": job["target"],
                "status": f"error:{str(exc)[:200]}",
            }
        results = [row for row in results if row.get("job_id") != result.get("job_id")]
        results.append(result)
        (OUT / "summary.json").write_text(json.dumps(results, indent=2))

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\nFinal R16 topical chromanol anchor triad 200 ns summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
