# paper_A v6 / paper_B v1 manuscript validation tools

## check_tables.py

Pre-publish gate that detects "truncated table" bugs in manuscript files
(markdown and LaTeX `tabular` / `longtable` / `tabularx`).

### What it catches

1. **Markdown column-count drift** — header row has 5 `|`-separated cells,
   data row has 4 (typical copy/paste truncation).
2. **Body↔table count mismatch** — body claims `Table 3 lists 17 compounds`
   but the nearest markdown/LaTeX table has 14 data rows.
3. **LaTeX `tabular` column-spec mismatch** — `\begin{tabular}{ccccc}`
   declares 5 columns but rows only have 4 `&` separators (= 4 cells).
   Handles `p{...}`, `m{...}`, `b{...}`, `*{n}{spec}` repeated specs and
   `\multicolumn{cols}{...}{...}` width-adjusted cells.
4. **Explicit truncation markers** — rows containing `[truncated]`,
   `(truncated)`, or ellipsis-only `...` cells.

### Usage

```bash
# from the paper directory
python3 tools/check_tables.py manuscript_v0.2.md

# or supply multiple files at once
python3 tools/check_tables.py manuscript_v0.2.md ../24_paper_B_v1_boltz_xtb_rescue_zn_mmp1/manuscript_skeleton_v0.1.md

# quiet mode (only print failing files)
python3 tools/check_tables.py --quiet manuscript_v0.2.md
```

### Exit codes

- `0` — every table looks consistent (publish-safe).
- `1` — at least one issue reported on stdout / stderr.

### When to run

- **Before every Zenodo / bioRxiv / preprint server submission.**
- **Before tagging a manuscript v_N.M release.**
- The 2026-05-30 paper_A v6 publish checklist includes
  `python3 tools/check_tables.py manuscript_v0.2.md` as a required step
  (must exit 0 before upload).

### Examples of caught bugs

`paper_B_xtb_robustness/manuscript.tex` (legacy, 2026-05) — the §Results
top-K IoU comparison declares `\begin{tabular}{ccccc}` (5 columns) but
every data row only emits 4 `&`-separated cells. The 5th column was
likely a `Boltz $\cap$ xtb-HOMO` placeholder that was renamed but never
backfilled.

### Caveats

- The body-claim heuristic ("Table N lists M") is conservative and only
  pairs with the next markdown/LaTeX table after the claim line. If your
  manuscript references a table N pages earlier and the next table on
  the page is unrelated, you may see a false positive — investigate, then
  ignore if benign.
- LaTeX detection currently handles single-environment `tabular` blocks;
  it does not parse nested `\begin{tabular}` inside `\multicolumn{}{...}{}`
  cells (rare in practice).
