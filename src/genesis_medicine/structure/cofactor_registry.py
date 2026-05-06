"""Holo cofactor registry loader.

Maps target keys (UniProt-style symbols: MMP1, TYR, SIRT1, …) to the metal
ion / non-ion cofactor CCD codes that should be appended to OpenFold3 /
AQAffinity / Boltz-2 cofold inputs to obtain a holo-form prediction.

Source-of-truth YAML: ``conf/skin_targets/holo_cofactors.yaml``.

Usage:

    from genesis_medicine.structure.cofactor_registry import (
        get_cofactors,
        augment_request_with_cofactors,
    )

    augment_request_with_cofactors(req, target_key="MMP1")

leaves ``req`` with ``metal_ions=["ZN", "ZN", "CA", "CA", "CA"]`` and
``cofactor_ccds=[]`` filled in. Targets with no cofactor entry are no-ops.

The registry is loaded once and cached (LRU). Reloads happen only when the
YAML mtime changes.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = (
    Path(__file__).resolve().parents[3]
    / "conf/skin_targets/holo_cofactors.yaml"
)


@dataclass(frozen=True)
class TargetCofactors:
    target: str
    metal_ions: tuple[str, ...] = ()
    cofactor_ccds: tuple[str, ...] = ()
    holo_pdb_examples: tuple[str, ...] = ()
    note: str = ""

    def is_holo_required(self) -> bool:
        return bool(self.metal_ions) or bool(self.cofactor_ccds)


@dataclass
class CofactorRegistry:
    path: Path
    schema_version: int
    entries: dict[str, TargetCofactors] = field(default_factory=dict)

    def get(self, target: str) -> TargetCofactors:
        if not target:
            return TargetCofactors(target="")
        key = target.upper().replace("-", "").replace(" ", "")
        if key in self.entries:
            return self.entries[key]
        # Try canonical aliases (e.g. TRP1 → TYRP1, TRP2 → DCT, COX2 → PTGS2)
        for alias, canon in _ALIASES.items():
            if key == alias and canon in self.entries:
                return self.entries[canon]
        return TargetCofactors(target=key)


_ALIASES: dict[str, str] = {
    "TRP1": "TYRP1",
    "TYR1": "TYRP1",
    "TRP2": "DCT",
    "TYR2": "DCT",
    "COX2": "PTGS2",
    "TYROSINASE": "TYR",
    "MMP_1": "MMP1",
    "MMP_3": "MMP3",
    "MMP_9": "MMP9",
    "5AR1": "SRD5A1",
    "5AR2": "SRD5A2",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        raise RuntimeError(
            "PyYAML 미설치 — holo cofactor registry 로드 불가"
        ) from exc
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


@lru_cache(maxsize=8)
def _load_registry_cached(path_str: str, mtime: float) -> CofactorRegistry:  # noqa: ARG001
    path = Path(path_str)
    doc = _load_yaml(path)
    schema = int(doc.get("schema_version", 1))
    raw = doc.get("cofactors", {}) or {}
    entries: dict[str, TargetCofactors] = {}
    for k, v in raw.items():
        if not isinstance(v, dict):
            continue
        entries[k.upper()] = TargetCofactors(
            target=k.upper(),
            metal_ions=tuple(v.get("metal_ions") or []),
            cofactor_ccds=tuple(v.get("cofactor_ccds") or []),
            holo_pdb_examples=tuple(v.get("holo_pdb_examples") or []),
            note=str(v.get("note") or ""),
        )
    return CofactorRegistry(path=path, schema_version=schema, entries=entries)


def load_registry(path: Path | None = None) -> CofactorRegistry:
    p = Path(path or os.environ.get("GENESIS_HOLO_COFACTORS", DEFAULT_REGISTRY))
    mtime = p.stat().st_mtime if p.exists() else 0.0
    return _load_registry_cached(str(p), mtime)


def get_cofactors(target: str, *, path: Path | None = None) -> TargetCofactors:
    return load_registry(path).get(target)


def augment_request_with_cofactors(
    request: Any,
    target_key: str,
    *,
    path: Path | None = None,
    overwrite: bool = False,
) -> Any:
    """Append registry-derived metal_ions + cofactor_ccds to a request.

    Mutates ``request`` in place when its fields are lists (Pydantic
    ``StructurePredictionRequest``-style). Returns the same object so
    callers can chain.

    ``overwrite=False`` (default) merges with existing values; set True
    to replace.
    """
    spec = get_cofactors(target_key, path=path)
    if not spec.is_holo_required():
        return request

    def _merge(existing: list, addition: tuple[str, ...]) -> list:
        if overwrite:
            return list(addition)
        merged = list(existing or [])
        merged.extend(addition)
        return merged

    cur_ions = getattr(request, "metal_ions", []) or []
    cur_ccds = getattr(request, "cofactor_ccds", []) or []
    setattr(request, "metal_ions", _merge(cur_ions, spec.metal_ions))
    setattr(request, "cofactor_ccds", _merge(cur_ccds, spec.cofactor_ccds))
    return request
