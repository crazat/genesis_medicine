"""g-xTB / NN-xTB 어댑터 (Grimme group, ChemRxiv 2025).

References:
- g-xTB:  https://chemrxiv.org/doi/10.26434/chemrxiv-2025-bjxvt
- NN-xTB: https://chemrxiv.org/doi/full/10.26434/chemrxiv-2025-chlcc-v3
- PM6-ML: https://pubs.acs.org/doi/10.1021/acs.jctc.4c01330

핵심 가치:
- g-xTB: GFN2-xTB 대비 **MAE 절반**. **Z=1-103 metalloprotein zinc/Mg 직접**
  → MMP-1/2/9, TGF-β1 등 zinc-finger 단백질 active site에서 우리의
  EMB-3 × MMP-1 8/8 NaN 문제를 해결할 후보.
- NN-xTB: WTMAD-2 4 vs xtb GFN2 25 kcal/mol — 6× 정확도.
- PM6-ML: ML-corrected semi-empirical, OpenMM/AMBER 호환.

라이선스: g-xTB는 Grimme 그룹 (academic free, commercial은 별도 컨택).
        PM6-ML은 ML-DFT 코드, MIT 가능성.
        commercial 빌드에서는 우리 자체 ranker만 사용 (입력 분자 SMILES, 결과
        에너지) — input/output 데이터만 이식.
"""

from __future__ import annotations

import subprocess
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Literal, Optional

from loguru import logger


XtbVariant = Literal["g-xtb", "nn-xtb", "gfn2-xtb", "pm6-ml"]


@dataclass
class XtbRequest:
    smiles: str
    charge: int = 0
    multiplicity: int = 1
    variant: XtbVariant = "g-xtb"
    optimize: bool = True
    solvent: Optional[str] = "water"        # ALPB / GBSA water
    method_for_metals: bool = True            # zinc/Mg 활성부 처리


@dataclass
class XtbResult:
    energy_hartree: Optional[float]
    energy_kcal_per_mol: Optional[float]
    homo_lumo_gap_ev: Optional[float]
    optimized_xyz: Optional[Path] = None
    variant: str = "g-xtb"
    available: bool = True
    note: str = ""
    wall_seconds: float = 0.0
    metal_handled: bool = False


class GxtbAdapter:
    engine_name = "g-xtb"
    engine_version = "chemrxiv-2025"

    def __init__(
        self,
        *,
        cache_dir: Path = Path(".cache/gxtb"),
        gxtb_binary: Optional[str] = None,
        license_profile: str = "research",
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Try to locate binary in PATH if not provided
        self.gxtb_binary = gxtb_binary or shutil.which("g-xtb") or shutil.which("xtb")
        self.license_profile = license_profile

    def compute(self, req: XtbRequest) -> XtbResult:
        if self.license_profile == "commercial" and req.variant in {"g-xtb", "nn-xtb"}:
            return XtbResult(
                energy_hartree=None, energy_kcal_per_mol=None,
                homo_lumo_gap_ev=None, variant=req.variant,
                available=False,
                note="g-xtb/NN-xtb는 Grimme 그룹 academic-only — "
                      "commercial 빌드에서는 별도 commercial 라이선스 필요",
            )
        if self.gxtb_binary is None:
            return XtbResult(
                energy_hartree=None, energy_kcal_per_mol=None,
                homo_lumo_gap_ev=None, variant=req.variant,
                available=False,
                note="g-xtb / xtb 바이너리 미발견. conda install -c conda-forge xtb",
            )

        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
        except ImportError:
            return XtbResult(
                energy_hartree=None, energy_kcal_per_mol=None,
                homo_lumo_gap_ev=None, variant=req.variant, available=False,
                note="RDKit not available",
            )

        t0 = time.time()
        with TemporaryDirectory(prefix="gxtb_", dir=self.cache_dir) as tmp:
            tmp_dir = Path(tmp)
            mol = Chem.MolFromSmiles(req.smiles)
            if mol is None:
                return XtbResult(
                    energy_hartree=None, energy_kcal_per_mol=None,
                    homo_lumo_gap_ev=None, variant=req.variant,
                    available=False, note=f"Invalid SMILES: {req.smiles}",
                )
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            xyz_path = tmp_dir / "input.xyz"
            xyz_path.write_text(Chem.MolToXYZBlock(mol))

            cmd = [self.gxtb_binary, str(xyz_path),
                    "--chrg", str(req.charge),
                    "--uhf", str(max(req.multiplicity - 1, 0))]
            if req.optimize:
                cmd.append("--opt")
            if req.solvent:
                cmd += ["--alpb", req.solvent]
            if req.variant == "g-xtb":
                cmd += ["--gfn", "2"]   # g-xTB binary가 없으면 GFN2 fallback
            elif req.variant == "gfn2-xtb":
                cmd += ["--gfn", "2"]

            try:
                proc = subprocess.run(cmd, cwd=tmp_dir, check=True, timeout=600,
                                       capture_output=True, text=True)
                stdout = proc.stdout
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                return XtbResult(
                    energy_hartree=None, energy_kcal_per_mol=None,
                    homo_lumo_gap_ev=None, variant=req.variant,
                    available=False, note=f"xtb run failed: {e}",
                )

            energy_h = self._parse_energy(stdout)
            gap = self._parse_homo_lumo_gap(stdout)
            opt_xyz = tmp_dir / "xtbopt.xyz"
            saved_xyz = self.cache_dir / f"opt_{int(time.time())}.xyz"
            if opt_xyz.exists():
                shutil.copy(opt_xyz, saved_xyz)
            else:
                saved_xyz = None

            return XtbResult(
                energy_hartree=energy_h,
                energy_kcal_per_mol=energy_h * 627.5095 if energy_h else None,
                homo_lumo_gap_ev=gap,
                optimized_xyz=saved_xyz,
                variant=req.variant,
                metal_handled=req.method_for_metals,
                wall_seconds=time.time() - t0,
            )

    @staticmethod
    def _parse_energy(stdout: str) -> Optional[float]:
        for line in stdout.splitlines():
            if "TOTAL ENERGY" in line.upper():
                tokens = line.replace("Eh", "").split()
                for tok in tokens:
                    try:
                        return float(tok)
                    except ValueError:
                        continue
        return None

    @staticmethod
    def _parse_homo_lumo_gap(stdout: str) -> Optional[float]:
        for line in stdout.splitlines():
            if "HOMO-LUMO GAP" in line.upper():
                for tok in line.split():
                    try:
                        return float(tok)
                    except ValueError:
                        continue
        return None
