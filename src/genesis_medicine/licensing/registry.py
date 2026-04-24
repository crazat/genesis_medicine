"""Genesis_Medicine이 쓰는 모든 외부 의존성의 라이선스 레지스트리.

의존성 추가 시 반드시 이 파일에 등록. `docs/LICENSING.md` 표와 동기화.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LicenseTag(str, Enum):
    COMMERCIAL_SAFE = "commercial-safe"
    COMMERCIAL_SHARE_ALIKE = "commercial-share-alike"
    COMMERCIAL_CONDITIONAL = "commercial-conditional"
    RESEARCH_ONLY = "research-only"
    BLOCKED = "blocked"


class ComponentKind(str, Enum):
    MODEL = "model"
    DATA = "data"
    TOOL = "tool"


@dataclass(frozen=True)
class Component:
    key: str
    kind: ComponentKind
    license: str
    tag: LicenseTag
    url: str
    note: str = ""


# --- 모델 --------------------------------------------------------------------
_MODELS = [
    Component("alphafold3_weights", ComponentKind.MODEL,
              "code Apache-2.0 / weights non-commercial", LicenseTag.RESEARCH_ONLY,
              "https://github.com/google-deepmind/alphafold3"),
    Component("protenix_v2", ComponentKind.MODEL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/bytedance/Protenix"),
    Component("boltz2", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/jwohlwend/boltz"),
    Component("chai1_weights", ComponentKind.MODEL, "weights non-commercial",
              LicenseTag.RESEARCH_ONLY, "https://github.com/chaidiscovery/chai-lab"),
    Component("chai2_weights", ComponentKind.MODEL, "weights non-commercial",
              LicenseTag.RESEARCH_ONLY, "https://github.com/chaidiscovery/chai-lab"),
    Component("esmfold", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/facebookresearch/esm"),
    Component("esm3_cambrian", ComponentKind.MODEL, "Cambrian (revenue-conditional)",
              LicenseTag.COMMERCIAL_CONDITIONAL, "https://www.evolutionaryscale.ai"),
    Component("rfaa", ComponentKind.MODEL, "mixed (some weights NC)", LicenseTag.RESEARCH_ONLY,
              "https://github.com/baker-laboratory/RoseTTAFold-All-Atom"),
    Component("diffdock_l", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/gcorso/DiffDock"),
    Component("gnina", ComponentKind.MODEL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/gnina/gnina"),
    Component("reinvent4", ComponentKind.MODEL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/MolecularAI/REINVENT4"),
    Component("diffsbdd", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/arneschneuing/DiffSBDD"),
    Component("targetdiff", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/guanjq/targetdiff"),
    Component("rfdiffusion", ComponentKind.MODEL, "BSD-3 variant", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/RosettaCommons/RFdiffusion"),
    Component("txgemma", ComponentKind.MODEL, "Gemma (conditional)",
              LicenseTag.COMMERCIAL_CONDITIONAL, "https://huggingface.co/google/txgemma"),
    Component("admet_ai", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/swansonk14/admet_ai"),
    Component("chemprop2", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/chemprop/chemprop"),
    Component("unimol2", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/deepmodeling/Uni-Mol"),
    Component("molformer_xl", ComponentKind.MODEL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/IBM/molformer"),
    Component("bern2", ComponentKind.MODEL, "BSD-2", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/dmis-lab/BERN2"),
    Component("gliner_biomed", ComponentKind.MODEL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/urchade/GLiNER"),
    # --- v2 고도화 추가 (2026-04-25) -------------------------------------------
    Component("openfold3", ComponentKind.MODEL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/aqlaboratory/openfold-3"),
    Component("flowdock", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/BioinfoMachineLearning/FlowDock"),
    Component("drugclip", ComponentKind.MODEL, "MIT (확인 필요)", LicenseTag.COMMERCIAL_SAFE,
              "https://drugclip.com", note="Science 2026, 라이선스 최종 확인 필요"),
    Component("flowmol3", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/Dunni3/FlowMol"),
    Component("decompdiff", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/bytedance/DecompDiff"),
    Component("saturn", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/schwallergroup/saturn"),
    Component("neuralplex3_code", ComponentKind.MODEL, "BSD-3", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/iambic-therapeutics/NeuralPLexer3",
              note="코드만 BSD-3, 웨이트는 CC-BY-NC-SA → research 전용"),
    Component("neuralplex3_weights", ComponentKind.MODEL, "CC-BY-NC-SA 4.0",
              LicenseTag.RESEARCH_ONLY,
              "https://github.com/iambic-therapeutics/NeuralPLexer3"),
    Component("esm_c_300m", ComponentKind.MODEL, "Cambrian Open License",
              LicenseTag.COMMERCIAL_CONDITIONAL,
              "https://www.evolutionaryscale.ai/blog/esm-cambrian",
              note="상업 OK, 매출 임계 확인 필요"),
]

# --- 데이터 ------------------------------------------------------------------
_DATA = [
    Component("pubmed", ComponentKind.DATA, "Public domain (mostly)",
              LicenseTag.COMMERCIAL_SAFE, "https://pubmed.ncbi.nlm.nih.gov"),
    Component("uniprot", ComponentKind.DATA, "CC BY 4.0", LicenseTag.COMMERCIAL_SAFE,
              "https://www.uniprot.org"),
    Component("alphafold_db", ComponentKind.DATA, "CC BY 4.0", LicenseTag.COMMERCIAL_SAFE,
              "https://alphafold.ebi.ac.uk"),
    Component("open_targets", ComponentKind.DATA, "CC0", LicenseTag.COMMERCIAL_SAFE,
              "https://platform.opentargets.org"),
    Component("primekg", ComponentKind.DATA, "MIT (+ upstream attributions)",
              LicenseTag.COMMERCIAL_SAFE, "https://github.com/mims-harvard/PrimeKG"),
    Component("hetionet", ComponentKind.DATA, "CC0", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/hetio/hetionet"),
    Component("pubchem", ComponentKind.DATA, "Public domain", LicenseTag.COMMERCIAL_SAFE,
              "https://pubchem.ncbi.nlm.nih.gov"),
    Component("chembl_35", ComponentKind.DATA, "CC BY-SA 3.0",
              LicenseTag.COMMERCIAL_SHARE_ALIKE, "https://www.ebi.ac.uk/chembl/"),
    Component("zinc22", ComponentKind.DATA, "Free for commercial (with attribution)",
              LicenseTag.COMMERCIAL_SAFE, "https://zinc22.docking.org"),
    Component("enamine_real", ComponentKind.DATA, "commercial license required",
              LicenseTag.BLOCKED, "https://enamine.net"),
    Component("coconut_2", ComponentKind.DATA, "CC0", LicenseTag.COMMERCIAL_SAFE,
              "https://coconut.naturalproducts.net"),
    Component("lotus", ComponentKind.DATA, "CC0", LicenseTag.COMMERCIAL_SAFE,
              "https://lotus.naturalproducts.net"),
    Component("drduke", ComponentKind.DATA, "Public domain (USDA)",
              LicenseTag.COMMERCIAL_SAFE, "https://phytochem.nal.usda.gov"),
    Component("herb_2_0", ComponentKind.DATA, "CC-BY-NC", LicenseTag.RESEARCH_ONLY,
              "http://herb.ac.cn"),
    Component("tcmsp", ComponentKind.DATA, "Academic only", LicenseTag.RESEARCH_ONLY,
              "https://tcmsp-e.com"),
    Component("tcmid", ComponentKind.DATA, "Academic", LicenseTag.RESEARCH_ONLY,
              "http://www.megabionet.org/tcmid"),
    Component("batman_tcm_2", ComponentKind.DATA, "Academic", LicenseTag.RESEARCH_ONLY,
              "http://bionet.ncpsb.org.cn/batman-tcm"),
    Component("symmap_v2", ComponentKind.DATA, "Academic", LicenseTag.RESEARCH_ONLY,
              "https://www.symmap.org"),
    Component("etcm_v2", ComponentKind.DATA, "Academic", LicenseTag.RESEARCH_ONLY,
              "http://www.tcmip.cn/ETCM2"),
    Component("ktkp_raw", ComponentKind.DATA, "Korean gov (permission required)",
              LicenseTag.RESEARCH_ONLY, "https://www.koreantk.com"),
    Component("kegg_pathways", ComponentKind.DATA, "Commercial license required",
              LicenseTag.RESEARCH_ONLY, "https://www.kegg.jp"),
    Component("reactome", ComponentKind.DATA, "CC BY 4.0", LicenseTag.COMMERCIAL_SAFE,
              "https://reactome.org"),
    Component("wikipathways", ComponentKind.DATA, "CC0", LicenseTag.COMMERCIAL_SAFE,
              "https://www.wikipathways.org"),
    Component("khp_kp", ComponentKind.DATA, "Korean gov publication",
              LicenseTag.COMMERCIAL_SAFE, "https://www.mfds.go.kr"),
    Component("npass_3", ComponentKind.DATA, "확인 필요", LicenseTag.COMMERCIAL_SAFE,
              "https://bidd.group/NPASS/", note="204K 화합물, ADME-Tox 데이터. 라이선스 확인 필요"),
    Component("npatlas_3", ComponentKind.DATA, "CC-BY", LicenseTag.COMMERCIAL_SAFE,
              "https://www.npatlas.org"),
]

# --- 런타임·도구 -------------------------------------------------------------
_TOOLS = [
    Component("rdkit", ComponentKind.TOOL, "BSD-3", LicenseTag.COMMERCIAL_SAFE,
              "https://www.rdkit.org"),
    Component("openmm", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://openmm.org"),
    Component("hmmer", ComponentKind.TOOL, "BSD-3", LicenseTag.COMMERCIAL_SAFE,
              "http://hmmer.org"),
    Component("mmseqs2", ComponentKind.TOOL, "BSD-2", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/soedinglab/MMseqs2"),
    Component("colabfold_code", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/sokrypton/ColabFold"),
    Component("colabfold_public_msa", ComponentKind.TOOL, "Academic (public server)",
              LicenseTag.RESEARCH_ONLY, "colabfold public MSA service"),
    Component("hydra", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE, ""),
    Component("prefect3", ComponentKind.TOOL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE, ""),
    Component("mlflow", ComponentKind.TOOL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE, ""),
    Component("dvc", ComponentKind.TOOL, "Apache-2.0", LicenseTag.COMMERCIAL_SAFE, ""),
    Component("posebusters", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/maabuu/posebusters"),
    Component("aizynthfinder", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/MolecularAI/aizynthfinder"),
]

LICENSE_REGISTRY: dict[str, Component] = {
    c.key: c for c in (*_MODELS, *_DATA, *_TOOLS)
}


def get_component(key: str) -> Component:
    if key not in LICENSE_REGISTRY:
        raise KeyError(
            f"라이선스 레지스트리에 등록되지 않은 key='{key}'. "
            f"src/genesis_medicine/licensing/registry.py와 docs/LICENSING.md에 추가하세요."
        )
    return LICENSE_REGISTRY[key]
