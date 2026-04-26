"""Federated Learning Network for Korean 한의원 협업.

npj Digital Medicine 2025 + Korean Society of Medical Informatics 2024:
  - Synthetic data + federated learning for privacy-preserving RWD
  - Homomorphic encryption + GDPR/PIPA 호환

목적:
  Recover (강남) 단독 환자 데이터 → 한국 한의원 5-10개 federated network
  - 각 한의원 raw data는 로컬에 유지 (개인정보 보호)
  - 모델만 weighted average로 통합
  - 결과: "한국 한약 외용제 효능 multi-center evidence"

기대 가치:
  - Recover 처방 데이터 (~200-500/년) → 5-10× 확장 (~2,000-5,000/년)
  - 한국 식약처 IND 자료의 다기관 evidence
  - Lunit이 imaging에서 한 것을 한의원 vertical에서

라이브러리 (모두 MIT/Apache):
  - Flower (https://flower.dev) — federated framework
  - PySyft (OpenMined) — privacy-preserving ML
  - syft → secure aggregation
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HanwonNetworkNode:
    """Federated 노드 (한의원)."""

    clinic_name: str = ""
    location: str = ""        # 강남, 부산, 대구 등
    n_patients_per_year: int = 0
    treatment_focus: list = field(default_factory=list)   # 흉터, 기미, 탈모...
    data_protocol: str = "OMOP_CDM_KR"                    # 한국 표준
    privacy_tier: str = "high"                              # high | medium | low


@dataclass
class FederatedTask:
    """Federated 학습 task."""

    task_name: str = ""
    rounds: int = 50
    aggregation: str = "FedAvg"     # FedAvg | FedProx | scaffold
    privacy_mechanism: str = "differential_privacy"
    min_clinics_required: int = 3


# Recover + 가상의 협업 한의원 노드 (실제는 협의 후 결정)
RECOMMENDED_NETWORK = [
    HanwonNetworkNode(
        clinic_name="Recover 한의원",
        location="서울 강남",
        n_patients_per_year=300,
        treatment_focus=["흉터 (자운고)", "기미", "탈모", "여드름", "광노화"],
        privacy_tier="high",
    ),
    HanwonNetworkNode(
        clinic_name="(협력 후보 1)",
        location="서울 강북", n_patients_per_year=200,
        treatment_focus=["흉터", "한방 외용제"],
    ),
    HanwonNetworkNode(
        clinic_name="(협력 후보 2)",
        location="부산", n_patients_per_year=300,
        treatment_focus=["기미", "광노화"],
    ),
    HanwonNetworkNode(
        clinic_name="(협력 후보 3)",
        location="대구", n_patients_per_year=250,
        treatment_focus=["탈모", "한방 침"],
    ),
    HanwonNetworkNode(
        clinic_name="(협력 후보 4)",
        location="광주", n_patients_per_year=180,
        treatment_focus=["여드름", "아토피"],
    ),
]


# 협업 federated tasks (paper 가치 ↑ 순)
FEDERATED_TASKS = [
    FederatedTask(
        task_name="EMB-3 vs 자운고 단독 효능 ATE 추정",
        rounds=30,
        privacy_mechanism="differential_privacy_epsilon_2.0",
        min_clinics_required=5,
    ),
    FederatedTask(
        task_name="환자 fibroblast subtype → 처방 자동 매칭 정확도",
        rounds=50,
        min_clinics_required=4,
    ),
    FederatedTask(
        task_name="흉터 유형 5분류 (위축성/비후성/켈로이드/외상/수술 후) AI",
        rounds=100,
        min_clinics_required=3,
    ),
    FederatedTask(
        task_name="한약 외용제 부작용 (skin reaction) early detection",
        rounds=50,
        min_clinics_required=4,
    ),
]


def design_federated_workflow() -> dict:
    """전체 federated workflow 설계."""
    return {
        "phase_1_recruitment": {
            "duration_months": 3,
            "actions": [
                "Recover 핵심 협업 한의원 5개 컨택",
                "한국한의사협회 (KAOMP) 협력 요청",
                "보건복지부 한방 디지털 사업 응모",
                "법무: PIPA + IRB 다기관 승인",
            ],
        },
        "phase_2_infrastructure": {
            "duration_months": 6,
            "actions": [
                "각 한의원에 Flower client 설치 (Docker container)",
                "Recover에 Flower server 운영",
                "OMOP CDM Korean adapter 환자 데이터 표준화",
                "Differential privacy ε=2.0 보장",
                "Synthetic data fallback (KIOM 협력)",
            ],
        },
        "phase_3_first_task": {
            "duration_months": 6,
            "task": FEDERATED_TASKS[0].__dict__,
            "expected_outcome": (
                "다기관 evidence — Recover 단독 200명 → network 1,500명+. "
                "MFDS IND 자료에 'multi-center real-world evidence' 추가."
            ),
        },
        "total_timeline": "~15개월",
        "expected_paper": "Lancet Digital Health / npj Digital Medicine tier",
        "regulatory_value": "외용제 IND 통과 가속 + 한국 식약처 신뢰",
        "competitive_position": (
            "Lunit imaging의 한방 vertical 버전 — 미국에 유사 사례 없음. "
            "Korea-specific 'AI-augmented Korean medicine network'. "
            "K-MEDI Hub + NIPA 정부 사업 핵심 모델 가능"
        ),
    }


def estimate_costs() -> dict:
    """비용 추정 (24개월 운영)."""
    return {
        "infrastructure": {
            "Flower server (Recover)": "₩5M/년 (cloud GPU)",
            "각 한의원 client": "₩1M/년 × 5 = ₩5M",
            "Subtotal": "₩10M/년",
        },
        "법무 + IRB": {
            "다기관 IRB": "₩30M (1회)",
            "PIPA 컨설팅": "₩10M",
        },
        "환자 데이터 보상": {
            "환자 동의 사례비": "₩50K/명 × 1,500명 = ₩75M",
        },
        "총 24개월 예산": "약 ₩200M",
        "정부 지원 가능성": (
            "보건복지부 한방 디지털 50%, NIPA 의료 AI 30%. "
            "자부담 ₩40M 수준"
        ),
    }
