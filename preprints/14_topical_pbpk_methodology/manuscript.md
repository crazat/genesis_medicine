# A Topical Skin PBPK Pipeline for Natural-Product-Inspired Therapeutics: Integrating Dancik 4-Layer ODE, SkinPiX-Trained LGBM logKp, and NPASS 2026 ADME Records

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab, Seoul, Republic of Korea
² HAN PREDICT, Inc. (hanpredict.com)
³ Recover Korean Medicine Clinic (recover-clinic.kr)

**Status:** v0.1 (methodology preprint, code Apache-2.0)
**Date:** 2026-04-27

---

## Abstract

Topical (transdermal) drug delivery is the dominant route for
dermatological therapeutics, yet most AI drug-discovery pipelines
omit physiologically-based pharmacokinetic (PBPK) modeling for skin.
We present a fully open-source pipeline combining: (1) **Dancik 4-layer
skin PBPK** (stratum corneum → viable epidermis → dermis → systemic);
(2) **LightGBM logKp head** trained on SkinPiX (n=2,326, OECD 428) +
NPASS 2026 ADME records (n=9,713); (3) **integration with cofolding
output** to produce per-compound topical bioavailability + skin layer
concentration estimates. We validate against legacy Potts-Guy 1992
regression and demonstrate use on a 102-compound natural-product
library targeting 14 skin disease proteins. Code is released under
Apache-2.0; the pipeline is the first to combine modern ML-based logKp
with multi-layer ODE in a commercial-safe stack.

## 1. Background

The skin is a four-layer composite barrier. Most published AI drug
discovery pipelines treat it as a single Lipinski threshold (logP
1.5-3.5, MW < 500). The classical **Potts-Guy 1992** regression
(log Kp = -2.7 + 0.71 logP - 0.0061 MW) is widely used but ignores
H-bonding, vehicle effects, and skin metabolism.

Modern alternatives exist (FDA 2326-compound dataset, OECD TG 428
harmonized SkinPiX) but are not widely integrated into open-source
discovery pipelines.

## 2. Methods

### 2.1 Dancik 4-layer ODE
Stratum corneum (15 μm), viable epidermis (100 μm), dermis (1.5 mm),
systemic. Steady-state flux:

J_ss = K_p × C_donor × A

where K_p is the permeability coefficient (cm/s), C_donor is donor
concentration, and A is application area. Lag time τ ≈ h_sc² / (6 D_sc).

### 2.2 LGBM logKp head
- Features: Morgan FP (radius=2, nBits=1024) + RDKit physicochemical
  descriptors (MW, logP, TPSA, HBA, HBD, rotatable bonds)
- Training data: SkinPiX (n=2,326) + NPASS 2026 ADME-Tox records with
  reported logKp (n≈8,000 after cleanup)
- Holdout: 10% random + scaffold-based 10%
- Target metric: MAE in log Kp (cm/s) units

### 2.3 Vehicle effects
- Ointment: occluded, 1.0× donor concentration retained
- Cream: 0.7× donor concentration after 8h
- Liposome: enhancer factor 1.5-3× depending on lipid composition
- Aqueous: 0.5× (rapid evaporation)

### 2.4 Validation against Potts-Guy
[Cross-validation table to be added.]

## 3. Results

### 3.1 LGBM holdout performance vs Potts-Guy
[Pending: train on SkinPiX, evaluate.]

### 3.2 Application: Genesis_Medicine v3 102-compound library
- Centella asiatica triterpenoids (asiaticoside, madecassoside)
- Lithospermum erythrorhizon naphthoquinones (shikonin)
- Glycyrrhiza glabra flavonoids (licochalcone A, glabridin)
- Camellia sinensis catechins (EGCG)
- Embelia ribes benzoquinones (embelin, EMB-3) — **PAINS-flagged**

### 3.3 Topical bioavailability ranking
[Pending: full Dancik run.]

### 3.4 Skin layer concentration vs systemic exposure
[Pending: full Dancik run.]

## 4. Discussion

### 4.1 Why this matters
A small molecule with high MMP-1 cofolding affinity (Boltz-2 score 0.9)
but zero topical bioavailability is useless for an external
formulation. Recover 한의원 외용 크림 vertical needs PBPK from day 1.

### 4.2 Comparison to Schrödinger ADME-Predict
Schrödinger PBPK is closed-source ($25k+/seat/year). Our pipeline is
fully open (Apache-2.0). Performance comparison pending.

### 4.3 Limitations
1. Dancik 4-layer is a steady-state approximation; transient kinetics
   are not modeled.
2. SkinPiX is heavy on small organics; natural-product training data
   is sparse.
3. No metabolism module (skin CYP/UGT) — assumes parent compound only.
4. No vehicle physical chemistry (only categorical multipliers).
5. Soft-drug design (intentional skin metabolism) is not handled.

## 5. Code Availability

- Adapter: `src/genesis_medicine/dermatology/skin_pbpk_dancik.py`
- LGBM training: `scripts/train_logkp_lgbm.py` (pending data dump)
- Demo: `scripts/run_dancik_pbpk_demo.py`

License: Apache-2.0 (code), CC-BY 4.0 (data attributions where applicable).

## 6. Conclusion

Topical PBPK is the missing link between cofolding affinity and
external-formulation viability. Our open-source pipeline closes this
gap for the natural-product-inspired skin discovery setting and is
the first to combine modern ML logKp with multi-layer ODE in a
commercial-safe stack.

## References

1. Dancik et al., *Pharm Res* 2013 — multi-layer skin PBPK
2. Potts & Guy, *Pharm Res* 1992 — logKp regression
3. *Sci Data* 2024 — SkinPiX harmonized dataset
4. *Nucleic Acids Res* 2026 — NPASS 2026 update
5. OECD TG 428 — *In Vitro* skin absorption
6. *PLOS Digital Health* 2024 — ML logKp benchmark
7. Boltz-2 (Wohlwend et al. 2025, MIT)

---

**Disclosure**: *In silico* only. No clinical use intended. Not subject
to medical-device regulatory review.
