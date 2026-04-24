"""FlowMol3 어댑터 (MIT, Aug 2025).

https://github.com/Dunni3/FlowMol

SE(3)-equivariant flow matching 기반 3D 분자 생성.
- 거의 100% 분자 유효성
- 확산 모델 대비 10배 적은 파라미터
- Self-conditioning + fake atoms + geometry distortion
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import GeneratedMolecule, GenerationRequest, GenerationResult


class FlowMol3Adapter:
    """FlowMol3 flow matching 3D 생성기."""

    engine_name = "flowmol3"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/flowmol3"),
        checkpoint: Path | None = None,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint = checkpoint
        self.device = device

    def supports_scaffold_hopping(self) -> bool:
        return False

    def supports_linker_design(self) -> bool:
        return False

    def generate(self, req: GenerationRequest) -> GenerationResult:
        t0 = time.time()

        with TemporaryDirectory(prefix="flowmol3_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            out_dir = tmp_dir / "output"
            out_dir.mkdir()

            cmd = [
                "python", "-m", "flowmol.generate",
                "--protein", str(req.protein_structure),
                "--output_dir", str(out_dir),
                "--num_molecules", str(req.num_molecules),
                "--device", self.device,
                "--seed", str(req.seed),
            ]

            if self.checkpoint:
                cmd += ["--checkpoint", str(self.checkpoint)]
            if req.pocket_center:
                cmd += [
                    "--pocket_center",
                    ",".join(str(c) for c in req.pocket_center),
                ]

            logger.info("FlowMol3: {} 분자 생성 시작", req.num_molecules)

            try:
                result = subprocess.run(
                    cmd, check=True, capture_output=True, text=True, timeout=3600,
                )
            except FileNotFoundError:
                raise RuntimeError(
                    "FlowMol3 미설치. "
                    "https://github.com/Dunni3/FlowMol 참고"
                )

            molecules = self._parse_output(out_dir)

        return GenerationResult(
            engine=self.engine_name,
            molecules=molecules,
            wall_seconds=time.time() - t0,
        )

    def _parse_output(self, out_dir: Path) -> list[GeneratedMolecule]:
        """FlowMol3 출력 SDF → GeneratedMolecule 목록."""
        molecules: list[GeneratedMolecule] = []

        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, QED

            for sdf in sorted(out_dir.rglob("*.sdf")):
                supplier = Chem.SDMolSupplier(str(sdf), removeHs=True)
                for mol in supplier:
                    if mol is None:
                        continue
                    smi = Chem.MolToSmiles(mol, canonical=True)
                    molecules.append(
                        GeneratedMolecule(
                            smiles=smi,
                            score=float(mol.GetPropsAsDict().get("score", 0.0)),
                            qed=float(QED.qed(mol)),
                            engine=self.engine_name,
                        )
                    )
        except ImportError:
            # SDF 파싱 실패 시 텍스트 기반 fallback
            for smi_file in sorted(out_dir.rglob("*.smi")):
                for line in smi_file.read_text().strip().splitlines():
                    parts = line.split()
                    if parts:
                        molecules.append(
                            GeneratedMolecule(
                                smiles=parts[0],
                                engine=self.engine_name,
                            )
                        )

        logger.info("FlowMol3: {} 분자 생성 완료", len(molecules))
        return molecules
