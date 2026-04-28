# Preprint Upload Step-by-Step Guide (Option A — 14편 즉시 업로드)

**Date**: 2026-04-28
**Plan**: 옵션 A — 영문 미교정 즉시 업로드, priority date 확보
**Distribution**: ChemRxiv 5편 + bioRxiv 7편 + medRxiv 2편

---

## Step 1 — ORCID 가입 (10분, 무료)

1. <https://orcid.org/register> 접속
2. 입력:
   - **First name**: HanCheongWoo (또는 Cheongwoo Han)
   - **Last name**: (성이 분리되면 별도)
   - **Primary email**: admin@hanpredict.com
   - **Backup email**: crazat7@gmail.com
   - **Password**: 8-자 이상
3. 이메일 verification (1분)
4. ORCID iD 발급 (예: `0000-0002-XXXX-XXXX`)
5. **Affiliations 추가**:
   - Genesis_Medicine Lab, Seoul, Republic of Korea (Founder, 2026)
   - HAN PREDICT, Inc. (Founder, 2025-)
   - Recover Korean Medicine Clinic (Director, 2026-)

**완료 후 알려주실 정보**: ORCID iD (예: `0000-0002-XXXX-XXXX`)

---

## Step 2 — ChemRxiv 가입 (5분, 5편 업로드 대상)

대상 paper: **#1 Embelia ribes review · #3 EMB-3 case study · #8 ABFE methodology · #12 50-tool perspective · #14 Topical PBPK**

1. <https://chemrxiv.org/engage/chemrxiv/dashboard> 접속
2. **"Sign in"** → **"Sign in with ORCID"** 클릭
3. ORCID 인증 완료 → ChemRxiv 자동 가입
4. Profile 보강:
   - **Affiliation**: HAN PREDICT, Inc.
   - **Email**: admin@hanpredict.com
   - **Country**: Republic of Korea

**완료 후**: 별도 정보 불필요 (ORCID 인증으로 충분)

---

## Step 3 — bioRxiv 가입 (5분, 7편 업로드 대상)

대상 paper: **#4 Pigmentation · #5 Alopecia · #6 Acne · #7 Photoaging · #9 IPF · #10 Chronotherapy · #13 PIEZO1/MLCK**

1. <https://www.biorxiv.org/submit-a-manuscript> 접속
2. **"Create an account"** → 이메일 가입
3. 입력:
   - **Email**: admin@hanpredict.com
   - **Password**: (별도 password)
   - **First/Last name**: HanCheongWoo
   - **Institution**: HAN PREDICT, Inc.
4. 이메일 verification (1분)

**완료 후 알려주실 정보**: bioRxiv 계정 생성 완료 confirmation

---

## Step 4 — medRxiv 가입 (5분, 2편 업로드 대상)

대상 paper: **#2 Recover workflow · #11 Korean PGx**

1. <https://www.medrxiv.org/submit-a-manuscript> 접속
2. bioRxiv 동일 계정 사용 가능 (동일 plat form)
3. 별도 가입 필요시 동일 절차

---

## Step 5 — 업로드 시작 (편당 10-15분, 총 14편 ~3-4시간)

### 권장 업로드 순서

**Wave 1 (오늘 오전, ChemRxiv 5편)**:
1. #1 Embelia ribes review (foundation paper)
2. #3 EMB-3 case study (가장 풍부한 결과)
3. #14 Topical PBPK methodology
4. #8 ABFE methodology
5. #12 50-tool perspective

**Wave 2 (오늘 오후, bioRxiv 7편)**:
6. #4 Pigmentation screening
7. #5 Alopecia screening
8. #6 Acne microbiome
9. #7 Photoaging EGCG
10. #9 Cross-disease IPF
11. #13 PIEZO1/MLCK (가장 신규)
12. #10 Chronotherapy

**Wave 3 (오늘 저녁, medRxiv 2편)**:
13. #2 Recover workflow
14. #11 Korean PGx topical

### 각 paper 업로드 절차 (공통)

```
1. preprints/_metadata/<NN>_metadata.json 열기
2. 해당 server 로그인 → "Submit new" 클릭
3. Title 복사 (metadata json의 "title")
4. Abstract 복사 (metadata json의 "abstract")
5. Keywords 입력 (metadata json의 "keywords")
6. Author block:
   - Name: HanCheongWoo
   - Email: admin@hanpredict.com
   - ORCID: <Step 1에서 발급받은 iD>
   - Affiliations: 3개 (Genesis_Medicine Lab + HAN PREDICT + Recover)
7. Funding: "Self-funded by HAN PREDICT, Inc."
8. Competing interests: metadata json의 "competing_interests" copy
9. License: CC-BY 4.0
10. Subject category: metadata json의 "category"
11. PDF 업로드: preprints/<NN>/manuscript.pdf
12. Figures 업로드: preprints/<NN>/figures/*.png (이미 PDF 임베드되어 있어 별도 업로드 불필요할 수도)
13. Code repository: <https://github.com/crazat/genesis_medicine>
14. Submit → 24-48시간 후 DOI 발급
```

### 자주 묻는 질문 (FAQ)

**Q1: ChemRxiv가 카테고리 선택을 강요해요**
- A1: "Medicinal Chemistry" 또는 "Theoretical and Computational Chemistry"
- 대부분 paper는 둘 다 해당, 하나 선택

**Q2: bioRxiv가 ORCID 또 입력해요**
- A2: 첫 paper에 입력 후 profile 자동 저장. 다음부터 불필요.

**Q3: 실패한 PDF는?**
- A3: HTML version도 함께 첨부 (preprints/<NN>/manuscript.html)

**Q4: "Funding" 필수 입력?**
- A4: "Self-funded by HAN PREDICT, Inc." 입력 OK

**Q5: "Conflict of interest" 작성?**
- A5: metadata json의 "competing_interests" 그대로 copy

---

## 업로드 후 (3-7일)

### DOI 발급 확인
- ChemRxiv: 24-48시간
- bioRxiv: 24-72시간
- medRxiv: 24-72시간

### 14개 DOI 받은 후 후속:
1. 각 preprint markdown에 DOI 추가 (footer)
2. CLAUDE.md "Submitted preprints" 섹션 업데이트
3. Recover 한의원 홈페이지 RESEARCH 페이지에 DOI list 게재
4. HAN PREDICT 마케팅 카피 "DOI 14편 보유" 사용

---

## 사용자 액션 체크리스트

```
□ Step 1: ORCID 가입 (10분) — ORCID iD 알려주기
□ Step 2: ChemRxiv 가입 (5분, ORCID 인증)
□ Step 3: bioRxiv 가입 (5분)
□ Step 4: medRxiv 가입 (5분 또는 bioRxiv 동일 계정 사용)
□ Step 5: Wave 1 업로드 (5편, 1-2시간)
□ Wave 2 업로드 (7편, 2시간)
□ Wave 3 업로드 (2편, 30분)
```

총 시간 예상: **3-4시간 (단일 day)**
비용: **무료** (모든 server 무료)
출력: **14 DOI** (3-7일 내)
