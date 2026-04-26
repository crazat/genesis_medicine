"""Causal inference adapters: Mendelian randomization + Causal Forests + DoWhy.

Provides paper-tier causal evidence for our anti-fibrotic / depigmenting
target nominations beyond pathway-level association.
"""

from .twosample_mr_adapter import TwoSampleMRAdapter, TwoSampleMRResult

__all__ = ["TwoSampleMRAdapter", "TwoSampleMRResult"]
