#!/usr/bin/env bash
# Genesis_Medicine 일일 모니터 cron 등록
# 매일 오전 8시 KST 자동 실행 → .cache/daily_alerts/ 에 결과 저장

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="$ROOT/.venv/bin/python"
SCRIPT="$ROOT/scripts/run_daily_monitor.py"
LOG="$HOME/genesis_medicine/.cache/daily_alerts/cron.log"

# crontab 추가 (기존 line 중복 방지)
LINE="0 8 * * * cd $ROOT && $PYTHON $SCRIPT >> $LOG 2>&1"

if crontab -l 2>/dev/null | grep -qF "run_daily_monitor.py"; then
    echo "✅ cron job 이미 등록됨"
    crontab -l | grep -F "run_daily_monitor.py"
else
    (crontab -l 2>/dev/null; echo "$LINE") | crontab -
    echo "✅ cron 등록 완료 (매일 8시 KST)"
    echo "   $LINE"
fi

echo ""
echo "=== 다음 실행 후 확인 ==="
echo "  ls $HOME/genesis_medicine/.cache/daily_alerts/"
echo "  cat $HOME/genesis_medicine/.cache/daily_alerts/alert_\$(date +%Y-%m-%d).md"
echo ""
echo "=== 수동 테스트 ==="
echo "  $PYTHON $SCRIPT"
echo ""
echo "=== 제거 ==="
echo "  crontab -e   # 또는: crontab -l | grep -v run_daily_monitor.py | crontab -"
