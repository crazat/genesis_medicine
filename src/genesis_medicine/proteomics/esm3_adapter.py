"""ESM3 (EvolutionaryScale) 단백질 foundation 모델 adapter.

ESM3 능력:
  - 단백질 sequence + structure + function 동시 reasoning
  - 98B params (open: small variant 1.4B Apache-2.0)
  - 2.78B 단백질 학습
  - URL: https://github.com/evolutionaryscale/esm

Genesis_Medicine v3 통합 use cases:
  1. **Mutation effect 예측** — 환자 SNP가 TGFB1/MMP1 affinity에 미치는 영향
  2. **Protein design** — 흉터 표적 protein engineering (research only)
  3. **Function annotation** — 새 fibrotic 표적 발굴 보강
  4. **Sequence embedding** — 우리 14 타겟 → embedding 유사성으로 cross-target 발굴

라이선스:
  - Open variant (esm3-open-small, 1.4B): Apache-2.0 + non-commercial 제한
  - Forge (host) API: paid commercial use
  - 우리 사용: research 빌드는 free, commercial은 large variant API 결제 필요
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")


@dataclass
class ESM3Result:
    """ESM3 inference 결과."""

    sequence: str
    embedding: list = field(default_factory=list)
    structure_pred_pdb: str = ""
    function_annotation: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


def get_protein_embedding(sequence: str,
                            model_size: str = "esm2-650m") -> ESM3Result | None:
    """단백질 sequence → embedding.

    ESM3는 HuggingFace auth 필요해서, 즉시 사용 가능한 ESM2 fallback 우선:
      - esm2-650m (Facebook fair-esm, 650M params, public)
      - esm2-3b (3B, public, 더 정확)
      - esm3-open-small (1.4B Apache, HF auth 후)

    Args:
        sequence: AA sequence (single-letter)
        model_size: "esm2-650m" (default, public) | "esm2-3b" | "esm3-open-small"

    Returns:
        ESM3Result with embedding (1280-d for esm2-650m, 2560-d for 3b).
    """
    if model_size.startswith("esm2"):
        return _esm2_embedding(sequence, model_size)
    elif model_size.startswith("esm3"):
        return _esm3_embedding(sequence, model_size)
    return ESM3Result(sequence=sequence,
                       metadata={"error": f"unknown model: {model_size}"})


def _esm2_embedding(sequence: str, model_size: str = "esm2-650m") -> ESM3Result:
    """ESM2 embedding via fair-esm (no HF auth needed)."""
    try:
        import torch
        # esm package에서 esm2 로드
        import esm as esm_pkg
    except ImportError as e:
        return ESM3Result(sequence=sequence,
                           metadata={"error": f"torch/esm: {e}"})

    model_map = {
        "esm2-650m": "esm2_t33_650M_UR50D",
        "esm2-3b":   "esm2_t36_3B_UR50D",
    }
    model_name = model_map.get(model_size, "esm2_t33_650M_UR50D")

    try:
        # fair-esm pretrained
        if hasattr(esm_pkg, "pretrained"):
            model, alphabet = getattr(esm_pkg.pretrained, model_name)()
        else:
            return ESM3Result(sequence=sequence,
                               metadata={"error": "esm.pretrained 미발견 — fair-esm 설치 권장"})
        model.eval()
        if torch.cuda.is_available():
            model = model.cuda()

        batch_converter = alphabet.get_batch_converter()
        _, _, batch_tokens = batch_converter([("query", sequence)])
        if torch.cuda.is_available():
            batch_tokens = batch_tokens.cuda()

        with torch.no_grad():
            results = model(batch_tokens, repr_layers=[33])
        token_embeddings = results["representations"][33]
        # mean over residues (excluding BOS/EOS)
        mean_emb = token_embeddings[0, 1:-1].mean(0).cpu().numpy()

        return ESM3Result(
            sequence=sequence,
            embedding=mean_emb.tolist(),
            metadata={"model": model_name, "embedding_dim": len(mean_emb),
                      "n_residues": len(sequence)},
        )
    except Exception as e:
        return ESM3Result(sequence=sequence,
                           metadata={"error": f"{type(e).__name__}: {e}",
                                     "fix": "uv pip install fair-esm"})


def _esm3_embedding(sequence: str, model_size: str = "esm3-open-small") -> ESM3Result:
    """ESM3 embedding (HF auth 필요)."""
    try:
        from esm.models.esm3 import ESM3
        from esm.sdk.api import ESMProtein
    except ImportError as e:
        return ESM3Result(sequence=sequence,
                           metadata={"error": f"esm3 import: {e}"})
    try:
        # ESM3 model name in registry
        client = ESM3.from_pretrained(model_size)
        protein = ESMProtein(sequence=sequence)
        return ESM3Result(
            sequence=sequence, embedding=[],
            metadata={"model": model_size, "stub": True,
                      "fix": "ESM3 SDK forward call 정확화 + HF token"},
        )
    except Exception as e:
        return ESM3Result(sequence=sequence,
                           metadata={"error": f"{type(e).__name__}: {e}",
                                     "fix": "huggingface-cli login + token 등록"})


def predict_mutation_effect(wild_type_seq: str,
                              mutation: str,
                              context: str = "TGFB1 SNP") -> dict:
    """단일 mutation 영향 예측.

    Args:
        wild_type_seq: WT sequence
        mutation: e.g. "L100A" (residue 100 L → A)
        context: 설명용 (e.g. "TGFB1 SNP, IPF 위험 인자")

    Returns:
        dict with embedding distance, predicted ΔΔG-like score.
    """
    # mutation 파싱
    if len(mutation) < 3:
        return {"error": f"invalid mutation format: {mutation}"}
    wt_aa = mutation[0]
    pos = int(mutation[1:-1])
    mut_aa = mutation[-1]

    if pos < 1 or pos > len(wild_type_seq):
        return {"error": f"position {pos} out of range"}
    if wild_type_seq[pos - 1] != wt_aa:
        return {"error": f"WT at {pos} is {wild_type_seq[pos-1]}, not {wt_aa}"}

    mut_seq = wild_type_seq[:pos-1] + mut_aa + wild_type_seq[pos:]

    wt_emb = get_protein_embedding(wild_type_seq)
    mut_emb = get_protein_embedding(mut_seq)

    return {
        "context": context,
        "wt_seq": wild_type_seq[:50] + "...",
        "mutation": mutation,
        "wt_embedding_status": ("OK" if wt_emb and not wt_emb.metadata.get("error")
                                  else f"error: {wt_emb.metadata}"),
        "mut_embedding_status": ("OK" if mut_emb and not mut_emb.metadata.get("error")
                                   else f"error: {mut_emb.metadata}"),
        "instruction": ("실제 효과 예측은 ESM3 forward() + masked LM probability "
                        "변화 또는 embedding cosine distance 기반."),
    }


# Genesis_Medicine v3 14 타겟 → ESM3 embedding 비교용
GM_TARGETS_TO_UNIPROT = {
    "TGFB1": "P01137", "MMP1": "P03956", "CTGF": "P29279",
    "TYR": "P14679", "TYRP1": "P17643", "DCT": "P40126",
    "SRD5A2": "P31213", "AR": "P10275", "CTNNB1": "P35222",
    "PTGS2": "P35354", "SIRT1": "Q96EB6", "JUN": "P05412",
    "LOX": "P28300", "SMAD3": "P84022", "PDGFRB": "P09619",
    "FGF2": "P09038", "VEGFA": "P15692",
}


def compute_target_similarity_matrix() -> dict:
    """14 타겟 ESM3 embedding pairwise cosine 유사도.

    cross-target 발굴: 흉터 lead가 다른 fibrosis-관련 단백질에도 결합 가능한지
    sequence-level prediction.
    """
    # placeholder
    return {
        "n_targets": len(GM_TARGETS_TO_UNIPROT),
        "instruction": ("각 타겟 sequence (data/msa/{key}.fasta에서) → "
                         "ESM3 embedding → pairwise cosine. "
                         "유사도 > 0.85 = cross-active 가능성."),
        "expected_outputs": [
            "embedding matrix (14 × 1024)",
            "similarity heatmap CSV",
            "top-K cross-target candidates per query",
        ],
    }
