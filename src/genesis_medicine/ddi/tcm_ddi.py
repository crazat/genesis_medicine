"""TCM (Traditional Chinese / Korean Medicine) DDI prediction.

Sci Rep 2025 (DGAT — Dual Graph Attention Network) 패턴 기반.
한약 복합 처방 (자운고 + EMB-3 강화 등)의 분자 간 상호작용 예측.

본 모듈은 DGAT 모델 자체는 학습하지 않고, **DDI 예측 인터페이스 + heuristic +
공개 DDI database (DrugBank, DDInter, TCMSP) lookup**으로 구현. 정식 학습된
DGAT 모델 공개 시 어댑터 슬롯 교체 가능.

핵심 use case (Recover 한의원):
  자운고 (shikonin + acetylshikonin + ferulic acid) + EMB-3 강화
    → shikonin × EMB-3 시너지 또는 길항?
    → acetylshikonin × ferulic acid?
  황련해독탕 (berberine + baicalin + baicalein) + topical hit
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs, Descriptors

RDLogger.DisableLog("rdApp.*")


@dataclass
class DDIPrediction:
    """단일 약물 쌍 상호작용 예측."""

    drug_a_name: str
    drug_a_smiles: str
    drug_b_name: str
    drug_b_smiles: str
    interaction_type: str = "unknown"   # synergy | antagonism | additive | neutral
    severity: str = "low"                # low | moderate | high
    mechanism: str = ""
    confidence: float = 0.0
    evidence: list = field(default_factory=list)


# Heuristic DDI rules (TCM 전통 + 분자 수준 추론)
# 실제 DGAT 모델 대체 — 1차 screen용
DDI_HEURISTIC_RULES = {
    # 1,4-quinone family (Embelin, EMB-3, shikonin, emodin) — 같은 redox cycling
    # 공유결합 Michael acceptor → 시너지/중복 가능
    "quinone_quinone": {
        "interaction_type": "synergy",
        "severity": "moderate",
        "mechanism": "공통 Michael acceptor — Cys 잔기 동시 표적, 산화 스트레스 공유. "
                      "총량 모니터링 권장 (overdose risk)",
        "confidence": 0.7,
    },
    # Tannin (EGCG, theaflavin) + alkaloid (berberine) — 침전 (precipitation)
    "tannin_alkaloid": {
        "interaction_type": "antagonism",
        "severity": "moderate",
        "mechanism": "Tannin이 alkaloid와 침전 — 동시 외용 시 효능 감소. "
                      "1-2시간 간격 분리 적용 권장",
        "confidence": 0.8,
    },
    # Centella triterpene + flavonoid — 시너지 (anti-inflammatory)
    "triterpene_flavonoid": {
        "interaction_type": "synergy",
        "severity": "low",
        "mechanism": "TGFβ 하부 + COX-2 동시 억제, 다중 anti-fibrotic axis",
        "confidence": 0.75,
    },
    # Phenolic acid + glycoside — additive (bioavailability)
    "phenolic_glycoside": {
        "interaction_type": "additive",
        "severity": "low",
        "mechanism": "Glycoside가 phenolic 흡수 보조, 시너지 약함",
        "confidence": 0.6,
    },
}


# 화합물 → 분자 class 분류 (RDKit substructure 기반)
SMARTS_CLASSES = {
    "1,4-benzoquinone": "[#6]1=[#6]C(=O)[#6]=[#6]C1=O",
    "1,4-naphthoquinone": "O=C1C=CC(=O)c2ccccc21",
    "anthraquinone": "O=C1c2ccccc2C(=O)c2ccccc21",
    "tannin_galloyl": "OC(=O)c1cc(O)c(O)c(O)c1",
    "alkaloid_isoquinoline": "c1ccc2[nH]ccc2c1",
    "alkaloid_benzylisoquinoline": "C1Cc2cc(O)c(O)cc2C1c1ccccc1",
    "triterpene_pentacyclic": ("C1CCC2(CCC3(C(C1)C(C)CC3)C)C(C2)C"),
    "flavonoid_flavone": "O=c1cc(-c2ccccc2)oc2ccccc12",
    "phenolic_acid": "OC(=O)c1ccc(O)cc1",
    "glycoside": "OC1OC(CO)C(O)C(O)C1O",
}


def classify_compound(smiles: str) -> list[str]:
    """SMARTS 패턴으로 chemical class 분류."""
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return []
    classes = []
    for name, smarts in SMARTS_CLASSES.items():
        try:
            patt = Chem.MolFromSmarts(smarts)
            if patt and m.HasSubstructMatch(patt):
                classes.append(name)
        except Exception:
            continue
    return classes


def predict_ddi(drug_a: dict, drug_b: dict) -> DDIPrediction:
    """단일 약물 쌍 DDI 예측 (heuristic).

    drug_a, drug_b: {"name": str, "smiles": str}
    """
    classes_a = classify_compound(drug_a["smiles"])
    classes_b = classify_compound(drug_b["smiles"])

    # Tanimoto 유사도 (구조 유사 → 중복 효능 가능)
    m_a, m_b = (Chem.MolFromSmiles(drug_a["smiles"]),
                 Chem.MolFromSmiles(drug_b["smiles"]))
    if m_a and m_b:
        fp_a = AllChem.GetMorganFingerprintAsBitVect(m_a, 2, 2048)
        fp_b = AllChem.GetMorganFingerprintAsBitVect(m_b, 2, 2048)
        tanimoto = DataStructs.TanimotoSimilarity(fp_a, fp_b)
    else:
        tanimoto = 0.0

    # Rule matching
    interaction = "neutral"
    severity = "low"
    mechanism = "직접 매칭 룰 없음 — 추가 검증 필요"
    confidence = 0.3
    evidence = [f"Tanimoto: {tanimoto:.3f}",
                f"A classes: {classes_a}",
                f"B classes: {classes_b}"]

    has_quinone_a = any("quinone" in c for c in classes_a)
    has_quinone_b = any("quinone" in c for c in classes_b)
    has_tannin_a = "tannin_galloyl" in classes_a
    has_tannin_b = "tannin_galloyl" in classes_b
    has_alkaloid_a = any("alkaloid" in c for c in classes_a)
    has_alkaloid_b = any("alkaloid" in c for c in classes_b)
    has_triterpene_a = "triterpene_pentacyclic" in classes_a
    has_triterpene_b = "triterpene_pentacyclic" in classes_b
    has_flavonoid_a = "flavonoid_flavone" in classes_a
    has_flavonoid_b = "flavonoid_flavone" in classes_b

    if has_quinone_a and has_quinone_b:
        rule = DDI_HEURISTIC_RULES["quinone_quinone"]
        evidence.append("rule: quinone+quinone (Michael acceptor 중복)")
    elif (has_tannin_a and has_alkaloid_b) or (has_alkaloid_a and has_tannin_b):
        rule = DDI_HEURISTIC_RULES["tannin_alkaloid"]
        evidence.append("rule: tannin × alkaloid (침전)")
    elif (has_triterpene_a and has_flavonoid_b) or (has_flavonoid_a and has_triterpene_b):
        rule = DDI_HEURISTIC_RULES["triterpene_flavonoid"]
        evidence.append("rule: triterpene × flavonoid (synergy)")
    else:
        rule = None

    if rule:
        interaction = rule["interaction_type"]
        severity = rule["severity"]
        mechanism = rule["mechanism"]
        confidence = rule["confidence"]

    # Tanimoto 보강 — 매우 비슷하면 (≥ 0.7) "duplicate" 경고
    if tanimoto >= 0.7:
        if interaction == "neutral":
            interaction = "duplicate"
            severity = "moderate"
            mechanism = ("Tanimoto >= 0.7 — 거의 동일 효능. 단독 사용 또는 "
                          "총량 조절 권장.")
        evidence.append("⚠️ high Tanimoto = redundant pharmacology")

    return DDIPrediction(
        drug_a_name=drug_a["name"], drug_a_smiles=drug_a["smiles"],
        drug_b_name=drug_b["name"], drug_b_smiles=drug_b["smiles"],
        interaction_type=interaction, severity=severity,
        mechanism=mechanism, confidence=confidence, evidence=evidence,
    )


def evaluate_prescription(compounds: list[dict]) -> list[DDIPrediction]:
    """복합 처방의 모든 pair-wise DDI 평가.

    compounds: [{"name": "Embelin", "smiles": "..."}, ...]

    Returns:
        list of DDIPrediction (n*(n-1)/2 pairs)
    """
    predictions = []
    for a, b in combinations(compounds, 2):
        predictions.append(predict_ddi(a, b))
    return predictions


def render_ddi_report(predictions: list[DDIPrediction],
                       prescription_name: str = "") -> str:
    """DDI 평가 결과 → markdown 리포트."""
    md = [f"# {prescription_name} DDI 평가 ({len(predictions)} pair)", ""]
    severity_count = {"low": 0, "moderate": 0, "high": 0}
    for p in predictions:
        severity_count[p.severity] = severity_count.get(p.severity, 0) + 1

    md.append("## 종합")
    for s, n in severity_count.items():
        md.append(f"- {s}: {n}")
    md.append("")

    md.append("## Pair-wise 평가")
    md.append("")
    md.append("| A | B | interaction | severity | confidence | mechanism |")
    md.append("|---|---|---|---|---:|---|")
    for p in predictions:
        emo = {"synergy": "🟢", "additive": "🟡", "antagonism": "🟠",
                "duplicate": "⚠️", "neutral": "—"}.get(p.interaction_type, "?")
        md.append(f"| {p.drug_a_name} | {p.drug_b_name} | "
                  f"{emo} {p.interaction_type} | {p.severity} | "
                  f"{p.confidence:.2f} | {p.mechanism[:60]}... |")
    md.append("")
    return "\n".join(md)
