"""NeuralPLexer3 어댑터 (Iambic Therapeutics, 2025-09).

https://github.com/iambic-therapeutics/NeuralPLexer3

라이선스
--------
- 코드: BSD-3 (commercial-safe)
- 웨이트: CC-BY-NC-SA 4.0 (research-only)

따라서 LicenseGate가 commercial 빌드에서 'neuralplex3_weights' 사용을 차단.
research 프로파일에서만 사용 가능.

성능
----
- AF3 73% 대비 78% 결합부 정확도 (RMSD ≤ 2 Å)
- 15× 빠름 (단일 L40S)
- 공유결합 ligand, post-translational modification 지원

용도
----
공유 BACE1 inhibitor (FAH65 같은 APP-selective) 같은 covalent ligand 검증.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from .base import StructurePredictionRequest, StructurePredictionResult


class NeuralPLexer3Adapter:
    engine_name = "neuralplexer3"
    engine_version = "3.0-beta"

    def __init__(
        self,
        cache_dir: Path,
        weights_dir: Path | None = None,
        device: str = "cuda:0",
        binary: str = "neuralplexer3",
        covalent: bool = False,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.weights_dir = weights_dir
        self.device = device
        self.binary = binary
        self.covalent = covalent

    def supports_ligands(self) -> bool:
        return True

    def supports_affinity(self) -> bool:
        return False  # NP3는 구조 예측 전용. affinity는 Boltz-2에 위임.

    def supports_covalent(self) -> bool:
        return True

    def predict(self, req: StructurePredictionRequest) -> StructurePredictionResult:
        t0 = time.time()
        with TemporaryDirectory(prefix="np3_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            input_json = self._write_input(req, tmp_dir)
            out_dir = tmp_dir / "out"
            out_dir.mkdir()

            cmd = [
                self.binary, "predict",
                "--input", str(input_json),
                "--output_dir", str(out_dir),
                "--num_samples", str(req.num_samples),
                "--seed", str(req.seed),
                "--device", self.device,
            ]
            if self.weights_dir:
                cmd += ["--weights_dir", str(self.weights_dir)]
            if self.covalent:
                cmd.append("--covalent")

            logger.info("NeuralPLexer3 (research-only): {}", " ".join(cmd[:6]))
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
            except FileNotFoundError:
                logger.warning("NeuralPLexer3 binary 미발견 — research/Dockerfile.np3 빌드 필요.")
                return StructurePredictionResult(
                    cif_path=Path("/dev/null"),
                    plddt_mean=0.0,
                    confidence_json=Path("/dev/null"),
                    engine=self.engine_name,
                    engine_version=self.engine_version,
                    wall_seconds=time.time() - t0,
                )

            return self._parse_output(out_dir, t0)

    def _write_input(self, req: StructurePredictionRequest, tmp: Path) -> Path:
        payload = {
            "protein_sequences": req.protein_sequences,
            "ligands": [{"smiles": l.smiles, "ccd": l.ccd_code} for l in req.ligands],
            "rna_sequences": req.rna_sequences,
            "dna_sequences": req.dna_sequences,
            "num_recycles": req.num_recycles,
        }
        path = tmp / "input.json"
        path.write_text(json.dumps(payload))
        return path

    def _parse_output(self, out_dir: Path, t0: float) -> StructurePredictionResult:
        cifs = sorted(out_dir.rglob("*.cif"))
        if not cifs:
            raise RuntimeError(f"NeuralPLexer3 출력 cif 없음: {out_dir}")
        confidence_files = list(out_dir.rglob("confidence.json"))
        plddt_mean = 0.0
        per_res: list[float] = []
        if confidence_files:
            data = json.loads(confidence_files[0].read_text())
            plddt_mean = float(data.get("plddt_mean", 0.0))
            per_res = data.get("plddt_per_residue", [])
        return StructurePredictionResult(
            cif_path=cifs[0],
            plddt_mean=plddt_mean,
            plddt_per_residue=per_res,
            confidence_json=confidence_files[0] if confidence_files else cifs[0],
            engine=self.engine_name,
            engine_version=self.engine_version,
            wall_seconds=time.time() - t0,
        )
