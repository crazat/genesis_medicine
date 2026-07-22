# HANDOFF — recover-clinic.kr `/research/` 페이지 갱신 + 중요도순 재배열

- **수신**: 홈페이지(recover-clinic.kr) 담당 에이전트
- **작성**: 2026-06-03
- **대상 페이지**: https://recover-clinic.kr/research/
- **저자 정책(중요)**: 모든 레코드 **단독저자 — 한정우 / Han, Cheongwoo** (ORCID 0009-0004-4805-8815). 공동저자 추가 금지.
- **언어**: 페이지 KO/EN 토글 유지. 아래 영문 제목/APA는 **그대로(verbatim)** 사용.

이 문서는 두 가지 작업을 지시한다.
**[A] 콘텐츠 갱신** — 신규 published 논문 1건(paper_A v6) 반영 + 카운트/카드 갱신.
**[B] 중요도순 재배열** — 게시된 전체 레코드를 성과(achievement) 높은 순으로 위→아래 재정렬.

---

## [A] 콘텐츠 갱신 — 해야 할 일 체크리스트

### A-1. 신규 레코드 추가 (가장 중요) — paper_A v6 (Record **XXVI**)

현재 페이지 Card 03(MMP-1)에 "forthcoming paper_A v6"로 적혀 있으나 **이미 정식 published 되었다.** 신규 레코드로 추가할 것.

- **상태**: ✅ Published on Zenodo (2026-06-02, v1, CC-BY-4.0, Preprint, **단독저자**) **+ 동료심사 진행 중** (Journal of Chemical Information and Modeling)
- **DOI**: `10.5281/zenodo.20247828`
- **링크**: https://doi.org/10.5281/zenodo.20247828
- **영문 제목 (verbatim)**:
  > Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide
- **국문 제목 (제안 — 조정 가능)**:
  > MMP-1 아연 활성부위 억제제 랭킹을 위한 3종 신경망 퍼텐셜 교차검증: 보리노스타트·인다파마이드 전산 기반 리포지셔닝 연구
- **APA (verbatim)**:
  > Han, C. (2026). *Cross-Validation of Three Neural Network Potentials for MMP-1 Zn Active-Site Inhibitor Ranking: A Computationally-Driven Repositioning Study of Vorinostat and Indapamide*. Zenodo. https://doi.org/10.5281/zenodo.20247828
- **핵심 성과 (카드/요약용, 수치 verbatim)**:
  - 3종 NNP 랭킹 일치도 Pearson **r = 0.9146** (1000-bootstrap 95% CI [0.817, 0.973]; LOO r = 0.9146 ± 0.0115)
  - 상류 GFN2-xTB OPT pre-relaxation이 컨포머-에너지 이상치(CHEMBL94487)를 **σ 14.27 → 0.007 kcal/mol (2,068배 감소)** — 일반화 가능한 mandatory-OPT-rescue 워크플로
  - PoseBusters v2 물리적 타당성 **94.5%** 통과 (Boltz-2 PDBBind 벤치마크 89.2% 상회)
  - Coverage-calibrated **conformal reliability layer** (보장 커버리지 신뢰구간)
  - 리포지셔닝 가설: **보리노스타트 + 설폰아마이드 이뇨제 계열(인다파마이드 + FDA 승인 16종)** 이 MMP-1 촉매 Zn²⁺ 포켓에 대해 predictable-conformer 영역에 위치 (해당 계열은 ChEMBL에 정량적 MMP-1 활성 기록 없음)
- **분류(status 태그)**: "Published + Under journal review" (또는 페이지 표기 관례에 맞춰 "Preprint · 심사 중")

> **paper_A v6와 기존 MMP-1 테크리포트 관계**: paper_A v6(XXVI)는 기존 레코드 **XXIII(OMol25 paradox) / XXIV(Boltz-2 steering) / XXV(de novo Zn design)** 의 방법론 줄기를 통합·확장한 **종합 플래그십**이다. XXIII/XXIV/XXV는 각자 별도 DOI로 그대로 두고(불변 레코드), XXVI를 그 클러스터의 대표로 상단 배치.

### A-2. 카운트 갱신

| 항목 | 현재 | 갱신 후 |
|---|---|---|
| 상세 공개 기록 (공개 기록) | 25 | **26** |
| 공개 식별자 (DOI/OSF/Zenodo) | 39 | **40** (Zenodo DOI 1건 추가) |

> 14 targets / 50+ tools / 770+ refs 등 다른 카운트는 변경 없음. (만약 paper_A v6용 OSF 미러를 별도 생성하면 식별자 41이 되지만, 현재 Zenodo 단일 — 41은 사용자 결정 사항.)

### A-3. Featured Programs 카드 갱신

- **Card 03 (MMP-1)** 본문에서 "Tech reports × 5; forthcoming paper_A v6/paper_B v1" 문구 **삭제/교체**:
  - 신규 문구(예): "paper_A v6 정식 published (Zenodo `10.5281/zenodo.20247828`) + J. Chem. Inf. Model. **동료심사 진행 중**. 지원 테크리포트: OMol25 paradox(XXIII), Boltz-2 steering(XXIV), de novo Zn design(XXV)."
- **paper_B v1**: 아직 **별도 DOI 미발행** (신뢰성 cascade로 데이터 계속 생성 중). 기존 레코드 XXIV(zenodo.20134442)가 paper_B v0.1. 페이지에는 "준비 중(in preparation)"으로만 표기하고 **새 DOI를 만들지 말 것.**

### A-4. 저자/이해상충(COI) 일관성

- 전 레코드 **단독저자** 표기 유지 (한정우 / Han, Cheongwoo). 공동저자 표기/추가 금지.
- 페이지 소속(Affiliation)에 이미 **HAN PREDICT, Inc. + Genesis_Medicine Lab + Recover Korean Medicine Clinic** 가 명시되어 있어 COI 투명성은 확보됨 → **추가 조치 불필요**.
- 참고(웹 액션 아님): paper_A v6의 Zenodo published 레코드에는 현재 COI 문구가 표시돼 있지 않음. 원고에는 "HAN PREDICT 창업자 / Genesis Medicine R&D, 자금·역할 없음" COI가 기재됨. Zenodo COI는 별도 New-version으로 반영 예정(업로드 에이전트 담당) — 홈페이지 식별자/링크에는 영향 없음.
- "Collaboration Inquiry"의 "Co-author/method development" 트랙은 **기존 사이트 콘텐츠 그대로 유지** — 본 핸드오프는 신규 outreach/협업 제안을 포함하지 않음. 단독저자 정책과 "향후 협업 일반 문의"는 상충하지 않으므로 변경 불필요(문구 조정 여부는 사용자 판단).

---

## [B] 중요도순 재배열 — 성과 높은 순으로 위 배치

### B-1. 정렬 기준 (위에서부터 우선 적용)

1. **외부 검증 단계** — 인덱싱 저널 동료심사 진행 > Zenodo preprint > OSF 테크리포트
2. **방법론 깊이·신규성** — first-in-class 주장, 대규모 재현성 데이터셋, 다중엔진 교차검증, conformal 보정
3. **정량 결과 강도** — r=0.9146, 2,068배 이상치 붕괴, 94.5% PoseBusters, MD 검증 리드 등
4. **임상(피부재생) 번역 관련성** — 리드 동정 + MD 검증된 질환-표적 응용
5. **개념/프레임워크 기여** (상대적으로 하단)

> **대안 관점**: 위는 "과학적 성과" 기준이다. 만약 클리닉 방문자 대상 "임상 번역 우선" 관점을 원하면 **Tier B와 Tier C를 통째로 맞교환**하면 된다. Tier 내부 순서는 자유 조정 가능. 기본 권고는 아래 순서.

### B-2. 권장 전체 정렬 (위 → 아래)

번호는 새 표시 순서. 괄호는 현재 페이지의 기존 Roman 번호.

**◆ Tier A — 동료심사 트랙 플래그십 (최상단 고정)**
1. (XXVI, NEW) **paper_A v6** — MMP-1 3종 NNP 교차검증 + 보리노스타트/인다파마이드 리포지셔닝 — *Published + JCIM 심사 중* — `10.5281/zenodo.20247828`

**◆ Tier B — 핵심 방법론 기여 (신규·정량·재현성)**
2. (XXIII) OMol25 Paradox: NNP 학습-도메인 특이성 — `10.5281/zenodo.20134439`
3. (XXIV) Boltz-2 cofold 이상치 제거 (steering potentials) — `10.5281/zenodo.20134442`
4. (XXV) de novo Zn²⁺ 메탈로하이드롤라제 설계 (LigandMPNN) — `10.5281/zenodo.20134447`
5. (VIII) Calibrated ABFE 파이프라인 (OpenMM 8) — `10.5281/zenodo.20018254`
6. (XVIII) Cost-aware multi-fidelity Bayesian 최적화 스케줄러 — `10.5281/zenodo.20018356`
7. (XIV) Topical skin PBPK 파이프라인 (Dancik 4-layer + logKp) — `10.5281/zenodo.20018345`
8. (XII) Genesis_Medicine 오픈소스 AI 파이프라인 — `10.5281/zenodo.20018343`
9. (XXII) xtb robustness 벤치마크 (method/conformer/solvent) — `10.17605/OSF.IO/6XQNW`
10. (XXI) ZAFF-AMBER Zn 메탈로엔자임 한계 — `10.17605/OSF.IO/Q4Z6W`

**◆ Tier C — 질환-표적 번역 연구 (MD 검증 리드, 클리닉 관련)**
11. (III) EMB-3 항섬유화 후보 (scaffold-hopping) — `10.5281/zenodo.20018333`
12. (I) *Embelia ribes* 리뷰 (EMB-3 모체 맥락) — `10.5281/zenodo.20018329`
13. (IV) 색소침착 tyrosinase/TYRP1/DCT (oxyresveratrol/curcumin, 30 ns MD) — `10.5281/zenodo.20018337`
14. (XV) Universal pterocarpan 스캐폴드 (6-cycle Bayesian, 6 멀티타깃 리드) — `10.5281/zenodo.20018349`
15. (XVII) R16 topical chromanol 리드 (30/60/200 ns MD) — `10.5281/zenodo.20018353`
16. (XVI) R15 chromanol safety-first triage — `10.5281/zenodo.20018351`
17. (XX) R17 chromanol 생성형 atlas (*In Prep*) — `10.5281/zenodo.20018359`
18. (V) 탈모 SRD5A2/AR (Saponin Re/Emodin/Biochanin A) — `10.5281/zenodo.20018339`
19. (XIII) AGA PIEZO1+MLCK 기계전달 리포지셔닝 — `10.5281/zenodo.20018378`
20. (VII) 광노화 MMP-1+SIRT1 폴리페놀 — `10.5281/zenodo.20018372`
21. (VI) 염증성 여드름 SRD5A2/AR (Baicalein; Berberine hERG 플래그) — `10.5281/zenodo.20018370`
22. (IX) 피부흉터→전신섬유증 Open Targets (cross-disease 한계) — `10.5281/zenodo.20018374`

**◆ Tier D — 통합 프레임워크 / 맥락**
23. (XIX) 한약재 스캐폴드 atlas (동의보감/향약집성방) — `10.17605/OSF.IO/78WY5`
24. (XI) 한국인 약물유전체 패널 (국소 개인화) — `10.17605/OSF.IO/BXRGA`
25. (X) 자오류주(子午流注) 시간치료 프레임워크 — `10.5281/zenodo.20018376`
26. (II) 한의원 통합 AI 워크플로 (Framework) — `10.17605/OSF.IO/7ZWQS`

> 편집 옵션: (II) 통합 워크플로는 성과 기준상 하단이지만, 방문자 오리엔테이션용 "개요" 글로 별도 상단 고정(pin)을 원하면 가능 — 성과-랭킹과 분리된 편집 결정. 사용자 판단.

### B-3. Featured Programs 카드 순서도 재배열

성과 최상단 = paper_A v6(MMP-1)이므로 카드 순서를 다음으로 권장:
- **Card 01 → MMP-1** (paper_A v6, 저널 심사 트랙) ← 기존 Card 03을 1번으로 승격 + A-3 문구로 갱신
- **Card 02 → EMB-3** (기존 Card 01)
- **Card 03 → R16/R17 chromanol** (기존 Card 02)

---

## [C] 게시 가능 vs 비공개 경계 (반드시 준수)

**게시 OK**
- 모든 Zenodo/OSF DOI 및 링크 (공개 영구 식별자)
- paper_A v6 "Journal of Chemical Information and Modeling **동료심사 진행 중**" — 일반적·신뢰도 제고 표현 (저널명/일반 상태만)
- 단독저자명, ORCID, 소속 3종

**게시 금지 (내부 정보)**
- JCIM 내부 **Submission ID** (51B8CAD3-… 형식) 및 향후 부여될 Manuscript ID — 비공개
- 내부 제출/심사 일정, COI 내부 검토 메모, cascade/compute 운영 세부

> 주의: "심사 중" 표기는 저널 심사 결과가 불확실하므로 선택 사항(되돌릴 위험 존재). 보수적으로 가려면 paper_A v6를 "Published (Zenodo)"로만 표기하고 저널 언급은 게재확정(accept) 후 추가하는 방안도 가능 — **사용자/담당 에이전트 재량**. 본 핸드오프 기본 권고는 "Published + 심사 중" 동시 표기.

---

## [D] 요약 — 담당 에이전트 액션 5줄

1. 신규 레코드 **XXVI = paper_A v6** 추가 (`10.5281/zenodo.20247828`, 단독저자, Published + JCIM 심사 중) — 위 A-1의 제목/APA/수치 verbatim 사용.
2. 카운트 **25→26 기록, 39→40 식별자**.
3. Card 03(MMP-1) "forthcoming paper_A v6" 문구 교체 + Featured 카드 순서 **MMP-1 → 1번** 승격.
4. 전체 레코드를 **[B] Tier A→D 순서**로 재배열 (성과 높은 순 위로).
5. 내부 Submission/Manuscript ID는 절대 게시하지 말 것. paper_B v1 새 DOI 만들지 말 것(준비 중 표기만).
