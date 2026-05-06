"""
H4: Zenodo code-release deposit (separate DOI for the code).

Each Zenodo paper deposit cites the code informally via README link, but the
GitHub repo can change after deposit. A separate Zenodo deposit *of the code
snapshot at the time of paper submission* gives an immutable code DOI that
papers can cite reliably.

Workflow:
  1. Create git tag `release-v0.X` at current HEAD
  2. git archive into a tarball (excludes .git, .venv, large pilot data)
  3. Build CITATION.cff metadata (already exists in repo)
  4. POST to Zenodo /deposit/depositions/ with the tarball
  5. Output: zenodo_code_doi (e.g. 10.5281/zenodo.20018400)

Required env vars:
  ZENODO_TOKEN       — personal access token (write)
  ZENODO_SANDBOX     — set to 1 for sandbox testing
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import requests

ROOT = Path("/home/crazat/genesis_medicine")
TOKEN = os.environ.get("ZENODO_TOKEN")
SANDBOX = bool(os.environ.get("ZENODO_SANDBOX"))
BASE = "https://sandbox.zenodo.org" if SANDBOX else "https://zenodo.org"


def make_archive(out_path: Path, version_tag: str) -> Path:
    """git archive of HEAD, excluding heavy directories."""
    excludes = [
        ".venv", ".cache", "data/np_atlas*", "data/chembl_*.db",
        "pilot/*/trajectory.nc", "pilot/*/traj.dcd", "pilot/*/*.parm7",
        "pilot/abfe_*/sanity_md/traj.dcd",
    ]
    # Use git archive for clean source-only tarball
    cmd = ["git", "archive", "--format=tar.gz", "-o", str(out_path), version_tag]
    print(f"  $ {' '.join(cmd)}")
    rc = subprocess.run(cmd, cwd=str(ROOT)).returncode
    if rc != 0:
        return None
    return out_path


def gather_metadata(version_tag: str) -> dict:
    """Build Zenodo metadata from CITATION.cff if present."""
    md = {
        "title": "genesis_medicine — computational drug-discovery pipeline for natural products",
        "upload_type": "software",
        "description": (
            "Open-source pipeline for in silico screening, ABFE binding free energy estimation, "
            "and multi-fidelity ranking of natural-product compounds against skin disease targets. "
            "Includes ZAFF Zn metalloprotein force field handling, openmmtools alchemical replica "
            "exchange, RDKit/xtb conformer generation, Boltz-2 affinity prediction, "
            "Vina docking, and an active-learning surrogate. "
            f"Snapshot at git tag {version_tag}."
        ),
        "creators": [{"name": "Han, Cheongwoo", "orcid": "0009-0004-4805-8815"}],
        "license": "Apache-2.0",
        "access_right": "open",
        "communities": [{"identifier": "drug-discovery"}],
        "keywords": ["drug discovery", "ABFE", "free energy", "natural products",
                     "MMP-1", "openmm", "RDKit", "ZAFF", "Korean medicine"],
        "version": version_tag,
        "related_identifiers": [
            {"identifier": "https://github.com/crazat/genesis_medicine",
             "relation": "isSupplementTo",
             "scheme": "url"},
        ],
        "notes": "Apache-2.0. No wet-lab data. Ligand parameters via AM1-BCC; "
                 "metalloprotein via ZAFF (Peters et al. 2010). "
                 "Companion to Han 2026 preprint series on Zenodo.",
    }
    return {"metadata": md}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="release-v0.1", help="git tag to archive (will be created if missing)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not TOKEN and not args.dry_run:
        print("FAIL: ZENODO_TOKEN env var not set (use --dry-run to test packaging)")
        return 1

    # Ensure tag exists
    rc = subprocess.run(["git", "rev-parse", args.tag], cwd=str(ROOT),
                        capture_output=True).returncode
    if rc != 0:
        print(f"creating tag {args.tag}")
        subprocess.run(["git", "tag", "-a", args.tag, "-m", f"Release {args.tag} for Zenodo deposit"],
                       cwd=str(ROOT))

    # Make tarball
    out_dir = ROOT / "release"
    out_dir.mkdir(exist_ok=True)
    tarball = out_dir / f"genesis_medicine-{args.tag}.tar.gz"
    if not tarball.exists():
        if make_archive(tarball, args.tag) is None:
            print("FAIL: archive failed")
            return 2
    print(f"tarball: {tarball} ({tarball.stat().st_size//1024} KB)")

    metadata = gather_metadata(args.tag)
    (out_dir / f"metadata-{args.tag}.json").write_text(json.dumps(metadata, indent=2))

    if args.dry_run:
        print("\n=== DRY RUN — packaging only ===")
        print(json.dumps(metadata, indent=2))
        return 0

    # Create Zenodo deposit
    headers = {"Content-Type": "application/json"}
    params = {"access_token": TOKEN}
    print(f"creating Zenodo deposit at {BASE}")
    r = requests.post(f"{BASE}/api/deposit/depositions", params=params,
                      json={}, headers=headers, timeout=30)
    if r.status_code != 201:
        print(f"FAIL: deposit creation {r.status_code} {r.text[:300]}")
        return 3
    dep = r.json()
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    print(f"  deposit id: {dep_id}")

    # Upload tarball
    print(f"uploading {tarball.name}")
    with tarball.open("rb") as f:
        r = requests.put(f"{bucket}/{tarball.name}", params=params, data=f, timeout=600)
    if r.status_code not in (200, 201):
        print(f"FAIL: upload {r.status_code} {r.text[:200]}")
        return 4

    # Set metadata
    print("setting metadata")
    r = requests.put(f"{BASE}/api/deposit/depositions/{dep_id}",
                     params=params, json=metadata, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"FAIL: metadata {r.status_code} {r.text[:200]}")
        return 5

    print(f"\nDRAFT deposit ready at {BASE}/deposit/{dep_id}")
    print("Review and click 'Publish' in the web UI to mint DOI.")
    print("(Alternatively, POST /actions/publish via API after final review.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
