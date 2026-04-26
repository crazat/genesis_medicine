"""facial_dx 진단 엔진 ↔ Genesis_Medicine v3 통합 bridge.

facial_dx 위치: C:\\Projects\\facial_dx (Windows native, WSL: /mnt/c/Projects/facial_dx)
- 3D 안면 분석 (Morpheus .mpa / iPhone TrueDepth)
- HAN PREDICT Station Kit v1
- IRB 제출 2026-04-27 (D-1)
- 30 ultrathink cycles, 1,781+ tests passed
- Recover 한의원 진단 vertical (시술 플래닝)

Genesis_Medicine v3 (이 시스템) = 한약 신약 vertical (분자 처방).
두 시스템 통합 → Recover 환자 동선 자동화.

자연어 호출:
  "환자 facial_dx 분석 결과 → 흉터 처방 추천"
  → call_facial_dx_then_prescribe(mpa_path)

  "facial_dx 결과 가져오기"
  → fetch_facial_dx_analysis(patient_id)

라이선스: facial_dx 자체는 별도 license. 우리는 IPC (subprocess/REST) 호출만.
"""

from __future__ import annotations

import json
import subprocess
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")


# facial_dx 프로젝트 위치 (WSL에서 Windows 경로)
FACIAL_DX_ROOT = Path("/mnt/c/Projects/facial_dx")
FACIAL_DX_CLI = FACIAL_DX_ROOT / "scripts" / "facial_dx_completion.bash"


@dataclass
class FacialDxAnalysis:
    """facial_dx 분석 결과 wrapper."""

    patient_id: str = ""
    input_type: str = ""              # mpa | iphone_truedepth
    asymmetry_rms: float = 0.0
    landmarks_n: int = 0
    zones: list = field(default_factory=list)
    safety_supervisor_decision: dict = field(default_factory=dict)
    treatment_recommendations: list = field(default_factory=list)
    raw_json_path: str = ""
    natural_language_summary: str = ""


@dataclass
class IntegratedTreatmentPlan:
    """facial_dx + Genesis_Medicine 통합 시술 + 처방 plan."""

    patient_id: str = ""
    facial_dx_analysis: dict = field(default_factory=dict)
    facial_dx_treatments: list = field(default_factory=list)   # HIFU/RF/filler
    genesis_medicine_topical: list = field(default_factory=list)  # EMB-3/자운고
    genesis_medicine_systemic: list = field(default_factory=list)  # 한방 처방
    sequence: list = field(default_factory=list)              # 시술 순서
    safety_flags: list = field(default_factory=list)
    natural_language_plan: str = ""


def is_facial_dx_available() -> dict:
    """facial_dx 프로젝트 접근 가능성 확인."""
    if not FACIAL_DX_ROOT.exists():
        return {
            "available": False,
            "error": f"{FACIAL_DX_ROOT} 미존재 — Windows에서 git clone 또는 path 확인",
        }

    claude_md = FACIAL_DX_ROOT / "CLAUDE.md"
    if not claude_md.exists():
        return {"available": False,
                "error": "CLAUDE.md 미존재 — facial_dx 미초기화"}

    # 최근 활동 확인
    test_dirs = list(FACIAL_DX_ROOT.glob("test_v5_sprint*"))
    return {
        "available": True,
        "root": str(FACIAL_DX_ROOT),
        "n_sprint_tests": len(test_dirs),
        "latest_sprint": max([d.name for d in test_dirs]) if test_dirs else None,
        "claude_md_size": claude_md.stat().st_size,
    }


def fetch_facial_dx_analysis(
    patient_id: str = "",
    test_sprint: str = "test_v5_sprint4",
) -> FacialDxAnalysis:
    """기존 facial_dx 분석 결과 로드 (test sprint output 또는 환자 record).

    Args:
        patient_id: Recover 환자 ID (실제 운영 시)
        test_sprint: 개발 단계 sprint output 이름
    """
    # test sprint output 우선 (개발 단계)
    sprint_dir = FACIAL_DX_ROOT / test_sprint
    if not sprint_dir.exists():
        return FacialDxAnalysis(
            patient_id=patient_id,
            natural_language_summary=(
                f"❌ {sprint_dir} 미존재 — facial_dx에서 분석 먼저 실행 필요. "
                f"Windows: facial_dx analyze <mpa> --output {test_sprint}/"
            ),
        )

    # 핵심 결과 파일들
    files = {
        "analysis": sprint_dir / "analysis_v3.json",
        "landmarks": sprint_dir / "landmarks.json",
        "manifest": sprint_dir / "manifest.json",
        "injection_guide": sprint_dir / "injection_guide.json",
        "lifting_guide": sprint_dir / "lifting_guide.json",
        "nerve_map": sprint_dir / "nerve_map.json",
        "vessel_map": sprint_dir / "vessel_map.json",
    }

    data = {}
    for key, fp in files.items():
        if fp.exists():
            try:
                data[key] = json.loads(fp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data[key] = {"error": "JSON parse 실패"}

    # 핵심 metric 추출
    analysis = data.get("analysis", {})
    landmarks = data.get("landmarks", {})

    asymmetry = (analysis.get("asymmetry_rms")
                  or analysis.get("metrics", {}).get("asymmetry_rms", 0))
    n_landmarks = len(landmarks.get("landmarks", [])) if landmarks else 0

    # treatment recommendations (injection + lifting guide)
    treatments = []
    if "injection_guide" in data:
        treatments.append({"type": "injection",
                            "data": data["injection_guide"]})
    if "lifting_guide" in data:
        treatments.append({"type": "lifting",
                            "data": data["lifting_guide"]})

    nl = (
        f"facial_dx 분석 결과 ({test_sprint}):\n"
        f"- Landmarks: {n_landmarks}\n"
        f"- Asymmetry RMS: {asymmetry}\n"
        f"- 시술 권장: {len(treatments)} 종류\n"
        f"- Files loaded: {[k for k, v in data.items() if v]}\n\n"
        f"다음 단계: Genesis_Medicine v3로 분자 처방 추천 호출\n"
        f"  → integrated_treatment_plan(facial_dx_result, scar_diagnosis='hypertrophic')"
    )

    return FacialDxAnalysis(
        patient_id=patient_id,
        input_type="mpa" if any("mpa" in str(v) for v in data.values())
                    else "iphone_truedepth",
        asymmetry_rms=float(asymmetry) if asymmetry else 0.0,
        landmarks_n=n_landmarks,
        zones=analysis.get("zones", []),
        treatment_recommendations=treatments,
        raw_json_path=str(sprint_dir),
        natural_language_summary=nl,
    )


def integrated_treatment_plan(
    facial_dx_result: FacialDxAnalysis | dict,
    scar_diagnosis: str = "hypertrophic",
    patient_skin_type: str = "korean",
) -> IntegratedTreatmentPlan:
    """facial_dx 결과 + Genesis_Medicine 분자 처방 통합 plan.

    Recover 환자 동선:
      1. facial_dx 분석 (3D mesh + zone + asymmetry)
      2. 본 함수 → Genesis_Medicine v3 호출 → 분자 처방
      3. facial_dx 시술 (HIFU/RF/filler) + Genesis_Medicine 외용제
    """
    if isinstance(facial_dx_result, FacialDxAnalysis):
        facial_dx_dict = facial_dx_result.__dict__
        patient_id = facial_dx_result.patient_id
    else:
        facial_dx_dict = facial_dx_result
        patient_id = facial_dx_dict.get("patient_id", "unknown")

    # facial_dx 시술 (예시)
    fdx_treatments = facial_dx_dict.get("treatment_recommendations", [])
    fdx_summary = []
    for t in fdx_treatments:
        if t.get("type") == "injection":
            fdx_summary.append("Injection therapy (filler/botox 위치)")
        elif t.get("type") == "lifting":
            fdx_summary.append("Thread/HIFU lifting")

    # Genesis_Medicine 분자 처방 (T7-4 Pro-Hyp triple combination 활용)
    if scar_diagnosis == "hypertrophic":
        topical = [
            "Recover Hypertrophic Cream (자운고 + EMB-3 + Embelin)",
            "EMB-3 25% / Shikonin 25% / Embelin 5%",
        ]
        systemic = ["활혈거어탕 (단삼·호장근, 어혈 해소)"]
    elif scar_diagnosis == "atrophic":
        topical = [
            "Recover Atrophic Cream (Asiaticoside 30% + Pro-Hyp 20% + EMB-3 5%)",
        ]
        systemic = ["당귀음자 (혈허·만성 건조)"]
    elif scar_diagnosis == "keloid":
        topical = [
            "Recover Hypertrophic Cream + 황련 외용",
        ]
        systemic = ["활혈거어탕 + 황련해독탕 (염증 동시)"]
    else:   # universal
        topical = ["Recover Triple Cream (Universal)"]
        systemic = ["환자 체질에 맞는 한방 보완"]

    # 시술 순서 (chronotherapy + safety)
    sequence = [
        "1. facial_dx 분석 결과 의사 검토 (9-gate Safety)",
        "2. PIPA + IRB 환자 동의 확인",
        f"3. {fdx_summary[0] if fdx_summary else 'facial_dx 시술 시행'}",
        "4. 시술 직후 PBM LED (660 nm + 830 nm, T7-5 protocol)",
        f"5. Topical 외용제: {topical[0]}",
        "6. 환자 자가 외용 — chronotherapy 자오류주 (戌時 19-21시 야간)",
        f"7. 내복약: {systemic[0]} (한의사 처방)",
        "8. Recover Smart Clinic App (T6-4) 매일 사진 업로드",
        "9. 4-12주 추적 → AI 자동 효능 평가",
    ]

    # Safety flags (facial_dx 9-gate + 우리 PGx)
    safety_flags = []
    if facial_dx_dict.get("asymmetry_rms", 0) > 5:
        safety_flags.append("⚠️ 비대칭 RMS > 5 — 시술 전 추가 평가")

    nl = (
        f"**Recover 통합 시술 + 처방 plan ({patient_id}, {scar_diagnosis})**\n\n"
        f"**facial_dx 진단**:\n"
        f"- Asymmetry RMS: {facial_dx_dict.get('asymmetry_rms', 0)}\n"
        f"- Landmarks: {facial_dx_dict.get('landmarks_n', 0)}\n"
        f"- 시술 권장: {len(fdx_summary)} 종류\n\n"
        f"**Genesis_Medicine v3 분자 처방**:\n"
        f"- 외용: {', '.join(topical)}\n"
        f"- 내복: {', '.join(systemic)}\n\n"
        f"**시술 순서** ({len(sequence)} 단계):\n"
        + "\n".join(f"  {s}" for s in sequence)
        + (f"\n\n**안전 경고**: {safety_flags}" if safety_flags else "")
    )

    return IntegratedTreatmentPlan(
        patient_id=patient_id,
        facial_dx_analysis=facial_dx_dict,
        facial_dx_treatments=fdx_summary,
        genesis_medicine_topical=topical,
        genesis_medicine_systemic=systemic,
        sequence=sequence,
        safety_flags=safety_flags,
        natural_language_plan=nl,
    )


def call_facial_dx_then_prescribe(
    test_sprint: str = "test_v5_sprint4",
    scar_diagnosis: str = "hypertrophic",
    patient_id: str = "",
) -> dict:
    """End-to-end Recover 환자 동선 (자연어 호출 entry).

    "환자 facial_dx 분석 결과 → 통합 처방"
    """
    fdx = fetch_facial_dx_analysis(patient_id, test_sprint)
    if "❌" in fdx.natural_language_summary:
        return {
            "step_1_facial_dx": fdx.natural_language_summary,
            "next_action": "Windows에서 facial_dx 먼저 실행 필요",
        }
    plan = integrated_treatment_plan(fdx, scar_diagnosis, "korean")
    return {
        "step_1_facial_dx": fdx.natural_language_summary,
        "step_2_integrated_plan": plan.natural_language_plan,
        "patient_id": patient_id or "demo",
    }
