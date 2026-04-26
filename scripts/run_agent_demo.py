"""Genesis_Medicine v3 LLM agent demo.

ChemCrow-style wrapper로 자연어 요청 → 14단계 파이프라인 자율 실행.

사용:
    .venv/bin/python scripts/run_agent_demo.py "EMB-3와 비슷한 hERG 더 낮은 후보 30개 만들어서 TGFB1 affinity 검증"

전제: .env에 ANTHROPIC_API_KEY 설정 + anthropic SDK 설치.
"""

from __future__ import annotations

import json
import sys

from genesis_medicine.agents.chemcrow_wrapper import run_agent, TOOLS


def main() -> int:
    if len(sys.argv) < 2:
        print("\n=== Genesis_Medicine v3 LLM agent ===")
        print(f"\n사용 가능 tools ({len(TOOLS)}):")
        for t in TOOLS:
            print(f"  - {t.name:25s} : {t.description[:70]}")
        print(f"\n사용:")
        print(f'  {sys.argv[0]} "<자연어 요청>"')
        print(f"\n예시:")
        print(f'  ... "Embelin scaffold-hop으로 hERG 0.2 미만 후보 30개"')
        print(f'  ... "TGFB1 cryptic site에 결합하는 새 분자 추천"')
        print(f'  ... "EMB-3가 IPF에도 적용 가능한지 분석해줘"')
        return 0

    query = sys.argv[1]
    print(f"\n=== Agent 요청 ===\n{query}\n")
    print("=== Agent 실행 (Anthropic Claude API) ===\n")

    session = run_agent(query, max_iter=5)

    print(f"\n=== Tool calls ({len(session.tool_calls)}) ===")
    for i, (tc, tr) in enumerate(zip(session.tool_calls, session.tool_results)):
        print(f"\n[{i+1}] {tc['name']}({json.dumps(tc['input'], ensure_ascii=False)})")
        print(f"    → {json.dumps(tr, ensure_ascii=False, default=str)[:200]}")

    print(f"\n=== 최종 답변 ===\n{session.final_summary}")
    print(f"\n총 토큰: {session.total_tokens}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
