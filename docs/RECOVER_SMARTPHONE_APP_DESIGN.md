---
title: "Recover Smart Clinic App Design"
subtitle: "Smartphone scar/skin assessment + Genesis_Medicine v3 통합"
date: 2026-04-26
target_users: Recover 한의원 환자 + 의료진
---

# Recover 스마트 클리닉 앱 설계

## 1. 비전

Recover 한의원 환자가 **스마트폰으로 흉터·기미·여드름·탈모 사진을 촬영** → AI 분석 → 자동 PSCR/POSAS 추정 → 처방 효능 추적 → 의료진 자동 보고. **PanDerm 모델 + Genesis_Medicine v3 분자 처방 + 한의사 임상 판단 통합**.

## 2. 핵심 기능 (MVP, 3개월 개발)

### 2.1 사진 캡처 & 분석
- iOS/Android 앱 (Flutter cross-platform)
- 특정 각도·조명 가이드 (UI overlay)
- 5질환 분류 (PanDerm + 자체 fine-tune 한국인)
- PSCR (Patient Scar Cosmesis Rating) 자동 추정 (1-5 score)
- POSAS (Patient and Observer Scar Assessment Scale) 매핑

### 2.2 처방 효능 추적
- 시술 후 1주/2주/4주/8주 사진 자동 알림
- 비교 사진 자동 정렬 (SIFT/SuperPoint 기반)
- 흉터 면적 변화 정량 (cm² → 정밀)
- 색조 (erythema, pigmentation) RGB 분석

### 2.3 미생물·마이크로바이옴 (선택)
- 16S sequencing kit 우편 발송 (Macrogen 협업, ₩50K)
- 결과 → 앱에서 dysbiosis pattern 표시
- Genesis_Medicine v3 자동 처방 추천

### 2.4 의료진 대시보드
- 환자별 추적 그래프 (PSCR over time)
- 자동 alert (악화 감지)
- 처방 변경 권장 (Bayesian SAR + Causal inference)
- IRB 승인 시 federated learning 데이터 기여

## 3. 기술 스택

```
Frontend:
  Flutter (iOS + Android single codebase)
  Camera + ML Kit (사진 처리 가이드)
  
Backend:
  FastAPI (Python) — Recover 자체 서버
  PostgreSQL (환자 메타데이터)
  S3 / Cloudflare R2 (이미지)
  
AI Inference:
  PanDerm fine-tuned (Korean dermatology)
  ONNX Runtime / TensorRT (mobile + server)
  
Privacy:
  PIPA 호환 (데이터 한국 거주)
  E2E 암호화 환자 사진
  익명화 로그

Integration:
  Genesis_Medicine v3 API (처방 추천)
  Macrogen 16S API (uploaded results)
  Korean EMR (이지원, 닥터트리) optional
```

## 4. 단계별 개발

### Phase 1 (3개월) — MVP
- 사진 캡처 + 5질환 분류
- PSCR 자동 추정
- 시술 전후 비교
- 인력: Flutter dev 1, Python backend 1, ML eng 0.5

### Phase 2 (6개월) — Recover 운영 통합
- 의료진 대시보드
- 자동 알림 + 처방 효능 추적
- IRB 승인 + 임상 데이터 수집
- 인력: 추가 임상 데이터 1, UI/UX 1

### Phase 3 (12개월) — 한국 한의원 확장
- Federated learning network (T5-5)
- 다른 한의원 license 모델
- 임상 시험 플랫폼

## 5. 비용 추정

| 항목 | Phase 1 | Phase 2 | Phase 3 |
|---|---:|---:|---:|
| 개발 인력 (3-4명) | ₩60M | ₩120M | ₩240M |
| 인프라 (cloud) | ₩5M | ₩15M | ₩30M |
| ML 학습 (GPU) | ₩10M | ₩20M | ₩40M |
| 의료기기 인증 | — | ₩50M | — |
| **총** | **₩75M** | **₩205M** | **₩310M** |

NIPA 사업 자금 + 자부담 매칭 가능.

## 6. 기대 효과

- **환자 만족도**: 시술 효능 정량 추적 → 신뢰
- **임상 데이터**: Recover 자체 RCT급 데이터 축적
- **사업 차별화**: 한국 첫 한방 + AI 안면분석 + 분자 수준 처방 통합 앱
- **글로벌 진출**: K-beauty 한방 외용제 + AI 통합 → 동남아 시장
- **Paper**: "AI-augmented Korean Medicine — 5-disease smart clinic platform"
