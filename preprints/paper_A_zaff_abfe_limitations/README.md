# Paper #A — ZAFF-AMBER ABFE limitations

LaTeX source for "Limitations of ZAFF-AMBER absolute binding free energy
calculation for zinc metalloenzyme inhibitors: a replicate-pair analysis
on MMP-1." Target submission: J. Chem. Theory Comput. (JCTC) /
J. Chem. Inf. Model. (JCIM) / RSC Digital Discovery.

## Files

- `manuscript.tex` — main document (~700 lines)
- `refs.bib` — BibTeX, 11 entries
- `figures/` — placeholder; populate with the four headline plots
  (see TODOs in §4)

## Compile

```bash
cd preprints/paper_A_zaff_abfe_limitations
pdflatex manuscript
bibtex manuscript
pdflatex manuscript
pdflatex manuscript
```

Or with `latexmk` (automates the pdflatex/bibtex round-trips):

```bash
latexmk -pdf manuscript
```

## Status

- [x] Title locked
- [x] Abstract drafted with current 7-compound dataset
- [x] §1 Introduction (ABFE on metalloenzymes, reproducibility-vs-accuracy framing, pipeline pitfalls)
- [x] §2 Methods (compounds, force fields, ABFE protocol, replicates, cross-method)
- [x] §3 Results — table, reproducibility analysis, three-replicate recovery, potency stratification
- [x] §4 Discussion — what ZAFF can/cannot do, mechanism speculation, ReplicaExchangeSampler bug
- [x] §5 Limitations
- [x] §6 Reproducibility / open code
- [ ] xtb cross-method sub-section (§3.5) — `\todo{}` placeholder, needs final solvent variation matrix
- [ ] Figures: 4 panel figure planned
  - (a) replicate scatter (rep1 vs rep2 vs experiment) for each compound
  - (b) per-compound bar chart of replicate dispersion vs $|\Delta\dGexp|$
  - (c) potency-stratified residual plot
  - (d) pipeline schematic (warmup + MSS swap)
- [ ] Zenodo code DOI (to be issued at submission)
- [ ] CHEMBL443684 (Marimastat) only has rep1 — rep2 would extend the
  three-replicate-mean argument; ETA after orchestrator current run
  reaches CHEMBL443684_rep2 (not yet queued)

## Data sources

All raw `dG_bind.json` files live under
`pilot/abfe_benchmark_chembl/{CHEMBL_ID}/abfe_production_mss/`
and `_rep{2,3}` siblings. Cross-method xtb data:
`pilot/cpu_meaningful/xtb_npass_top9997_hetero10_{refine,gfn1}_432conf.csv`.

## Pre-registration

Methodology lock and pre-registered hypotheses at
`preprints/PRE_REGISTRATION_TEMPLATE.md` (OSF deposit pending).

## License

CC-BY 4.0 for manuscript text; Apache-2.0 for code.
