"""Carga y resolución de configuración para Transcribot."""

from __future__ import annotations

import logging
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

import yaml

from transcribot.hardware import detect_device

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default.yaml"


@dataclass
class TranscribotConfig:
    """Configuración efectiva de una ejecución de Transcribot."""

    model_size: str = "auto"
    language: str = "es"
    chunk_duration: int = 600
    compute_type: str = "auto"
    device: str = "auto"
    hf_token: str | None = None
    output_format: str = "txt"
    log_level: str = "INFO"
    log_file: str | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        logger.warning("Config no encontrada en %s; se usarán defaults del dataclass.", path)
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"El contenido de {path} no es un mapping YAML válido.")
    return data


def _apply_hardware_defaults(cfg: TranscribotConfig) -> TranscribotConfig:
    """Resuelve los campos 'auto' a partir de la detección de hardware."""
    needs_detection = "auto" in {cfg.model_size, cfg.compute_type, cfg.device}
    if not needs_detection:
        return cfg

    hw = detect_device()
    if cfg.device == "auto":
        cfg.device = hw["device"]
    if cfg.compute_type == "auto":
        cfg.compute_type = hw["compute_type"]
    if cfg.model_size == "auto":
        cfg.model_size = hw["model_size"]
    return cfg


def load_config(config_path: Path | None = None, **overrides: Any) -> TranscribotConfig:
    """Carga la configuración desde YAML, aplica overrides y resuelve 'auto'.

    Args:
        config_path: Ruta opcional a un YAML alternativo. Si es None, usa default.yaml.
        **overrides: Valores que sobrescriben lo cargado del YAML (típicamente del CLI).
            Los valores None se ignoran para no pisar lo definido en el YAML.

    Returns:
        Instancia de TranscribotConfig con todos los campos resueltos.
    """
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    data = _load_yaml(path)

    valid_keys = {f.name for f in fields(TranscribotConfig)}
    filtered = {k: v for k, v in data.items() if k in valid_keys}

    for key, value in overrides.items():
        if value is not None and key in valid_keys:
            filtered[key] = value

    cfg = TranscribotConfig(**filtered)
    return _apply_hardware_defaults(cfg)
