"""Entry point del CLI de Transcribot (Click)."""

from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path

import click

from transcribot import __version__
from transcribot.audio import extract_audio
from transcribot.config import load_config
from transcribot.hardware import detect_device
from transcribot.logger import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__, prog_name="transcribot")
def main() -> None:
    """Transcribot — Transcripción local con IA."""


@main.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Ruta del archivo de salida final.",
)
@click.option(
    "--config", "-c", "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Ruta a un YAML de configuración alternativo.",
)
def transcribe(input_path: Path, output: Path | None, config_path: Path | None) -> None:
    """Transcribe un archivo de audio/video.

    En esta oleada (W-001) solo se ejecuta la extracción de audio; la transcripción
    real se implementa en oleadas posteriores.
    """
    cfg = load_config(config_path=config_path)
    setup_logging(cfg.log_level, cfg.log_file)

    output_dir = output.parent if output else None
    wav_path = extract_audio(input_path, output_dir=output_dir)

    click.echo(f"Audio extraído: {wav_path}")
    click.echo("Transcripción: pendiente (se implementa en oleadas futuras).")


@main.command()
def info() -> None:
    """Muestra hardware detectado, configuración activa y versión."""
    cfg = load_config()
    setup_logging(cfg.log_level, cfg.log_file)

    hw = detect_device()

    click.echo(f"transcribot v{__version__}")
    click.echo("")
    click.echo("Hardware detectado:")
    for key, value in hw.items():
        click.echo(f"  {key}: {value}")

    click.echo("")
    click.echo("Configuración activa:")
    for key, value in asdict(cfg).items():
        click.echo(f"  {key}: {value}")


if __name__ == "__main__":
    main()
