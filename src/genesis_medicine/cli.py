"""Genesis_Medicine CLI 진입점.

예:
    python -m genesis_medicine.cli run disease=alzheimer structure=boltz2
    python -m genesis_medicine.cli targets-only disease=alzheimer
"""

from __future__ import annotations

from pathlib import Path

import hydra
import typer
from loguru import logger
from omegaconf import DictConfig, OmegaConf

app = typer.Typer(help="Genesis_Medicine drug & herbal discovery pipeline.")


@app.command()
def version() -> None:
    """버전 출력."""
    from . import __version__

    typer.echo(__version__)


@app.command()
def show_config(path: str = "conf/config.yaml") -> None:
    """현재 설정 덤프."""
    cfg = OmegaConf.load(path)
    typer.echo(OmegaConf.to_yaml(cfg))


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def _hydra_entry(cfg: DictConfig) -> None:
    out = Path(cfg.project.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    logger.add(cfg.logging.file, level=cfg.logging.level, rotation="100 MB")
    logger.info("Genesis_Medicine 시작: {}", cfg.project.name)
    logger.info("Hydra config snapshot:\n{}", OmegaConf.to_yaml(cfg))

    # 실제 파이프라인 호출 (Prefect flow)
    from pipelines.full_pipeline import run

    run(cfg)


@app.command(name="run")
def run_pipeline() -> None:
    """전체 파이프라인 실행 (Hydra 오버라이드는 `--` 이후에)."""
    _hydra_entry()


if __name__ == "__main__":
    app()
