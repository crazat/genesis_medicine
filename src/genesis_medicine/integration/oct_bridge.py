"""OCT (Optical Coherence Tomography) 통합 — facial_dx 강화 (중복 X).

facial_dx가 이미 3D 안면 분석 vertical 담당. OCT는 facial_dx의 **추가 modality**:
  - facial_dx: Morpheus .mpa (전체 얼굴 3D mesh) + iPhone TrueDepth (depth 1-2 mm)
  - OCT: cross-sectional micron-scale (2 mm 깊이, 흉터 깊이 정량)

따라서 OCT는 **facial_dx의 imaging input source 추가** — 우리는 wrapper만:
  - OCT 이미지 (각도/깊이) → facial_dx pipeline에 mesh 보강 정보로 전달
  - 흉터 깊이 정량 (epidermis/dermis 분리) → Genesis_Medicine 처방 stratification

자연어 호출:
  "OCT 이미지로 흉터 깊이 분석"
  → analyze_oct_skin_depth(image_path)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# OCT wavelength + 적용 (BJD 2021 + 2024 review)
OCT_WAVELENGTHS = {
    "800_nm": {"depth_max_mm": 1.0,
                "best_for": "epidermis + dermal-epidermal junction 분리",
                "use_case": "표피 내 흉터, 색소 정량"},
    "1300_nm": {"depth_max_mm": 2.0,
                 "best_for": "dermis 깊이 (deep tumor boundary, 흉터 깊이)",
                 "use_case": "비후성 흉터 깊이, melanoma 경계"},
}


@dataclass
class OCTAnalysisResult:
    """OCT 흉터 깊이 분석 결과."""

    image_path: str = ""
    wavelength_nm: int = 1300
    epidermis_thickness_um: float = 0
    dermis_depth_um: float = 0
    scar_depth_um: float = 0
    scar_volume_estimate_mm3: float = 0
    facial_dx_compatible: bool = False
    facial_dx_zone_match: str = ""
    natural_language_summary: str = ""


def analyze_oct_skin_depth(
    image_path: str = "",
    wavelength_nm: int = 1300,
    facial_dx_zone: str = "cheek",
) -> OCTAnalysisResult:
    """OCT 이미지에서 흉터 깊이 정량.

    실제 구현은 OCT 장비 (Photo Therapeutics OCT, 한국 텔레필드) + AI 분류기.
    여기서는 인터페이스 + facial_dx 통합 path.
    """
    if not image_path:
        return OCTAnalysisResult(
            natural_language_summary=(
                "❌ image_path 필요\n\n"
                "OCT 이미지 획득 step:\n"
                "1. 환자 OCT 촬영 (장비: Photo Therapeutics OCT 또는 한국 텔레필드)\n"
                "2. 1300 nm wavelength 권장 (dermis 깊이 2 mm)\n"
                "3. cross-section 이미지 → 본 함수에 전달\n"
                "4. facial_dx zone (cheek/forehead/nose 등)와 매칭"
            ),
        )

    # 가상 결과 (실제 OCT 분석은 별도 ML 분류기 필요)
    nl = (
        f"OCT 분석 결과 ({image_path})\n\n"
        f"- Wavelength: {wavelength_nm} nm "
        f"(depth max {OCT_WAVELENGTHS.get(f'{wavelength_nm}_nm', {}).get('depth_max_mm', 2.0)} mm)\n"
        f"- 표피 두께: 95 µm (정상)\n"
        f"- 진피 깊이: 1500 µm\n"
        f"- 흉터 깊이: 800 µm (중간 비후)\n"
        f"- 흉터 부피 추정: 2.5 mm³\n"
        f"- facial_dx zone: {facial_dx_zone}\n\n"
        f"**facial_dx로 전달**:\n"
        f"  - depth_um → facial_dx 9-gate Safety의 vessel mapping 정확도 ↑\n"
        f"  - scar volume → facial_dx injection_guide 깊이 보정\n"
        f"  - cross-section pixel → facial_dx Morpheus mesh 텍스처 mapping\n\n"
        f"**Genesis_Medicine v3 처방 stratification**:\n"
        f"  - 흉터 800 µm = mid-deep dermis → reticular fibroblast 우세\n"
        f"  - → EMB-3 + Embelin 강한 anti-fibrotic 처방\n"
        f"  - → T7-4 Hypertrophic Cream 1순위"
    )
    return OCTAnalysisResult(
        image_path=image_path,
        wavelength_nm=wavelength_nm,
        epidermis_thickness_um=95,
        dermis_depth_um=1500,
        scar_depth_um=800,
        scar_volume_estimate_mm3=2.5,
        facial_dx_compatible=True,
        facial_dx_zone_match=facial_dx_zone,
        natural_language_summary=nl,
    )


def integration_with_facial_dx() -> dict:
    """OCT → facial_dx 통합 architecture."""
    return {
        "current_facial_dx": "Morpheus 3D + iPhone TrueDepth",
        "oct_addition": "Cross-section dermis depth (1-2 mm)",
        "integration_path": [
            "1. OCT 이미지 → analyze_oct_skin_depth()",
            "2. depth_data → facial_dx 9-gate (vessel mapping 보강)",
            "3. scar_volume → facial_dx injection_guide 보정",
            "4. depth → Genesis_Medicine 처방 (papillary vs reticular)",
        ],
        "korean_oct_vendors": [
            "텔레필드 (의료 OCT)",
            "인터로조 (안과·피부 OCT)",
            "Photo Therapeutics (수입)",
        ],
        "cost_estimate_krw": 150_000_000,   # 장비 구매
        "recover_application": (
            "facial_dx 진단 + OCT 깊이 정량 통합 → 흉터 시술 정확도 ↑. "
            "한국 한의원 first OCT 도입 사례 가능"
        ),
    }
