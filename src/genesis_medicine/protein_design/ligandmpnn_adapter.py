"""LigandMPNN adapter (Dauparas et al., Nat Methods 2025; MIT).

Sequence design conditioned on ligand contacts. Critically, LigandMPNN
handles metal cofactors (TYR has 2× Cu²⁺, MMP-1 has Zn²⁺) explicitly:
sequence recovery 77.5 % on metal sites vs ProteinMPNN 40.6 %.

License: MIT
GitHub : https://github.com/dauparas/LigandMPNN
Paper  : Nat Methods 2025, 10.1038/s41592-025-02626-1

Use case (Round 6 약침 vertical):
    Combined with RFdiffusion3 + BindCraft, LigandMPNN provides the
    "metal-aware" sequence design step needed for TYR (dicopper) and
    MMP-1 (zinc) targets that off-the-shelf ProteinMPNN underperforms on.

Install path (NOT via pip — pip ligandmpnn pulls torch ≤ 2.2 which
breaks Boltz-2 / Chai-1):
    git clone https://github.com/dauparas/LigandMPNN $HOME/LigandMPNN
    cd $HOME/LigandMPNN && pip install -e . --no-deps
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from loguru import logger


@dataclass
class LigandMPNNResult:
    target_pdb: Path
    n_designs: int
    designed_sequences: List[str] = field(default_factory=list)
    sequence_recovery: Optional[float] = None
    metal_site_recovery: Optional[float] = None
    method: str = "ligandmpnn"
    available: bool = False
    note: str = ""


class LigandMPNNAdapter:
    engine_name = "ligandmpnn"

    def __init__(self, *, cache_dir: Path = Path(".cache/ligandmpnn"),
                 repo_root: Optional[Path] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.repo_root = repo_root or (Path.home() / "LigandMPNN")
        self._available = self._check_install()

    def _check_install(self) -> bool:
        # Either repo cloned or pip-installed (verify import safe before)
        if self.repo_root.exists():
            return True
        try:
            import ligandmpnn  # noqa: F401
            return True
        except ImportError:
            return False

    def design(self, *, target_pdb: Path, n_designs: int = 8,
               temperature: float = 0.1,
               fix_residues: Optional[List[int]] = None,
               metal_aware: bool = True) -> LigandMPNNResult:
        if not self._available:
            return LigandMPNNResult(
                target_pdb=target_pdb, n_designs=n_designs,
                available=False,
                note=("LigandMPNN not installed. "
                       "git clone https://github.com/dauparas/LigandMPNN "
                       "into $HOME/LigandMPNN and `pip install -e . --no-deps`."),
            )

        out_dir = self.cache_dir / target_pdb.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python", str(self.repo_root / "run.py"),
            "--pdb_path", str(target_pdb),
            "--out_folder", str(out_dir),
            "--num_seq_per_target", str(n_designs),
            "--temperature", str(temperature),
        ]
        if metal_aware:
            cmd.extend(["--ligand_mpnn_use_side_chain_context", "1"])
        if fix_residues:
            cmd.extend(["--fixed_residues", ",".join(map(str, fix_residues))])

        try:
            subprocess.run(cmd, check=True, timeout=3600)
            seq_files = sorted(out_dir.glob("seqs/*.fa"))
            sequences = []
            for f in seq_files[:n_designs]:
                lines = f.read_text().strip().split("\n")
                if len(lines) >= 2:
                    sequences.append(lines[1])
            return LigandMPNNResult(
                target_pdb=target_pdb, n_designs=n_designs,
                designed_sequences=sequences,
                available=True,
            )
        except Exception as e:
            return LigandMPNNResult(
                target_pdb=target_pdb, n_designs=n_designs,
                available=False, note=f"runtime error: {str(e)[:200]}",
            )
