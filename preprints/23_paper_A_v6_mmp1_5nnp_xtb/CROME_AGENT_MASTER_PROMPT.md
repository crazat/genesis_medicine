# Crome Agent Master Prompt — paper_A v6 D14 Zenodo Deposit Preparation

**User**: Cheongwoo Han (crazat7@gmail.com, ORCID 0009-0004-4805-8815)
**Date**: 2026-05-17 KST
**Authorization**: 사용자 명시 D0 외부 publication action confirm (2026-05-17 08:30경)

---

## OVERVIEW

paper_A v6 D14 Zenodo deposit (2026-05-30) prep 3-track parallel execution:
- **Task A** (CRITICAL, D15-D30 gate): Korean PI 3-PI 공동저자 outreach email 발송
- **Task B** (D13-D14 prep): Zenodo deposit draft 사전 작성
- **Task C** (D0+ continuous): PubMed daily alert 8-query 구독

**Dependencies**: A (immediate) → B (D14 publish) → C (continuous monitoring)
**Execution order**: A → C → B (A는 가장 시간 sensitive, B는 D14 직전, C는 background continuous)

---

# TASK A: Korean PI 3-PI 공동저자 outreach email 발송 (가장 critical)

## 목표
paper_A v6 mini-preprint (Zenodo D14 2026-05-30 deposit 예정)에 한국 PI 3명 공동저자 제안 한글 email 발송.

## 발송 시점
**Today (D0 2026-05-17)** — D7 (2026-05-23) response gate, D14 publish 위해 즉시 발송.

## Email source
파일 `/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/korean_co_author_emails.md` 안에 3개 한글 email 템플릿 그대로 복사 사용.

## 발송 대상 3 PI (각각 별도 email, CC 없음)

### Email A1 — SNUH 정진호 교수
- **To**: chungjh@snu.ac.kr (서울대학교병원 피부과 정진호 교수)
- **Subject**: paper_A 공동 저자 (Co-authorship) 제안: MMP-1 5-NNP cross-validation drug repositioning preprint
- **Body**: `korean_co_author_emails.md` "Email 1" 섹션 그대로
- **Attachments**:
  - `/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/manuscript_v0.2.md`
  - `/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/paper_a_part_ii_concept_1pager.md`
  - figures (figure1-5.pdf 5개)

### Email A2 — Amorepacific NBRI
- **To**: nbri@amorepacific.com (또는 https://www.amorepacific.com/kr/ko/contact 공식 inquiry form)
- **Subject**: 산학연 공동연구 - MMP-1 5-NNP cross-validation cosmeceutical translation (Zenodo preprint)
- **Body**: `korean_co_author_emails.md` "Email 2" 섹션 그대로
- **Attachments**: 동일

### Email A3 — KAIST 김우연 교수
- **To**: wykim@kaist.ac.kr (KAIST 화학생물공학과 김우연 교수, BInD lab)
- **Subject**: paper_A 공동 저자 - 5-NNP cross-validation methodology consultation (BInD framework parallel)
- **Body**: `korean_co_author_emails.md` "Email 3" 섹션 그대로
- **Attachments**: 동일

## Sender account
- **From**: crazat7@gmail.com (Gmail)
- **Signature**:
  ```
  한정우 드림
  ORCID: 0009-0004-4805-8815
  Email: crazat7@gmail.com
  ```

## Step-by-step actions
1. Gmail 로그인 (crazat7@gmail.com)
2. **3개 별도 Compose 창 작성** (PI별 별도, 일괄 발송 X)
3. 각 email body는 `korean_co_author_emails.md`에서 직접 복사 (한글 그대로)
4. Attachments 3-5개 첨부 (manuscript_v0.2.md PDF 변환 후 첨부 권장; .md 그대로 첨부도 ok)
5. **Send 클릭 전 사용자 final confirm 받기** (Subject + Body + Attachments review)
6. Send 후 Sent folder 3개 email 확인
7. 24h 안에 bounce-back (mailer-daemon) 모니터링

## Manuscript PDF 변환 (Optional but recommended)
- 사용자 local 또는 Pandoc CLI: `pandoc manuscript_v0.2.md -o manuscript_v0.2.pdf`
- 또는 markdown → Google Docs paste → Export PDF
- 또는 .md 파일 그대로 첨부 (수신자가 마크다운 viewer 사용 가능)

## Verification checkpoints
- [ ] 3 emails sent (Sent folder 3개 entry 확인)
- [ ] Subject line 각 PI별 정확
- [ ] Body 한글 인코딩 깨짐 없음
- [ ] Attachments 정확 첨부 (3-5개 per email)
- [ ] Signature 포함

## Fallback
- 이메일 주소 invalid → SNUH/Amorepacific/KAIST 공식 inquiry form 사용
- 24h 안 bounce 시 alternate 이메일 (snu.ac.kr 전체 검색 또는 KAIST faculty directory)
- D7 (2026-05-23) 무응답 → acknowledgment-only listing 또는 D14 single-author Zenodo deposit fallback (memory #20-22 precedent 동일)

---

# TASK B: Zenodo deposit draft 사전 작성 (D14 publish ready state)

## 목표
Zenodo (https://zenodo.org)에 paper_A v6 #23 record를 **draft 상태로 미리 작성**. D14 (2026-05-30) publish 실행만 남기는 ready state.

**중요**: Publish는 D14 시점 사용자가 직접 실행 (draft만 작성).

## Account
- **URL**: https://zenodo.org
- **Login**: ORCID 0009-0004-4805-8815 (OAuth) 또는 GitHub OAuth (existing 22 records 활성)
- **Sequence**: paper_A v6 = 23번째 record (next sequence after #20-22)

## Step-by-step actions

### Step 1: Login
1. https://zenodo.org 접속
2. 우상단 "Log in" → ORCID OAuth (또는 GitHub OAuth)
3. crazat7@gmail.com / Cheongwoo Han account 확인

### Step 2: New Upload
4. "New Upload" 버튼 클릭 (또는 https://zenodo.org/uploads/new)

### Step 3: Files upload
5. "Files" 영역에 다음 파일 drag-drop 또는 upload:
   - `/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/manuscript_v0.2.md` (또는 PDF 변환본)
   - figures/figure1-5.pdf (5개 separate files)
   - figures/figure1-5.png (300dpi version, optional)
   - references_expanded.md (98 references)
   - SI/ raw CSVs (xtb_all_chains_top1_v2_final.json + posebusters_v95_audit_v2.json + paper_b_full_140_signature.json + paper_a_nnp_bootstrap.json + zbg_rf_v3.json) — Supplementary Information

### Step 4: Metadata fields (cover_letter_zenodo_v0.1.md 참조 그대로 paste)

**Resource type**: Publication → Preprint

**Title**:
```
Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide
```

**Creators** (CRediT-ordered):
1. **Han, Cheongwoo** (ORCID 0009-0004-4805-8815)
   - Affiliation: Independent Researcher / Genesis Medicine (Korea)
   - Role: Conceptualization, Methodology, Software, Formal Analysis, Investigation, Data Curation, Writing-Original Draft, Visualization, Project Administration
   - **Corresponding author**: ✓ checked

2-4. **[Co-author placeholders]** (D7 response 후 추가):
   - SNUH Chung Jin Ho (D7 confirmed 시)
   - Amorepacific NBRI lead (D7 confirmed 시)
   - KAIST Kim Woo-Youn (D7 confirmed 시)

**Description** (250-300w):
`cover_letter_zenodo_v0.1.md` "Description" 섹션 그대로 paste (Abstract 4-paragraph form):

```
Matrix metalloproteinase-1 (MMP-1), a zinc-dependent collagenase central to skin photoaging, periodontal disease, atherosclerosis, and cancer metastasis, is a high-value drug target across seven major organ systems. The hydroxamate HDAC inhibitor vorinostat and the sulfonamide diuretic indapamide are clinically used drugs with multi-organ pleiotropy profiles, yet their direct atomistic binding modes against the MMP-1 catalytic Zn²⁺ pocket remain uncharacterized. ChEMBL332 (MMP-1 target) contains zero quantitative IC50/Ki records for vorinostat (despite 8,274 total ChEMBL activities) and only two placeholder records (standard_value=None) for indapamide — a quantitative repositioning gap.

We address this with a three-engine neural-network-potential (NNP) cross-validation pipeline: (1) Boltz-2 protein-ligand cofold (25 cycles × 100 samples × 15 ligands = 37,500 structures); (2) GFN2-xTB single-point + tight-optimization in three solvent modes (gas, water-ALPB, MMP-1-mimetic ε=4.0); (3) cross-NNP consensus over Orb-v2, MACE-OMol25, and Orb-v3-OMol25 (charge+spin-aware) — Pearson r=0.9146 with 1000-bootstrap 95% CI [0.817, 0.973]. xtb-refinement reduces CHEMBL94487 conformational energy variance from σ=14.27 to σ=0.007 kcal/mol (2,068× reduction).

PoseBusters v2 audit yields 94.5% mean pass rate (n=45, all structures ≥ 11/12 checks, 33% perfect 12/12) — exceeding the Boltz-2 PDBBind benchmark (89.2%). Indapamide ΔE_relax = 6.42-7.48 kcal/mol places it within the predictable-conformer regime (NOT a σ-outlier), supporting its repositioning candidacy.

A complexity-aware σ-outlier signature on n=140 SAR (BCUT/ETA/spectral descriptors, r<-0.97, p≈0) enables a priori xtb-OPT rescue triage for natural-product cofold ensembles. The work establishes vorinostat and indapamide as priority repositioning candidates for MMP-1 with a 7-organ Korean institutional pleiotropy framework anchored on the Periostat® FDA 1998 28-year mechanistic precedent.
```

**Keywords**:
```
MMP-1; matrix metalloproteinase; neural network potential; Boltz-2; GFN2-xTB; cross-validation; zinc coordination; drug repositioning; vorinostat; indapamide; photoaging; Periostat; computational chemistry; Korean dermatology; medicinal chemistry; Mordred descriptors; BCUT eigenvalues
```

**Subject categories** (Zenodo 카테고리 + ANZSRC FoR codes):
- Computational Chemistry
- Drug Discovery
- Machine Learning Potentials

**License**: Creative Commons Attribution 4.0 International (CC BY 4.0)

**Community** (선택):
- "drug-discovery" 시도
- Fallback: no-community (token publish scope 부족 시)

**Related identifiers** (선택):
- Cites: 98 references (references_expanded.md)
- IsPartOf: paper_A series (Part I/II/III/v6.1)

**Funding**: (Independent researcher, no external funding)

**COI + Ethics statement**:
- No conflicts of interest declared
- In-silico-only, ChEMBL/UniProt public data
- No human subjects, no animal experiments, no IRB required

### Step 5: SAVE DRAFT (publish 누르지 말 것!)
6. 페이지 하단 **"Save"** 클릭 (publish 아닌 save draft)
7. **"Preview"** 버튼으로 정확성 확인
8. URL 회신 (예: https://zenodo.org/records/draft/XXXXXX)

### Step 6: D14 publish 직전 추가 (사용자가 직접 진행)
- D14 (2026-05-30) 사용자 직접 publish 클릭 → DOI 자동 부여 (10.5281/zenodo.XXXXXXXX)
- D7 confirmed co-authors 추가 시 metadata edit
- Cover letter v1.0 finalize 후 attach (optional)

## Verification checkpoints
- [ ] Draft saved (publish 안 됨, draft URL 확인)
- [ ] Files upload 5-10개 정확
- [ ] Metadata 필드 모두 입력
- [ ] Title 정확 (95 chars, ASCII-safe)
- [ ] Creator ORCID 정확
- [ ] License CC-BY-4.0
- [ ] Draft URL 사용자에게 회신

---

# TASK C: PubMed daily alert 구독 (Dai 2025 fast-follower watch)

## 목표
paper_A v6 priority threat (Dai 2025 PMID 40158057) 후속 publications 매일 알림 구독.

## Account
- **URL**: https://www.ncbi.nlm.nih.gov/myncbi/
- **Login**: NCBI account (crazat7@gmail.com)
- **새 계정** 필요 시 무료 가입 (https://www.ncbi.nlm.nih.gov/account/)

## Search queries (8개, /tmp/pubmed_daily_alert.py 검증됨)

각 query 별도 alert subscription:
1. `MMP-1 AND (Boltz OR cofold)`
2. `MMP-1 AND (neural network potential OR NNP)`
3. `Vorinostat AND MMP-1`
4. `Indapamide AND MMP`
5. `Indapamide AND skin AND photoaging`
6. `Indapamide AND nephroprotection`
7. `sulfonamide diuretic AND MMP`
8. `matrix metalloproteinase AND machine learning AND zinc`

## Step-by-step actions

### Step 1: Login
1. https://www.ncbi.nlm.nih.gov/pubmed 접속
2. 우상단 "Sign in" → Google OAuth (crazat7@gmail.com) 또는 ORCID OAuth

### Step 2: Alert 8개 등록 (각 query 별도)
3. 각 query 검색창에 paste + Enter
4. 검색 결과 페이지 우상단 "Create alert" 클릭
5. Alert settings:
   - **Name**: 명확한 query 이름 (e.g., "MMP-1 × Boltz cofold 2026-05-17")
   - **Frequency**: Daily
   - **Email**: crazat7@gmail.com
   - **Format**: Plain text 또는 HTML
6. "Save" 클릭
7. 8개 alert subscription 모두 등록 후 https://www.ncbi.nlm.nih.gov/myncbi/collections/bibliography/ 에서 확인

## Verification checkpoints
- [ ] 8 alerts subscribed (My NCBI dashboard 확인)
- [ ] Daily frequency 모든 alert
- [ ] Email crazat7@gmail.com 정확
- [ ] 첫 alert email D+1 (2026-05-18) 수신 확인

## Fallback
- NCBI account 없으면 free signup
- Daily alert limit 도달 시 weekly로 일부 전환

---

# EXECUTION ORDER 권장

```
Day 0 (Today 2026-05-17):
  09:00-10:00  Task A (Korean PI 3 emails)        ★ 가장 critical, D15-D30 gate
  10:00-10:30  Task C (PubMed 8 alerts)            ★ background, 즉시 구독
  10:30-12:00  Task B (Zenodo draft 작성)          ★ D14 ready state

Day 1-7 (2026-05-18 to 2026-05-23):
  Daily       Task C alert email 확인
  Daily       Korean PI response monitor
  
Day 7 (2026-05-23): Korean PI response gate

Day 13-14 (2026-05-29 to 2026-05-30):
  Co-author 명단 finalize → Zenodo draft metadata update → Publish
```

---

# COMMON ERROR + RECOVERY

| Error | Cause | Recovery |
|-------|-------|----------|
| Gmail 로그인 실패 | 2FA / Captcha | User manual login 후 Crome resume |
| Attachment size too large | manuscript_v0.2.md PDF >25MB | Compress 또는 Google Drive link |
| Zenodo OAuth fail | Token expired | Re-authorize ORCID OAuth |
| PubMed alert limit | Account에 alerts 너무 많음 | Old alerts cleanup 후 add |
| Korean PI email bounce | Address invalid | 공식 inquiry form fallback |

---

## FINAL CONFIRMATION (Crome Agent → User)

Each task 완료 후 다음 정보 사용자에게 회신:
- Task A: 3 emails sent timestamps + Sent folder URL
- Task B: Zenodo draft URL (publish 안 함)
- Task C: 8 NCBI alert subscription URLs

User wakes 시 또는 D7/D14 critical gates에서 상태 review.

---

**Document**: Crome Agent master prompt v1.0
**Plan reference**: `/home/crazat/.claude/projects/-mnt-d/memory/project_paper_a_v6_zenodo_priority_2026_05_30.md`
**Manuscript reference**: `/home/crazat/genesis_medicine/preprints/23_paper_A_v6_mmp1_5nnp_xtb/`
