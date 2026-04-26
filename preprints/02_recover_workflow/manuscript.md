# An integrated AI workflow for a Korean medicine clinic: 3D facial diagnostics, RAG-based electronic medical records, and computational molecular prescription

**HanCheongWoo ¹,²,³**

¹ Genesis_Medicine Lab — AI in silico drug discovery R&D division, Seoul, Republic of Korea
² HAN PREDICT, Inc. — AI healthcare technology platform; <https://hanpredict.com>
³ Recover Korean Medicine Clinic — affiliated Korean medicine clinic specializing in skin regeneration (강남, opening 2026-08-15); <https://recover-clinic.kr>

Code repository: <https://github.com/crazat/genesis_medicine> · Correspondence: admin@hanpredict.com

**Manuscript type**: Technical workflow / clinical informatics report
**Target preprint server**: medRxiv (primary)
**Status**: System architecture and design report; clinical validation in IRB-approved study pending
**License**: CC-BY 4.0 (preprint); platform code licensed separately (Apache-2.0 for Genesis_Medicine; HAN PREDICT components proprietary unless otherwise noted)

---

## Abstract (250 words)

Korean medicine (한의학) clinics face a structural gap between traditional pattern-based diagnosis (변증) and modern personalized molecular medicine. We describe an integrated end-to-end workflow assembled across three affiliated entities — **HAN PREDICT, Inc.** (AI healthcare technology platform), **Genesis_Medicine Lab** (in silico natural-product drug discovery), and **Recover Korean Medicine Clinic** (skin-regeneration practice opening 2026-08-15) — that operationalizes a patient encounter as a sequence of (i) 3D facial-surface diagnostic capture (Morpheus 3D scanner and iPhone TrueDepth), (ii) retrieval-augmented electronic medical records with traditional-pattern reasoning (Smart Charts, integrating InBody body composition), and (iii) molecular-level prescription generation drawing on a curated library of Korean herbal natural products evaluated through a REINVENT4 + Boltz-2 + corrected absolute binding free energy (ABFE) pipeline. We outline the regulatory framework (Personal Information Protection Act §23-2 biometric-data handling, Korea AI Basic Act 2026, Medical Service Act §17/§56, HIPAA-aligned data security) under which the system operates, present a representative scar-treatment patient journey, and document specific limitations including the absence of randomized clinical validation, the in silico nature of the molecular-prescription module, and zinc-coordination constraints in metalloprotease modeling. We do not assert clinical efficacy. The integrated workflow is presented as a system-design contribution to support reproducible Korean medicine practice; clinical and regulatory validation under an IRB-approved protocol (filed 2026-04-27) is the explicit next step.

**Keywords**: Korean medicine, 한의학, AI clinic workflow, 3D facial diagnostics, retrieval-augmented EMR, in silico drug discovery, regulatory compliance, traditional-modern integration.

---

## Plain-language summary

This paper describes how a Korean medicine clinic — Recover Korean Medicine Clinic in Gangnam, Seoul, scheduled to open on August 15, 2026 — plans to use a connected set of AI tools at every step of a patient visit. When a patient arrives, a 3D camera and an iPhone scan the face to record skin-surface details and any asymmetry. The traditional Korean-medicine consultation is then recorded in a smart electronic medical record system (Smart Charts) that retrieves relevant clinical references automatically. Finally, a separate research module (Genesis_Medicine) suggests candidate herbal compounds at the molecular level, drawing on a public natural-products library and a computer-based scoring pipeline. **No diagnostic, treatment, or clinical efficacy claim is made in this report. All clinical use will follow a hospital institutional review board (IRB) protocol.** The paper documents the system design, regulatory framework, and known limitations.

---

## 1. Introduction

### 1.1 Korean medicine and the molecular-medicine gap

Korean medicine (한의학) is a state-licensed clinical practice in the Republic of Korea, with approximately 25,000 licensed Korean Medicine Doctors (한의사) and an annual outpatient volume in the tens of millions of visits [1]. The practice integrates pattern diagnosis (변증), constitutional theory (사상의학, 체질의학), acupuncture, herbal formulation, and increasingly modern diagnostics. The clinical reasoning, however, has historically been narrative and pattern-based: a herbal formulation is selected on the basis of symptom-pattern fit (e.g., 황련해독탕 for "삼초실열" pattern) rather than on the basis of identified molecular targets and quantitatively predicted ligand–protein binding.

Modern personalized medicine, in contrast, is driven by molecular evidence — genomic variants, single-cell transcriptomic profiles, structure-based drug-target interactions and quantitative pharmacokinetics. Bridging these two frames (pattern-based traditional reasoning ↔ molecular-mechanistic modern reasoning) without losing either requires an information infrastructure that respects both layers and that supports the clinician's actual workflow at the bedside.

### 1.2 The three-entity design

We describe an integrated workflow that operates across three affiliated entities, organized so that traditional-pattern diagnosis and molecular hypothesis-generation feed into each other through a shared electronic medical record:

- **HAN PREDICT, Inc.** ([hanpredict.com](https://hanpredict.com)) — the AI healthcare technology platform, providing the patient-facing front end (Clinic CRM with appointment scheduling and CTI call monitoring), the AI electronic health record (Smart Charts, RAG-based with InBody integration), the marketing-automation back office, mobile nutrition tracking (NutriDocH, with Gemini Vision meal analysis), and an AI-assisted media-production tool (AI Studio). HAN PREDICT also develops a 3D facial-diagnostic Station Kit supporting Morpheus 3D and iPhone TrueDepth capture.
- **Genesis_Medicine Lab** — the in silico drug-discovery R&D division, providing the molecular-prescription back-end. The Genesis_Medicine pipeline integrates REINVENT4 generative chemistry, ADMET-AI property prediction, Boltz-2 protein–ligand co-folding, molecular-dynamics validation (OpenMM 8 + GAFF-2.11 + ff14SB), and corrected absolute binding free energy estimation (openmmtools, flat-bottom centroid restraint, complex- and solvent-leg thermodynamic-cycle closure) for a curated library of approximately 100 Korean herbal natural products against a panel of skin-relevant molecular targets (TGF-β1, MMP-1, MMP-3, MMP-9, CTGF, SMAD3, COL1A1, LOX, PDGFRB and related fibrotic and pigment / hair-cycle / sebaceous targets).
- **Recover Korean Medicine Clinic** ([recover-clinic.kr](https://recover-clinic.kr)) — the affiliated 한방 clinical practice, specializing in skin regeneration (post-traumatic scar revision, keloid management, post-procedural healing, photoaging, alopecia, melasma). Recover provides the patient interface, regulatory accountability under the Korean Medical Service Act, and the clinical feedback loop (treatment outcomes → updated molecular hypotheses).

This three-entity arrangement is presented in Figure 1 (forthcoming): patient → 3D facial capture → Smart Charts EMR → 변증 + molecular co-reasoning → clinical decision (acupuncture, herbal formula, or topical/oral preparation supported by Genesis_Medicine compound suggestions, all under the prescribing 한의사's authority) → outcome capture → R&D feedback.

### 1.3 What this paper does and does not claim

This paper documents **system architecture, integration points, and the regulatory framework** under which the workflow is intended to operate. It does **not** present:
- randomized clinical trial results,
- claims of clinical efficacy for any individual herbal compound or formulation,
- patient outcome data,
- approved indications under the Korean Ministry of Food and Drug Safety (식약처).

All clinical use of the workflow described here will follow an IRB-approved protocol (initial submission 2026-04-27, currently under review).

---

## 2. System architecture

### 2.1 Layer A: 3D facial diagnostic capture (HAN PREDICT)

The patient is captured at the chair-side using one of two complementary modalities:

- **Morpheus 3D scanner** — structured-light capture producing a 3D mesh in proprietary `.mpa` format. Used when high-fidelity surface geometry is required (pre/post hypertrophic-scar comparison, asymmetry quantification before/after thread-lifting).
- **iPhone TrueDepth front-camera** — depth-camera stream captured through an iOS application, producing a coarser but still clinically useful 3D mesh; used for quick-turnaround follow-up visits and for at-home patient self-capture (kit-based deployment).

Both modalities feed a common processing pipeline:
1. Mesh import and registration to a canonical face frame.
2. Zone segmentation (forehead, periorbital, malar, perioral, mandibular) using a learned segmentation network.
3. Bilateral asymmetry quantification (root-mean-square of left–right vertex offset within each zone).
4. Cephalometric-landmark detection (23 standard points, including soft-tissue analogs of bony landmarks where applicable).
5. Optional pose-prediction of expected post-treatment surface (soft-Patch-CGAN + BP-ANN, where validated).
6. Nine-gate Safety Supervisor (BDD pattern flags, vessel-mapping quality check, drug–drug interaction flags, anticoagulant flags, malignancy markers).

Outputs are written as both a structured JSON record (for downstream EMR consumption) and as an interactive HTML report (Three.js viewer) for clinician review.

### 2.2 Layer B: Smart Charts AI electronic medical record (HAN PREDICT)

The clinician's work surface is **Smart Charts**, a retrieval-augmented EMR with the following features:

- **Free-text consultation note capture** with automatic extraction of pattern-diagnostic vocabulary (변증 keywords, 사상체질 markers).
- **InBody body-composition integration** (segmental impedance, body-water distribution) for whole-patient context, particularly relevant for body-constitution pattern reasoning.
- **RAG-based reference retrieval** over a curated knowledge base of approximately 114+ medical and Korean-medicine documents (commonly-referenced 한방 처방 textbooks, modern dermatological references, internal Recover clinical reference notes). The retriever surfaces relevant precedent cases and formulation rationales as the clinician types.
- **Treatment-recommendation surfacing** that brings together (i) the 변증 pattern inferred from the consultation, (ii) any Genesis_Medicine molecular suggestions associated with the patient's primary indication, and (iii) the safety-supervisor flags from Layer A. The recommendations are non-binding; the prescribing 한의사 retains full authority and is the sole decision-maker.
- **Audit trail** complying with 의료법 §17 (medical record retention) and §56 (advertising-claim substantiation).

### 2.3 Layer C: Genesis_Medicine molecular prescription engine

Genesis_Medicine is a research-grade in silico drug-discovery pipeline maintained as an open-source repository ([github.com/crazat/genesis_medicine](https://github.com/crazat/genesis_medicine), Apache-2.0 license). Its role in the workflow is **hypothesis-generation only** — to provide the prescribing 한의사 with a molecular-level lens onto which Korean herbal natural-product compounds may be relevant for an indication, and at what predicted affinity / safety profile. It is explicitly **not** a treatment-decision system.

The pipeline modules are:

1. **Curated natural-product library** (`data/skin_compounds_curated.csv`): approximately 100 compounds drawn from KP/KHP-listed herbs and from open-data resources (COCONUT 2.0 [2], NPASS 3.0 [3], NPAtlas [4]), each annotated with source herb, traditional indication, and SMILES.
2. **REINVENT4** generative scaffold-hopping [5] — produces analogs of natural-product seeds that may improve drug-like properties without losing the pharmacophore (e.g., Embelin → EMB-3 case study, described elsewhere).
3. **ADMET-AI** property prediction [6] — hERG, skin irritation, AMES, ClinTox, oral bioavailability, aqueous solubility.
4. **Boltz-2 protein–ligand co-folding** [7] — predicts a 3D complex structure and an affinity probability for each compound × target pair, MSA-conditioned.
5. **Molecular dynamics validation** — 10 ns explicit-solvent MD (OpenMM 8 + GAFF-2.11 + ff14SB + TIP3P + 0.15 M NaCl, 310 K NPT) for the top compounds, with mdtraj-based ligand RMSD analysis.
6. **Corrected absolute binding free energy** — 16-window alchemical replica exchange in openmmtools [8] with flat-bottom centroid distance restraint, analytical standard-state correction, complex- and solvent-leg legs, validated against the T4 lysozyme L99A · benzene benchmark (literature ΔG_bind = -5.18 ± 0.18 kcal/mol [9]).

The resulting per-compound, per-target table is exposed to Smart Charts as a structured JSON; the clinician sees, for a given indication, a ranked list of Korean herbal compounds with their primary herb-of-origin, predicted affinity (with uncertainty), and ADMET safety summary, alongside any TRIPOD-AI checklist flags.

### 2.4 Cross-layer data and feedback flows

A unified patient record schema (under design) links:
- Layer A 3D facial outputs (per-zone asymmetry, landmark deltas)
- Layer B EMR consultation notes and prescription decisions
- Layer C molecular-prescription suggestions surfaced at the time of decision
- Outcome capture (follow-up 3D scans, patient-reported outcome measures, photographic comparison)

The outcome layer is critical for the long-term R&D loop: aggregated, de-identified outcome data feeds back into the Genesis_Medicine compound-library re-prioritization and (where appropriate, after IRB approval and informed consent) into model retraining.

---

## 3. Regulatory framework

The workflow operates under multiple overlapping Korean and international regulatory regimes. We summarize the principal compliance commitments:

### 3.1 Personal Information Protection Act (PIPA) §23 / §23-2

Section 23 governs the processing of *sensitive personal information* and Section 23-2 explicitly covers *biometric information*, which includes 3D facial scans and the cephalometric-landmark vectors derived from them [10]. Specific commitments:

- **Separate, written, opt-in consent** for biometric-data collection and processing.
- **Purpose-limited processing**: data collected for diagnostic / treatment-planning purposes is not used for marketing without separate consent.
- **At-rest encryption** (Fernet AES-128 in HAN PREDICT's current implementation; HIPAA-aligned key management).
- **Retention limits**: 3D scans retained for the period necessary for clinical follow-up, then either de-identified for R&D use (with separate opt-in consent) or destroyed.
- **PIPC biometric-information protection guidelines** (issued 2024-12-30) followed.

### 3.2 Korea AI Basic Act (인공지능 기본법)

The AI Basic Act, the principal Korean statute is taking effect 2026-01-22 with implementing regulations under public notice in 2026-Q2 [11]. The system's classification under the act is anticipated to be a *high-impact AI system* in the medical domain, with implications for:

- Pre-deployment risk assessment documentation.
- Human-oversight requirement (the prescribing 한의사 as the human-in-the-loop decision-maker).
- Transparency notice to patients regarding AI involvement in any aspect of their care.
- Audit-log retention for at least the period required by 의료법 (medical records retention).

### 3.3 Medical Service Act (의료법) §17 and §56

- **§17 (medical records)**: all consultation and treatment records, including AI-generated suggestions surfaced to the clinician, are retained as part of the medical record.
- **§56 (medical advertising)**: any clinic-facing communication (website, brochures, social media) referring to AI-augmented services is substantiated by the relevant peer-reviewed or preprint reference; the clinic does **not** advertise specific clinical efficacy claims for any compound discussed in this workflow without a controlled clinical study to support it.

### 3.4 International alignment

- **HIPAA** (United States) — the HAN PREDICT platform is built to be HIPAA-ready (encryption-in-transit and at-rest, audit logs, role-based access control). This positions the platform for potential future B2B SaaS deployment to U.S.-based clinics.
- **EU AI Act Annex IV** — the system architecture is documented in the form expected for a high-risk AI system under the EU AI Act; this supports any future European deployment without separate redesign.
- **21 CFR Part 11** — for any data destined to support FDA or 식약처 regulatory filings, the audit-chain and electronic-signature requirements are observed.

---

## 4. Worked example: a scar-revision patient encounter

The following walks through a hypothetical encounter to illustrate the layered workflow. **It is illustrative; no individual patient data are reported.**

### 4.1 Pre-visit
- Patient books online via Clinic CRM. Initial intake form captures chief complaint ("post-acne scarring on cheeks, 2-year history") and demographic / regulatory consent items.

### 4.2 In-clinic, Layer A capture
- iPhone TrueDepth capture (90 seconds in-chair) produces a coarse 3D mesh.
- For high-fidelity baseline, Morpheus 3D scan is performed (3–5 minutes).
- Layer A pipeline produces per-zone asymmetry RMS, depth-map delta against an age-matched reference, and a Safety Supervisor pass/flag report.

### 4.3 Consultation, Layer B capture
- Korean medicine doctor performs traditional pattern interview (한열·허실·표리·음양). Transcribed into Smart Charts.
- InBody body composition is recorded.
- Smart Charts retrieves relevant 변증 references for "post-acne scar" + the patient's pattern profile and surfaces recommended traditional formulations from the curated reference library.

### 4.4 Molecular co-reasoning, Layer C surface
- Smart Charts queries the Genesis_Medicine output table for "scar regeneration" indication.
- The table returns ranked Korean herbal compounds (e.g., asiaticoside, madecassoside from *Centella asiatica*; specific flavonoids from *Lithospermum erythrorhizon* root used in 자운고; specific compounds from constitutional formulations) with their predicted affinity for skin-fibrosis targets (TGF-β1, MMP-1, CTGF) and their ADMET / topical-suitability flags.
- The doctor reviews the molecular suggestions alongside the 변증-driven traditional recommendation and forms a prescription decision.

### 4.5 Decision and informed consent
- Final prescription decision is made by the licensed 한의사. AI suggestions are **advisory only** and are not binding on the prescription.
- If a topical preparation is recommended, the patient is informed which active components are believed (on the basis of the molecular module) to be most relevant, and which clinical evidence (literature, preprint, peer-reviewed) supports those beliefs. The patient is informed of the in silico nature of the molecular module and the absence of randomized controlled clinical trial evidence for any compound novel to the workflow.

### 4.6 Follow-up and outcome capture
- Follow-up visits (typically 4-week intervals) include repeat 3D capture for objective surface comparison, photographic comparison, and patient-reported outcome instruments (Vancouver Scar Scale, POSAS).
- Aggregated outcome data feed back to Layer C model re-prioritization and (if separately consented) to model retraining.

---

## 5. Limitations and ethical considerations

### 5.1 Limitations of this report

1. **No clinical validation reported here.** This paper is a system architecture and design report. The clinical workflow has not been validated in a randomized controlled study at the time of writing.
2. **No molecular module validation reported here.** The Genesis_Medicine outputs that feed Layer C are in silico predictions. The absolute-binding-free-energy module is calibrated against a small-molecule benchmark (T4 lysozyme L99A · benzene); calibration on clinical-relevance benchmarks (e.g., MMP-1 inhibitor sets) is in progress and will be reported in a companion methodology preprint.
3. **MMP-1 and other zinc-coordinating targets**: MMP-1 is a zinc metalloprotease whose catalytic Zn²⁺ ion is essential for inhibitor binding. The current Genesis_Medicine MD/ABFE protocol does not include explicit zinc-bonded force-field modeling (a future ZAFF [12] integration is planned). Predicted affinity values for MMP-1 in the present workflow should be interpreted as a "MMP-1 minus zinc" model and not as direct inhibitor-affinity predictions.
4. **3D facial diagnostic limitations**: The Layer A pipeline produces *surface* geometric metrics (asymmetry, landmark deltas). It does not replace a board-certified clinician's diagnostic judgment and must not be interpreted as a stand-alone diagnostic device under Korean medical-device regulation.
5. **No claim of substitution for individualized medical judgment**: All AI outputs in the workflow are advisory. The licensed 한의사 retains full clinical authority and responsibility.

### 5.2 Ethical considerations

- **Informed consent**: separate, written, granular consent is obtained for (i) clinical care, (ii) biometric data collection (PIPA §23-2), and (iii) optional research use of de-identified data.
- **Data minimization**: the workflow processes only data necessary for the patient's stated clinical purpose; data collected for one purpose is not silently repurposed.
- **Human oversight**: AI recommendations are surfaced to a licensed clinician; no autonomous decision-making is implemented for any clinical decision affecting the patient.
- **Transparency**: patients are informed at intake that AI is used in their care, in what capacity, and where the limits lie.
- **Equity**: the workflow is built primarily on Korean-context data (KP / KHP herbs, Korean PGx panel where applicable, Korean-language clinical references). External validation in other populations / contexts is required before any claim of generalizability.

### 5.3 Correction of one earlier internal claim

In an earlier version of internal Genesis_Medicine documentation, the herbal compound *embelin* was associated with the Korean topical formulation **자운고(紫雲膏)**. For chemical clarity, we note: 자운고 is a sesame-oil-based ointment whose principal herbal ingredient is *Lithospermum erythrorhizon* (자초), which produces 1,4-naphthoquinone derivatives (shikonin, acetyl-shikonin) — structurally distinct from embelin's 1,4-benzoquinone-2,5-diol scaffold. The traditional context of embelin is properly the *Embelia ribes* (자단 / Vidanga) lineage, as we discuss in the companion review preprint.

---

## 6. Conclusions and forward path

We have outlined a three-layer integrated workflow — 3D facial diagnostics (HAN PREDICT) → RAG-based AI EMR (Smart Charts) → molecular-prescription back-end (Genesis_Medicine) — operating across HAN PREDICT, Inc., the Genesis_Medicine Lab, and Recover Korean Medicine Clinic. The workflow is intended to bridge traditional pattern-based Korean medicine reasoning with modern molecular-mechanistic evidence in a way that respects both layers and that respects the clinician's authority and the patient's autonomy.

**Specific forward actions (in order of priority):**

1. **IRB-approved clinical evaluation protocol** for the integrated workflow at Recover Korean Medicine Clinic (initial submission filed 2026-04-27). The first study examines feasibility, safety, and patient acceptability (n ≈ 50, observational).
2. **Peer-reviewed publication** of the present technical workflow report (anticipated submission to a 한국 한의학 / 의료 정보학 journal in 2026-Q3).
3. **Companion methodology preprint** describing the corrected ABFE protocol with calibration data (T4L99A·benzene benchmark + Boltz-2 calibration on the ChEMBL MMP-1 inhibitor set).
4. **Wet-lab validation** of selected Genesis_Medicine molecular suggestions at Korean CROs (KIT, 켐온; first-tier package budgeted at approximately 15.6 million KRW, 6-week timeline).
5. **Public-facing documentation** of the workflow for patients (consent forms, plain-language information sheets) compliant with PIPA, AI Basic Act, and 의료법 §56.
6. **Open-source release** of non-proprietary components (Genesis_Medicine pipeline; selected Smart Charts integration adapters under a permissive license).
7. **External-population validation**: a follow-on study is planned in cooperation with affiliated Korean medicine clinics in non-강남 metropolitan areas to evaluate generalizability beyond a single-clinic setting.

We emphasize the most important point of this report: this is a system-design and architecture document. **No clinical efficacy or treatment claim is asserted.** All clinical use is conditional on IRB approval and on the prescribing 한의사's individual judgment in each patient encounter.

---

## Acknowledgments

The author thanks the engineering team at HAN PREDICT, Inc. for platform development support and the clinical staff at Recover Korean Medicine Clinic for clinical-context guidance. The Genesis_Medicine Lab pipeline relies on the open-source stack Boltz-2 (MIT), REINVENT 4 (Apache-2.0), ADMET-AI (MIT), OpenMM 8 (MIT), openmmtools (MIT), RDKit (BSD-3), MACE-OFF24 (MIT). The AI assistant Claude (Anthropic) was used as a coding and writing collaborator throughout; all final scientific content is the responsibility of the author.

## Author contributions

HanCheongWoo: study conception, system architecture design, manuscript drafting and revision, regulatory framework analysis.

## Competing interests

The author is the founder and a representative of HAN PREDICT, Inc. (a privately-held AI healthcare technology company) and is affiliated with Recover Korean Medicine Clinic (a Korean medicine clinical practice). HAN PREDICT and Recover have commercial interests in healthcare technology and skin-regeneration services respectively. No patient outcome data are reported in this preprint; the workflow is presented as a system design and is openly documented under CC-BY 4.0.

## Data and code availability

- Genesis_Medicine pipeline (open source, Apache-2.0): <https://github.com/crazat/genesis_medicine>
- HAN PREDICT platform: described at <https://hanpredict.com>; specific clinic-facing components are not open-source.
- Recover Korean Medicine Clinic: <https://recover-clinic.kr>
- IRB protocol documentation will be released after IRB approval, with appropriate patient-information redaction.

---

## References

[1] Korea Health Industry Development Institute (KHIDI). Korean medicine workforce statistics, 2024. <https://www.khidi.or.kr/>

[2] Sorokina M, Merseburger P, Rajan K, et al. COCONUT online: Collection of Open Natural Products database. *J Cheminform* 2021, 13, 2. doi:10.1186/s13321-020-00478-9

[3] Zeng X, Zhang P, Wang Y, et al. NPASS database update: natural-product activity-species source. *Nucleic Acids Res* 2024, 52, D639–D645.

[4] van Santen JA, et al. The Natural Products Atlas 2.0. *Nucleic Acids Res* 2022, 50, D1317–D1323.

[5] Loeffler HH, He J, Tibo A, et al. REINVENT 4: modern AI-driven generative molecule design. *J Cheminform* 2024, 16, 20. doi:10.1186/s13321-024-00812-5

[6] Swanson K, Walther P, Leitz J, et al. ADMET-AI: a machine learning ADMET platform for evaluation of large-scale chemical libraries. *Bioinformatics* 2024, 40, btae416. doi:10.1093/bioinformatics/btae416

[7] Wohlwend J, Corso G, Passaro S, et al. Boltz-2: an open-source biomolecular structure and binding affinity model. Preprint, 2024. <https://github.com/jwohlwend/boltz>

[8] Chodera JD, et al. openmmtools: a batteries-included Python toolkit for OpenMM (v0.26). 2026. doi:10.5281/zenodo.4248373

[9] Mobley DL, Chodera JD, Dill KA. Confine-and-release method: obtaining correct binding free energies in the presence of protein conformational change. *J Chem Theory Comput* 2007, 3, 1231–1235.

[10] Personal Information Protection Commission (PIPC), Republic of Korea. Guidelines for the protection of biometric information, 2024-12-30.

[11] Republic of Korea, Act on the Promotion of Artificial Intelligence Industry and the Establishment of a Foundation for Trustworthy AI (AI Basic Act), promulgated 2024-12-26, in force 2026-01-22.

[12] Peters MB, Yang Y, Wang B, et al. Structural survey of zinc-containing proteins and development of the zinc Amber force field (ZAFF). *J Chem Theory Comput* 2010, 6, 2935–2947. doi:10.1021/ct1002626

---

*Manuscript word count*: ~3,400 (main text excluding references)
*Submission target*: medRxiv (immediate); a Korean Medicine / clinical-informatics peer-reviewed venue (anticipated 2026-Q3)
*Version*: 0.1 draft, 2026-04-26
*License*: CC-BY 4.0 (preprint); platform code licenses as noted in §6
