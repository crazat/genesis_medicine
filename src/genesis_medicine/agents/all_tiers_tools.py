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
    # ★ facial_dx integration (별도 프로젝트 C:\Projects\facial_dx)
    Tool("facial_dx_status",
          "facial_dx 진단 엔진 (3D Morpheus + iPhone TrueDepth) 가용성 확인",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.integration.facial_dx_bridge",
              fromlist=["is_facial_dx_available"]).is_facial_dx_available()),
    Tool("facial_dx_fetch_analysis",
          "facial_dx에서 환자 3D 분석 결과 가져오기 (asymmetry/landmarks/zones)",
          {"type": "object",
           "properties": {"patient_id": {"type": "string"},
                          "test_sprint": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.integration.facial_dx_bridge",
              fromlist=["fetch_facial_dx_analysis"]
              ).fetch_facial_dx_analysis(**kw).__dict__),
    Tool("integrated_treatment_plan",
          "facial_dx 결과 + Genesis_Medicine 분자 처방 통합 시술 plan (Recover 환자 동선)",
          {"type": "object",
           "properties": {"facial_dx_result": {"type": "object"},
                          "scar_diagnosis": {"type": "string"},
                          "patient_skin_type": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.integration.facial_dx_bridge",
              fromlist=["integrated_treatment_plan"]
              ).integrated_treatment_plan(**kw).__dict__),
    Tool("recover_patient_workflow",
          "Recover 한의원 환자 end-to-end 동선 (facial_dx 분석 → 분자 처방 → 시술 순서)",
          {"type": "object",
           "properties": {"test_sprint": {"type": "string"},
                          "scar_diagnosis": {"type": "string"},
                          "patient_id": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.integration.facial_dx_bridge",
              fromlist=["call_facial_dx_then_prescribe"]
              ).call_facial_dx_then_prescribe(**kw)),
    # Tier 9 (5 — PROTAC, chronotherapy, OCT bridge, syn-bio, ESG)
    Tool("design_protac_degrader",
          "EMB-3 PROTAC TGFB1 degrader 자동 디자인 (warhead+linker+E3)",
          {"type": "object",
           "properties": {"warhead_smiles": {"type": "string"},
                          "warhead_name": {"type": "string"},
                          "target": {"type": "string"},
                          "e3_ligase": {"type": "string"},
                          "linker_type": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.protac.protac_designer",
              fromlist=["design_protac"]).design_protac(**kw).__dict__),
    Tool("chronotherapy_schedule",
          "자오류주 + circadian medicine 시간대별 외용 schedule",
          {"type": "object",
           "properties": {"diagnosis": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.chronotherapy.jaoryuju",
              fromlist=["time_optimal_topical_schedule"]
              ).time_optimal_topical_schedule(**kw).__dict__),
    Tool("current_meridian",
          "현재 시간 활성 경락 (자오류주) — 시술 타이밍 권장",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.chronotherapy.jaoryuju",
              fromlist=["current_meridian_active"]
              ).current_meridian_active()),
    Tool("oct_skin_depth",
          "OCT cross-section 흉터 깊이 정량 → facial_dx 통합",
          {"type": "object",
           "properties": {"image_path": {"type": "string"},
                          "wavelength_nm": {"type": "integer"},
                          "facial_dx_zone": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.integration.oct_bridge",
              fromlist=["analyze_oct_skin_depth"]
              ).analyze_oct_skin_depth(**kw).__dict__),
    Tool("design_engineered_probiotic",
          "환자 자가 C. acnes engineering — anti-fibrotic/anti-acne/모낭",
          {"type": "object",
           "properties": {"patient_id": {"type": "string"},
                          "target_function": {"type": "string"},
                          "delivery_format": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.synbio.engineered_probiotic",
              fromlist=["design_engineered_probiotic"]
              ).design_engineered_probiotic(**kw).__dict__),
    Tool("esg_evaluation",
          "Genesis_Medicine + Recover ESG 평가 + 펀딩 매칭",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.sustainability.esg_analyzer",
              fromlist=["evaluate_esg_friendliness"]
              ).evaluate_esg_friendliness().__dict__),
    # ═══════════════════════════════════════════════════════════════════════
    # Tier 10 — Safety / MLOps / Knowledge Graph / Continual / Multi-omics
    # ═══════════════════════════════════════════════════════════════════════
    Tool("hallucination_check",
          "LLM output 환각/jailbreak 검증 (의료 fact citation 강제)",
          {"type": "object",
           "properties": {"text": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.safety.hallucination_guard",
              fromlist=["hallucination_check_natural"]
              ).hallucination_check_natural(**kw)),
    Tool("model_registry_list",
          "등록된 모델 버전 + baseline metric 조회 (FDA PCCP)",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.mlops.model_registry",
              fromlist=["list_models"]
              ).list_models()),
    Tool("model_registry_init",
          "Genesis_Medicine 핵심 모델 baseline 자동 등록 (Boltz-2/ADMET-AI/Chemprop 등)",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.mlops.model_registry",
              fromlist=["initialize_genesis_baseline"]
              ).initialize_genesis_baseline()),
    Tool("model_drift_detect",
          "model baseline 대비 drift 감지 (PCCP modification 트리거)",
          {"type": "object",
           "properties": {"model_name": {"type": "string"},
                          "new_metric_dict": {"type": "object"}}},
          lambda **kw: __import__(
              "genesis_medicine.mlops.model_registry",
              fromlist=["detect_drift"]
              ).detect_drift(**kw).__dict__),
    Tool("kg_path_query",
          "Knowledge Graph 경로 추론 (compound→target→disease)",
          {"type": "object",
           "properties": {"start": {"type": "string"},
                          "end": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.knowledge_graph.kg_completion",
              fromlist=["kg_path_query"]
              ).kg_path_query(**kw).__dict__),
    Tool("kg_shared_targets",
          "두 질환 공유 타겟 — cross-disease 분자 기반",
          {"type": "object",
           "properties": {"disease_a": {"type": "string"},
                          "disease_b": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.knowledge_graph.kg_completion",
              fromlist=["shared_targets"]
              ).shared_targets(**kw)),
    Tool("kg_repurposing_predict",
          "질환 → 화합물 재창출 ranking (sub-KG 기반)",
          {"type": "object",
           "properties": {"disease": {"type": "string"},
                          "top_k": {"type": "integer"}}},
          lambda **kw: __import__(
              "genesis_medicine.knowledge_graph.kg_completion",
              fromlist=["predict_repurposing_candidates"]
              ).predict_repurposing_candidates(**kw)),
    Tool("continual_forgetting_risk",
          "PA-EWC continual learning — 새 task 추가 시 forgetting 평가",
          {"type": "object",
           "properties": {"new_task": {"type": "string"},
                          "new_domain": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.continual.pa_ewc",
              fromlist=["estimate_forgetting_risk"]
              ).estimate_forgetting_risk(**kw).__dict__),
    Tool("continual_init_baseline",
          "현재 5 질환 task PA-EWC baseline 등록",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.continual.pa_ewc",
              fromlist=["initialize_genesis_baseline_tasks"]
              ).initialize_genesis_baseline_tasks()),
    Tool("multiomics_fuse",
          "환자 multi-omics (proteo+transcripto+metabolo+microbiome) 통합 → fibroblast subtype + EMB-3 반응 예측",
          {"type": "object",
           "properties": {"patient_id": {"type": "string"},
                          "proteomics": {"type": "object"},
                          "transcriptomics": {"type": "object"},
                          "metabolomics": {"type": "object"},
                          "skin_microbiome": {"type": "object"},
                          "strategy": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.omics.multiomics_fusion",
              fromlist=["fuse_patient_omics"]
              ).fuse_patient_omics(**kw).__dict__),
    Tool("multiomics_required_assays",
          "multi-omics fusion에 필요한 CRO assay 패키지 (₩645만/환자)",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.omics.multiomics_fusion",
              fromlist=["required_assays_for_fusion"]
              ).required_assays_for_fusion()),
    # ═══════════════════════════════════════════════════════════════════════
    # Tier 11 — NaFM / Bayesian Trial / Patent / SkinAge / Chai-1 / JUMP-CP
    # ═══════════════════════════════════════════════════════════════════════
    Tool("nafm_embedding",
          "NaFM (NP foundation model) 임베딩 추출 — 한약 천연물 정밀도 +14%",
          {"type": "object",
           "properties": {"smiles": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.foundation.nafm_loader",
              fromlist=["get_np_embedding"]
              ).get_np_embedding(**kw).__dict__),
    Tool("nafm_finetune_guide",
          "NaFM fine-tune 가이드 (target별 +14% AUROC 추정)",
          {"type": "object",
           "properties": {"target": {"type": "string"},
                          "training_csv": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.foundation.nafm_loader",
              fromlist=["fine_tune_for_skin_targets"]
              ).fine_tune_for_skin_targets(**kw)),
    Tool("nafm_screen_nps",
          "한약 NP library NaFM 임베딩 스크리닝",
          {"type": "object",
           "properties": {"target": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.foundation.nafm_loader",
              fromlist=["screen_natural_products"]
              ).screen_natural_products(**kw)),
    Tool("bayesian_trial_design",
          "외용제 Bayesian adaptive trial 설계 (Recover IRB 자료)",
          {"type": "object",
           "properties": {"drug_name": {"type": "string"},
                          "n_total": {"type": "integer"},
                          "primary_endpoint": {"type": "string"},
                          "success_threshold": {"type": "number"}}},
          lambda **kw: __import__(
              "genesis_medicine.trial_design.bayesian_adaptive",
              fromlist=["design_adaptive_topical_trial"]
              ).design_adaptive_topical_trial(**kw).__dict__),
    Tool("n_of_1_design",
          "n-of-1 trial 한약 personalization (ABA-BAB cross-over)",
          {"type": "object",
           "properties": {"patient_id": {"type": "string"},
                          "primary_endpoint": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.trial_design.bayesian_adaptive",
              fromlist=["design_n_of_1_herbal"]
              ).design_n_of_1_herbal(**kw).__dict__),
    Tool("mfds_dtx_check",
          "MFDS 2025 DTx pathway 적합성 점검",
          {"type": "object",
           "properties": {"product_class": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.trial_design.bayesian_adaptive",
              fromlist=["mfds_dtx_pathway_check"]
              ).mfds_dtx_pathway_check(**kw)),
    Tool("prior_art_search",
          "EMB-3 prior-art 자동 검색 (KIPRIS + USPTO)",
          {"type": "object",
           "properties": {"compound_name": {"type": "string"},
                          "smiles": {"type": "string"},
                          "scaffold_class": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.ip.prior_art",
              fromlist=["search_prior_art"]
              ).search_prior_art(**kw)),
    Tool("freedom_to_operate",
          "Freedom-to-Operate 평가 (출원 전 필수)",
          {"type": "object",
           "properties": {"compound_name": {"type": "string"},
                          "smiles": {"type": "string"},
                          "scaffold_class": {"type": "string"},
                          "intended_indication": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.ip.prior_art",
              fromlist=["freedom_to_operate"]
              ).freedom_to_operate(**kw).__dict__),
    Tool("patent_drafting_suggestions",
          "EMB-3 청구항 layered strategy + PCT 진입 가이드",
          {"type": "object",
           "properties": {"compound_name": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.ip.prior_art",
              fromlist=["patent_drafting_suggestions"]
              ).patent_drafting_suggestions(**kw)),
    Tool("skin_age_predict",
          "안면 RGB → biological skin age (Recover 회춘 점수 KPI)",
          {"type": "object",
           "properties": {"chronological_age": {"type": "number"},
                          "fitzpatrick_type": {"type": "integer"},
                          "pore_density_per_cm2": {"type": "number"},
                          "pigment_lesion_area_pct": {"type": "number"},
                          "wrinkle_depth_mm": {"type": "number"},
                          "wrinkle_count": {"type": "integer"},
                          "spf_lifetime_use_pct": {"type": "number"}}},
          lambda **kw: __import__(
              "genesis_medicine.aging.skin_age_clock",
              fromlist=["predict_skin_age"]
              ).predict_skin_age(**kw).__dict__),
    Tool("dnam_panel_design",
          "DNAm 391-CpG skin clock 패널 설계 (Recover 시술 정량)",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.aging.skin_age_clock",
              fromlist=["design_dnam_panel"]
              ).design_dnam_panel()),
    Tool("emb3_anti_aging",
          "EMB-3 anti-aging 효과 정량 예측 (회춘 점수 마케팅 자료)",
          {"type": "object",
           "properties": {"emb3_baseline_response": {"type": "number"}}},
          lambda **kw: __import__(
              "genesis_medicine.aging.skin_age_clock",
              fromlist=["emb3_anti_aging_prediction"]
              ).emb3_anti_aging_prediction(**kw)),
    Tool("chai1_cofold",
          "Chai-1 cofold (Apache-2.0) — Boltz-2 ensemble 3rd member",
          {"type": "object",
           "properties": {"target_sequence": {"type": "string"},
                          "ligand_smiles": {"type": "string"},
                          "msa_path": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.structure.chai1_ensemble",
              fromlist=["chai1_cofold"]
              ).chai1_cofold(**kw).__dict__),
    Tool("ensemble_consensus",
          "Boltz-2 + Protenix + Chai-1 3-way consensus affinity (+6% accuracy)",
          {"type": "object",
           "properties": {"target": {"type": "string"},
                          "compound": {"type": "string"},
                          "boltz2_affinity": {"type": "number"},
                          "protenix_affinity": {"type": "number"},
                          "chai1_affinity": {"type": "number"}}},
          lambda **kw: __import__(
              "genesis_medicine.structure.chai1_ensemble",
              fromlist=["ensemble_consensus"]
              ).ensemble_consensus(**kw).__dict__),
    Tool("morphology_predict",
          "JUMP-CP morphology profile 예측 (off-target detection)",
          {"type": "object",
           "properties": {"compound": {"type": "string"},
                          "smiles": {"type": "string"},
                          "target_class": {"type": "string"}}},
          lambda **kw: __import__(
              "genesis_medicine.phenotypic.jump_cp",
              fromlist=["predict_morphology"]
              ).predict_morphology(**kw).__dict__),
    Tool("morphology_screen_nps",
          "한약 NP 30종 cell painting 스크리닝",
          {"type": "object", "properties": {}},
          lambda **kw: __import__(
              "genesis_medicine.phenotypic.jump_cp",
              fromlist=["screen_natural_products_morphology"]
              ).screen_natural_products_morphology()),
]
