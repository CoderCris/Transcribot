"""Configuración centralizada de logging para Transcribot."""

from __future__ import annotations

import logging
from pathlib import Path

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configura el logger raíz con un StreamHandler y, opcionalmente, un FileHandler.

    Args:
        level: Nivel para el FileHandler y el logger raíz (ej. "DEBUG", "INFO").
        log_file: Ruta opcional al archivo de log. Si es None, solo se usa stderr.

    Notes:
        El StreamHandler solo emite mensajes de WARNING en adelante para no ensuciar
        la salida estándar del CLI. El FileHandler respeta el nivel solicitado.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = logging.Formatter(_LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    if log_file:
        path = Path(log_file).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
