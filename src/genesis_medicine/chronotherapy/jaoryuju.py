"""자오류주 (子午流注) chronotherapy + 현대 circadian medicine.

12 시진 (時辰) × 12 경락 (經絡) → 시간대별 약효 변화 매핑.
RSC 2025 + Springer 2024 chronotherapy + 한방 자오류주 결합.

자연어 호출:
  "이 환자 시간대별 외용 처방"
  → time_optimal_topical_schedule(diagnosis="흉터")

  "현재 시간 어떤 경락 활성?"
  → current_meridian_active()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


# 12 시진 + 12 경락 매핑 (한방 자오류주)
JAORYUJU_MAP = [
    {"hour_start": 23, "hour_end": 1, "name": "子時 (자시)",
     "meridian": "膽經 (담경/Gallbladder)",
     "skin_relevance": "low", "function": "양기 발동, 수면"},
    {"hour_start": 1, "hour_end": 3, "name": "丑時 (축시)",
     "meridian": "肝經 (간경/Liver)",
     "skin_relevance": "high",
     "function": "혈액 정화, 피부 재생 (야간 수면 시 콜라겐 합성)",
     "topical_recommend": "anti-aging cream 자기 전 적용"},
    {"hour_start": 3, "hour_end": 5, "name": "寅時 (인시)",
     "meridian": "肺經 (폐경/Lung)",
     "skin_relevance": "very_high",
     "function": "★ 폐경 우세 — 피부 표면, IPF cross-disease 활성",
     "ipf_relevance": "lung fibroblast 회복 시간"},
    {"hour_start": 5, "hour_end": 7, "name": "卯時 (묘시)",
     "meridian": "大腸經 (대장경/Large Intestine)",
     "skin_relevance": "high",
     "function": "★ 배출 강함 — 외용제 흡수 최적 (사과 시간)",
     "topical_recommend": "주요 외용제 (자운고+EMB-3) 적용"},
    {"hour_start": 7, "hour_end": 9, "name": "辰時 (진시)",
     "meridian": "胃經 (위경/Stomach)",
     "skin_relevance": "low", "function": "소화, 영양 흡수"},
    {"hour_start": 9, "hour_end": 11, "name": "巳時 (사시)",
     "meridian": "脾經 (비경/Spleen)",
     "skin_relevance": "moderate",
     "function": "피부 영양 운반"},
    {"hour_start": 11, "hour_end": 13, "name": "午時 (오시)",
     "meridian": "心經 (심경/Heart)",
     "skin_relevance": "high",
     "function": "혈액 순환 강함 — 약침 시술 권장 시간",
     "treatment_recommend": "facial_dx + 약침 시술 (혈류 강함)"},
    {"hour_start": 13, "hour_end": 15, "name": "未時 (미시)",
     "meridian": "小腸經 (소장경/Small Intestine)",
     "skin_relevance": "low"},
    {"hour_start": 15, "hour_end": 17, "name": "申時 (신시)",
     "meridian": "膀胱經 (방광경/Bladder)",
     "skin_relevance": "moderate",
     "function": "수분 대사 — moisturizer 권장"},
    {"hour_start": 17, "hour_end": 19, "name": "酉時 (유시)",
     "meridian": "腎經 (신경/Kidney)",
     "skin_relevance": "high",
     "function": "신정 보강 — 항노화 시간"},
    {"hour_start": 19, "hour_end": 21, "name": "戌時 (술시)",
     "meridian": "心包經 (심포경/Pericardium)",
     "skin_relevance": "very_high",
     "function": "★ 심포경 — 회복 시간, 흉터 야간 외용 최적",
     "topical_recommend": "흉터 anti-fibrotic 외용제 적용"},
    {"hour_start": 21, "hour_end": 23, "name": "亥時 (해시)",
     "meridian": "三焦經 (삼초경/Triple Burner)",
     "skin_relevance": "moderate",
     "function": "전신 조절 — 휴식"},
]


@dataclass
class TimeOptimalSchedule:
    """시간 최적 외용 schedule."""

    diagnosis: str = ""
    morning_protocol: dict = field(default_factory=dict)
    evening_protocol: dict = field(default_factory=dict)
    night_protocol: dict = field(default_factory=dict)
    in_clinic_protocol: dict = field(default_factory=dict)
    natural_language_summary: str = ""


def current_meridian_active(now: datetime | None = None) -> dict:
    """현재 시간 활성 경락."""
    now = now or datetime.now()
    h = now.hour
    for slot in JAORYUJU_MAP:
        start = slot["hour_start"]
        end = slot["hour_end"]
        if start > end:   # 자정 걸침
            if h >= start or h < end:
                return {**slot, "current_time": now.isoformat()}
        else:
            if start <= h < end:
                return {**slot, "current_time": now.isoformat()}
    return {"error": "매칭 안됨"}


def time_optimal_topical_schedule(diagnosis: str = "흉터") -> TimeOptimalSchedule:
    """질환별 시간 최적 외용 schedule (자연어 호출).

    한방 자오류주 + 현대 chronotherapy 융합.
    """
    if diagnosis in ["흉터", "scar", "비후성", "위축성"]:
        morning = {
            "time": "卯時 (5-7시)",
            "rationale": "대장경 — 외용제 흡수 최적, 사과 시간",
            "product": "Recover Hypertrophic Cream (자운고+EMB-3+Embelin)",
            "note": "활성 시술 — 가장 깊이 침투",
        }
        evening = {
            "time": "酉時 (17-19시)",
            "rationale": "신경 — 항노화 시간",
            "product": "moisturizer (saline + ceramide) 보호",
        }
        night = {
            "time": "戌時 (19-21시)",
            "rationale": "★ 심포경 — 흉터 야간 회복 최적",
            "product": "Recover Hypertrophic Cream 강화 layer",
            "note": "콜라겐 야간 합성 + Pro-Hyp 보강",
        }
        in_clinic = {
            "time": "午時 (11-13시)",
            "rationale": "심경 — 혈류 강함",
            "treatment": "facial_dx + 약침 + PBM LED 통합 시술",
        }
    elif diagnosis in ["여드름", "acne"]:
        morning = {
            "time": "卯時 (5-7시)",
            "rationale": "대장경 — 배출 강함 (해독)",
            "product": "황련해독탕 외용 (berberine, baicalin)",
        }
        evening = {
            "time": "戌時 (19-21시)",
            "rationale": "심포경 회복",
            "product": "감초 외용 (licochalcone A) 진정",
        }
        night = {"time": "—", "product": "건드리지 않음 (자연 회복)"}
        in_clinic = {"time": "辰時 (7-9시)", "rationale": "위경",
                      "treatment": "황련 약침 + LED 415 nm blue (anti-acne)"}
    elif diagnosis in ["탈모", "alopecia"]:
        morning = {"time": "卯時 (5-7시)",
                    "product": "측백엽 외용 + D+Q senolytic (T8-4)"}
        evening = {"time": "酉時 (17-19시)",
                    "rationale": "신경 — 모발 영양",
                    "product": "하수오 추출 + EMB-3 (모낭 anti-fibrotic)"}
        night = {"time": "戌時 (19-21시)",
                  "product": "scalp serum 두피 마사지"}
        in_clinic = {"time": "午時 (11-13시)",
                      "treatment": "새살침 두피 + PBM LED 660 nm + EMB-3 약침"}
    else:
        morning = evening = night = in_clinic = {
            "rationale": "diagnosis 명시 필요",
        }

    nl = (
        f"**{diagnosis} 자오류주 + chronotherapy schedule**\n\n"
        f"🌅 **아침 외용** ({morning.get('time', '')}):\n"
        f"   {morning.get('product', '')}\n"
        f"   → {morning.get('rationale', '')}\n\n"
        f"🏥 **시술 in-clinic** ({in_clinic.get('time', '')}):\n"
        f"   {in_clinic.get('treatment', '')}\n"
        f"   → {in_clinic.get('rationale', '')}\n\n"
        f"🌆 **저녁 외용** ({evening.get('time', '')}):\n"
        f"   {evening.get('product', '')}\n"
        f"   → {evening.get('rationale', '')}\n\n"
        f"🌙 **야간 외용** ({night.get('time', '')}):\n"
        f"   {night.get('product', '')}\n"
        f"   → {night.get('rationale', '')}\n\n"
        f"※ 한방 자오류주 + 현대 circadian 융합 = 한국 unique 시술 프로토콜"
    )
    return TimeOptimalSchedule(
        diagnosis=diagnosis,
        morning_protocol=morning, evening_protocol=evening,
        night_protocol=night, in_clinic_protocol=in_clinic,
        natural_language_summary=nl,
    )
