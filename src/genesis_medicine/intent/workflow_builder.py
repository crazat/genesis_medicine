"""Intent → workflow YAML/CLI 변환.

Claude Code가 사용자 자연어를 parse_intent로 표준화한 후 이 모듈로
실행 가능한 명령 또는 workflow YAML을 자동 생성.
"""

from __future__ import annotations

from pathlib import Path

from .parser import Intent

ROOT = Path(__file__).resolve().parents[3]


def intent_to_command(intent: Intent) -> dict:
    """Intent → CLI 명령 + 작업 메타.

    Returns: {
        "command": str | list[str],
        "description": str,
        "expected_minutes": int,
        "preconditions": list[str],
    }
    """
    if intent.intent_type == "run_pilot":
        d = intent.slots.get("disease", "scar")
        if d == "scar":
            return {
                "command": [str(ROOT / ".venv/bin/python"),
                            str(ROOT / "pilot/skin_scar/run_scar_pilot_v2.py")],
                "description": f"흉터 파일럿 v2 실행 (49 화합물 × 3 타겟)",
                "expected_minutes": 35,
                "preconditions": ["GPU 30GB free", "data/skin_compounds_curated.csv"],
            }
        else:
            return {
                "command": [str(ROOT / ".venv/bin/python"),
                            str(ROOT / "pilot/run_skin_pilot.py"),
                            "--disease", d],
                "description": f"{d} 파일럿 실행 (generic runner)",
                "expected_minutes": 30,
                "preconditions": ["GPU free"],
            }

    if intent.intent_type == "run_md":
        return {
            "command": ["conda", "run", "-n", "genesis-md",
                        "python", str(ROOT / "pilot/skin_scar/run_md_top_hits.py")],
            "description": "Top 3 화합물 × 3 타겟 = 9 MD 10 ns",
            "expected_minutes": 90,
            "preconditions": ["genesis-md conda env", "Boltz output"],
        }

    if intent.intent_type == "build_manuscript":
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        str(ROOT / "scripts/build_system_manuscript.py")],
            "description": "5 파일럿 통합 시스템 manuscript draft",
            "expected_minutes": 1,
            "preconditions": ["pilot/cross_disease/* 결과"],
        }

    if intent.intent_type == "novelty_check":
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        str(ROOT / "scripts/demo_novelty_scar.py")],
            "description": "Top 10 화합물 × 6 데이터소스 novelty 평가",
            "expected_minutes": 5,
            "preconditions": ["network"],
        }

    if intent.intent_type == "monitor":
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        "-m", "genesis_medicine.monitoring",
                        "--days", "7"],
            "description": "bioRxiv + Semantic Scholar 새 paper 검색 + diff alert",
            "expected_minutes": 5,
            "preconditions": ["network"],
        }

    if intent.intent_type == "extend_to_disease":
        d = intent.slots.get("disease", "atopic")
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        str(ROOT / "pilot/run_skin_pilot.py"),
                        "--disease", d],
            "description": f"{d}으로 파이프라인 확장",
            "expected_minutes": 30,
            "preconditions": ["GPU free", f"conf/disease/{d}.yaml"],
        }

    if intent.intent_type == "irb_protocol":
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        str(ROOT / "scripts/demo_clinical.py")],
            "description": "흉터·기미 IRB 프로토콜 + 동의서 자동",
            "expected_minutes": 1,
            "preconditions": [],
        }

    if intent.intent_type == "cro_quote":
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        str(ROOT / "scripts/demo_clinical.py")],
            "description": "5 질환 CRO 견적 (~1.14억원 통합)",
            "expected_minutes": 1,
            "preconditions": [],
        }

    if intent.intent_type == "scaffold_hop":
        return {
            "command": ["echo", "REINVENT 4 prior 다운로드 필요 (다음 세션)"],
            "description": "Embelin/Curcumin scaffold hopping (보류)",
            "expected_minutes": 60,
            "preconditions": ["REINVENT 4 prior", "GPU"],
        }

    if intent.intent_type == "summary":
        return {
            "command": [str(ROOT / ".venv/bin/python"),
                        str(ROOT / "scripts/skin_pilots_summary.py")],
            "description": "5 파일럿 종합 비교 표",
            "expected_minutes": 1,
            "preconditions": [],
        }

    return {
        "command": None,
        "description": "Intent 인식 실패. 사용자 확인 필요.",
        "expected_minutes": 0,
        "preconditions": [],
    }


def build_workflow(intents: list[Intent]) -> dict:
    """여러 intent를 순차 workflow로 묶음."""
    steps = []
    total_minutes = 0
    for i, intent in enumerate(intents, 1):
        cmd = intent_to_command(intent)
        steps.append({
            "step": i,
            "intent": intent.intent_type,
            "raw": intent.raw_text,
            "command": cmd["command"],
            "description": cmd["description"],
            "expected_minutes": cmd["expected_minutes"],
            "preconditions": cmd["preconditions"],
        })
        total_minutes += cmd["expected_minutes"]
    return {
        "n_steps": len(steps),
        "total_expected_minutes": total_minutes,
        "steps": steps,
    }
