"""매일 자동 실행 — 새 paper 모니터링 + 가설 conflict 검사.

cron / systemd timer로 등록해 사용. 결과는 .cache/daily_alerts/에 저장.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALERT_DIR = Path.home() / "genesis_medicine" / ".cache" / "daily_alerts"
ALERT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    from genesis_medicine.monitoring import (
        MonitoringTopic, run_monitoring, save_state, diff_against_state,
    )
    from genesis_medicine.conflict import monitor_main_hypotheses
    from genesis_medicine.conflict.regression_detector import render_conflict_report

    # 1. 우리 핵심 토픽 정의
    topics = [
        MonitoringTopic(
            name="Embelin × scar/fibrosis",
            keywords=["embelin", "scar", "fibrosis"],
        ),
        MonitoringTopic(
            name="Acetylshikonin × scar (자운고)",
            keywords=["acetylshikonin", "shikonin", "keloid"],
        ),
        MonitoringTopic(
            name="EGCG × multi-skin",
            keywords=["EGCG", "skin"],
        ),
        MonitoringTopic(
            name="Korean herb × Boltz-2 / virtual screening",
            keywords=["Korean traditional medicine",
                      "structure-based virtual screening", "skin"],
        ),
        MonitoringTopic(
            name="Spirulina phycocyanin × scar (zero-paper hypothesis)",
            keywords=["phycocyanin", "scar", "fibrosis"],
        ),
    ]

    print(f"=== Daily Monitor ({date.today().isoformat()}) ===")
    print(f"Topics: {len(topics)}")

    report = run_monitoring(topics, days=7)
    state_path = save_state(report)
    print(f"  state saved: {state_path}")

    diff = diff_against_state(report)
    print(f"  diff: {diff.get('n_new_papers', 0)} new papers since "
          f"{diff.get('previous_date', 'first run')}")

    # 2. 가설 conflict 검사
    print("\n=== Hypothesis conflict check ===")
    checks = monitor_main_hypotheses()
    md = render_conflict_report(checks)

    # 3. 알림 파일 작성
    alert_path = ALERT_DIR / f"alert_{date.today().isoformat()}.md"
    alert_lines = [
        f"# Daily Alert ({date.today().isoformat()})",
        "",
        f"## 새 paper ({diff.get('n_new_papers', 0)}건)",
        "",
    ]
    if diff.get("n_new_papers", 0) > 0:
        for p in diff.get("new_papers", []):
            alert_lines.append(f"- [{p['source']}] **{p['topic']}**")
            alert_lines.append(f"  - {p['title']}")
            if p.get("url"):
                alert_lines.append(f"  - {p['url']}")
            alert_lines.append("")
    else:
        alert_lines.append("- 새 paper 없음 (또는 첫 실행)")
        alert_lines.append("")
    alert_lines.append("## 가설 conflict 검사")
    alert_lines.append("")
    alert_lines.append(md)

    alert_path.write_text("\n".join(alert_lines), encoding="utf-8")
    print(f"\n✅ alert: {alert_path}")

    # 4. critical alert 시 추가 출력
    n_critical = sum(1 for c in checks if c.alert_level == "critical")
    n_warning = sum(1 for c in checks if c.alert_level == "warning")
    if n_critical > 0:
        print(f"\n🔴 {n_critical} CRITICAL hypothesis conflict — 가설 재검토 필요")
        return 2
    if n_warning > 0:
        print(f"\n🟡 {n_warning} warning — 차별점 명시 필요")
    return 0


if __name__ == "__main__":
    sys.exit(main())
