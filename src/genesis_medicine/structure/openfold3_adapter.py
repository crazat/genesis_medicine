"""OpenFold3 어댑터 (Apache-2.0, 2025-10).

https://github.com/aqlaboratory/openfold-3

- AlQuraishi Lab (Columbia) + LLNL + Seoul National.
- AF3급 성능, 신규 리간드 카테고리에서 Boltz-2보다 우수할 수 있음.
- AbbVie/BMS/J&J/Takeda가 federated fine-tuning 중.
- 상업 빌드 안전 (Apache-2.0).
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import (
    StructurePredictionRequest,
    StructurePredictionResult,
    StructurePredictor,
)


class OpenFold3Adapter(StructurePredictor):
    engine_name = "openfold3"
    engine_version = "3.0-2025-10"

    def __init__(
        self,
        cache_dir: Path,
        num_recycles: int = 10,
        num_samples: int = 5,
        use_msa: bool = True,
        msa_dir: Path | None = None,
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.num_recycles = num_recycles
        self.num_samples = num_samples
        self.use_msa = use_msa
        self.msa_dir = msa_dir
        self.device = device

    def supports_ligands(self) -> bool:
        return True

    def supports_affinity(self) -> bool:
        return False  # AQAffinity는 별도 모듈

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="openfold3_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            input_json = self._write_input(req, tmp_dir)
            out_dir = tmp_dir / "output"
            out_dir.mkdir()

            cmd = [
                "python", "-m", "openfold.predict",
                "--input_json", str(input_json),
                "--output_dir", str(out_dir),
                "--num_recycling_iters", str(req.num_recycles),
                "--num_samples", str(self.num_samples),
                "--device", self.device,
                "--seed", str(req.seed),
            ]

            if self.use_msa and self.msa_dir:
                cmd += ["--msa_dir", str(self.msa_dir)]
            elif not self.use_msa:
                cmd.append("--no_msa")

            logger.info("OpenFold3 실행: {}", " ".join(cmd))

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except FileNotFoundError:
                raise RuntimeError(
                    "OpenFold3 미설치. "
                    "https://github.com/aqlaboratory/openfold-3 참고"
                )

            return self._parse_output(out_dir, t0)

    def _write_input(self, req: StructurePredictionRequest, tmp: Path) -> Path:
        """OpenFold3 AF3-style JSON 입력."""
        sequences = []
        for i, seq in enumerate(req.protein_sequences):
            sequences.append({
                "proteinChain": {"sequence": seq, "count": 1, "id": chr(65 + i)}
            })
        for i, lig in enumerate(req.ligands):
            if lig.ccd_code:
                sequences.append({"ligand": {"ccdCode": lig.ccd_code, "count": 1}})
            else:
                sequences.append({"ligand": {"smiles": lig.smiles, "count": 1}})
        for i, rna in enumerate(req.rna_sequences):
            sequences.append({"rnaChain": {"sequence": rna, "count": 1}})

        payload = [{"name": "genesis_openfold3", "sequences": sequences}]
        path = tmp / "input.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def _parse_output(self, out_dir: Path, t0: float) -> StructurePredictionResult:
        cif_files = sorted(out_dir.rglob("*.cif"))
        if not cif_files:
            raise RuntimeError(f"OpenFold3 출력 cif 없음: {out_dir}")
        cif_path = cif_files[0]

        conf_files = list(out_dir.rglob("*confidence*.json")) or list(
            out_dir.rglob("*scores*.json")
        )
        conf_json = conf_files[0] if conf_files else (out_dir / "confidence.json")

        plddt_mean = 0.0
        per_res: list[float] = []
        if conf_json.exists():
            conf = json.loads(conf_json.read_text())
            plddt_mean = float(
                conf.get("plddt_mean", conf.get("mean_plddt", 0.0))
            )
            per_res = conf.get("plddt_per_residue", conf.get("per_residue", []))

        return StructurePredictionResult(
            cif_path=cif_path,
            plddt_mean=plddt_mean,
            plddt_per_residue=per_res,
            confidence_json=conf_json,
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=time.time() - t0,
        )
