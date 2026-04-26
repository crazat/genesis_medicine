"""Genesis_Medicine v3 — 전 Tier 0-8 도구 통합 카탈로그.

ChemCrow agent에 모든 모듈 자연어 호출 가능하게 등록.
이전 chemcrow_wrapper.py (11 tools) → 30+ tools로 확장.

자연어 호출 예시:
  "TRIPOD-AI 점검해줘"
  "EMB-3 한국 보험 수가 추정"
  "동의보감에서 흉터 약재 찾아줘"
  "Recover 환자 microbiome 분석해 처방해줘"
  "EMB-3 vs Embelin causal effect 추정"
  "EMB-3 외용 PBPK 시뮬"
  "자운고 + EMB-3 처방 DDI 평가"
"""

from __future__ import annotations

from .chemcrow_wrapper import Tool


# ═══════════════════════════════════════════════════════════════════════════
# Tier 0-1 (이미 chemcrow_wrapper.py 11 tools 보유)
# Tier 2-8 추가 도구 (모든 모듈 자연어 호출 가능)
# ═══════════════════════════════════════════════════════════════════════════


def _t2_panderm(image_path: str = "", diagnosis: str = "") -> dict:
    from ..dermatology.panderm_adapter import (
        analyze_skin_image, get_treatment_recommendations,
    )
    if image_path:
        a = analyze_skin_image(image_path)
        return {"tool": "panderm", "result": a.__dict__}
    if diagnosis:
        return {"tool": "panderm_treatment_rec",
                "result": get_treatment_recommendations(diagnosis)}
    return {"error": "image_path 또는 diagnosis 제공"}


def _t2_logkp(smiles: str) -> dict:
    import pickle, numpy as np
    from rdkit import Chem
    from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski
    from pathlib import Path
    p = Path(__file__).resolve().parents[3] / "src/genesis_medicine/admet/logkp_model.pkl"
    if not p.exists():
        return {"error": "logkp_model.pkl 미존재 — train_logkp_head.py 실행"}
    with p.open("rb") as f:
        d = pickle.load(f)
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"error": f"invalid SMILES: {smiles}"}
    desc = [Descriptors.MolWt(m), Crippen.MolLogP(m), Lipinski.NumHDonors(m),
            Lipinski.NumHAcceptors(m), Descriptors.TPSA(m),
            Descriptors.NumRotatableBonds(m), Descriptors.NumAromaticRings(m),
            Descriptors.HeavyAtomCount(m)]
    fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=512)
    feat = np.concatenate([np.array(desc), np.array(fp)])
    p_logkp = float(d["model"].predict(feat.reshape(1, -1))[0])
    return {"tool": "logkp_predict", "smiles": smiles,
            "log_kp_cm_h": round(p_logkp, 2),
            "topical_suitability": "good" if p_logkp >= -2 else
                                    ("medium" if p_logkp >= -4 else "poor")}


def _t2_bayesian_sar() -> dict:
    return {"instruction": "scripts/run_bayesian_sar.py — EMB-3 SAR 다음 라운드 추천"}


def _t2_esm2_embedding(sequence: str) -> dict:
    from ..proteomics.esm3_adapter import get_protein_embedding
    r = get_protein_embedding(sequence, "esm2-650m")
    return {"tool": "esm2_embedding",
            "embedding_dim": len(r.embedding) if r.embedding else 0,
            "metadata": r.metadata}


def _t3_qmmm_abfe() -> dict:
    from ..md.qmmm_abfe import EMB3_CORRECTION_ESTIMATE
    return {"tool": "qmmm_abfe", "emb3_correction": EMB3_CORRECTION_ESTIMATE}


def _t4_chou_talalay(drugs: list, doses: list, observed_fa: float = 0.45) -> dict:
    from ..synergy.chou_talalay import (fit_median_effect, evaluate_combination,
                                          evaluate_recover_jaungo_emb3)
    if not drugs:
        # default Recover 자운고 + EMB-3 PBPK
        return evaluate_recover_jaungo_emb3()
    return {"tool": "chou_talalay", "instruction": "drugs[i].smiles + doses[i] 입력"}


def _t4_residence_time() -> dict:
    from ..kinetics.residence_time import compare_emb3_vs_embelin_protocol
    return compare_emb3_vs_embelin_protocol()


def _t4_enamine_real_match(query_smiles: list = None) -> dict:
    from ..screening.enamine_real import estimate_screening_cost_and_time
    return estimate_screening_cost_and_time(1_000_000)


def _t5_causal_inference() -> dict:
    from ..causal.rwe_inference import run_emb3_causal_analysis
    return run_emb3_causal_analysis()


def _t5_fibroblast_subtype(markers: dict = None, patient_id: str = "") -> dict:
    from ..stratification.fibroblast_subtype import classify_from_markers
    if markers is None:
        markers = {"COL6A5": 1.0, "MGP": -0.5}  # demo
    return classify_from_markers(markers, patient_id).__dict__


def _t5_microbiome(rel_abund: dict = None, shannon: float = 1.5,
                     patient_id: str = "") -> dict:
    from ..microbiome.skin_microbiome import analyze_patient_microbiome
    if rel_abund is None:
        rel_abund = {"Cutibacterium_acnes": 0.4, "Staphylococcus_epidermidis": 0.25}
    p = analyze_patient_microbiome(rel_abund, shannon, patient_id)
    return p.__dict__


def _t6_korean_pgx(patient_alleles: dict = None, drug_name: str = "EMB-3") -> dict:
    from ..pharmacogenomics.korean_pgx import (
        evaluate_topical_drug_compatibility, korean_pgx_population_summary,
    )
    if patient_alleles is None:
        return korean_pgx_population_summary()
    return evaluate_topical_drug_compatibility(patient_alleles, drug_name)


def _t6_mitochondrial() -> dict:
    from ..mitochondria.mito_targets import emb3_mito_hypothesis, MITO_TARGETS
    return {"n_targets": len(MITO_TARGETS),
            "hypothesis": emb3_mito_hypothesis()}


def _t6_cellchat() -> dict:
    from ..cellcomm.cellchat_adapter import estimate_emb3_lr_impact
    return estimate_emb3_lr_impact()


def _t7_epigenetic() -> dict:
    from ..epigenetics.epigenetic_targets import emb3_epigenetic_hypothesis
    return emb3_epigenetic_hypothesis()


def _t7_nlrp3() -> dict:
    from ..inflammasome.nlrp3_targets import predict_emb3_hwang_ryun_synergy
    return predict_emb3_hwang_ryun_synergy().__dict__


def _t7_prohyp_triple() -> dict:
    from ..peptides.prohyp_synergy import (
        RECOVER_TRIPLE_FORMULATIONS, predict_synergy_chou_talalay,
    )
    return {
        "formulations": [f.__dict__ for f in RECOVER_TRIPLE_FORMULATIONS],
        "synergy": predict_synergy_chou_talalay(),
    }


def _t8_tripod_check(manuscript_path: str) -> dict:
    from ..reporting_quality.tripod_ai import check_manuscript_tripod_ai
    r = check_manuscript_tripod_ai(manuscript_path)
    return {"summary": r.summary, "pass_rate": r.pass_rate,
            "n_passed": r.n_passed, "suggestions": r.suggestions[:5]}


def _t8_xai_explain(compound: str = "EMB-3", context: str = "scar",
                      smiles: str = "", endpoint: str = "hERG") -> dict:
    from ..explainability.xai_tools import (
        explain_compound_recommendation, explain_admet_prediction,
    )
    if smiles:
        r = explain_admet_prediction(smiles, endpoint)
    else:
        r = explain_compound_recommendation(compound, context)
    return {"explanation": r.natural_language_explanation,
            "method": r.method, "top_features": r.top_features[:5]}


def _t8_donguibogam(query: str = "흉터") -> dict:
    from ..ethnobotany.donguibogam_miner import search_donguibogam_for_disease
    return search_donguibogam_for_disease(query).__dict__


def _t8_dq_hair() -> dict:
    from ..senolytics.dq_hair_module import (
        evaluate_dq_emb3_combination, recover_alopecia_protocol,
    )
    return {"combination": evaluate_dq_emb3_combination().__dict__,
            "recover_protocol": recover_alopecia_protocol()}


def _t8_hira_qaly(drug_name: str = "EMB-3", drug_a: str = "",
                    drug_b: str = "") -> dict:
    from ..health_economics.hira_qaly import (
        estimate_hira_reimbursement, calculate_icer,
    )
    if drug_a and drug_b:
        return calculate_icer(drug_a, drug_b)
    return estimate_hira_reimbursement(drug_name).__dict__


# ═══════════════════════════════════════════════════════════════════════════
# 통합 도구 카탈로그 — 자연어 호출 매핑
# ═══════════════════════════════════════════════════════════════════════════


ALL_TIERS_TOOLS: list[Tool] = [
    # Tier 2 (6)
    Tool("panderm_skin_diagnosis",
          "PanDerm 피부 사진 분류 + 5질환 진단 + Recover 한약 처방 추천",
          {"type": "object",
           "properties": {"image_path": {"type": "string"},
                          "diagnosis": {"type": "string"}}},
          _t2_panderm),
    Tool("logkp_predict",
          "외용제 logKp (skin permeability cm/h) 예측 + 외용 적합성 평가",
          {"type": "object",
           "properties": {"smiles": {"type": "string"}},
           "required": ["smiles"]},
          _t2_logkp),
    Tool("bayesian_sar_recommend",
          "EMB-3 SAR 다음 라운드 합성 후보 자동 추천 (BATCHIE-style)",
          {"type": "object", "properties": {}},
          _t2_bayesian_sar),
    Tool("esm2_protein_embedding",
          "단백질 sequence → ESM2-650M 1280-d embedding (cross-target 유사도)",
          {"type": "object",
           "properties": {"sequence": {"type": "string"}},
           "required": ["sequence"]},
          _t2_esm2_embedding),
    # Tier 3 (5 — cofold prep, network already in chemcrow base)
    Tool("qmmm_abfe_correction",
          "ABFE에 QM/MM book-ending correction (chemical accuracy)",
          {"type": "object", "properties": {}},
          _t3_qmmm_abfe),
    # Tier 4 (5)
    Tool("chou_talalay_synergy",
          "약물 조합 Chou-Talalay CI 계산 (synergy/additive/antagonism)",
          {"type": "object",
           "properties": {"drugs": {"type": "array"},
                          "doses": {"type": "array"},
                          "observed_fa": {"type": "number"}}},
          _t4_chou_talalay),
    Tool("residence_time_md",
          "EMB-3 vs Embelin k_off + binding kinetics measurement",
          {"type": "object", "properties": {}},
          _t4_residence_time),
    Tool("enamine_real_screening",
          "29B Enamine REAL 1M subset Tanimoto match 비용/시간 추정",
          {"type": "object",
           "properties": {"query_smiles": {"type": "array"}}},
          _t4_enamine_real_match),
    # Tier 5 (5)
    Tool("causal_inference_rwe",
          "EMB-3 효과 causal estimation (PS matching + AIPW doubly robust)",
          {"type": "object", "properties": {}},
          _t5_causal_inference),
    Tool("fibroblast_subtype_classify",
          "환자 fibroblast subtype (papillary/reticular) → 자동 처방 추천",
          {"type": "object",
           "properties": {"markers": {"type": "object"},
                          "patient_id": {"type": "string"}}},
          _t5_fibroblast_subtype),
    Tool("skin_microbiome_analysis",
          "환자 16S 결과 → dysbiosis pattern → 한약 처방 자동",
          {"type": "object",
           "properties": {"rel_abund": {"type": "object"},
                          "shannon": {"type": "number"},
                          "patient_id": {"type": "string"}}},
          _t5_microbiome),
    # Tier 6 (3 + smartphone/OliX docs)
    Tool("korean_pgx_panel",
          "한국 PGx 변이 → EMB-3 metabolism 예측 + SCAR 위험",
          {"type": "object",
           "properties": {"patient_alleles": {"type": "object"},
                          "drug_name": {"type": "string"}}},
          _t6_korean_pgx),
    Tool("mitochondrial_targets",
          "PGC-1α/TFAM/NRF1/NRF2 mitochondrial axis cofold + EMB-3 dual-action 가설",
          {"type": "object", "properties": {}},
          _t6_mitochondrial),
    Tool("cellchat_lr_pairs",
          "CellChat 흉터 niche LR pair → EMB-3 직접 차단 매핑",
          {"type": "object", "properties": {}},
          _t6_cellchat),
    # Tier 7 (3 + 2 docs)
    Tool("epigenetic_targets",
          "EZH2/G9a/DNMT/TET/HDAC epigenetic targets + EMB-3 quinone 가설",
          {"type": "object", "properties": {}},
          _t7_epigenetic),
    Tool("nlrp3_inflammasome",
          "NLRP3 + 황련해독탕 + EMB-3 combination CI synergy",
          {"type": "object", "properties": {}},
          _t7_nlrp3),
    Tool("prohyp_triple_combination",
          "Pro-Hyp + EMB-3 + 자운고 triple formulation (위축/비후)",
          {"type": "object", "properties": {}},
          _t7_prohyp_triple),
    # Tier 8 (5 — 본 라운드)
    Tool("tripod_ai_check",
          "Manuscript TRIPOD+AI 27-item compliance 자동 점검",
          {"type": "object",
           "properties": {"manuscript_path": {"type": "string"}},
           "required": ["manuscript_path"]},
          _t8_tripod_check),
    Tool("xai_explain_decision",
          "결정 이유 SHAP/Grad-CAM 자연어 설명 (의사·환자 신뢰)",
          {"type": "object",
           "properties": {"compound": {"type": "string"},
                          "context": {"type": "string"},
                          "smiles": {"type": "string"},
                          "endpoint": {"type": "string"}}},
          _t8_xai_explain),
    Tool("donguibogam_search",
          "동의보감에서 질환 keyword 매칭 약재 + 분자 검색",
          {"type": "object",
           "properties": {"query": {"type": "string"}},
           "required": ["query"]},
          _t8_donguibogam),
    Tool("dq_senolytic_hair",
          "Dasatinib + Quercetin + EMB-3 모낭 회복 combination + Recover 탈모 protocol",
          {"type": "object", "properties": {}},
          _t8_dq_hair),
    Tool("hira_qaly_estimate",
          "한국 HIRA 보험 수가 + QALY ICER 추정 (vs Pirfenidone 등)",
          {"type": "object",
           "properties": {"drug_name": {"type": "string"},
                          "drug_a": {"type": "string"},
                          "drug_b": {"type": "string"}}},
          _t8_hira_qaly),
]
