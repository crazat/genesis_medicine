# Preprint Submission Guide

> 16주 12편 preprint mass-production 일정의 실행 가이드.
> 사용자 실행 방법을 단계별로 명시. 의료법 §56 광고 활용 카피 템플릿 포함.

작성: 2026-04-26 · 대상: HanCheongWoo (HAN PREDICT Inc. founder + Recover 한의원 운영)

---

## 0. 사전 준비 (W1 D-1, 30분)

### 0.1 ORCID 등록 — 모든 preprint 플랫폼의 공통 author identity
1. <https://orcid.org/register> 접속
2. 이메일 (admin@hanpredict.com 또는 별도 학술 계정) + 이름 등록
   - First name: HanCheongWoo (또는 분리 표기 Han, CheongWoo)
   - Family name: 사용자 결정
3. ORCID iD 발급 (예: `0000-0000-0000-0000` 형식)
4. **Affiliations 추가**:
   - HAN PREDICT, Inc. (Founder, 2024–present 또는 정확 일자)
   - Recover Korean Medicine Clinic (Affiliated, 2026–present)
   - Genesis_Medicine Lab (Lead, 2026–present)
5. **Works**: 향후 preprint 발행 시 자동 연결되도록 설정

→ ORCID iD를 모든 preprint manuscript의 byline에 추가 (예: `HanCheongWoo (ORCID: 0000-0000-0000-0000)`)

### 0.2 GitHub 공개 리포지토리 정비
- <https://github.com/crazat/genesis_medicine> 공개 상태 확인
- README.md 업데이트 (HAN PREDICT + Recover + Genesis_Medicine 3-pillar 명시)
- LICENSE 파일 (Apache-2.0) 확인
- 각 preprint의 supporting code 링크 명시 (manuscript "Data and code availability" 섹션)

### 0.3 ResearchGate / Google Scholar 프로필 (선택, 권장)
- 마케팅 가시성 ↑
- ResearchGate: <https://www.researchgate.net/signup>
- Google Scholar: ORCID 연결 시 자동 인덱싱

---

## 1. 플랫폼별 제출 가이드

### 1.1 bioRxiv (Wave 1 #1, Wave 2-3 대부분)

**대상 preprints**:
- #1 *Embelia ribes* review
- #4-#7 5 disease case studies
- #9-#11 cross-disease, chronotherapy, Korean PGx
- #12 50-tool perspective

**제출 절차** (~30분):

1. **계정 등록**: <https://www.biorxiv.org/login>
   - Email + ORCID 연결
   - Co-author 정보 (단독 저자 시 본인만)
2. **제출 페이지**: <https://www.biorxiv.org/submit-a-manuscript>
3. **원고 형식**:
   - PDF 업로드 (가장 일반적, manuscript.md → pandoc/Word/LaTeX → PDF)
   - 또는 Word `.docx` (LaTeX·Markdown 자동 변환 가능)
   - Supplementary files 별도 upload 가능
4. **메타데이터 입력**:
   - Title (제목 100-150자)
   - Abstract (250자, manuscript abstract 그대로)
   - Subject area: "Pharmacology" 또는 "Plant Biology" 또는 "Genetics" 등
   - Keywords (5-8개)
   - License: **CC-BY 4.0** 권장 (가장 자유로운 reuse)
5. **Co-authors**: 단독 저자 시 본인만 (HanCheongWoo + ORCID + 3 affiliations)
6. **승인 위원회 (screening)**: bioRxiv 자체 screening 1-2일
7. **DOI 발급**: 승인 시 즉시 DOI 부여 (예: `10.1101/2026.04.26.123456`)
8. **마케팅 노출**: bioRxiv RSS, Twitter/X, 학술 검색 인덱싱

**수정 / 새 버전**: 동일 DOI 유지, 버전 v2/v3 표기. 흔적 남으나 "이전 버전 오류 수정" 정직하게 가능.

---

### 1.2 medRxiv (Wave 1 #2 + Wave 3 #6 등 임상 정보학)

**대상**: #2 Recover workflow, #6 facial_dx + 분자 처방 통합 등 임상 데이터 / 시스템 설계 paper

**bioRxiv와 동일 절차**, 단:
- Subject area: "Health Informatics" / "Health Policy" / "Public and Global Health"
- IRB 정보 명시 필수 (IRB 미신청 시 "system design and protocol; not requiring IRB at this stage" 식 명시)
- 임상 데이터 포함 시 환자 동의·익명화 명시

---

### 1.3 ChemRxiv (Wave 1 일부 + Wave 3 #8)

**대상**:
- #3 Embelin → EMB-3 case study (이번 작성, computational chemistry 특화)
- #8 ABFE methodology
- 향후 모든 분자 신약 발굴 정량 결과 paper

**제출 절차** (~30분):

1. **계정 등록**: <https://chemrxiv.org/engage/chemrxiv/log-in>
2. **제출 페이지**: <https://chemrxiv.org/engage/chemrxiv/dashboard>
3. **원고 형식**: PDF 권장. Word·LaTeX OK
4. **카테고리**: "Theoretical and Computational Chemistry" / "Medicinal Chemistry"
5. **Section**: "Drug Discovery and Drug Delivery"
6. **License**: CC-BY 4.0
7. **DOI 발급**: 1-2일 내 (예: `10.26434/chemrxiv-2026-...`)

**ChemRxiv 특수 사항**:
- 화학 구조 SMILES 직접 검증 (자동 RDKit 검사)
- 분자 image / SAR table figure 포함 시 더 viewable
- Cambridge Open Engage 호스팅 (RSC + ACS + GDCh 연합)

---

### 1.4 OSF Preprints (백업 / 비주류 주제)

**대상**: 기성 플랫폼이 거부할 만한 양식 또는 fast publication 필요 시 backup

- <https://osf.io/preprints/>
- 분류 자유도 높음
- DOI 부여
- 빠른 turnaround (수 시간)

---

## 2. Word/PDF 변환 — Markdown → 제출 형식

**현재 manuscript은 모두 Markdown (.md)**. 제출용으로 변환 필요.

### 2.1 가장 빠른 옵션 (Pandoc, 1분)

```bash
sudo apt install pandoc texlive-xetex   # 1회만
cd preprints/01_embelia_ribes_review/
pandoc manuscript.md -o manuscript.pdf --pdf-engine=xelatex \
    --variable=mainfont:"Liberation Serif" \
    --variable=monofont:"Courier New" \
    --variable=geometry:margin=1in \
    --toc --number-sections
```

**또는 Word (학술지 호환):**
```bash
pandoc manuscript.md -o manuscript.docx --reference-doc=template.docx
```

### 2.2 더 예쁜 LaTeX (학술지 양식)
- Overleaf 사용 권장 (<https://www.overleaf.com/>)
- IEEE / ACS / Springer template 적용
- bioRxiv·ChemRxiv·medRxiv 모두 LaTeX 양식 OK
- **단**: preprint 단계는 PDF 양식 자유. LaTeX 미적용해도 무방.

### 2.3 Figure / Table 처리
- 본 manuscript 내 inline table은 그대로 유지
- 별도 figure (예: pipeline diagram, SAR scatter) 필요 시 matplotlib로 PNG 생성 후 supplementary 첨부
- W4 시점: SAR panel scatter chart 생성 (코드 작성 별도 요청 시 가능)

---

## 3. 제출 후 마케팅 활용 (Recover 한의원)

### 3.1 Recover 홈페이지 RESEARCH 페이지 구조 (제안)

```
recover-clinic.kr/research

[헤더] 본원 부설 Genesis_Medicine Lab의 학술 연구 활동

[섹션 1: 연구 활동 소개]
"Recover 한의원은 HAN PREDICT (AI 헬스케어 테크 회사) 및 Genesis_Medicine
연구실과 통합 운영되며, 한약·천연물 기반 신약 개발 in silico 연구를
자체 수행하고 있습니다."

[섹션 2: 발표 연구]
- Preprint 1: [제목] (DOI: 10.1101/...)
- Preprint 2: [제목] (DOI: 10.1101/...)
- ...

[섹션 3: 연구의 의의]
"본원의 임상은 위 연구로 뒷받침됩니다. 단, 모든 연구는 in silico
단계이며, 임상 효능은 별도 IRB 승인 임상시험으로 검증할 예정입니다."

[섹션 4: 더 읽기]
- GitHub 오픈소스: github.com/crazat/genesis_medicine
- Preprint 전문: bioRxiv / medRxiv / ChemRxiv 직접 링크
```

### 3.2 마케팅 카피 템플릿 (의료법 §56 안전)

#### 카피 A — 일반 환자 대상 (홈페이지·블로그)
```
"Recover는 단순한 한의원이 아닙니다. 본원의 부설 연구실 (Genesis_Medicine)에서
수행한 N편의 학술 연구가 bioRxiv·ChemRxiv 등 국제 학술 플랫폼에 공개되어
있습니다. AI 시대의 한방 신약 발굴 — 본원에서 직접 진행합니다."

[하단] "* 본 연구는 in silico (컴퓨터 시뮬레이션) 단계이며, 임상 효능은
별도 검증이 필요합니다. 자세한 내용은 RESEARCH 페이지의 각 논문을 참고하세요."
```

#### 카피 B — 의료인 / 학술 대상
```
"Recover Korean Medicine Clinic operates an integrated research program with
HAN PREDICT, Inc. and Genesis_Medicine Lab. Our publications (preprints to date:
N): [DOI list]. The clinic's practice is informed by, but not limited to,
this research program; all clinical decisions are made under the prescribing
한의사's authority."
```

#### 카피 C — 보도자료 (W14, D-14)
```
[제목] "강남 Recover 한의원, 한방 신약 in silico 연구 12편 학술 등재
       — AI 시대 한방 클리닉 모델 첫 사례"

[리드] 강남에 8월 15일 개원하는 Recover 한의원 (대표 한청우)이 부설
연구실 Genesis_Medicine Lab과 통합 운영사 HAN PREDICT (testifying.com)를
통해 한약·천연물 기반 신약 발굴 in silico 연구 12편을 학술 플랫폼
bioRxiv·medRxiv·ChemRxiv에 등재했다.

[중간] 한청우 대표는 "환자 진료의 분자 수준 근거를 직접 자체 연구로
구축하는 한의원 모델"이라고 설명했다. 12편의 연구는 흉터·기미·탈모·
여드름·광노화의 5대 피부 분자 메커니즘 + AI 신약 발굴 방법론 + 한약
처방 정합성 review 등을 다룬다.

[하단] 모든 연구는 in silico (컴퓨터 시뮬레이션) 단계이며, 임상 효능
입증은 별도 IRB 승인 임상시험을 통해 진행 예정이라고 본원은 밝혔다.
```

### 3.3 의료법 §56 방어 체크리스트

광고 카피 작성 시 다음 모든 항목을 충족시키면 §56 위반 위험 최소화:

- [ ] 각 marketing claim에 DOI 또는 preprint URL 인용
- [ ] "in silico, 임상 효능 미검증" disclaimer 명시
- [ ] 특정 화합물 이름의 "치료 효능" 표현 회피
- [ ] "연구 활동" 자체를 brand로 표현
- [ ] 모든 광고에 "RESEARCH 페이지 참고" 링크 첨부
- [ ] 환자 사례 / 전후 사진은 IRB 승인 임상자료에서만
- [ ] AI 사용 자체를 환자에게 disclosure (AI 기본법 transparency)

---

## 4. 16주 일정 — 제출 timeline

| 주 | 작업 | 산출 |
|---|---|---|
| W1 (D-110) | ORCID + GitHub 정비 + Pandoc 설치 | 사전준비 완료 |
| W2 (D-103) | Preprint #1 (Embelia ribes review) → bioRxiv 제출 | DOI #1 |
| W3 (D-96) | Preprint #2 (Recover workflow) → medRxiv 제출 | DOI #2 |
| W4 (D-89) | **Recover RESEARCH 페이지 라이브** + Preprint #3 (EMB-3 case study) → ChemRxiv | DOI #3, 마케팅 1차 |
| W5-7 (D-82~) | Preprints #4-#7 (5 disease cases) | DOI #4-#7 |
| W8-11 (D-58~) | Preprints #8-#11 (methodology + cross-disease + chronotherapy + PGx) | DOI #8-#11 |
| W12-14 (D-30~) | Preprint #12 (50-tool perspective) + 보도자료 + TV 컨택 | DOI #12, 미디어 |
| W15-16 (D-Day) | Phytomedicine + J Cheminform peer-review submission | in-review × 2 |

**개원 D-Day (2026-08-15)**: preprint 12편 + peer-review 2편 in-review 보유.

---

## 5. 비용·시간 자원 추정

### 5.1 직접 비용
- ORCID, bioRxiv, medRxiv, ChemRxiv 모두 **무료**
- Overleaf 무료 tier 충분 (LaTeX 사용 시)
- Pandoc 무료
- **총 직접 비용: ₩0**

### 5.2 옵션 비용 (선택)
- 영문 교정 서비스 (preprint 1편당 ~₩200,000-300,000): 우선순위 paper만 권장 (Phytomedicine peer-review 제출용 #1, #8)
- DOAJ / Hindawi 같은 부적절 vanity 저널 회피

### 5.3 시간 자원
- 사용자 검토 시간: preprint 1편당 1-2시간 (수정 코멘트 + 승인)
- 제출 시간: preprint 1편당 30분
- **사용자 16주 총 부담: ~30-40시간** (= 주 2-3시간)

---

## 6. 즉시 실행 (오늘-내일)

### 오늘
1. ORCID 등록 (5분)
2. bioRxiv 계정 (5분)
3. ChemRxiv 계정 (5분)
4. medRxiv 계정 (5분)
5. Pandoc 설치 (`sudo apt install pandoc texlive-xetex`)

### 내일
1. Preprint #1 (`preprints/01_embelia_ribes_review/manuscript.md`) → 사용자 검토
2. 검토 OK → Pandoc PDF 변환 → bioRxiv 제출
3. DOI 부여 1-2일 대기

### W2 (D-103, 다음 주)
1. Preprint #2 사용자 검토 → medRxiv 제출
2. Preprint #3 사용자 검토 (이번 작성) → ChemRxiv 제출
3. **3개 DOI 보유 시점부터 Recover RESEARCH 페이지 wireframe 발주 가능**

---

## 7. 잠재 위험 + 대비

| 위험 | 대비 |
|---|---|
| bioRxiv screening rejection | 30%만 reject (in silico만 reject 거의 없음) → OSF Preprints fallback |
| 영문 표현 critique | 우선순위 #1·#8 paper만 영문 교정 발주 |
| Boltz-2 / ABFE 결과 잘못 발견 | Errata 또는 v2 업로드 (DOI 유지) |
| 의료법 §56 민원 | 광고 카피 모두 §56 체크리스트 통과 + 즉시 정정 가능 형태 |
| 12편 모두 채우기 어려움 | 8-10편으로 줄이고 quality 강화. 양보단 quality |

---

## 8. 도움 필요한 시점

다음 단계에서 사용자 입력 필요:

- ORCID iD 발급 후 알려주시면 모든 manuscript에 자동 추가
- 첫 bioRxiv 제출 후 DOI 부여되면 알려주시면 후속 preprint에 cross-reference
- Pandoc PDF 변환 결과 만족 안 하면 LaTeX 양식 변환 작업 가능
- Recover RESEARCH 페이지 wireframe 시각화 필요 시 추가 작업
