"""DecompDiff 어댑터 (MIT, ICML 2024).

https://github.com/bytedance/DecompDiff

리간드를 arm + scaffold로 분해하여 포켓 인식 확산 생성.
TargetDiff 대비 큰 폭으로 우수한 친화도 달성.
Scaffold hopping과 R-group 탐색에 특히 유용.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import GeneratedMolecule, GenerationRequest, GenerationResult


class DecompDiffAdapter:
    """DecompDiff scaffold-arm 분해 생성기."""

    engine_name = "decompdiff"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/decompdiff"),
        checkpoint: Path | None = None,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint = checkpoint
        self.device = device

    def supports_scaffold_hopping(self) -> bool:
        return True

    def supports_linker_design(self) -> bool:
        return False

    def generate(self, req: GenerationRequest) -> GenerationResult:
        t0 = time.time()

        with TemporaryDirectory(prefix="decompdiff_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            out_dir = tmp_dir / "output"
            out_dir.mkdir()

            cmd = [
                "python", "-m", "decompdiff.sample",
                "--protein_path", str(req.protein_structure),
                "--outdir", str(out_dir),
                "--num_samples", str(req.num_molecules),
                "--device", self.device,
                "--seed", str(req.seed),
            ]

            if self.checkpoint:
                cmd += ["--checkpoint", str(self.checkpoint)]
            if req.seed_smiles:
                cmd += ["--ref_ligand_smiles", req.seed_smiles[0]]

            logger.info("DecompDiff: {} 분자 생성 시작", req.num_molecules)

            try:
                subprocess.run(
                    cmd, check=True, capture_output=True, text=True, timeout=3600,
                )
            except FileNotFoundError:
                raise RuntimeError(
                    "DecompDiff 미설치. "
                    "https://github.com/bytedance/DecompDiff 참고"
                )

            molecules = self._parse_output(out_dir)

        return GenerationResult(
            engine=self.engine_name,
            molecules=molecules,
            wall_seconds=time.time() - t0,
        )

    def _parse_output(self, out_dir: Path) -> list[GeneratedMolecule]:
        molecules: list[GeneratedMolecule] = []
        try:
            from rdkit import Chem
            from rdkit.Chem import QED

            for sdf in sorted(out_dir.rglob("*.sdf")):
                supplier = Chem.SDMolSupplier(str(sdf), removeHs=True)
                for mol in supplier:
                    if mol is None:
                        continue
                    smi = Chem.MolToSmiles(mol, canonical=True)
                    props = mol.GetPropsAsDict()
                    molecules.append(
                        GeneratedMolecule(
                            smiles=smi,
                            score=float(props.get("vina_score", props.get("score", 0.0))),
                            qed=float(QED.qed(mol)),
                            engine=self.engine_name,
                            extra={
                                "scaffold": props.get("scaffold", ""),
                                "arms": props.get("arms", ""),
                            },
                        )
                    )
        except ImportError:
            for smi_file in sorted(out_dir.rglob("*.smi")):
                for line in smi_file.read_text().strip().splitlines():
                    parts = line.split()
                    if parts:
                        molecules.append(
                            GeneratedMolecule(smiles=parts[0], engine=self.engine_name)
                        )

        logger.info("DecompDiff: {} 분자 생성 완료", len(molecules))
        return molecules
