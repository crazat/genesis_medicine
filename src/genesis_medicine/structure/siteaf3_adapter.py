"""SiteAF3 어댑터 (PNAS 2026, conditional diffusion AF3 변형).

https://github.com/HaCTang/SiteAF3
https://www.pnas.org/doi/10.1073/pnas.2521048122

핵심 가치:
- AF3-derived 모델이지만 receptor를 고정하고 pocket/hotspot residue를
  주입하는 conditional diffusion. **TGF-β1 / MMP-1 / CTGF 등 우리 stack의
  allosteric / cryptic site 직접 타겟팅** (B 가설 음성 rescue).
- 파라미터 효율 ↑, AF3 대비 less compute.

라이선스 주의: SiteAF3 코드는 공개되어 있으나 AF3-derived 가중치는
**연구 전용** 가능성. 상용 빌드에서는 LicenseGate 차단.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional

from loguru import logger


@dataclass
class SiteAF3Request:
    target_uniprot: str
    target_sequence: str
    pocket_residues: List[int]            # receptor residue index (1-based)
    hotspot_residues: Optional[List[int]] = None
    ligand_smiles: Optional[str] = None    # 선택적, 결합 모드 conditioning
    seed: int = 42
    num_samples: int = 5


@dataclass
class SiteAF3Result:
    cif_path: Optional[Path]
    pocket_score: float                    # 0-1, allosteric site 적합도
    hotspot_engagement: float              # 0-1, hotspot residue 접촉 비율
    plddt_pocket: float
    plddt_global: float
    available: bool = True
    method: str = "siteaf3_pnas2026"
    wall_seconds: float = 0.0
    note: str = ""
    pocket_residues_resolved: List[int] = field(default_factory=list)


class SiteAF3Adapter:
    engine_name = "siteaf3"
    engine_version = "pnas-2026"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/siteaf3"),
        repo_path: Path = Path("external_tools/siteaf3"),
        device: str = "cuda:0",
        license_profile: str = "research",
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.repo_path = Path(repo_path)
        self.device = device
        self.license_profile = license_profile

    def predict(self, req: SiteAF3Request) -> SiteAF3Result:
        if self.license_profile == "commercial":
            return SiteAF3Result(
                cif_path=None, pocket_score=0.0, hotspot_engagement=0.0,
                plddt_pocket=0.0, plddt_global=0.0, available=False,
                note="SiteAF3 가중치 라이선스 검증 전 — commercial 빌드 차단",
            )
        if not self.repo_path.exists():
            return SiteAF3Result(
                cif_path=None, pocket_score=0.0, hotspot_engagement=0.0,
                plddt_pocket=0.0, plddt_global=0.0, available=False,
                note=f"SiteAF3 repo not found: {self.repo_path}",
            )

        t0 = time.time()
        with TemporaryDirectory(prefix="siteaf3_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            input_yaml = self._write_input(req, tmp_dir)
            out_dir = tmp_dir / "out"
            out_dir.mkdir()
            try:
                cmd = [
                    "python", str(self.repo_path / "predict.py"),
                    "--input", str(input_yaml),
                    "--out", str(out_dir),
                    "--device", self.device,
                    "--num_samples", str(req.num_samples),
                ]
                logger.info("SiteAF3 실행: {}", " ".join(cmd))
                subprocess.run(cmd, check=True, timeout=3600)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                return SiteAF3Result(
                    cif_path=None, pocket_score=0.0, hotspot_engagement=0.0,
                    plddt_pocket=0.0, plddt_global=0.0, available=False,
                    note=f"SiteAF3 run failed: {e}",
                )
            return self._parse_output(out_dir, req, t0)

    def _write_input(self, req: SiteAF3Request, tmp: Path) -> Path:
        payload = {
            "target_uniprot": req.target_uniprot,
            "target_sequence": req.target_sequence,
            "pocket_residues": req.pocket_residues,
            "hotspot_residues": req.hotspot_residues or [],
            "ligand_smiles": req.ligand_smiles,
            "seed": req.seed,
        }
        path = tmp / "input.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def _parse_output(self, out_dir: Path, req: SiteAF3Request, t0: float) -> SiteAF3Result:
        cif_paths = sorted(out_dir.rglob("*.cif"))
        cif = cif_paths[0] if cif_paths else None
        scorer = list(out_dir.rglob("score*.json"))
        if scorer:
            sc = json.loads(scorer[0].read_text())
            return SiteAF3Result(
                cif_path=cif,
                pocket_score=float(sc.get("pocket_score", 0.0)),
                hotspot_engagement=float(sc.get("hotspot_engagement", 0.0)),
                plddt_pocket=float(sc.get("plddt_pocket", 0.0)),
                plddt_global=float(sc.get("plddt_global", 0.0)),
                method=self.engine_name,
                wall_seconds=time.time() - t0,
                pocket_residues_resolved=req.pocket_residues,
            )
        return SiteAF3Result(
            cif_path=cif, pocket_score=0.0, hotspot_engagement=0.0,
            plddt_pocket=0.0, plddt_global=0.0,
            method=self.engine_name, wall_seconds=time.time() - t0,
            note="score json 미발견",
        )
