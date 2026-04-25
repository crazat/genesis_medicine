"""지속적 prior art 모니터링.

cron-friendly. 매일/매주 실행 → 우리 hit 화합물·타겟·시스템 토픽에 대해
새 paper 자동 감지 → diff alert.

데이터 소스
-----------
- bioRxiv / medRxiv: <https://api.biorxiv.org>
- Semantic Scholar: <https://api.semanticscholar.org>
- KCI 한국학술지: 키워드 검색 + OAI-PMH (선택)
- 기존 PubMed/EPMC도 호출 (novelty 모듈 재사용)
"""

from .biorxiv_feed import biorxiv_recent, medrxiv_recent
from .semantic_scholar import semantic_scholar_search
from .kci_search import kci_search
from .continuous_monitor import (
    MonitoringTopic,
    ContinuousMonitorReport,
    run_monitoring,
    save_state,
    load_state,
    diff_against_state,
)

__all__ = [
    "biorxiv_recent", "medrxiv_recent",
    "semantic_scholar_search",
    "kci_search",
    "MonitoringTopic", "ContinuousMonitorReport",
    "run_monitoring", "save_state", "load_state", "diff_against_state",
]
