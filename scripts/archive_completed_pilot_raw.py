"""Archive completed pilot MD raw outputs to D: while keeping local summaries.

The script is intentionally conservative:
- only archives top-level `pilot/md_*` directories with a summary file;
- skips active paths mentioned by running processes;
- mirrors the full directory to the archive first;
- validates source->archive rsync before deleting local raw subdirectories;
- keeps local summary.json/summary.csv and an archive marker.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"
DEFAULT_ARCHIVE_ROOT = Path("/mnt/d/genesis_archive/genesis_medicine")
MANIFEST = PILOT / "completed_pilot_raw_archive_manifest.jsonl"
LOG = PILOT / "completed_pilot_raw_archive.log"

KEEP_TOP_LEVEL = {
    "summary.json",
    "summary.csv",
    "README.md",
    "ARCHIVED_TO_D.txt",
    ".archive_manifest.json",
}


def log(message: str) -> None:
    line = f"[{datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')}] {message}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def du_kib(path: Path) -> int:
    proc = run(["du", "-sk", str(path)], timeout=300)
    if proc.returncode != 0:
        return -1
    try:
        return int(proc.stdout.split()[0])
    except Exception:
        return -1


def running_command_lines() -> str:
    proc = run(["pgrep", "-af", "."], timeout=30)
    return proc.stdout if proc.returncode == 0 else ""


def has_summary(path: Path) -> bool:
    return (path / "summary.json").exists() or (path / "summary.csv").exists()


def already_archived(path: Path) -> bool:
    return (path / "ARCHIVED_TO_D.txt").exists()


def local_raw_children(path: Path) -> list[Path]:
    raw: list[Path] = []
    for child in path.iterdir():
        if child.name in KEEP_TOP_LEVEL:
            continue
        if child.is_dir() and not child.is_symlink():
            raw.append(child)
    return raw


def select_candidates(min_gb: float, max_count: int | None) -> list[Path]:
    commands = running_command_lines()
    rows: list[tuple[int, Path]] = []
    for path in PILOT.iterdir():
        if not path.is_dir() or not path.name.startswith("md_"):
            continue
        if already_archived(path) or not has_summary(path):
            continue
        if not local_raw_children(path):
            continue
        rel = str(path.relative_to(ROOT))
        if rel in commands or str(path) in commands:
            log(f"skip active-looking path in process table: {rel}")
            continue
        size = du_kib(path)
        if size < int(min_gb * 1024 * 1024):
            continue
        rows.append((size, path))
    rows.sort(reverse=True)
    selected = [path for _, path in rows]
    if max_count is not None:
        selected = selected[:max_count]
    return selected


def rsync_copy(src: Path, dst: Path, bwlimit_kb: int, dry_run: bool) -> int:
    dst.mkdir(parents=True, exist_ok=True)
    cmd = [
        "rsync",
        "-a",
        "--human-readable",
        "--info=stats1",
    ]
    if bwlimit_kb > 0:
        cmd.append(f"--bwlimit={bwlimit_kb}")
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend([f"{src}/", f"{dst}/"])
    proc = run(cmd)
    if proc.stdout.strip():
        log(proc.stdout.strip()[-4000:])
    return proc.returncode


def rsync_validate(src: Path, dst: Path, bwlimit_kb: int) -> bool:
    cmd = ["rsync", "-a", "--dry-run", "--itemize-changes"]
    if bwlimit_kb > 0:
        cmd.append(f"--bwlimit={bwlimit_kb}")
    cmd.extend([f"{src}/", f"{dst}/"])
    proc = run(cmd)
    if proc.returncode != 0:
        log(f"validation rsync failed for {src}: {proc.stdout.strip()[-2000:]}")
        return False
    changes = [line for line in proc.stdout.splitlines() if line.strip()]
    if changes:
        log(f"validation found uncopied changes for {src}: {changes[:20]}")
        return False
    return True


def write_marker(src: Path, dst: Path, before_kib: int, archived_children: list[str]) -> None:
    now = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    marker = {
        "timestamp": now,
        "source": str(src.relative_to(ROOT)),
        "archive": str(dst),
        "source_size_gb_before": round(before_kib / 1024 / 1024, 3),
        "archived_children": archived_children,
        "local_kept": sorted(KEEP_TOP_LEVEL),
        "restore_hint": f"rsync -a '{dst}/' '{src}/'",
    }
    (src / ".archive_manifest.json").write_text(json.dumps(marker, indent=2), encoding="utf-8")
    (src / "ARCHIVED_TO_D.txt").write_text(
        "\n".join(
            [
                "Completed raw outputs archived to D:.",
                f"timestamp: {now}",
                f"archive: {dst}",
                f"restore: rsync -a '{dst}/' '{src}/'",
                "Local summaries were retained for planner/manuscript evidence.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    with MANIFEST.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(marker, ensure_ascii=True) + "\n")


def archive_one(src: Path, archive_root: Path, bwlimit_kb: int, dry_run: bool) -> bool:
    rel = src.relative_to(ROOT)
    dst = archive_root / rel
    before = du_kib(src)
    raw_children = local_raw_children(src)
    raw_names = [child.name for child in raw_children]
    log(f"archive start: {rel} size={before / 1024 / 1024:.2f}GB raw_children={len(raw_children)}")
    rc = rsync_copy(src, dst, bwlimit_kb=bwlimit_kb, dry_run=dry_run)
    if rc != 0:
        log(f"archive copy failed: {rel} rc={rc}")
        return False
    if dry_run:
        log(f"dry-run complete: {rel}")
        return True
    if not rsync_validate(src, dst, bwlimit_kb=bwlimit_kb):
        log(f"archive validation failed; local raw retained: {rel}")
        return False
    write_marker(src, dst, before, raw_names)
    for child in raw_children:
        if child.exists() and child.is_dir() and not child.is_symlink() and child.parent == src:
            shutil.rmtree(child)
    after = du_kib(src)
    log(
        f"archive done: {rel} local_before={before / 1024 / 1024:.2f}GB "
        f"local_after={after / 1024 / 1024:.4f}GB archive={dst}"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-root", default=str(DEFAULT_ARCHIVE_ROOT))
    parser.add_argument("--min-gb", type=float, default=5.0)
    parser.add_argument("--max-count", type=int, default=0, help="0 means no limit")
    parser.add_argument(
        "--bwlimit-kb",
        type=int,
        default=int(os.environ.get("GENESIS_ARCHIVE_RSYNC_BWLIMIT_KB", "80000")),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    archive_root = Path(args.archive_root)
    if not archive_root.exists() and not args.dry_run:
        archive_root.mkdir(parents=True, exist_ok=True)
    max_count = None if args.max_count <= 0 else args.max_count
    candidates = select_candidates(min_gb=args.min_gb, max_count=max_count)
    log(
        f"selected {len(candidates)} completed md_* directories "
        f"min_gb={args.min_gb} archive_root={archive_root} dry_run={args.dry_run}"
    )
    ok = 0
    for src in candidates:
        if archive_one(src, archive_root, bwlimit_kb=args.bwlimit_kb, dry_run=args.dry_run):
            ok += 1
    log(f"archive run complete: ok={ok}/{len(candidates)}")
    return 0 if ok == len(candidates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
