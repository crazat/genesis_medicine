"""Protenix v2 어댑터 (ByteDance, Apache-2.0, 2026-04-08).

https://github.com/bytedance/Protenix

- AF3 능가 (antibody-antigen + ligand plausibility)
- 웨이트 포함 완전 오픈, Apache-2.0 상용 허용
- Boltz-2가 실패하거나 대체 검증이 필요할 때 사용
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


class ProtenixAdapter(StructurePredictor):
    engine_name = "protenix"
    engine_version = "v2-2026-04"

    def __init__(
        self,
        cache_dir: Path,
        num_recycles: int = 10,
        diffusion_samples: int = 25,
        num_samples: int = 5,
        use_msa: bool = True,
        msa_server: str = "colabfold",
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.num_recycles = num_recycles
        self.diffusion_samples = diffusion_samples
        self.num_samples = num_samples
        self.use_msa = use_msa
        self.msa_server = msa_server
        self.device = device

    def supports_ligands(self) -> bool:
        return True

    def supports_affinity(self) -> bool:
        return False

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="protenix_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            input_json = self._write_input(req, tmp_dir)
            out_dir = tmp_dir / "out"
            out_dir.mkdir()

            cmd = [
                "protenix", "predict",
                "--input_json_path", str(input_json),
                "--dump_dir", str(out_dir),
                "--seeds", str(req.seed),
                "--cycle", str(req.num_recycles),
                "--sample_diffusion", str(self.diffusion_samples),
                "--num_samples", str(self.num_samples),
            ]
            if self.use_msa:
                cmd += ["--use_msa_server"]

            logger.info("Protenix v2 실행: {}", " ".join(cmd))
            subprocess.run(cmd, check=True)
            return self._parse_output(out_dir, t0)

    def _write_input(self, req: StructurePredictionRequest, tmp: Path) -> Path:
        """Protenix AF3-style JSON 스키마."""
        sequences = []
        for i, seq in enumerate(req.protein_sequences):
            sequences.append(
                {"proteinChain": {"sequence": seq, "count": 1, "id": f"P{i}"}}
            )
        for i, lig in enumerate(req.ligands):
            if lig.ccd_code:
                sequences.append({"ligand": {"ligand": f"CCD_{lig.ccd_code}", "count": 1}})
            else:
                sequences.append({"ligand": {"ligand": lig.smiles, "count": 1}})
        for i, rna in enumerate(req.rna_sequences):
            sequences.append({"rnaSequence": {"sequence": rna, "count": 1, "id": f"R{i}"}})
        for i, dna in enumerate(req.dna_sequences):
            sequences.append({"dnaSequence": {"sequence": dna, "count": 1, "id": f"D{i}"}})

        payload = [{"name": "genesis_job", "sequences": sequences}]
        path = tmp / "input.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def _parse_output(self, out_dir: Path, t0: float) -> StructurePredictionResult:
        cif_candidates = sorted(out_dir.rglob("*_model_0.cif")) or sorted(
            out_dir.rglob("*.cif")
        )
        if not cif_candidates:
            raise RuntimeError(f"Protenix 출력 cif 없음: {out_dir}")
        cif_path = cif_candidates[0]

        conf_candidates = list(out_dir.rglob("summary_confidences*.json")) or list(
            out_dir.rglob("confidence*.json")
        )
        conf_json = conf_candidates[0] if conf_candidates else (out_dir / "confidence.json")

        plddt_mean = 0.0
        per_res: list[float] = []
        if conf_json.exists():
            conf = json.loads(conf_json.read_text())
            plddt_mean = float(conf.get("plddt", {}).get("mean", conf.get("mean_plddt", 0.0)))
            per_res = conf.get("plddt", {}).get("per_residue", [])

        return StructurePredictionResult(
            cif_path=cif_path,
            plddt_mean=plddt_mean,
            plddt_per_residue=per_res,
            confidence_json=conf_json,
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=time.time() - t0,
        )
