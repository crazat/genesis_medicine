"""라이선스 게이트 · provenance 태깅.

Genesis_Medicine은 두 빌드 프로파일(`commercial`, `research`)을 갖는다.
이 모듈은 상업 빌드에서 비상업 데이터·모델 사용을 **런타임에 차단**한다.
"""

from .gate import LicenseGate, LicenseViolation
from .registry import LICENSE_REGISTRY, ComponentKind, LicenseTag

__all__ = [
    "LICENSE_REGISTRY",
    "ComponentKind",
    "LicenseGate",
    "LicenseTag",
    "LicenseViolation",
]
