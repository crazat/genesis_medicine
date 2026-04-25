"""학술 출판용 자동 리포팅.

Genesis_Medicine v3 모듈 — 각 pilot 디렉터리를
manuscript-ready output (markdown + figures + tables + bib + checklist)
으로 변환.

표준 입력 (pilot 디렉터리):
    pilot/<NAME>/
        results/
            <STUDY>_consensus.csv          ← target × compound × score 매트릭스
            <STUDY>_full.csv               ← detailed long-form
        run.log (또는 mlflow run)
        config.snapshot.yaml               (Hydra config snapshot)

표준 출력:
    pilot/<NAME>/manuscript/
        manuscript.md          ← Pandoc 호환 (LaTeX/PDF 변환 가능)
        figures/
            fig1_heatmap.{png,pdf}
            fig2_distribution.{png,pdf}
            fig3_lipinski_radar.{png,pdf}
            fig4_roc.{png,pdf}
        tables/
            table1_top_hits.{csv,tex}
            tableS1_full_screen.csv
        references.bib
        checklist_tripod_ai.md
        supp_data_availability.md
"""

from .base import StudyContext, ManuscriptResult
from .citations import bibtex_for_components, bibtex_string
from .figure_factory import (
    consensus_heatmap,
    distribution_plot,
    lipinski_radar,
    top_hits_table,
)
from .manuscript_writer import build_manuscript
from .methods_section import generate_methods_section
from .reporting_checklist import tripod_ai_checklist, miclaim_checklist
from .statistics_runner import (
    benjamini_hochberg,
    hit_rate,
    mann_whitney_test,
    roc_auc_with_baseline,
)

__all__ = [
    "StudyContext", "ManuscriptResult",
    "bibtex_for_components", "bibtex_string",
    "consensus_heatmap", "distribution_plot", "lipinski_radar", "top_hits_table",
    "build_manuscript",
    "generate_methods_section",
    "tripod_ai_checklist", "miclaim_checklist",
    "benjamini_hochberg", "hit_rate", "mann_whitney_test", "roc_auc_with_baseline",
]
