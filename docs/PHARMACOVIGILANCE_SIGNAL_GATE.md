# Pharmacovigilance Signal Gate

- timestamp: `2026-05-06T12:46:30+09:00`
- rows: `442`
- gate_counts: `{'pv_signal_review': 240, 'pv_class_caveat': 140, 'pv_signal_not_mapped': 62}`
- purpose: FDA AEMS/FAERS 또는 class analog safety signal을 논문 safety caveat와 systemic/topical path 분리에 연결한다.

## PV Rows

| candidate | target | gate | warning terms | class context | next |
|---|---|---|---|---|---|
| R15_chromanol_Cl_pos9 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos6 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos6 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | ptgs2 | pv_signal_review | known_systemic_class_warning | NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos9 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos10 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Cl_pos10 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | tyrp1 | pv_signal_review | photosensitivity_or_pigment_AE_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me9_Me10 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me9 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me9 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me9_Me10 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me10 | tyr | pv_signal_review | photosensitivity_or_pigment_AE_review | depigmenting agent class: irritation, ochronosis-like, photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol_Me6_Me10 | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| R15_chromanol | ar | pv_signal_review | known_systemic_class_warning | antiandrogen/endocrine class: libido, teratogenicity, systemic endocrine effects | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC243469 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC194985 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC281540 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC469970 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC84346 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC474914 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC324003 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC479534 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC329517 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC93630 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC327468 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC251201 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC228994 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC196136 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC35553 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC327424 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC257680 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC306634 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC273290 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC157431 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC243184 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC321984 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC58557 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC323203 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| NPC280090 | nan | pv_signal_review | systemic_absorption_or_accumulation_review | no close approved-drug class signal mapped | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| chromanol_arom9+arom10_Cl+Cl_ptgs2 | ptgs2 | pv_signal_review | known_systemic_class_warning | NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| chromanol_arom9+arom10_Cl+Cl_dct | dct | pv_signal_review | photosensitivity_or_pigment_AE_review | pigmentation pathway class: pigment alteration and photosensitivity review | query AEMS/FAERS or literature class safety before systemic or topical safety claim |
| chromanol_arom6+arom9_Cl+Cl_ptgs2 | ptgs2 | pv_signal_review | known_systemic_class_warning | NSAID/COX class: GI, renal, hypersensitivity, cardiovascular warning | query AEMS/FAERS or literature class safety before systemic or topical safety claim |

## Curator Rule

- `pv_signal_review`: AEMS/FAERS/literature class safety query 전까지 safety-positive 표현 금지.
- `pv_class_caveat`: 신호는 causation이 아니며 manuscript limitation으로만 사용한다.
- `pv_signal_not_mapped`: 안전하다는 뜻이 아니라 데이터 미연결 상태다.
