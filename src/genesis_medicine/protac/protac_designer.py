"""PROTAC designer — EMB-3 TGFB1 degrader 자동 디자인.

JMC 2025 + Springer 2026:
  - PROTAC = warhead (target binder) + linker + E3 ligase ligand
  - Topical PROTAC delivery 가능성 검증
  - ETTAC-2 LRG1 degrader for renal fibrosis
  - BRD4 PROTAC for cardiac fibrosis (EndMT)

Genesis_Medicine v3 + Recover:
  - EMB-3 warhead (TGFB1 ABFE -32.9 kcal/mol) + linker + VHL/Cereblon ligand
  - 외용 가능한 PROTAC (작은 분자 < 800 Da, lipophilic)
  - 신호 차단보다 단백질 자체 제거 → 더 강력
  - Paper 가치: "First quinone-scaffold TGFB1 PROTAC"

자연어 호출:
  "EMB-3를 TGFB1 PROTAC으로 디자인해줘"
  → design_protac(warhead_smiles="...", target="TGFB1", e3_ligase="VHL")
"""

from __future__ import annotations

from dataclasses import dataclass, field


# E3 ligase ligands (PROTAC 표준)
E3_LIGASE_LIGANDS = {
    "VHL": {
        "ligand_smiles": "CC(C)(C)C(=O)N[C@@H](C(C)C)C(=O)N1C[C@@H](O)C[C@H]1C(=O)NCc1ccc(-c2ncccs2)cc1",
        "mw": 425,
        "logp_estimate": 2.3,
        "topical_compatible": True,
        "expression": "broadly expressed (kidney high)",
        "best_use": "fibroblast targeted PROTAC",
    },
    "CRBN": {
        "ligand_smiles": "O=C1CCC(=O)N1c1ccc2c(c1)C(=O)NC2=O",
        "mw": 273,
        "logp_estimate": 0.5,
        "topical_compatible": True,
        "expression": "broadly expressed",
        "best_use": "general targeted degradation",
        "warning": "thalidomide derivative — teratogenic, 외용 시 임산부 금기",
    },
    "MDM2": {
        "ligand_smiles": "(complex Nutlin-3 derivative)",
        "topical_compatible": False,   # 너무 커서 외용 어려움
    },
    "IAP": {
        "ligand_smiles": "(LCL161 derivative)",
        "topical_compatible": True,
    },
}


# Linker types (PROTAC chemistry)
LINKER_TYPES = {
    "PEG3": {"smiles_template": "OCCOCCOCC", "length_atoms": 9,
              "flexibility": "high", "ligEff_score": 0.7},
    "PEG6": {"smiles_template": "OCCOCCOCCOCCOCCOCC", "length_atoms": 18,
              "flexibility": "very_high", "ligEff_score": 0.6},
    "alkyl_C5": {"smiles_template": "CCCCC", "length_atoms": 5,
                  "flexibility": "low", "ligEff_score": 0.8},
    "alkyl_C8": {"smiles_template": "CCCCCCCC", "length_atoms": 8,
                  "flexibility": "moderate", "ligEff_score": 0.75},
    "triazole": {"smiles_template": "Cn1cc(C)nn1", "length_atoms": 5,
                  "flexibility": "low", "ligEff_score": 0.85,
                  "advantage": "click chemistry, rigid"},
    "amide_PEG2": {"smiles_template": "C(=O)NCCOCC", "length_atoms": 8,
                    "ligEff_score": 0.78},
}


@dataclass
class PROTACDesign:
    """단일 PROTAC 디자인."""

    name: str = ""
    warhead: dict = field(default_factory=dict)        # EMB-3 등 target binder
    linker: dict = field(default_factory=dict)
    e3_ligase: dict = field(default_factory=dict)
    full_smiles: str = ""                                # 추정 (linker 연결)
    estimated_mw: float = 0
    estimated_logp: float = 0
    topical_compatible: bool = False
    safety_flags: list = field(default_factory=list)
    natural_language_summary: str = ""


def design_protac(
    warhead_smiles: str = "CCCCCC1=C(O)C(=O)C(O)=C(C)C1=O",  # EMB-3
    warhead_name: str = "EMB-3",
    target: str = "TGFB1",
    e3_ligase: str = "VHL",
    linker_type: str = "alkyl_C5",
) -> PROTACDesign:
    """EMB-3 + linker + E3 ligase = TGFB1 degrader 자동 조립 (자연어 호출).

    실제 PROTAC 합성은 별도 (5-10 단계). 본 함수는 design + property 추정.
    """
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import Descriptors, Crippen
        RDLogger.DisableLog("rdApp.*")
    except ImportError:
        return PROTACDesign(
            name=f"{warhead_name}-{linker_type}-{e3_ligase}",
            natural_language_summary="❌ rdkit 필요",
        )

    # Property 추정 (실제 합성 후 정확도 ↑)
    warhead_mol = Chem.MolFromSmiles(warhead_smiles)
    warhead_mw = Descriptors.MolWt(warhead_mol) if warhead_mol else 0
    warhead_logp = Crippen.MolLogP(warhead_mol) if warhead_mol else 0

    e3 = E3_LIGASE_LIGANDS.get(e3_ligase)
    if e3 is None:
        return PROTACDesign(natural_language_summary=f"❌ E3 {e3_ligase} 미등록")

    linker = LINKER_TYPES.get(linker_type)
    if linker is None:
        return PROTACDesign(natural_language_summary=f"❌ Linker {linker_type} 미등록")

    # 추정 properties
    total_mw = warhead_mw + e3.get("mw", 400) + linker["length_atoms"] * 14
    total_logp = warhead_logp + e3.get("logp_estimate", 2.5) + 0.5

    # Topical compatibility 기준
    topical = (total_mw < 900 and 1.5 < total_logp < 5.0
                and e3.get("topical_compatible", False))

    safety = []
    if e3_ligase == "CRBN":
        safety.append("⚠️ CRBN ligand thalidomide 유래 — 임산부 금기")
    if total_mw > 900:
        safety.append("⚠️ MW > 900 — 외용 흡수 한계")
    if total_logp > 5:
        safety.append("⚠️ logP > 5 — 외용 자극 + bioavailability 한계")

    nl = (
        f"**PROTAC 디자인: {warhead_name}-{linker_type}-{e3_ligase}** ({target} degrader)\n\n"
        f"**조립**:\n"
        f"  Warhead: {warhead_name} (MW {warhead_mw:.0f}, logP {warhead_logp:.2f})\n"
        f"  Linker: {linker_type} ({linker['length_atoms']} atoms, "
        f"flex {linker.get('flexibility', '?')})\n"
        f"  E3 ligand: {e3_ligase} ({e3.get('best_use', '')})\n\n"
        f"**추정 properties**:\n"
        f"  MW total: {total_mw:.0f}\n"
        f"  logP total: {total_logp:.2f}\n"
        f"  외용 적합: {'✅' if topical else '❌'}\n"
    )
    if safety:
        nl += f"\n**경고**: {', '.join(safety)}\n"
    nl += (
        f"\n**다음 단계**:\n"
        f"  1. 합성 경로 자동 제안 (T1 DeepRetro 호출)\n"
        f"  2. ABFE 정량 (TGFB1 degradation efficiency)\n"
        f"  3. In vitro PROTAC 검증 (HEK293 + TGFB1-luciferase)\n"
        f"  4. 한국 CRO 합성 ₩30-50M, 8-12주\n"
        f"\n**Paper 가치**: 'First quinone-scaffold TGFB1 PROTAC for fibrosis' "
        f"— Nat Comm Chem tier 가능"
    )

    return PROTACDesign(
        name=f"{warhead_name}-{linker_type}-{e3_ligase}",
        warhead={"name": warhead_name, "smiles": warhead_smiles,
                  "mw": warhead_mw, "logp": warhead_logp},
        linker={"type": linker_type, **linker},
        e3_ligase={"name": e3_ligase, **e3},
        estimated_mw=total_mw, estimated_logp=total_logp,
        topical_compatible=topical, safety_flags=safety,
        natural_language_summary=nl,
    )


def evaluate_protac_panel() -> dict:
    """EMB-3 + 6 linker × 3 E3 ligase = 18 PROTAC 후보 panel 평가."""
    panel = []
    for linker in ["PEG3", "alkyl_C5", "alkyl_C8", "triazole", "amide_PEG2"]:
        for e3 in ["VHL", "CRBN"]:
            d = design_protac(linker_type=linker, e3_ligase=e3)
            panel.append({
                "name": d.name,
                "mw": d.estimated_mw,
                "logp": d.estimated_logp,
                "topical": d.topical_compatible,
                "warnings": len(d.safety_flags),
            })
    panel.sort(key=lambda x: (-x["topical"], x["warnings"], x["mw"]))
    return {
        "total_candidates": len(panel),
        "top_5": panel[:5],
        "summary": (
            f"EMB-3 PROTAC panel 평가 — top 외용 적합 후보 {sum(1 for p in panel if p['topical'])} "
            f"개 / 전체 {len(panel)}"
        ),
        "next_action": (
            "Top 3 → 한국 CRO 합성 + ABFE × Boltz-2 cofold 추가 검증"
        ),
    }
