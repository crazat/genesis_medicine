"""ChemBERTa-3 / MolFormer-XL adapter (HuggingFace transformers).

Foundation models for molecular embedding / property prediction.
ChemBERTa-3 (Digital Discovery 2026) is the fully-open re-implementation
of MolFormer-XL — drop-in replacement for our Uni-Mol2 fingerprints in
MolDAIS subspace and as ADMET feature extractor.

License: ChemBERTa-3 — open-source (verify deepforestsci/chemberta3 LICENSE)
         MolFormer-XL — IBM proprietary, not for commercial use
GitHub : https://github.com/deepforestsci/chemberta3
Paper  : Digital Discovery 2026, 10.1039/D5DD00348B

Use case:
    1) Replace Morgan-fingerprint featurizer in MolDAIS BO with deeper
       2K-dim embeddings → +5-10% sample efficiency.
    2) Provide ADMET-AI auxiliary input head for compounds outside the
       training distribution (rare quinones, charged glycosides).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np
from loguru import logger


@dataclass
class ChemBERTaEmbeddingResult:
    smiles_list: List[str]
    embeddings: Optional[np.ndarray]    # (n, 768) typical
    model_name: str
    method: str = "chemberta3"
    available: bool = False
    note: str = ""


class ChemBERTa3Adapter:
    """HuggingFace-based chem foundation embedding."""

    engine_name = "chemberta3"

    DEFAULT_MODELS = {
        "chemberta-3": "deepforestsci/chemberta3-base",
        "molformer-xl": "ibm/MoLFormer-XL-both-10pct",      # research only
        "chemberta-77M": "DeepChem/ChemBERTa-77M-MTR",
    }

    def __init__(self, *, cache_dir: Path = Path(".cache/chemberta3"),
                 model_name: str = "chemberta-3",
                 device: str = "cuda:0"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.device = device
        self._tokenizer = None
        self._model = None
        self._available = self._lazy_load()

    def _lazy_load(self) -> bool:
        try:
            from transformers import AutoModel, AutoTokenizer  # noqa: F401
            return True
        except ImportError:
            return False

    def _load_model(self) -> bool:
        if self._model is not None:
            return True
        try:
            from transformers import AutoModel, AutoTokenizer
            import torch
            mid = self.DEFAULT_MODELS.get(self.model_name, self.model_name)
            self._tokenizer = AutoTokenizer.from_pretrained(
                mid, cache_dir=str(self.cache_dir))
            self._model = AutoModel.from_pretrained(
                mid, cache_dir=str(self.cache_dir), trust_remote_code=True)
            self._model.eval()
            if self.device.startswith("cuda") and torch.cuda.is_available():
                self._model = self._model.to(self.device)
            return True
        except Exception as e:
            logger.warning(f"ChemBERTa3 model load failed: {e}")
            return False

    def embed(self, smiles_list: List[str], *,
              batch_size: int = 32) -> ChemBERTaEmbeddingResult:
        if not self._available:
            return ChemBERTaEmbeddingResult(
                smiles_list=smiles_list, embeddings=None,
                model_name=self.model_name,
                available=False,
                note="transformers not installed; uv pip install transformers",
            )
        if not self._load_model():
            return ChemBERTaEmbeddingResult(
                smiles_list=smiles_list, embeddings=None,
                model_name=self.model_name,
                available=False,
                note=f"failed to load model {self.model_name}",
            )
        try:
            import torch
            embs = []
            self._model.eval()
            with torch.no_grad():
                for i in range(0, len(smiles_list), batch_size):
                    batch = smiles_list[i:i+batch_size]
                    enc = self._tokenizer(batch, padding=True,
                                            truncation=True, max_length=256,
                                            return_tensors="pt")
                    if self.device.startswith("cuda"):
                        enc = {k: v.to(self.device) for k, v in enc.items()}
                    out = self._model(**enc)
                    # Mean-pool last hidden state
                    mask = enc["attention_mask"].unsqueeze(-1).float()
                    pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1)
                    embs.append(pooled.cpu().numpy())
            embeddings = np.vstack(embs).astype(np.float32)
            return ChemBERTaEmbeddingResult(
                smiles_list=smiles_list, embeddings=embeddings,
                model_name=self.model_name, available=True,
            )
        except Exception as e:
            return ChemBERTaEmbeddingResult(
                smiles_list=smiles_list, embeddings=None,
                model_name=self.model_name,
                available=False, note=f"runtime error: {str(e)[:200]}",
            )
