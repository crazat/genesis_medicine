"""TRIPOD+AI checklist (BMJ + Nat Med 2024-04, 한국어 번역 PubMed 40739973).

27 항목 manuscript 자동 점검. 자연어 호출:
  "내 EGCG paper TRIPOD-AI 점검해줘"
  → check_manuscript_tripod_ai("manuscript_egcg/manuscript.md")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# TRIPOD+AI 27 항목 (BMJ 2024-04)
TRIPOD_AI_CHECKLIST = [
    # Title and abstract (1-2)
    {"id": 1, "section": "Title", "item": "AI/ML method 명시 + study type",
     "required_keywords": ["machine learning", "AI", "deep learning",
                            "neural network", "boltz", "model"]},
    {"id": 2, "section": "Abstract",
     "item": "Background, objective, methods, results, conclusion 모두",
     "required_sections": ["background", "method", "result", "conclu"]},
    # Introduction (3-4)
    {"id": 3, "section": "Background and objectives",
     "item": "Clinical context + 기존 연구 + gap 명시",
     "required_keywords": ["background", "rationale", "context"]},
    {"id": 4, "section": "Objectives",
     "item": "Specific aim 명시"},
    # Methods (5-19)
    {"id": 5, "section": "Source of data",
     "item": "Data source + collection 명시",
     "required_keywords": ["data", "source", "dataset"]},
    {"id": 6, "section": "Eligibility criteria",
     "item": "Inclusion/exclusion criteria"},
    {"id": 7, "section": "Outcomes",
     "item": "Predicted outcome definition"},
    {"id": 8, "section": "Predictors",
     "item": "Input variables/features 명시",
     "required_keywords": ["feature", "input", "predictor", "variable"]},
    {"id": 9, "section": "Sample size",
     "item": "정당화 + 계산"},
    {"id": 10, "section": "Missing data",
     "item": "Missing data handling"},
    {"id": 11, "section": "Statistical analysis",
     "item": "ML method + hyperparameters",
     "required_keywords": ["validation", "training", "test"]},
    {"id": 12, "section": "Risk of bias", "item": "Bias 평가"},
    {"id": 13, "section": "Calibration",
     "item": "Model calibration evaluation"},
    {"id": 14, "section": "Validation",
     "item": "Internal/external validation",
     "required_keywords": ["validation", "cross-valid"]},
    {"id": 15, "section": "Discrimination",
     "item": "AUC/AUROC/concordance"},
    {"id": 16, "section": "Hardware/software",
     "item": "GPU/CPU + 라이브러리 버전"},
    {"id": 17, "section": "Reproducibility",
     "item": "Code + data availability"},
    {"id": 18, "section": "Random seed/initialization", "item": "재현성"},
    {"id": 19, "section": "Hyperparameter tuning",
     "item": "튜닝 절차"},
    # Results (20-23)
    {"id": 20, "section": "Participants",
     "item": "demographics, inclusion 후 N"},
    {"id": 21, "section": "Model development",
     "item": "Final model description"},
    {"id": 22, "section": "Model performance",
     "item": "Metrics + uncertainty (CI)",
     "required_keywords": ["mean", "±", "CI", "uncertainty"]},
    {"id": 23, "section": "Model interpretation",
     "item": "SHAP/LIME/attention/feature importance",
     "required_keywords": ["SHAP", "feature importance", "attention",
                            "interpret"]},
    # Discussion (24-26)
    {"id": 24, "section": "Limitations", "item": "Limitations 명시",
     "required_keywords": ["limitation", "limit"]},
    {"id": 25, "section": "Implications",
     "item": "Clinical/practical implications"},
    {"id": 26, "section": "Future research", "item": "Next steps"},
    # Other information (27)
    {"id": 27, "section": "Funding + COI", "item": "Conflicts of interest"},
]


@dataclass
class ChecklistItemResult:
    """단일 항목 점검 결과."""

    id: int
    section: str
    item: str
    found: bool = False
    matched_keywords: list = field(default_factory=list)
    note: str = ""


@dataclass
class TRIPODReport:
    """전체 manuscript 점검 결과."""

    manuscript_path: str = ""
    n_total: int = 27
    n_passed: int = 0
    n_failed: int = 0
    pass_rate: float = 0.0
    items: list = field(default_factory=list)
    summary: str = ""
    suggestions: list = field(default_factory=list)


def check_manuscript_tripod_ai(manuscript_path: str) -> TRIPODReport:
    """TRIPOD+AI 27 항목 자동 점검 (자연어 agent 호출 가능).

    Args:
        manuscript_path: manuscript.md 경로

    Returns:
        TRIPODReport with 항목별 통과/실패 + suggestions
    """
    p = Path(manuscript_path)
    if not p.exists():
        return TRIPODReport(manuscript_path=manuscript_path,
                             summary=f"❌ 파일 없음: {manuscript_path}")

    text = p.read_text(encoding="utf-8").lower()

    items_results = []
    n_passed = 0
    suggestions = []
    for item in TRIPOD_AI_CHECKLIST:
        result = ChecklistItemResult(
            id=item["id"], section=item["section"], item=item["item"]
        )
        # keyword 검색
        kws = item.get("required_keywords", [])
        sections = item.get("required_sections", [])
        if kws:
            matched = [kw for kw in kws if kw.lower() in text]
            result.matched_keywords = matched
            result.found = len(matched) > 0
        elif sections:
            matched = [s for s in sections if s.lower() in text]
            result.matched_keywords = matched
            result.found = len(matched) >= len(sections) * 0.5  # 50%+
        else:
            # heuristic — section title 찾기
            section_lower = item["section"].lower()
            result.found = section_lower in text or any(
                w in text for w in section_lower.split()
            )

        if result.found:
            n_passed += 1
        else:
            suggestions.append(
                f"[Item {item['id']}] {item['section']}: {item['item']}"
            )
        items_results.append(result)

    pass_rate = n_passed / 27 * 100

    return TRIPODReport(
        manuscript_path=manuscript_path,
        n_total=27, n_passed=n_passed, n_failed=27 - n_passed,
        pass_rate=pass_rate, items=items_results,
        summary=(f"TRIPOD+AI compliance: {n_passed}/27 ({pass_rate:.0f}%)"
                  + (" ✅ 게재 적합" if pass_rate >= 80 else
                     " ⚠️ 보강 필요" if pass_rate >= 60 else
                     " ❌ 대폭 보완")),
        suggestions=suggestions,
    )


def render_report_markdown(report: TRIPODReport) -> str:
    """Report → 한국어 markdown."""
    lines = [
        f"# TRIPOD+AI Compliance Report",
        f"",
        f"**Manuscript**: `{report.manuscript_path}`",
        f"**Compliance**: {report.summary}",
        f"",
        f"| ID | Section | Item | Status |",
        f"|---:|---------|------|:------:|",
    ]
    for r in report.items:
        status = "✅" if r.found else "❌"
        lines.append(f"| {r.id} | {r.section} | {r.item[:50]} | {status} |")
    if report.suggestions:
        lines.append(f"\n## 보강 권장 ({len(report.suggestions)} 항목)")
        for s in report.suggestions[:10]:
            lines.append(f"- {s}")
    return "\n".join(lines)
