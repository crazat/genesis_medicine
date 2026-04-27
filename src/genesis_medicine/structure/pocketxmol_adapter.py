"""PocketXMol 어댑터 (Cell 2026, MIT) — unified atom-level generative.

https://github.com/pengxingang/PocketXMol
DOI: 10.1016/j.cell.2026.01.050

11/13 SBDD benchmark에서 SOTA. **단일 모델로**:
- 소분자 SBDD (structure-based drug design)
- cyclic peptide (약침/주사용 macrocycle)
- linker design (PROTAC, ADC linker)
- protein-protein interaction modulator

라이선스: MIT (2026-02 confirmed). 상업 빌드 OK.

Pipeline 통합 위치:
- generation/ 단계에서 DiffSBDD / FlowMol3와 함께 ensemble
- 약침 (acupoint injection) cyclic peptide vertical에서 unique
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Literal, Optional

from loguru import logger


GenerationMode = Literal[
    "small_molecule",        # 소분자 SBDD
    "cyclic_peptide",         # 약침 / 주사용 macrocycle
    "ppi_modulator",          # PPI 표면 결합제
    "linker",                  # PROTAC / ADC linker
    "fragment_growing",        # fragment-based 확장
    "scaffold_hopping",        # scaffold 변형
]


@dataclass
class PocketXMolRequest:
    target_pdb: Path
    pocket_residues: List[int]
    mode: GenerationMode = "small_molecule"
    num_molecules: int = 100
    seed_ligand_smiles: Optional[str] = None   # scaffold_hopping/fragment_growing용
    macrocycle_size_min: int = 5                # cyclic_peptide 모드
    macrocycle_size_max: int = 15
    use_cofold_consistency: bool = True
    seed: int = 42


@dataclass
class PocketXMolResult:
    smiles: List[str] = field(default_factory=list)
    sdf_path: Optional[Path] = None
    confidence: List[float] = field(default_factory=list)
    pocket_match_score: List[float] = field(default_factory=list)  # 0-1
    method: str = "pocketxmol_cell2026"
    mode: str = "small_molecule"
    available: bool = True
    wall_seconds: float = 0.0
    note: str = ""


class PocketXMolAdapter:
    engine_name = "pocketxmol"
    engine_version = "cell-2026-v1"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/pocketxmol"),
        repo_path: Path = Path("external_tools/pocketxmol"),
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.repo_path = Path(repo_path)
        self.device = device

    def generate(self, req: PocketXMolRequest) -> PocketXMolResult:
        if not self.repo_path.exists():
            return PocketXMolResult(
                available=False,
                note=f"PocketXMol repo not found: {self.repo_path}. "
                      f"Clone: git clone https://github.com/pengxingang/PocketXMol.git",
            )
        t0 = time.time()
        with TemporaryDirectory(prefix="pxmol_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            input_yaml = self._write_input(req, tmp_dir)
            out_dir = tmp_dir / "out"
            out_dir.mkdir()
            try:
                cmd = [
                    "python", str(self.repo_path / "scripts" / "sample.py"),
                    "--config", str(input_yaml),
                    "--outdir", str(out_dir),
                    "--device", self.device,
                ]
                logger.info("PocketXMol 실행 ({}): {}", req.mode, " ".join(cmd))
                subprocess.run(cmd, check=True, timeout=7200)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                return PocketXMolResult(
                    mode=req.mode, available=False,
                    note=f"PocketXMol run failed: {e}",
                )
            return self._parse_output(out_dir, req, t0)

    def _write_input(self, req: PocketXMolRequest, tmp: Path) -> Path:
        cfg = {
            "mode": req.mode,
            "target_pdb": str(req.target_pdb),
            "pocket_residues": req.pocket_residues,
            "num_molecules": req.num_molecules,
            "seed_ligand_smiles": req.seed_ligand_smiles,
            "seed": req.seed,
        }
        if req.mode == "cyclic_peptide":
            cfg["macrocycle_size_min"] = req.macrocycle_size_min
            cfg["macrocycle_size_max"] = req.macrocycle_size_max
        if req.use_cofold_consistency:
            cfg["use_cofold_consistency"] = True
        path = tmp / "config.json"
        path.write_text(json.dumps(cfg, indent=2))
        return path

    def _parse_output(self, out_dir: Path, req: PocketXMolRequest,
                       t0: float) -> PocketXMolResult:
        sdf_files = sorted(out_dir.rglob("*.sdf"))
        sdf = sdf_files[0] if sdf_files else None
        smiles: List[str] = []
        confidences: List[float] = []
        pocket_scores: List[float] = []

        scores_json = list(out_dir.rglob("scores*.json"))
        if scores_json:
            data = json.loads(scores_json[0].read_text())
            for entry in data.get("molecules", []):
                smiles.append(entry.get("smiles", ""))
                confidences.append(float(entry.get("confidence", 0.0)))
                pocket_scores.append(float(entry.get("pocket_match", 0.0)))

        return PocketXMolResult(
            smiles=smiles, sdf_path=sdf, confidence=confidences,
            pocket_match_score=pocket_scores,
            mode=req.mode, wall_seconds=time.time() - t0,
        )
