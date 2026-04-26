# Recover 한의원 — Photo cube + REDCap + OMOP CDM 임상 데이터 통합 (D-110 deployment)

**Status**: planning document, 2026-04-27. 30-day deployment to ship before Recover opening (2026-08-15).

**Why this matters**: today our in silico predictions are unfalsifiable. The minute Recover ships standardized pre/post photos with quantitative scar-area regression coefficients tied to compound exposure, every preprint gains a feedback prior — and every CRO Tier-1 investment is risk-adjusted by real human evidence. The loop converts Recover from a clinic into a Phase-0 evidence engine.

**Total budget**: ≤ KRW 5,000,000. Total compute: existing RTX 5090. Total integration: ~1 dev × 3 months.

---

## Stack overview

```
Recover visit (D0/W4/W12) 
  → iPad/iPhone photo (standardized lighting cube, KRW 1.5M)
  → Upload via REDCap mobile (free, MPL-2.0)
  → Auto-segment with MedSAM-2 fine-tuned on 50 Recover scars
  → Quantitative metrics: scar area (mm²), erythema (a* in CIELAB), 
                           melanin (ITA°), height (3D photogrammetry)
  → Store as FHIR Observation in OpenMRS-O3
  → Nightly ETL → OMOP CDM 5.4 (Broadsea Docker)
  → R Shiny dashboard: per-patient slope of scar area vs. time-on-treatment
  → Cross-link: patient prescription (한약/외용) → Genesis_Medicine compound DB by SMILES
  → Aggregate posterior: each compound's clinical Δarea per week (Bayesian RBesT)
  → Feed back as "clinical prior" weight into next round of in-silico screening
```

## Hardware (all open licenses or commercial-purchased one-time)

| Item | Vendor | Purpose | Cost (KRW) |
|---|---|---|---:|
| Polarized photo cube | OEM (KR) | Standardized lighting for scar/lesion photos; cross-polarized for sub-surface melanin | 1,500,000 |
| iPad Pro 11" | Apple | Patient-facing capture + REDCap mobile | 1,200,000 |
| iPhone 16 Pro | Apple | Backup capture + 3D LiDAR photogrammetry | 1,500,000 |
| Lenovo ThinkCentre tiny PC | Lenovo | OpenMRS + REDCap + Broadsea Docker on-premise | 800,000 |
| Total | | | **5,000,000** |

## Software stack

| Layer | Tool | License | Notes |
|---|---|---|---|
| Patient capture | REDCap mobile | MPL-2.0 | Free for non-profit medical institutions |
| EHR | OpenMRS 3 (O3) | MPL-2.0 | FHIR R5 native |
| Image segmentation | MedSAM-2 | Apache-2.0 | Fine-tune 50 Recover scars on RTX 5090 (1 day) |
| 3D photogrammetry | Polycam free API | Free tier | Volume + height metrics |
| ETL | Broadsea OHDSI Docker | Apache-2.0 | OMOP CDM 5.4 |
| Vocabulary | OHDSI Athena | Apache-2.0 | KCD-8 ↔ ICD-10 ↔ SNOMED-CT mapping |
| 한의 codes | KIMSCC | Public, KOGL | Korean Medicine Standard Common Codes |
| Statistics | R 4.4 + RBesT | GPL-3 | Bayesian borrowing, synthetic control arms |
| Dashboard | R Shiny | GPL-3 | Per-patient outcome slope tracker |
| Causal inference | TwoSampleMR | MIT | Mendelian randomization on relevant GWAS |

## REDCap form templates (POSAS 3.0 + DLQI + photo upload)

### Form 1: 흉터 시각 평가 (POSAS 3.0)

| Field | Type | Validation |
|---|---|---|
| 환자 ID | text | matches Recover EMR |
| 평가일 | date | yyyy-mm-dd |
| 흉터 위치 | text | anatomical site |
| 흉터 발생일 | date | for time-since-injury covariate |
| POSAS 환자측 (Patient Scale, 6 items × 1-10) | radio | 1=정상피부, 10=극단 차이 |
| POSAS 관찰자측 (Observer Scale, 6 items × 1-10) | radio | clinician score |
| VAS 통증 0-10 | slider | numerical |
| VAS 가려움 0-10 | slider | numerical |
| 사진 업로드 — 정면 polarized | file | jpg/png, max 10MB |
| 사진 업로드 — 정면 cross-polarized | file | "for sub-surface melanin" |
| 사진 업로드 — 측면 (3D 깊이) | file | LiDAR photogrammetry export |

### Form 2: 처방 + 외용제 사용 추적

| Field | Type |
|---|---|
| 처방 한약 (탕약/환제/산제) | dropdown — KIMSCC code |
| 외용제 — Recover 자체 제조 | dropdown — Genesis_Medicine compound ID |
| 외용제 — 시판제품 | text — manual entry |
| 1일 적용 횟수 | integer 1-4 |
| 적용 부위 면적 (cm²) | float |
| 부작용 보고 | text optional |

### Form 3: 부작용 / 안전성 모니터링 (KIDS-KAERS aligned)

Aligned with Korean Adverse Event Reporting System format for direct
KFDA submission of any signal observed.

## MedSAM-2 fine-tuning on Recover dataset

```bash
# After 50 manually-annotated Recover scars accumulated:
git clone https://github.com/bowang-lab/MedSAM
cd MedSAM
python finetune_one_gpu.py \
  --data_path /data/recover_scars \
  --pretrained_model checkpoints/medsam_vit_b.pth \
  --output_dir checkpoints/recover_scar_medsam_v1 \
  --batch_size 4 --epochs 100
```

Expected: AUROC > 0.93 on held-out Recover scars (typical MedSAM fine-tune
performance with 50 examples).

## Data flow → Genesis_Medicine feedback loop

1. **Per-visit**: REDCap collects forms 1+2+3 → OMOP CDM via Broadsea ETL
2. **Per-week**: R Shiny dashboard recomputes per-patient
   `lm(scar_area ~ days_on_treatment + age + initial_size)` slopes
3. **Per-month**: aggregate compound × cohort `Bayesian` posterior of slope
4. **Per-quarter**: positive-signal compounds get weighted prior into next
   in silico screening round (`scripts/round5_sweep.py` enriched with
   `clinical_prior` column reading from OMOP)

## Year-1 publication

> "Real-world quantitative photo-based outcome of `센텔라+자근` 한방 외용제
> in 200 post-acne scars: a single-center prospective cohort with in silico
> molecular target attribution"

Single-center prospective cohort with N≥150 patients × 3-time-points (D0/W4/W12)
= 450 paired observations. Target journal: J Am Acad Dermatol or Dermatologic
Therapy. Expected acceptance: post-12-month accumulation, 2027-Q3 submission.

## Regulatory framing

All photo-based outcome scoring is "clinical research observational" not
"medical device" (no diagnostic claim). REDCap deployment is research-only
pending IRB approval (Recover affiliated with Yonsei or Kyung Hee KMU).
KFDA / MFDS pre-consultation for cosmetics + 외용제 dossiers leverages
these prospective outcome data as supporting evidence.

## Critical open-source pillars

| Pillar | License | Status |
|---|---|---|
| REDCap mobile | MPL-2.0 | Free |
| OpenMRS-O3 | MPL-2.0 | Free |
| MedSAM-2 | Apache-2.0 | Free |
| Broadsea (OMOP) | Apache-2.0 | Free |
| RBesT | GPL-3 | Free |
| TwoSampleMR | MIT | Free |
| Total license cost | | **KRW 0** |
