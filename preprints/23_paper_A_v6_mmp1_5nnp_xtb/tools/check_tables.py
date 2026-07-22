#!/usr/bin/env python3
"""check_tables.py - validate tables in a manuscript markdown/latex file.

Detects 4 categories of "table truncation":
  1. Markdown table: header column count vs data row column count mismatch.
  2. Body claim "Table N shows / contains / lists M ..." but actual row count != M.
  3. LaTeX \\begin{tabular}{spec} column spec count vs row & count mismatch.
  4. Explicit truncation markers ("...", "[truncated]", "(truncated)") inside table.

Exit codes:
  0 - clean
  1 - at least one issue found

Usage:
  python tools/check_tables.py manuscript_v0.2.md
  python tools/check_tables.py manuscript_v0.2.md --quiet   # only failures
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ----- helpers ---------------------------------------------------------------


def _count_md_cols(line: str) -> int:
    """Count columns in a markdown table row.

    A markdown row looks like: | a | b | c |
    Strip leading/trailing pipes, then split on un-escaped pipes.
    """
    s = line.strip()
    if not s.startswith("|"):
        return 0
    # Strip leading/trailing pipe
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    # Split on '|' but not '\|'
    parts = re.split(r"(?<!\\)\|", s)
    return len(parts)


def _is_md_separator(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    # Cells must be only -, :, spaces
    cells = [c.strip() for c in s.strip("|").split("|")]
    if not cells:
        return False
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def _tabular_col_count(spec: str) -> int:
    """Count column count from LaTeX tabular column spec.

    Spec characters that consume a column: l c r p m b X.
    p{...}, m{...}, b{...} count as 1 each.
    Vertical bars '|' and '@{...}' are not columns.
    """
    spec = spec.strip()
    n = 0
    i = 0
    while i < len(spec):
        ch = spec[i]
        if ch in "lcrX":
            n += 1
            i += 1
        elif ch in "pmb":
            n += 1
            i += 1
            # skip {...}
            if i < len(spec) and spec[i] == "{":
                depth = 1
                i += 1
                while i < len(spec) and depth:
                    if spec[i] == "{":
                        depth += 1
                    elif spec[i] == "}":
                        depth -= 1
                    i += 1
        elif ch == "*":
            # *{n}{cols}
            i += 1
            if i < len(spec) and spec[i] == "{":
                end = spec.find("}", i)
                if end == -1:
                    break
                try:
                    repeat = int(spec[i + 1 : end])
                except ValueError:
                    repeat = 1
                i = end + 1
                # consume nested {cols}
                if i < len(spec) and spec[i] == "{":
                    end2 = spec.find("}", i)
                    if end2 == -1:
                        break
                    sub = spec[i + 1 : end2]
                    n += repeat * _tabular_col_count(sub)
                    i = end2 + 1
        elif ch == "@":
            # @{...} - skip braces
            i += 1
            if i < len(spec) and spec[i] == "{":
                depth = 1
                i += 1
                while i < len(spec) and depth:
                    if spec[i] == "{":
                        depth += 1
                    elif spec[i] == "}":
                        depth -= 1
                    i += 1
        else:
            # | or whitespace etc
            i += 1
    return n


def _count_latex_row_cols(row: str) -> int:
    """Count & separators (+1 = column count) in a LaTeX tabular row body.

    Ignores escaped \\& . Stops at \\\\ if present (caller already removed it).
    """
    # Remove escaped ampersands
    cleaned = re.sub(r"\\&", "", row)
    return cleaned.count("&") + 1


# ----- data structures -------------------------------------------------------


@dataclass
class TableFinding:
    file: str
    line: int
    kind: str  # "md_colcount", "md_truncate", "latex_colcount", "latex_truncate", "body_count"
    message: str


@dataclass
class TableRecord:
    start_line: int
    end_line: int
    kind: str  # "markdown" | "latex"
    data_row_count: int = 0
    label: Optional[str] = None  # for LaTeX \label{...}
    caption: Optional[str] = None


# ----- detectors -------------------------------------------------------------


def scan_markdown_tables(text: str, path: str) -> Tuple[List[TableFinding], List[TableRecord]]:
    findings: List[TableFinding] = []
    records: List[TableRecord] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # candidate header: row that starts with |, next line is separator
        if stripped.startswith("|") and i + 1 < len(lines) and _is_md_separator(lines[i + 1]):
            header_cols = _count_md_cols(line)
            sep_cols = _count_md_cols(lines[i + 1])
            start_line = i + 1  # 1-indexed
            if header_cols != sep_cols:
                findings.append(
                    TableFinding(
                        path,
                        start_line + 1,
                        "md_colcount",
                        f"markdown table separator has {sep_cols} cols vs header {header_cols}",
                    )
                )
            j = i + 2
            data_rows = 0
            while j < len(lines) and lines[j].strip().startswith("|"):
                cols = _count_md_cols(lines[j])
                if cols != header_cols:
                    findings.append(
                        TableFinding(
                            path,
                            j + 1,
                            "md_colcount",
                            f"row has {cols} cols, header has {header_cols}",
                        )
                    )
                # truncation marker
                body = lines[j].lower()
                if "[truncated]" in body or "(truncated)" in body:
                    findings.append(
                        TableFinding(
                            path,
                            j + 1,
                            "md_truncate",
                            "explicit truncation marker inside table row",
                        )
                    )
                # ellipsis-only row
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if cells and all(c in {"...", "…", "..."} for c in cells if c):
                    findings.append(
                        TableFinding(
                            path,
                            j + 1,
                            "md_truncate",
                            "ellipsis-only row (table appears truncated)",
                        )
                    )
                data_rows += 1
                j += 1
            records.append(
                TableRecord(
                    start_line=start_line,
                    end_line=j,
                    kind="markdown",
                    data_row_count=data_rows,
                )
            )
            i = j
        else:
            i += 1
    return findings, records


def scan_latex_tabular(text: str, path: str) -> Tuple[List[TableFinding], List[TableRecord]]:
    findings: List[TableFinding] = []
    records: List[TableRecord] = []
    lines = text.splitlines()
    # Find tabular and longtable blocks
    pat_begin = re.compile(r"\\begin\{(tabular\*?|longtable|tabularx)\}\s*(?:\[[^\]]*\])?\s*(?:\{[^}]*\}\s*)?\{([^}]*)\}")
    pat_end = re.compile(r"\\end\{(tabular\*?|longtable|tabularx)\}")

    i = 0
    while i < len(lines):
        m = pat_begin.search(lines[i])
        if not m:
            i += 1
            continue
        env_name = m.group(1)
        spec = m.group(2)
        expected_cols = _tabular_col_count(spec)
        start_line = i + 1
        # collect until \end
        body_lines: List[Tuple[int, str]] = []
        j = i + 1
        while j < len(lines) and not pat_end.search(lines[j]):
            body_lines.append((j + 1, lines[j]))
            j += 1
        end_line = j + 1 if j < len(lines) else j
        # Build rows by splitting joined body on \\
        joined = "\n".join(b[1] for b in body_lines)
        # Each row terminated by \\ (LaTeX)
        # Use regex split that captures positions
        raw_rows = re.split(r"\\\\(?:\[[^\]]*\])?", joined)
        data_row_count = 0
        # We track which source line each row started on (approx) for reporting
        line_cursor = i + 2  # first body line is i+1 (0-indexed) -> 1-indexed = i+2
        for raw in raw_rows:
            stripped = raw.strip()
            if not stripped:
                line_cursor += raw.count("\n")
                continue
            # Skip pure latex directives like \hline, \midrule, \toprule, \bottomrule
            cleaned_for_check = stripped
            # Remove \hline / \toprule / \midrule / \bottomrule / \cmidrule{...}
            cleaned_for_check = re.sub(
                r"\\(hline|toprule|midrule|bottomrule|cmidrule(\[[^\]]*\])?(\{[^}]*\})?)",
                "",
                cleaned_for_check,
            )
            # Remove \multicolumn{cols}{spec}{content} - these consume "cols" columns
            # Count their contribution before stripping
            mc_pat = re.compile(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{")
            mc_extra = 0
            for mc in mc_pat.finditer(cleaned_for_check):
                mc_extra += int(mc.group(1)) - 1  # -1 because multicolumn contributes 1 & already
            cleaned_for_check2 = mc_pat.sub("", cleaned_for_check)
            # Also strip multirow
            cleaned_for_check2 = re.sub(r"\\multirow\{[^}]*\}\{[^}]*\}\{", "", cleaned_for_check2)
            if not cleaned_for_check2.strip():
                line_cursor += raw.count("\n")
                continue
            row_cols = _count_latex_row_cols(cleaned_for_check2) + mc_extra
            if row_cols != expected_cols:
                # tolerate header-only with only rule (already skipped above)
                findings.append(
                    TableFinding(
                        path,
                        line_cursor,
                        "latex_colcount",
                        f"tabular row has {row_cols} cols (spec={expected_cols}) - row: {stripped[:80]}",
                    )
                )
            if "[truncated]" in raw.lower() or "(truncated)" in raw.lower():
                findings.append(
                    TableFinding(path, line_cursor, "latex_truncate", "explicit truncation marker"),
                )
            if re.search(r"^\s*\\?\\?\.\.\.\s*(&\s*\\?\\?\.\.\.\s*)*$", stripped):
                findings.append(
                    TableFinding(path, line_cursor, "latex_truncate", "ellipsis-only row"),
                )
            data_row_count += 1
            line_cursor += raw.count("\n")
        records.append(
            TableRecord(
                start_line=start_line, end_line=end_line, kind="latex", data_row_count=data_row_count
            )
        )
        i = end_line
    return findings, records


def scan_body_counts(text: str, path: str, md_records: List[TableRecord]) -> List[TableFinding]:
    """Look for body claims like 'Table 3 lists 17 ...' and compare to nearest table.

    Heuristic: pair each claim with the next markdown/latex table after the
    claim's line; warn if counts mismatch (allow off-by-one to tolerate header row
    treated as a data row).
    """
    findings: List[TableFinding] = []
    # Combine markdown + latex for proximity matching (caller passes md_records;
    # we'd ideally use both, but markdown is the primary format here)
    records = md_records
    # Patterns: "Table 3 lists 17", "Table 3 shows N", "Table 3 contains N",
    # "Table 3 reports N", "all N <entries> in Table 3"
    patterns = [
        re.compile(r"[Tt]able\s+([A-Za-z0-9]+)[^.]{0,60}?(?:lists?|shows?|contains?|reports?|summari[sz]es?|presents?)\s+(\d{1,4})", re.MULTILINE),
        re.compile(r"all\s+(\d{1,4})\s+[^.]{0,40}?[Tt]able\s+([A-Za-z0-9]+)", re.MULTILINE),
    ]
    lines = text.splitlines()
    # Build a position->line map
    offsets: List[int] = [0]
    for ln in lines:
        offsets.append(offsets[-1] + len(ln) + 1)

    def offset_to_line(off: int) -> int:
        # binary search
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if offsets[mid] <= off:
                lo = mid + 1
            else:
                hi = mid
        return lo

    for pat in patterns:
        for m in pat.finditer(text):
            line_no = offset_to_line(m.start())
            # extract number and table id depending on group order
            groups = m.groups()
            try:
                if groups[0].isdigit():
                    claimed_n = int(groups[0])
                    table_id = groups[1]
                else:
                    table_id = groups[0]
                    claimed_n = int(groups[1])
            except (ValueError, IndexError):
                continue
            # find nearest table at or after this line
            nearest = None
            for r in records:
                if r.start_line >= line_no:
                    nearest = r
                    break
            if nearest is None:
                continue
            actual = nearest.data_row_count
            # Tolerate +/-1 (header counted or not)
            if abs(actual - claimed_n) > 1:
                findings.append(
                    TableFinding(
                        path,
                        line_no,
                        "body_count",
                        f"text claims Table {table_id} has {claimed_n} entries, "
                        f"nearest table (line {nearest.start_line}) has {actual} data rows",
                    )
                )
    return findings


# ----- main ------------------------------------------------------------------


def check_file(path: Path, quiet: bool = False) -> List[TableFinding]:
    text = path.read_text(encoding="utf-8")
    findings: List[TableFinding] = []
    md_findings, md_records = scan_markdown_tables(text, str(path))
    findings.extend(md_findings)
    lx_findings, lx_records = scan_latex_tabular(text, str(path))
    findings.extend(lx_findings)
    body_findings = scan_body_counts(text, str(path), md_records + lx_records)
    findings.extend(body_findings)
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="manuscript file(s) to check (.md or .tex)")
    ap.add_argument("--quiet", action="store_true", help="suppress per-file 'OK' lines")
    args = ap.parse_args()

    total = 0
    for p in args.paths:
        path = Path(p)
        if not path.is_file():
            print(f"[ERROR] {p}: not a file", file=sys.stderr)
            total += 1
            continue
        findings = check_file(path)
        if findings:
            for f in findings:
                print(f"{f.file}:{f.line}: [{f.kind}] {f.message}")
            total += len(findings)
        elif not args.quiet:
            print(f"{p}: OK (no table issues)")
    if total:
        print(f"\n{total} table issue(s) found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
