"""외부 데이터 API 통합.

Genesis_Medicine v3 paper 가치 강화 — 우리 분석 결과를 여러 각도에서 검증·확장.

사용 가능한 API
---------------
- GTEx (tissue expression): 우리 타겟의 피부 발현 검증
- BindingDB: ChEMBL 외 추가 affinity 데이터
- STRING DB: protein-protein interactions
- Reactome / WikiPathways: pathway enrichment
- DrugBank Open Data + DisGeNET: drug-disease 매핑
- InterPro / Pfam: 단백질 도메인
- IUPHAR Guide to Pharmacology: 약리학 분류

모든 응답은 ~/.cache/genesis_medicine/external_apis/ 에 캐시 저장.
"""

from .gtex import gtex_skin_expression, gtex_tissue_distribution
from .bindingdb import bindingdb_search
from .string_ppi import string_partners, string_enrichment
from .reactome import reactome_pathways_for_targets
from .interpro import interpro_domains

__all__ = [
    "gtex_skin_expression", "gtex_tissue_distribution",
    "bindingdb_search",
    "string_partners", "string_enrichment",
    "reactome_pathways_for_targets",
    "interpro_domains",
]
