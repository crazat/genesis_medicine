"""PocketMiner adapter (Meller et al., Nat Commun 2023; MIT).

Cryptic-pocket prediction GNN — 1-second per-residue scoring of where
ligand-binding sites might emerge from a holo / apo structure beyond
the orthosteric pocket. Critical for our scar / IPF / hyperpigmentation
targets where the orthosteric site is undruggable or saturated.

License: MIT (assumed from Bowman lab convention; verify upstream)
GitHub : https://github.com/Mickdub/gvp-pocketminer (or current fork)
Paper  : Meller et al., Nat Commun 2023, 14, 1-15.

Use case for skin-fibrosis pipeline:
    - TGF-β1 has a known cryptic allosteric pocket in the type-I receptor
      interface (literature precedent).
    - MMP-1 hemopexin-domain allosteric site is poorly characterized.
    - LOX has no orthosteric small-molecule site.
    PocketMiner per-residue probabilities → identify candidate cryptic
    sites for downstream Boltz-2 / Chai-1 cofold + ABFE.

Install path:
    git clone https://github.com/Mickdub/gvp-pocketminer $HOME/PocketMiner
    cd $HOME/PocketMiner && pip install -e . --no-deps
    # weights downloaded automatically on first run
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from loguru import logger


@dataclass
class CrypticSite:
    residue_index: int
    residue_name: str
    cryptic_probability: float
    chain_id: str = "A"


@dataclass
class PocketMinerResult:
    target_pdb: Path
    n_residues: int
    sites: List[CrypticSite] = field(default_factory=list)
    top_threshold: float = 0.5
    method: str = "pocketminer_gnn"
    available: bool = False
    note: str = ""

    def top_sites(self, k: int = 10) -> List[CrypticSite]:
        return sorted(self.sites, key=lambda s: -s.cryptic_probability)[:k]


class PocketMinerAdapter:
    engine_name = "pocketminer"

    def __init__(self, *, cache_dir: Path = Path(".cache/pocketminer"),
                 repo_root: Optional[Path] = None,
                 threshold: float = 0.5):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.repo_root = repo_root or (Path.home() / "PocketMiner")
        self.threshold = threshold
        self._available = self._check_install()

    def _check_install(self) -> bool:
        if self.repo_root.exists():
            return True
        try:
            import pocketminer  # noqa: F401
            return True
        except ImportError:
            return False

    def predict(self, target_pdb: Path) -> PocketMinerResult:
        if not self._available:
            return PocketMinerResult(
                target_pdb=target_pdb, n_residues=0,
                top_threshold=self.threshold, available=False,
                note=("PocketMiner not installed. Clone "
                       "https://github.com/Mickdub/gvp-pocketminer into "
                       "$HOME/PocketMiner; weights download on first run."),
            )

        out_csv = self.cache_dir / f"{target_pdb.stem}_cryptic.csv"
        cmd = [
            "python", str(self.repo_root / "predict_cryptic_sites.py"),
            "--pdb", str(target_pdb),
            "--out", str(out_csv),
        ]
        try:
            subprocess.run(cmd, check=True, timeout=600)
            import pandas as pd
            df = pd.read_csv(out_csv)
            sites = [
                CrypticSite(
                    residue_index=int(r["residue_index"]),
                    residue_name=str(r.get("residue_name", "")),
                    cryptic_probability=float(r["cryptic_probability"]),
                    chain_id=str(r.get("chain", "A")),
                )
                for _, r in df.iterrows()
                if float(r["cryptic_probability"]) > self.threshold
            ]
            return PocketMinerResult(
                target_pdb=target_pdb, n_residues=len(df), sites=sites,
                top_threshold=self.threshold, available=True,
            )
        except Exception as e:
            return PocketMinerResult(
                target_pdb=target_pdb, n_residues=0,
                top_threshold=self.threshold, available=False,
                note=f"runtime error: {str(e)[:200]}",
            )
