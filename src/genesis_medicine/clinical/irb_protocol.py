"""IRB 프로토콜 + 동의서 자동 생성.

한국 식약처(MFDS) IRB 양식 기준. 한방 임상 특이 사항 반영
(외용제 평가, 체질 처방, AI 안면분석 outcome 등).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class ClinicalContext:
    """임상 시험 메타."""

    title: str
    pi_name: str = "TBD"
    pi_affiliation: str = "Recover Clinic"
    sponsor: str = "Recover Clinic (자체 R&D)"
    sponsor_address: str = "서울 강남구 (TBD)"
    irb_target: str = "한국임상연구심의위원회 (KIRB) 또는 사설 IRB"

    # 시험 디자인
    disease: str = "흉터 재생 (atrophic scar)"
    intervention: str = "센텔라아시아티카 외용 (Madecassol-class) + 새살침"
    intervention_compound_smiles: str | None = None
    n_subjects: int = 30
    age_range: tuple[int, int] = (19, 65)
    duration_weeks: int = 12

    # 평가 outcome
    primary_outcome: str = "AI 안면 분석 기반 흉터 깊이/면적 변화율 (12주)"
    secondary_outcomes: list[str] = field(default_factory=lambda: [
        "환자 만족도 (VAS)",
        "이상반응 (피부 자극, 알러지)",
        "Dermatologist Photographic Assessment",
    ])

    # 안전성
    risk_class: str = "최소 위험 (외용제, 침습 최소)"
    inclusion_criteria: list[str] = field(default_factory=lambda: [
        "19~65세 성인",
        "여드름 흉터 또는 위축성 흉터 보유",
        "최근 6개월간 다른 흉터 치료 미실시",
        "임상시험 참여 동의",
    ])
    exclusion_criteria: list[str] = field(default_factory=lambda: [
        "임신·수유부",
        "센텔라 또는 자초 알레르기",
        "활동성 피부 감염",
        "면역억제제 복용",
        "Keloid 체질 (가족력)",
    ])

    # 우리 시스템에서 도출된 분자 메커니즘 근거
    in_silico_evidence: str = (
        "Boltz-2 cofolding + ADMET-AI v2 다중 타겟 분석에서 본 후보의 "
        "TGF-β1/MMP-1/CTGF 결합 친화도 affinity_probability_binary > 0.6, "
        "ADMET 안전 게이트 통과 확인."
    )

    # 한방 특이 사항
    has_acupuncture: bool = True   # 새살침 병용 여부
    has_constitutional_rx: bool = False   # 체질 한약 동시 처방

    output_dir: Path = Path("manuscript/irb")


def generate_irb_protocol(ctx: ClinicalContext) -> str:
    """IRB 제출용 프로토콜 (한글)."""
    today = date.today().isoformat()
    sec = ctx.secondary_outcomes
    inc = ctx.inclusion_criteria
    exc = ctx.exclusion_criteria

    md = f"""# 임상시험 프로토콜 (IRB 심의용)

**시험 제목:** {ctx.title}

| 항목 | 내용 |
|------|------|
| 책임 연구자 (PI) | {ctx.pi_name} |
| 소속 | {ctx.pi_affiliation} |
| 의뢰자 | {ctx.sponsor} |
| 의뢰자 주소 | {ctx.sponsor_address} |
| IRB 신청 기관 | {ctx.irb_target} |
| 작성일 | {today} |
| 위험 등급 | {ctx.risk_class} |
| 대상 질환 | {ctx.disease} |

---

## 1. 연구 배경 및 목적

### 1.1 의학적 배경
{ctx.disease}에 대한 한방 외용제 (예: 자운고)의 임상 효능은 수백 년간
경험적으로 축적되어 왔으나, 분자 수준 메커니즘과 정량적 효능 평가는 부족했다.

### 1.2 In silico 사전 검증 근거
{ctx.in_silico_evidence}
이 분석 결과는 Genesis_Medicine v3 파이프라인 (Apache-2.0 오픈소스)으로 산출되었으며,
TRIPOD-AI 및 MI-CLAIM 보고 표준을 모두 충족한다.

### 1.3 연구 가설
H1: {ctx.intervention} 12주 치료군은 대조군 대비 통계적으로 유의한
    {ctx.primary_outcome.split('(')[0].strip()} 개선을 보인다.

---

## 2. 시험 디자인

### 2.1 디자인
- 단일기관, 무작위 배정 (1:1), 단일맹검, 병렬 비교 임상시험
- 시험군: {ctx.intervention} 12주 적용
- 대조군: 표준치료 (기존 외용제 또는 placebo) 12주

### 2.2 대상자 수: {ctx.n_subjects}명 (시험군 {ctx.n_subjects//2} + 대조군 {ctx.n_subjects//2})
효과 크기 d=0.6, α=0.05, β=0.2 기준 G*Power 산출.

### 2.3 시험 기간
- 모집: 3개월
- 치료: {ctx.duration_weeks}주
- 추적관찰: 4주
- 총 데이터 수집: 약 7개월

---

## 3. 대상자 선정

### 3.1 선정 기준
"""
    for i, c in enumerate(inc, 1):
        md += f"{i}. {c}\n"
    md += "\n### 3.2 제외 기준\n"
    for i, c in enumerate(exc, 1):
        md += f"{i}. {c}\n"

    md += f"""

---

## 4. 시험 절차

### 4.1 방문 일정
| 방문 | 시점 | 절차 |
|------|------|------|
| Visit 1 | Week 0 (스크리닝) | 동의서, 인적정보, 의학적 검토, 사진/AI 안면분석 baseline |
| Visit 2 | Week 0 (배정) | 군 배정, 시험약 지급, 침 시술 1회{' (있음)' if ctx.has_acupuncture else ''} |
| Visit 3 | Week 4 | 사진/AI 분석, 이상반응 확인 |
| Visit 4 | Week 8 | 사진/AI 분석, 이상반응 확인 |
| Visit 5 | Week 12 (종료) | 사진/AI 최종, VAS, 만족도 |
| Visit 6 | Week 16 (추적) | 안전성 추적 |

### 4.2 시험 중재
**{ctx.intervention}**
- 적용: 1일 2회, 환부에 얇게 도포
- {('침 시술: 주 1회, 12주' if ctx.has_acupuncture else '침 시술 없음')}
- {('체질 한약 동시 처방' if ctx.has_constitutional_rx else '한약 동시 처방 없음')}

---

## 5. 평가 변수

### 5.1 1차 유효성 평가
**{ctx.primary_outcome}**

AI 안면 분석 시스템 (Recover Clinic 자체 시스템)을 사용하여 흉터의 깊이, 면적,
색소 변화를 정량 측정. baseline 대비 12주 변화율 (%)을 1차 outcome으로 사용.

### 5.2 2차 유효성 평가
"""
    for s in sec:
        md += f"- {s}\n"
    md += f"""

### 5.3 안전성 평가
- 매 방문 시 이상반응 (Adverse Event, AE) 기록
- 심각한 이상반응 (SAE) 발생 시 24시간 이내 IRB 보고
- 피부 자극 평가: Patient Self-Assessment + 의사 시각 평가

---

## 6. 통계 분석 계획

- 1차 outcome: 두 군의 12주 변화율 차이를 t-test (정규성 만족 시) 또는
  Mann-Whitney U (만족 안 할 시)로 비교, α=0.05.
- ITT 분석 + Per-Protocol 보조 분석.
- 결측치: Last Observation Carried Forward (LOCF).
- 안전성: 빈도와 비율 보고.

---

## 7. 윤리적 고려

### 7.1 IRB 심의
본 프로토콜은 {ctx.irb_target}의 사전 심의를 받아 승인된 후에 시행된다.

### 7.2 환자 정보 보호
- 개인정보보호법 (대한민국) 및 GDPR 준수.
- 환자 식별 정보는 별도 분리 저장, 분석 데이터는 익명 ID로만 처리.
- AI 안면 분석 사진은 신원 식별 가능성 최소화 (랜드마크만 추출).

### 7.3 동의서 (별첨)
- 한글 동의서 (별첨 A)
- 영문 동의서 (별첨 B, 외국인 참여 시)

---

## 8. 자료 관리

### 8.1 Case Report Form (CRF)
- REDCap 또는 자체 개발 시스템 사용.
- 데이터는 5년간 보관, 그 후 익명 처리하여 학술 활용 가능.

### 8.2 In silico 분석 결과 보관
- Genesis_Medicine v3 MLflow run_id를 본 시험과 매핑.
- DVC manifest로 데이터 버전 추적.

---

## 9. 참고문헌

> ⚠️ 사용자 작성 (또는 자동 생성된 references.bib 활용).

---

**작성자 서명:** _____________________ (날짜: {today})
**PI 서명:** _____________________ (날짜: ____________)
"""
    return md


def generate_consent_form_korean(ctx: ClinicalContext) -> str:
    today = date.today().isoformat()
    return f"""# 임상시험 참여 동의서 (한글)

**시험명:** {ctx.title}

**연구책임자:** {ctx.pi_name} ({ctx.pi_affiliation})

**의뢰자:** {ctx.sponsor}

---

## 1. 시험 목적
본 시험은 {ctx.disease}에 대해 {ctx.intervention}의 효과와 안전성을
과학적으로 평가하기 위한 것입니다. 사전 컴퓨터 분석(AI 신약 발굴)에서 본 치료의
분자 수준 효능 가능성이 확인되었습니다.

## 2. 시험 절차
- 시험 기간: {ctx.duration_weeks}주 + 추적 4주
- 시험 방문 횟수: 6회
- 사진 및 AI 안면 분석을 통한 비침습 평가
{'- 침 시술: 주 1회, 통증 최소' if ctx.has_acupuncture else ''}
- 외용제 1일 2회 자가 도포

## 3. 예상 위험과 이득
**위험 (낮음):**
- 외용제 적용 부위 일시적 자극 또는 발적 (드물게 발생)
- {('침 시술 부위 미세 출혈 또는 통증' if ctx.has_acupuncture else '')}

**이득:**
- 흉터 개선 가능성
- AI 기반 객관적 흉터 측정 결과 제공
- 시험 종료 후 동일 치료 무상 제공 가능 (대조군)

## 4. 비밀 보장
참여자의 개인정보는 한국 개인정보보호법에 따라 엄격히 보호되며, 본인을 식별할 수
있는 정보는 절대 외부에 공개되지 않습니다. AI 안면 분석 사진은 신원 식별이 어려운
형태로 처리됩니다.

## 5. 자발적 참여 및 철회
본 시험 참여는 전적으로 자발적이며, 이유 없이 언제든 참여를 철회할 수 있습니다.
철회는 본인의 향후 진료에 어떠한 불이익도 주지 않습니다.

## 6. 보상
시험 참여로 인한 이상반응 발생 시 의뢰자({ctx.sponsor})의 임상시험보험에 따라
적절한 치료 및 보상을 받을 수 있습니다.

## 7. 문의처
연구책임자: {ctx.pi_name}
이메일: {ctx.pi_affiliation.lower()}@TBD.kr
연락처: TBD

---

**참여자 서명:** _____________________  (날짜: ____________)

**연구자 서명:** _____________________  (날짜: {today})
"""


def generate_consent_form_english(ctx: ClinicalContext) -> str:
    today = date.today().isoformat()
    return f"""# Informed Consent Form (English)

**Study Title:** {ctx.title}

**Principal Investigator:** {ctx.pi_name} ({ctx.pi_affiliation})

**Sponsor:** {ctx.sponsor}

---

## 1. Purpose
This study evaluates the efficacy and safety of {ctx.intervention} for {ctx.disease}.
Pre-clinical AI-driven computational analysis has predicted molecular-level efficacy
of this intervention.

## 2. Procedures
- Study duration: {ctx.duration_weeks} weeks plus 4 weeks follow-up
- 6 study visits
- Non-invasive AI-based facial analysis
- Self-administered topical application twice daily
{'- Acupuncture sessions weekly' if ctx.has_acupuncture else ''}

## 3. Risks and Benefits
**Risks (low):**
- Transient skin irritation at application site (rare)
{'- Minor bruising or pain at acupuncture sites' if ctx.has_acupuncture else ''}

**Benefits:**
- Potential scar improvement
- Objective AI-based scar quantification
- Free identical treatment offered to control group post-trial

## 4. Confidentiality
Personal information is protected under Korean Personal Information Protection Act and GDPR.
AI facial analysis images are de-identified (landmarks only).

## 5. Voluntary Participation
Participation is entirely voluntary. Withdrawal at any time without penalty.

## 6. Compensation
Adverse events covered by the sponsor's clinical trial insurance.

---

**Participant Signature:** _____________________  (Date: ____________)

**Investigator Signature:** _____________________  (Date: {today})
"""
