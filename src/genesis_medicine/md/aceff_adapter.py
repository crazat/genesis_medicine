"""AceFF foundation potential 어댑터 (Acellera + ACEsuit, 2026).

References:
- AceFF 1.0/1.1/2.0: arXiv 2026-01 (TensorNet 기반)
- Repo: https://github.com/ACEsuit/aceff (또는 acemd / TorchMD-NET 통합)

핵심 가치:
- MACE-OFF24 동등 또는 우위, **charged 분자 + 12 medchem 원소 명시 학습**
- TGF-β1 (acidic patch), MMP-1 (zinc), tyrosinase (binuclear copper)
  active site에서 MACE-OFF24 한계 극복
- OpenMM-ML 인터페이스 호환 (drop-in replacement for MACE-OFF24)

라이선스: MIT (Acellera/ACEsuit, 2026-01) — commercial 빌드 OK.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal

from loguru import logger


AceFFVariant = Literal["aceff-1.0", "aceff-1.1", "aceff-2.0"]


@dataclass
class AceFFRequest:
    pdb_complex: Path
    ligand_resname: str = "LIG"
    variant: AceFFVariant = "aceff-2.0"
    sim_ns: float = 10.0
    timestep_fs: float = 1.0
    temperature_k: float = 310.0
    use_metal_native: bool = True       # zinc/Mg 직접 처리
    output_dir: Optional[Path] = None


@dataclass
class AceFFResult:
    trajectory_path: Optional[Path]
    rmsd_mean_ang: Optional[float]
    binding_pose_stable: Optional[bool]
    energy_kcal_mean: Optional[float]
    variant: str = "aceff-2.0"
    available: bool = True
    note: str = ""
    wall_seconds: float = 0.0


class AceFFAdapter:
    engine_name = "aceff"
    engine_version = "v2-2026-01"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/aceff"),
        device: str = "cuda:0",
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.device = device

    def simulate(self, req: AceFFRequest) -> AceFFResult:
        t0 = time.time()
        try:
            import torch  # noqa: F401
            try:
                import torchmdnet  # noqa: F401
            except ImportError:
                try:
                    import openmmml  # noqa: F401
                except ImportError:
                    return AceFFResult(
                        trajectory_path=None, rmsd_mean_ang=None,
                        binding_pose_stable=None, energy_kcal_mean=None,
                        variant=req.variant, available=False,
                        note="torchmd-net 또는 openmm-ml 필요. "
                              "pip install torchmd-net or conda install openmm-ml",
                    )
        except ImportError:
            return AceFFResult(
                trajectory_path=None, rmsd_mean_ang=None,
                binding_pose_stable=None, energy_kcal_mean=None,
                variant=req.variant, available=False,
                note="PyTorch not available",
            )

        try:
            from openmm import unit
            from openmm.app import PDBFile, Simulation, ForceField, NoCutoff
            try:
                from openmmml import MLPotential
            except ImportError:
                return AceFFResult(
                    trajectory_path=None, rmsd_mean_ang=None,
                    binding_pose_stable=None, energy_kcal_mean=None,
                    variant=req.variant, available=False,
                    note="openmm-ml 필요. conda install -c conda-forge openmm-ml",
                )
        except ImportError:
            return AceFFResult(
                trajectory_path=None, rmsd_mean_ang=None,
                binding_pose_stable=None, energy_kcal_mean=None,
                variant=req.variant, available=False,
                note="OpenMM 8 필요. conda env genesis-md 활성화",
            )

        if not req.pdb_complex.exists():
            return AceFFResult(
                trajectory_path=None, rmsd_mean_ang=None,
                binding_pose_stable=None, energy_kcal_mean=None,
                variant=req.variant, available=False,
                note=f"PDB not found: {req.pdb_complex}",
            )

        # Skeleton — 실제 구동은 별도 simulator 모듈에 위임
        out = req.output_dir or (self.cache_dir / f"aceff_{int(time.time())}")
        out.mkdir(parents=True, exist_ok=True)
        traj = out / "traj.dcd"
        logger.info("AceFF MD simulation skeleton — variant={}, sim_ns={}",
                     req.variant, req.sim_ns)

        return AceFFResult(
            trajectory_path=traj if traj.exists() else None,
            rmsd_mean_ang=None,
            binding_pose_stable=None,
            energy_kcal_mean=None,
            variant=req.variant,
            available=True,
            note="AceFF adapter scaffold — 실 simulation은 run_aceff_md.py 참조",
            wall_seconds=time.time() - t0,
        )
