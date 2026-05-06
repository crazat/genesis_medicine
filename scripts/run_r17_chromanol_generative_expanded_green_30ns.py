"""R17 expanded green-target 30 ns MD follow-up.

This extends the three non-duplicate safety-green DCT/TYR candidates that
completed run_r17_chromanol_generative_expanded_green_10ns.py.

Output:
  pilot/md_r17_chromanol_generative_expanded_green_30ns/summary.json
  pilot/md_r17_chromanol_generative_expanded_green_30ns/summary.csv
"""
from __future__ import annotations

import glob
import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CPU_OUT = ROOT / "pilot/cpu_meaningful"
PREV = ROOT / "pilot/md_r17_chromanol_generative_expanded_green_10ns/summary.json"
OUT = ROOT / "pilot/md_r17_chromanol_generative_expanded_green_30ns"
OUT.mkdir(parents=True, exist_ok=True)


def load_base():
    path = ROOT / "scripts/run_r17_chromanol_generative_top_green_10ns.py"
    spec = importlib.util.spec_from_file_location("r17_green_10ns", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    mod.OUT.mkdir(parents=True, exist_ok=True)
    return mod


def previous_ok_rows() -> list[dict[str, object]]:
    if not PREV.exists() or PREV.stat().st_size == 0:
        return []
    rows = json.loads(PREV.read_text())
    if not isinstance(rows, list):
        return []
    return [row for row in rows if row.get("status") == "ok" and row.get("job_id")]


def load_cofold_rows() -> pd.DataFrame:
    files = sorted(glob.glob(str(CPU_OUT / "r17_chromanol_generative_batch*_cofold.csv")))
    if not files:
        return pd.DataFrame()
    return pd.concat(
        [pd.read_csv(path).assign(source_file=path) for path in files],
        ignore_index=True,
    )


def build_jobs(base) -> list[dict[str, object]]:
    prev_rows = previous_ok_rows()
    df = load_cofold_rows()
    if df.empty:
        return []
    by_job = {str(row["job_id"]): row for _, row in df.iterrows()}
    jobs: list[dict[str, object]] = []
    for prev in prev_rows:
        job_id = str(prev["job_id"])
        source = by_job.get(job_id)
        if source is None:
            continue
        cif = base.prediction_cif(source)
        job = dict(prev)
        job["name"] = str(job["name"]).replace("__10ns", "__30ns")
        job["cif"] = str(cif.relative_to(ROOT))
        jobs.append(job)
    return jobs


def main() -> int:
    base = load_base()
    runner = base.load_runner()
    jobs = build_jobs(base)
    done = base.existing_ok()
    results: list[dict[str, object]] = list(done.values())

    print("R17 expanded green-target 30 ns MD")
    if not jobs:
        print("No completed expanded-green 10 ns jobs found.")
        return 0
    print(
        pd.DataFrame(jobs)[
            [
                "job_id",
                "analog_id",
                "target",
                "affinity_probability_binary",
                "photosafety_proxy",
                "cif",
            ]
        ].to_string(index=False)
    )

    for job in jobs:
        if str(job["job_id"]) in done:
            print(f"skip existing ok: {job['job_id']}")
            continue
        try:
            result = runner.run_md(job, ns=30.0)
            result["photosafety_proxy"] = job.get("photosafety_proxy")
            result["local_design_priority"] = job.get("local_design_priority")
        except Exception as exc:
            import traceback

            traceback.print_exc()
            result = {
                "name": job["name"],
                "job_id": job["job_id"],
                "analog_id": job["analog_id"],
                "target": job["target"],
                "status": f"error:{str(exc)[:200]}",
                "photosafety_proxy": job.get("photosafety_proxy"),
            }
        results = [row for row in results if row.get("job_id") != result.get("job_id")]
        results.append(result)
        (OUT / "summary.json").write_text(json.dumps(results, indent=2))

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\nFinal R17 expanded green-target 30 ns summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
