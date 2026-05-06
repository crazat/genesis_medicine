# Paper #B — xtb screening robustness

LaTeX source for "Method-, conformer-count-, and solvent-robust ranking
of natural-product screening corpora via xtb semi-empirical quantum
chemistry: a multi-axis robustness benchmark." Target submission:
J. Chem. Inf. Model. (JCIM) / RSC Digital Discovery / Bioinformatics.

## Files

- `manuscript.tex` — main document
- `refs.bib` — BibTeX, 10 entries
- `figures/` — placeholder

## Compile

```bash
latexmk -pdf manuscript
# or
pdflatex manuscript && bibtex manuscript && pdflatex manuscript && pdflatex manuscript
```

## Status

- [x] Title locked
- [x] Abstract drafted with current ladder + GFN1↔GFN2 data
- [x] §1 Introduction — three robustness axes framing
- [x] §2 Methods — xtb protocol, three axes (method, conformer-count, solvent), Boltz-2 cross-engine
- [x] §3 Results
  - [x] §3.1 ladder convergence (15 pairs, ρ=1.0000 4-decimal)
  - [x] §3.2 GFN1 vs GFN2 cross-method (ρ=0.99 energy, 0.98 gap)
  - [ ] §3.3 solvent-axis 4-solvent matrix — `\todo{}` placeholder, awaits running chain (~4-5h)
  - [x] §3.4 Boltz-2 cross-engine (mass-bias diagnosis, top-K IoU)
- [x] §4 Discussion + multi-fidelity ensemble pre-registration
- [x] §5 Limitations
- [x] §6 Reproducibility
- [ ] Figures planned:
  - fig1: ladder convergence heatmap (15-cell upper triangle)
  - fig2: GFN1 vs GFN2 scatter on energy + gap
  - fig3: solvent-axis pairwise rank correlation matrix
  - fig4: Boltz-2 vs xtb-gap top-K IoU bar chart
- [ ] Zenodo code DOI (at submission)

## Data sources

`pilot/cpu_meaningful/xtb_npass_top9997_hetero10_{refine_Nconf,gfn1_432conf,solvent_*_432conf}.csv`

## Pre-registration

Multi-fidelity ensemble triage recipe in §4.3 is the pre-registered
prospective protocol. To be deposited on OSF before any prospective
campaign launch.

## Companion paper

`preprints/paper_A_zaff_abfe_limitations/` — ABFE limitations paper.
This paper covers the screening-stage triage; companion covers the
free-energy confirmation step.

## License

CC-BY 4.0 (manuscript) + Apache-2.0 (code).
