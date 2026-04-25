"""임상 자동화 패키지.

Recover 한의원 (강남, 4월 오픈) 임상 진입 지원:
- IRB 프로토콜 자동 작성 (한국 식약처 + 한방 양식)
- 동의서 자동 생성 (한글 + 영문)
- In vitro CRO 견적 자동 추천 (한국 CRO 표준)
- 임상 모니터링 데이터 모델 (case form)
"""

from .irb_protocol import (
    ClinicalContext,
    generate_irb_protocol,
    generate_consent_form_korean,
    generate_consent_form_english,
)
from .cro_quote import (
    AssayCatalogue,
    recommend_assays,
    estimate_total_cost,
)

__all__ = [
    "ClinicalContext",
    "generate_irb_protocol",
    "generate_consent_form_korean",
    "generate_consent_form_english",
    "AssayCatalogue",
    "recommend_assays",
    "estimate_total_cost",
]
