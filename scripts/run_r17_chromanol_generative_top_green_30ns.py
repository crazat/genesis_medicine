"""R17 generative chromanol top green-target 30 ns MD follow-up.

This extends the same three DCT/TYR candidates selected by
run_r17_chromanol_generative_top_green_10ns.py after the 10 ns screen is
complete. Aryl-halogen candidates remain photosafety-review candidates, not
safety-positive topical leads.

Output:
  pilot/md_r17_chromanol_generative_top_green_30ns/summary.json
  pilot/md_r17_chromanol_generative_top_green_30ns/summary.csv
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r17_chromanol_generative_top_green_30ns"
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


def main() -> int:
    base = load_base()
    runner = base.load_runner()
    jobs = base.build_jobs(runner)
    done = base.existing_ok()
    results: list[dict[str, object]] = list(done.values())

    print("R17 generative chromanol top green-target 30 ns MD")
    if not jobs:
        print("No R17 cofold jobs found.")
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
        job = dict(job)
        job["name"] = str(job["name"]).replace("__10ns", "__30ns")
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
    print("\nFinal R17 generative chromanol top green-target 30 ns summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
