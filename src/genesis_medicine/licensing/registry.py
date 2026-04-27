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
    # --- v2.1 고도화 추가 (2026-04-25, ultrathink 검토 후) ---------------------
    # 약물 재창출 — Stage 1.5
    Component("txgnn", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/mims-harvard/TxGNN",
              note="Nature Med 2024, zero-shot 약물 재창출 GNN. 17,080 질병 × 7,957 후보."),
    # 컨포메이셔널 앙상블 — Stage 2.5
    Component("alphaflow", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/bjing2016/alphaflow",
              note="apo→holo conformational ensemble, cryptic pocket 발굴."),
    Component("bioemu", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/microsoft/bioemu",
              note="Microsoft BioEmu — Boltzmann emulator, 2026-01."),
    # ML potential MD — Stage 8'
    Component("mace_off24", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/ACEsuit/mace-off",
              note="MACE-OFF24(M) — protein-ligand binding free energy 가능."),
    Component("openmm_ml", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/openmm/openmm-ml",
              note="OpenMM ML potential 인터페이스 (ANI, MACE 지원)."),
    Component("aceff", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/ACEsuit/aceff",
              note="AceFF 1.0/1.1/2.0 foundation potential."),
    # 절대 결합자유에너지 — Stage 8.5
    Component("fep_spell_abfe", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/jackalbright/FEP-SPell-ABFE",
              note="JCIM 2025 — 자동화 ABFE 워크플로, FEP+ 오픈 대체."),
    Component("pmx", ComponentKind.TOOL, "GPL-3", LicenseTag.RESEARCH_ONLY,
              "https://github.com/deGrootLab/pmx",
              note="GROMACS 기반 alchemical, GPL-3 → research 또는 서브프로세스 격리."),
    # 단백질 바인더 모달리티
    Component("bindcraft", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/martinpacesa/BindCraft",
              note="Nature 2025, AlphaProteo 오픈 대체. 10-100% 실험 성공률."),
    # PROTAC/분자글루 (research only — 학습 데이터 출처 모호)
    Component("protac_jt_vae", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/divelab/PROTAC",
              note="JT-VAE 기반 PROTAC 생성. 학습 데이터 검증 필요."),
    Component("molglue_jtvae", ComponentKind.MODEL, "MIT", LicenseTag.RESEARCH_ONLY,
              "https://github.com/molecule-glue/glue-design",
              note="CRBN/VHL 조건부 분자글루. 학습 데이터에 NC 출처 포함 가능 → 안전 기본 research."),
    # 가속 커널 — NVIDIA EULA, 상업 사용 가능
    Component("cuequivariance_torch", ComponentKind.TOOL, "NVIDIA EULA",
              LicenseTag.COMMERCIAL_SAFE,
              "https://pypi.org/project/cuequivariance-torch/",
              note="NVIDIA cuEquivariance v0.7+, Boltz-2/Protenix 가속, 상업 OK."),
    Component("boltz_blackwell", ComponentKind.TOOL, "MIT",
              LicenseTag.COMMERCIAL_SAFE,
              "https://pypi.org/project/boltz-blackwell/",
              note="RTX 5090 (Blackwell)용 Boltz-2 휠. PreRelease."),
    # 활성 학습 / 점진적 도킹
    Component("deep_docking", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/jamesgleave/Deep-Docking-NonAutomated",
              note="Cherkasov lab Deep Docking — 1.4B 화합물 활성학습."),
    # PoseBench 검증
    Component("posebench_v2", ComponentKind.TOOL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/BioinfoMachineLearning/PoseBench",
              note="PoseBench v2 — 308 복합체 apo-to-holo 벤치마크 (Nat Mach Intell 2025)."),
    # --- 2026-04-27 SOTA audit 추가 (11개 Tier B 통합) -----------------------
    Component("siteaf3", ComponentKind.MODEL, "code TBD / weights NC?",
              LicenseTag.RESEARCH_ONLY,
              "https://github.com/HaCTang/SiteAF3",
              note="PNAS 2026, conditional diffusion AF3-derived. allosteric site 직접. 가중치 라이선스 검증 전 — research only."),
    Component("pocketxmol", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/pengxingang/PocketXMol",
              note="Cell 2026, 단일 모델 SBDD + cyclic peptide + linker + PROTAC. 약침 vertical 직접."),
    Component("g_xtb", ComponentKind.MODEL, "Grimme academic free",
              LicenseTag.RESEARCH_ONLY,
              "https://chemrxiv.org/doi/10.26434/chemrxiv-2025-bjxvt",
              note="g-xTB GFN2 대비 MAE 절반, Z=1-103 metalloprotein. commercial 별도 컨택."),
    Component("nn_xtb", ComponentKind.MODEL, "Grimme academic free",
              LicenseTag.RESEARCH_ONLY,
              "https://chemrxiv.org/doi/full/10.26434/chemrxiv-2025-chlcc-v3",
              note="NN-xTB WTMAD-2 4 vs xtb 25 kcal/mol — 6× 정확도."),
    Component("aceff_v2", ComponentKind.MODEL, "MIT", LicenseTag.COMMERCIAL_SAFE,
              "https://github.com/ACEsuit/aceff",
              note="AceFF 2.0 (2026-01) — TensorNet, charged + 12 medchem 원소. MACE-OFF24 drop-in."),
    Component("dancik_pbpk", ComponentKind.TOOL, "Method (published, 자체 구현)",
              LicenseTag.COMMERCIAL_SAFE,
              "https://link.springer.com/article/10.1007/s11095-013-1011-x",
              note="Dancik 4-layer skin PBPK ODE — published method 자체 구현."),
    Component("osp_mobi", ComponentKind.TOOL, "GPLv2", LicenseTag.RESEARCH_ONLY,
              "https://github.com/Open-Systems-Pharmacology/MoBi",
              note="OSP MoBi — research only (GPLv2). 결과 데이터만 commercial 이식."),
    Component("skinpix", ComponentKind.DATA, "Open dataset",
              LicenseTag.COMMERCIAL_SAFE,
              "https://www.nature.com/articles/s41597-024-03026-4",
              note="OECD 428 호환 harmonized logKp/flux/lag time. 자체 logKp LGBM 학습 데이터."),
    Component("npass_2026", ComponentKind.DATA, "Free academic+commercial",
              LicenseTag.COMMERCIAL_SAFE,
              "https://academic.oup.com/nar/article/54/D1/D1519/8324957",
              note="NPASS 2026 update — +87,507 quant composition + 9,713 ADME records."),
    Component("scprimekg", ComponentKind.DATA, "MIT (likely)",
              LicenseTag.COMMERCIAL_SAFE,
              "https://www.biorxiv.org/content/10.64898/2026.02.20.707076v1",
              note="bioRxiv 2026-02, single-cell context PrimeKG. 자가면역 +6% AUPRC."),
    Component("pilosebaceous_atlas", ComponentKind.DATA, "CC-BY 4.0 (CELLxGENE)",
              LicenseTag.COMMERCIAL_SAFE,
              "https://www.biorxiv.org/content/10.1101/2025.09.09.675235v1",
              note="821k cells × 34 datasets, 모낭/피지선 atlas. AGA 직격."),
    Component("multi_fidelity_bo", ComponentKind.TOOL, "Method (published)",
              LicenseTag.COMMERCIAL_SAFE,
              "https://pubs.acs.org/doi/10.1021/acscentsci.4c01991",
              note="ACS Cent Sci 2025 multi-fidelity BO cascade. 자체 구현."),
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
