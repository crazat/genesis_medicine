# HANDOFF — recover-clinic.kr `/research/` 무결성 정정 (2026-07-20)

- **수신**: 홈페이지(recover-clinic.kr) 담당 에이전트
- **작성**: 2026-07-20
- **대상 페이지**: https://recover-clinic.kr/research/
- **성격**: 콘텐츠 **정정(correction)**. 신규 추가가 아니라, 2026-06-03 핸드오프로 올린 내용 중 **이후 무효화된 주장**을 걷어내는 작업.
- **저자 정책(불변)**: 전 레코드 **단독저자 — 한정우 / Han, Cheongwoo** (ORCID 0009-0004-4805-8815). 공동저자 추가 금지.
- **언어**: 페이지 KO/EN 토글 유지.

## 배경 (왜 정정하나 — 1문단)

2026-07-16 1차출처(PubChem REST) 감사에서, MMP-1 작업의 리간드 패널 파일(`data/chembl_mmp1_calibration.csv`, 15행)의 **화합물 이름·IC50·문헌인용이 전부 검증 불가**로 판명됐다(이름 7개 전부 실제와 다른 분자, 15개 중 14개가 PubChem ~1.19억 화합물에 미등록). 이에 따라 **화합물 정체·역가·"알려진 MMP-1 억제제"·리포지셔닝(보리노스타트/인다파마이드) 주장 일체가 무효**다. 다만 **재현성 계산 주장(cross-NNP 일치·conformal·PoseBusters·σ 노이즈플로어·용매/선택 강건성)은 전부 생존**한다 — 계산은 실재하는(파싱 가능한) 분자로 정직하게 돌았고, 허구인 것은 그 분자들의 이름과 역가뿐이기 때문이다. 근거·범위 지도: `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md`.

---

## ⚠️ 작업 경계 — 반드시 먼저 읽을 것

홈페이지 에이전트는 **페이지 텍스트와 링크만** 바꾼다. 아래는 두 종류로 나뉜다.

- **[A] 지금 바로 가능** — 페이지 편집만으로 완결되는 정정. Zenodo 발행본이 이미 정정됐거나(링크만 교체) 발행본과 무관한 문구 문제.
- **[C] 발행본 정정 선행 필요(블로커)** — 페이지가 링크하는 Zenodo 발행본 자체가 아직 오염 상태다. 이건 별도 **Zenodo 업로드 에이전트**의 supersede 작업이 끝나야 페이지를 "clean"으로 표기할 수 있다. 홈페이지 에이전트는 그때까지 해당 항목을 **완화/보류 표기**만 한다.

혼동 주의: DOI 링크를 concept DOI로 바꾸면 자동으로 최신(정정)본으로 해석되는 레코드가 있고([A]), 발행본 자체가 미정정이라 링크를 바꿔도 오염본이 뜨는 레코드가 있다([C]). 아래 표에 구분해 뒀다.

---

## [A] 지금 바로 가능한 페이지 정정 (홈페이지 에이전트 단독 수행)

### A-1. Card 01 (MMP-1) 본문 — 철회된 화합물 정체/리포지셔닝 문구 삭제 (최우선)

현재 카드 본문(확인된 라이브 텍스트):
> "Compounds tested: Vorinostat, Indapamide, plus 14 additional sulfonamide-diuretic FDA-approved agents"

이 문구를 **삭제**한다. 이유:
- **CHEMBL406 ≠ 인다파미드, CHEMBL98 ≠ vorinostat** — 파이프라인은 이름과 다른 분자로 돌았다. 실재 시판약(인다파미드=이뇨제, vorinostat=HDAC 억제제)을 "MMP-1에 시험했다"고 공개페이지에 적는 것은 사실과 다르다.
- "sulfonamide-diuretic FDA-approved 리포지셔닝" 서사는 무효화된 paper_A v6 줄기다.

교체 문구(예시 — 조정 가능, 재현성만 남김):
> "구조 패널(정체·역가는 주장하지 않음)에 대한 3종 신경망 퍼텐셜(NNP)의 컨포머-에너지 순위 일치도, conformal 신뢰구간 보정, PoseBusters 물리적 타당성 검증. 결합/비결합 판별 성능 평가."

### A-2. Card 01 "Inhibitor Ranking" 프레이밍 완화

"MMP-1 Zn²⁺ Inhibitor Ranking"을 검증된 능력처럼 제시하지 말 것.
- **역가 순위 예측은 NULL**(독립 앵커 n=93에서 Spearman ≈ −0.005). σ 신호는 **결합/비결합 coarse 판별 필터**이지 역가 ranker가 아니다.
- 카드의 r=0.9146은 affinity 정확도가 아니라 **NNP 간 컨포머-에너지 일치도**(cross-NNP agreement)다.
- 권장 재프레이밍: "3종 NNP 교차-일치도(재현성 지표) + 결합/비결합 coarse 판별". "역가/affinity 랭킹 정확도" 주장 금지.

### A-3. Card 01 정량 수치 정정 (감사값으로 교체)

| 항목 | 현재 페이지 | 정정값 | 비고 |
|---|---|---|---|
| cross-NNP Pearson r | 0.9146, CI [0.817, 0.973] | **0.9142, CI [0.826, 0.971]** (LOO ±0.0104) | 감사통과 값 |
| 엔진 독립성 | (미공개) | **공개 추가**: MACE-OMol25 ↔ Orb-v3 r=0.9992 (둘 다 OMol25 학습) → "3 NNP"는 실질 2엔진, 0.9142는 세 쌍 중 **최저쌍** | v0.3에서 정정된 핵심 뉘앙스 |
| PoseBusters v2 통과율 | 94.5% | **93.9%** | |
| σ 이상치 붕괴 (CHEMBL94487) | 2,068× (14.27→0.007) | **2,039×** (0.0069 반올림) | 경미 |

### A-4. DOI 링크 교체 — 이미 정정 완료된 5개 레코드 (원본 version DOI → concept DOI)

이 5건은 Zenodo 발행본이 2026-07-19에 **concept DOI 하 new-version으로 supersede 완료**됐다. 그러나 페이지는 아직 **정정 전 원본 version DOI**를 링크 중이라, 클릭하면 정정 전(오염) 버전이 뜬다. **concept DOI로 교체**하면 자동으로 최신(정정)본으로 해석된다.

| 페이지 레코드 | 현재 링크 (원본 version, 오염) | → 교체: concept DOI (권장) | 참고: 정정 version DOI |
|---|---|---|---|
| III (EMB-3 scaffold-hopping) | `10.5281/zenodo.20018333` | **`10.5281/zenodo.20018332`** | 21431020 |
| V (AGA SRD5A2/AR) | `10.5281/zenodo.20018339` | **`10.5281/zenodo.20018338`** | 21431025 |
| XXIII (OMol25 Paradox) | `10.5281/zenodo.20134439` | **`10.5281/zenodo.20134438`** | 21430921 |
| XXIV (Steering potentials) | `10.5281/zenodo.20134442` | **`10.5281/zenodo.20134441`** | 21430923 |
| XXV (de novo Zn / LigandMPNN) | `10.5281/zenodo.20134447` | **`10.5281/zenodo.20134446`** | 21430926 |

- 링크 URL 형식: `https://doi.org/10.5281/zenodo.<concept>`.
- concept DOI는 Zenodo에서 "always latest version"으로 해석됨(2026-07-19 검증: 세 concept 모두 정정본으로 resolve 확인).
- **레코드 XXIV(steering) 제목 변경 반영**: 정정본에서 "…zinc-hydroxamate MMP-1 inhibitors" → "…zinc-hydroxamate-like MMP-1 active-site ligands". 페이지 제목도 맞출 것.

### A-5. 제목·부제에서 약물명 제거 확인

- 2026-06-03 핸드오프는 Record XXVI 제목을 "…Inhibitor Ranking: A Computationally-Driven Repositioning Study of **Vorinostat and Indapamide**"로 지시했다. **"Repositioning Study of Vorinostat and Indapamide" 부제가 페이지 어디든(제목/APA/카드) 남아 있으면 삭제.** (현재 페이지 상단 제목은 짧은 형태로 보이나, APA 인용문·메타태그·카드 캡션까지 재확인.)

---

## [C] 발행본 정정 선행 필요 — 홈페이지 단독 불가 (블로커)

아래 3건은 페이지가 링크하는 **원천(Zenodo 발행본 / OSF)이 아직 오염·미정정**이다. 홈페이지 에이전트는 근본 수정 불가. 각 항목에 대해 (1) 즉시 취할 페이지 임시조치와 (2) 별도 담당(업로드 에이전트)의 근본해결을 분리한다.

### C-1. Record VIII — `zenodo.20018254` "Calibrated ABFE pipeline" (= 08_abfe_methodology)

- **상태**: HIGH 오염 발행본(날조 약물명 10건·IC50 39건). 로컬 원고(`08_abfe_methodology/manuscript.md`)는 §3.6 철회+disclosure 배너로 **이미 정정됐으나**, 2026-07-19 정정 배치(5건)에 **미포함 → Zenodo 발행본은 정정 전 그대로**.
- **페이지 임시조치(홈페이지 에이전트)**: 이 레코드의 calibration/역가-상관 관련 강한 표현이 페이지에 있으면 보류. 링크는 유지하되 status를 "revision 준비 중"으로 표기 권장(삭제까지는 불필요 — ABFE 방법·T4L/benzene·EMB-3 코어는 무관하게 유효).
- **근본해결(별도)**: 업로드 에이전트가 #20/#21/#22와 동일하게 concept DOI 하 supersede. 정정본·도구 준비돼 있음(아래 [F]).

### C-2. Record XXVI — `zenodo.20247828` "paper_A v6" (Tier A 플래그십, Card 01의 근원)

- **상태**: 발행본(2026-06-02)이 v6 콘텐츠 = **제목·본문에 vorinostat/indapamide 다수 명시**(v0.2 66건·JCIM_v0.1 39건). 정정 배치 **미포함 → 발행본 오염 그대로**. de-identified 재작성본 `manuscript_v0.3_reproducibility.md`는 로컬에 존재하나(약물명 0건 수준) **미발행**.
- **의미**: [A-1~A-3]의 Card 01 정정은 페이지 텍스트 차원의 응급조치다. 그러나 **Card 01/Record XXVI가 가리키는 발행본 자체가 오염**이라, 페이지를 v0.3 기준으로 다시 써도 링크 목적지는 여전히 v6다. **이 레코드를 "clean"으로 제시하려면 발행본을 v0.3로 supersede해야 한다.**
- **페이지 임시조치**: [A-1~A-3] 적용 + status "revision 준비 중" 표기. 발행본 supersede 완료 후 concept DOI로 최종 정리.
- **근본해결(별도)**: 업로드 에이전트가 20247828을 v0.3로 supersede.

### C-3. Record XXI — `OSF.IO/Q4Z6W` "ZAFF-AMBER ABFE limitations" (= paper_A_zaff)

- **상태**: **quarantine 중.** 정확성 축(ΔGexp = RT·ln IC50, "reproducibility≠accuracy" 논지)이 날조 IC50에 얹혀 있어, 현재 **실 IC50 기반 ABFE 실패널 캠페인으로 재작성 중**(진행 10/14). OSF 발행본엔 부분정정(렌더 disclosure + keystone 허위출처 문장)만 반영됨.
- **페이지 임시조치**: 공개 리스팅 유지 여부/갱신 시점을 저자 판단으로. 재작성 완료 후 실역가 기반 결과로 갱신하는 것이 자연스러움. 그전까지 정량 정확도 주장 삽입 금지.
- **근본해결(별도)**: ABFE 캠페인 완료 → §Results/abstract 실역가 재작성 → 이름 de-id → OSF 갱신.

---

## [D] 게시 금지 경계 (기존 유지)

- 내부 저널 **Submission ID / Manuscript ID**, 제출·심사 일정, COI 내부 메모, cascade/compute 운영 세부 — 비공개.
- **날조 패널의 "경위·동기" 서술 금지.** 저자도 assistant도 경위를 기억하지 못하고 기록도 없다 → 사실과 날짜만. 페이지에 이 사건을 노출할 필요는 없으며(정정은 조용한 supersede로 충분), 만약 언급한다면 추측 없이 "annotations were unverifiable and have been corrected" 수준으로만.

---

## [E] 요약 — 홈페이지 에이전트 액션 (지금 수행)

1. **Card 01 (MMP-1)**: "Vorinostat, Indapamide, 14 sulfonamide-diuretic" 문구 삭제(A-1); "Inhibitor Ranking"→"NNP 교차일치+결합/비결합 판별"로 완화(A-2); 수치 정정 r 0.9142·PoseBusters 93.9%·2,039×·엔진중복 공개(A-3).
2. **DOI 링크 교체(5건)**: III/V/XXIII/XXIV/XXV를 concept DOI로(A-4 표). XXIV 제목 "inhibitors"→"active-site ligands".
3. **약물명 잔재 제거**: 제목/APA/메타/캡션에서 "Repositioning Study of Vorinostat and Indapamide" 부제 삭제(A-5).
4. **블로커 3건 표기**: Record VIII·XXVI·XXI는 status "revision 준비 중"으로만(C절). 근본 정정은 별도 업로드/재작성 task — 홈페이지에서 clean 확정 금지.
5. **금지선 준수**(D): 내부 ID·심사일정·날조 경위 서술 금지.

---

## [F] 참고 — 근본해결(발행본 정정) 담당자용 메모 (홈페이지 액션 아님)

- 정정 도구·절차는 기존 배치와 동일: `preprints/_metadata/ZENODO_UPLOAD_AGENT_PROMPT.md` + `zenodo_correct_orchestrate.py`(prep|verify|publish). concept DOI 하 new-version supersede(철회 아님).
- **신규 추가 대상 2건**: `20018254`(Record VIII, 08_abfe — 로컬 정정본 준비됨) / `20247828`(Record XXVI, paper_A v6 → v0.3로 교체 — 로컬 `manuscript_v0.3_reproducibility.md` 준비됨). 각 정정 PDF/배너/version note는 #20 방식으로 생성 필요.
- 이 2건이 supersede되면 홈페이지는 [C-1]/[C-2]의 "revision 준비 중"을 해제하고 concept DOI로 최종 링크.
- 지도: `preprints/_metadata/FABRICATED_PANEL_SCOPE_2026_07_16.md` / 정정 결과: `preprints/_metadata/ZENODO_CORRECTION_RESULT_2026_07_19.md`.

---

*이 핸드오프는 페이지 정정 지시서다. 실제 페이지 수정 및 Zenodo 발행본 정정은 각 담당(홈페이지/업로드 에이전트)이 수행하며, 외부 공개면 변경은 저자 최종 결정 사항이다.*
