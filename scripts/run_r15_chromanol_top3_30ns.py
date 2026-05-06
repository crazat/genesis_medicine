"""R15 chromanol top-3 Boltz-2 targets: 30 ns MD validation.

This extends the already-completed 10 ns R15 chromanol top-3 ensemble
to 30 ns for the systemic/triple-safe path narrative.

Output:
  pilot/md_r15_chromanol_top3_30ns/summary.json
  pilot/md_r15_chromanol_top3_30ns/summary.csv
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pilot/md_r15_chromanol_top3_30ns"
OUT.mkdir(parents=True, exist_ok=True)


def load_runner():
    path = ROOT / "scripts/run_r15_chromanol_top3_md.py"
    spec = importlib.util.spec_from_file_location("r15_top3_md", path)
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
        str(row.get("target")): row
        for row in rows
        if row.get("status") == "ok" and row.get("target")
    }


def build_jobs(runner) -> list[dict[str, object]]:
    jobs = runner.build_jobs()
    for job in jobs:
        job["name"] = str(job["name"]).replace("_10ns", "_30ns")
    return jobs


def main() -> int:
    runner = load_runner()
    jobs = build_jobs(runner)
    done = existing_ok()
    results: list[dict[str, object]] = list(done.values())

    print("R15 chromanol top-3 30 ns MD")
    print(pd.DataFrame(jobs)[["target", "affinity_probability_binary", "cif"]].to_string(index=False))

    for job in jobs:
        target = str(job["target"])
        if target in done:
            print(f"skip existing ok: {target}")
            continue
        try:
            result = runner.run_md(job, ns=30.0)
        except Exception as exc:
            import traceback

            traceback.print_exc()
            result = {
                "name": job["name"],
                "target": job["target"],
                "status": f"error:{str(exc)[:200]}",
            }
        results = [row for row in results if row.get("target") != result.get("target")]
        results.append(result)
        (OUT / "summary.json").write_text(json.dumps(results, indent=2))

    df = pd.DataFrame(results)
    df.to_csv(OUT / "summary.csv", index=False)
    print("\nFinal R15 chromanol top-3 30 ns MD summary:")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
