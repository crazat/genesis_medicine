# DrugBank Account Approval — 답변 template

**상황**: DrugBank Team이 commercial use case 의심 → 추가 정보 요청
**전략**: 현재 academic R&D 단계 + 향후 commercial 시 license 구매 약속 (정직)

---

## 영문 답변 (copy-paste, 사용자 수정 가능)

```
Subject: Re: DrugBank Account Approval — Genesis_Medicine Lab academic use case

Dear DrugBank Team,

Thank you for following up on our DrugBank Download account application.

I would like to clarify our current research stage and intended usage.

** Organization **
Genesis_Medicine Lab is an in silico drug discovery R&D research division
operated by HAN PREDICT, Inc. (a healthcare technology startup based in
Seoul, Republic of Korea). Our primary research output is open-source
preprint publications on AI-driven natural product drug discovery, with
a focus on Korean traditional medicine-inspired skin therapeutics.

** Current research stage: Pre-clinical academic R&D only **

We are currently in pre-clinical, in-silico-only research stage. Our
specific outputs to date:

  - 14 preprint manuscripts in preparation, intended for ChemRxiv,
    bioRxiv, and medRxiv (Creative Commons CC-BY-4.0 license)
  - All code published under Apache-2.0 at:
    https://github.com/crazat/genesis_medicine
  - 1,680+ Boltz-2 protein-ligand co-folding predictions (in silico)
  - Bayesian Active Learning cascade for natural-product scaffold-hopping
  - Molecular dynamics validation (RTX 5090, 14 paper-tier MD trajectories)
  - No commercial product currently sold, in distribution, or in clinical
    development

** Intended DrugBank usage **

We would use DrugBank Download for:

  1. Cross-reference our in-silico hit candidates against DrugBank's
     curated protein-drug interaction database for prior-art validation
     and mechanism cross-check
  2. Annotate Korean herbal natural products (asiaticoside, shikonin,
     embelin, licochalcone A) with DrugBank's pharmacological
     classification for our open-source preprints
  3. Reference DrugBank IDs in our Apache-2.0 / CC-BY-4.0 published
     preprints to ensure reproducibility for the academic community
  4. Map our predicted skin-disease targets (TGF-β1, MMP-1, CTGF, MITF,
     TYR, SRD5A1/2) to DrugBank approved drug repositioning candidates

** Future commercial intent (transparent disclosure) **

We acknowledge that:

  - HAN PREDICT, Inc. is incorporated as a for-profit entity
  - If our research leads to a commercial product (e.g., topical
    cosmeceutical through our affiliated clinic Recover Korean Medicine
    Clinic, opening 2026-08), we would purchase a DrugBank commercial
    license at that point.
  - Currently, no DrugBank-derived information will be embedded in any
    commercial product.

We are happy to provide additional documentation if needed:

  - ORCID iD: [Step 1 등록 후 채울 부분]
  - GitHub repository: https://github.com/crazat/genesis_medicine
  - Most recent commit (2026-04-28): commit e47774e — head-to-head MD
    comparison of dual leads (open-source)
  - Affiliated clinic: https://recover-clinic.kr (opening 2026-08-15)
  - Healthcare technology platform: https://hanpredict.com

If our use case still does not qualify for academic free access under
DrugBank's licensing terms, please let us know:

  1. The specific concern (e.g., for-profit organizational structure)
  2. A summary of pricing for a commercial license that would cover our
     intended use (in silico research, no embedded distribution).

Thank you for your time and consideration.

Best regards,

HanCheongWoo
Founder, HAN PREDICT, Inc.
Director, Genesis_Medicine Lab
admin@hanpredict.com
```

---

## 한국어 보충 설명 (사용자 참고용)

### 1. 핵심 메시지 3가지
1. **현재는 academic R&D만** — 14편 preprint, GitHub Apache-2.0, no commercial product
2. **DrugBank 사용 목적** — preprint cite + 한약 mechanism cross-check (open science)
3. **향후 commercial 시 license 구매 약속** — 정직 disclosure

### 2. 가능한 결과 시나리오

| 결과 | 의미 | 액션 |
|---|---|---|
| ✅ Academic free 승인 | 14편 preprint에 DrugBank cite 가능 | 즉시 사용 |
| ⚠️ Commercial license 견적 통보 | DrugBank 가격 받음 ($5K-50K/yr 추정) | Path A (cosmeceutical) 시 구매 검토 |
| ❌ 거부 | DrugBank 없이 진행 | ChEMBL + Open Targets + STITCH 대체 활용 |

### 3. DrugBank 사용 안 해도 가능한 alternative DB

| 대체 DB | 라이선스 | 우리 용도 |
|---|---|---|
| **ChEMBL 35** | CC-BY-SA 3.0 | bioassay 데이터 (이미 사용 중) |
| **Open Targets** | CC0 | disease-target association |
| **STITCH 5** | CC-BY-NC | chemical-protein interaction |
| **PubChem** | Public domain | compound metadata |
| **DrugCentral** | CC-BY-SA | approved drug DB (DrugBank 대체) |

→ DrugBank 없어도 **paper-tier 결과 가능** (이미 ChEMBL+Open Targets로 충분).

### 4. 답변 보낸 후 timeline
- 2-3 영업일 내 회신
- 승인 시: download 즉시 가능 (~1.5GB)
- 거부 시: DrugCentral (CC-BY-SA, 무료) 즉시 대체

### 5. 한국어 답변 추가 (필요 시)
대부분 미국 DrugBank Team은 영문 답변 충분. 한국어 추가 필요 없음.

---

## 추가 권고 (미래 academic license 신청 시)

다음 organization 가입 시 DrugBank academic license 더 쉬움:
- **NRF (한국연구재단) 과제**: NRF grant ID 명시 → academic 자동 승인
- **University affiliation**: 한국 대학 약대/한의대와 collaborator 등록
- **Open-access journal publication**: peer-review 통과 후 DOI cite

**현재 권고**: DrugBank 없이 진행 → 우리 stack은 ChEMBL + Open Targets + STITCH 충분.
DrugBank 답변은 정중하게 보내고 회신 기다리되, **dependency 없음**.
