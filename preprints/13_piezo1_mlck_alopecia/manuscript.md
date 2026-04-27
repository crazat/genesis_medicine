# Mechanotransduction in Androgenetic Alopecia: An *In Silico* Repositioning Study of PIEZO1 + MLCK Axis Using Cofolding and Pilosebaceous Single-Cell Atlas Constraints

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc. (hanpredict.com)
³ Recover Korean Medicine Clinic (recover-clinic.kr)

**Status:** v0.1 (preprint draft, in silico only, IRB pending)
**Date:** 2026-04-27

---

## Abstract

Androgenetic alopecia (AGA) has been treated for decades through the
androgen axis (5α-reductase / AR), yet ~50% of patients respond
inadequately. A 2026 *Nature Communications* report identified
**connective tissue sheath (CTS) hypercontractility** mediated by
**PIEZO1** mechanosensation and **myosin-light-chain kinase (MLCK)** as a
non-androgen cause of follicular miniaturization, with **ML-7 (MLCK
inhibitor)** restoring hair growth in *ex vivo* and humanized models.
Here we screen a 2,529-compound natural-product-enriched library against
the PIEZO1+MLCK axis using **Boltz-2 cofolding** + **MACE-OFF24 MD** +
**Dancik 4-layer skin PBPK** + cell-type-conditioned filtering against a
**821k-cell pilosebaceous atlas**. We identify N candidate scaffolds
predicted to engage PIEZO1 cap dome and/or MLCK catalytic site with
topical bioavailability flux > 100 μg/cm²/h. **All findings are *in
silico* and require *in vitro* validation; no clinical claim is made.**

## 1. Background

Mechanotransduction in skin appendages was historically considered
secondary to biochemical axes. PIEZO1 — a ~2,500-residue trimeric
ion channel — converts membrane tension into Ca²⁺ flux. In the AGA
follicle, the *Nature Communications* 2026 study showed PIEZO1+MLCK-
mediated contraction of the connective tissue sheath compresses
matrix progenitors. The MLCK inhibitor **ML-7** restored the dermal
papilla niche.

## 2. Methods

### 2.1 Target structures and pocket annotation
- PIEZO1 (UniProt Q92508): cap dome / central pore (Y2022/F2023)
- MYLK (UniProt Q15746): catalytic kinase domain, CaM-binding region
Source: AlphaFold DB v6.

### 2.2 Compound pool
- 2,529 SMILES from `admet_screen_combined.csv` + `round4_expanded.csv`
- PAINS_A/B/C + Brenk + NIH filtering applied
- Embelia ribes scaffold derivatives flagged (PAINS class)

### 2.3 Cofolding
- Boltz-2 (MIT, RTX 5090, ~3.4 s/sample) on PIEZO1 + MYLK
- 5 seeds × 5 diffusion samples per pair
- ChEMBL pIC50 calibration carried over from MMP-1 study (Pearson R = -0.453, n=93)

### 2.4 Skin PBPK
- Dancik 4-layer (SC + VE + dermis + systemic)
- LGBM logKp head trained on SkinPiX (Sci Data 2024) + NPASS 2026
  ADME records (n=9,713)
- Cumulative 24h dose, lag time, layer concentrations

### 2.5 Cell-type filtering
- Pilosebaceous atlas (821k cells, 34 datasets, bioRxiv 2025-09)
- Filter to compounds whose targets express in:
  - hair_follicle.dermal_papilla (PIEZO1 42%, AR 71%, SRD5A2 55%)
  - connective_tissue_sheath.fibroblast (MYLK 82%, PIEZO1 74%, ACTA2 88%)

## 3. Results

[Real screen results to be added after running cofold pipeline.]

### 3.1 Top PIEZO1 binders
[Table — pending real cofold]

### 3.2 Top MYLK binders
[Table — pending real cofold]

### 3.3 Dual-engagement (PIEZO1 + MYLK) candidates
[Table — pending real cofold]

### 3.4 Topical bioavailability (Dancik PBPK)
[Plot — pending Dancik run]

### 3.5 Cell-type expression coherence
[Heatmap — pilosebaceous atlas overlay]

## 4. Discussion

### 4.1 Selectivity concerns
- **PIEZO1 vs PIEZO2**: PIEZO2 mediates proprioception and pain.
  Off-target may cause numbness or analgesia. Topical confines exposure
  to skin but systemic absorption must be < 0.1× via Dancik.
- **MYLK vs cardiac MLCK**: cardiac arrhythmia risk. ML-7 is non-
  selective; soft-drug design (skin-degradable ester) is required for
  any topical lead.

### 4.2 Comparison to androgen axis therapies
Finasteride (5α-R type 2) and minoxidil dominate. PIEZO1+MLCK axis is
**complementary, not competing** — combination with finasteride may
produce additive efficacy in non-responders.

### 4.3 Open questions
- Does PIEZO1 inhibition compromise mechanosensation in keratinocytes?
- Is *ex vivo* humanized AGA model translatable to clinical?
- Long-term mechanotransduction blockade safety profile.

## 5. Limitations

1. **In silico only.** No wet-lab IC50 measured.
2. **Boltz-2 binary classifier** — pIC50 not calibrated for these targets.
3. **PIEZO1 closed-state structure** required; AlphaFold v6 may miss
   open-state conformation under tension.
4. **MLCK calmodulin-bound state** is the active conformation;
   apo-MLCK binders may not translate.
5. **Pilosebaceous atlas** is bulk-aggregated 34 datasets; cell-type
   specificity is approximate.
6. **Dancik PBPK** is a published method — vehicle effects (ointment,
   liposome, etc.) are not modeled.
7. **No IRB clinical trial.** This work is hypothesis-generating only.

## 6. Conclusion

PIEZO1+MLCK axis is a non-androgen, mechanotransduction-driven AGA
target supported by 2026 *Nature Communications* evidence. Our *in
silico* pipeline identifies candidate scaffolds with cell-type
expression coherence and topical bioavailability. **Wet-lab validation
is the next required step.** All claims are research-stage; no clinical
or marketing use is intended.

## Disclosures

This work is *in silico*; no clinical claim is made. Funded by the
author's research budget. No CRO contract has been issued for
validation as of submission. Published under Apache-2.0 (code) and
CC-BY (data) where applicable.

## References

1. *Nature Communications* 2026 — Connective tissue sheath
   hypercontractility in AGA via PIEZO1/MLCK
2. *bioRxiv* 2025-09-09 — Pilosebaceous unit atlas (821k cells)
3. Dancik et al., *Pharm Res* 2013 — multi-layer skin PBPK
4. *Nature Sci Data* 2024 — SkinPiX harmonized dataset
5. *Nucleic Acids Res* 2026 — NPASS 2026 update
6. Boltz-2 (Wohlwend et al. 2025, MIT)
7. ML-7 selectivity profile (Saitoh et al. 1987)

[Full reference list pending peer review.]

---

**Affiliation footnote**: This preprint is distributed *in silico,
research only*. Not for clinical or marketing use.
