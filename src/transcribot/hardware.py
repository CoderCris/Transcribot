"""Detección de hardware disponible (GPU/CPU) para elegir modelo y compute type."""

from __future__ import annotations

import logging
import shutil
from typing import Any

logger = logging.getLogger(__name__)


def detect_device() -> dict[str, Any]:
    """Detecta el dispositivo disponible y sugiere una configuración apropiada.

    Returns:
        Diccionario con claves:
            - device: "cuda" o "cpu"
            - compute_type: "float16" (cuda) o "int8" (cpu)
            - model_size: "large-v3" (cuda con VRAM suficiente) o "medium"
            - gpu_name: nombre de la GPU detectada, o None
            - vram_gb: VRAM en GB (aproximada), o None
    """
    info: dict[str, Any] = {
        "device": "cpu",
        "compute_type": "int8",
        "model_size": "medium",
        "gpu_name": None,
        "vram_gb": None,
    }

    try:
        import torch  # type: ignore[import-not-found]

        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(idx)
            vram_gb = round(props.total_memory / (1024**3), 2)
            info.update(
                {
                    "device": "cuda",
                    "compute_type": "float16",
                    "model_size": "large-v3" if vram_gb >= 8 else "medium",
                    "gpu_name": props.name,
                    "vram_gb": vram_gb,
                }
            )
            logger.info("CUDA detectado vía torch: %s (%.2f GB)", props.name, vram_gb)
            return info
    except Exception as exc:  # noqa: BLE001
        logger.debug("torch no disponible o sin CUDA: %s", exc)

    try:
        import ctranslate2  # type: ignore[import-not-found]

        cuda_count = ctranslate2.get_cuda_device_count()
        if cuda_count > 0:
            info.update(
                {
                    "device": "cuda",
                    "compute_type": "float16",
                    "model_size": "large-v3",
                }
            )
            logger.info("CUDA detectado vía ctranslate2 (%d dispositivos)", cuda_count)
            return info
    except Exception as exc:  # noqa: BLE001
        logger.debug("ctranslate2 no disponible: %s", exc)

    logger.info("No se detectó GPU CUDA; se usará CPU con compute_type=int8")
    return info


def check_system_requirements() -> dict[str, Any]:
    """Verifica dependencias de sistema/Python críticas para el pipeline.

    Returns:
        Diccionario con flags de disponibilidad y una lista `warnings` con mensajes
        accionables para el usuario (strings vacíos implican "todo en orden").
    """
    result: dict[str, Any] = {
        "ffmpeg_available": False,
        "torch_available": False,
        "ctranslate2_available": False,
        "faster_whisper_available": False,
        "warnings": [],
    }

    if shutil.which("ffmpeg"):
        result["ffmpeg_available"] = True
    else:
        result["warnings"].append(
            "ffmpeg no está en PATH; la extracción de audio fallará para formatos "
            "comprimidos (mp3, mp4, m4a, etc.)."
        )

    try:
        import torch  # type: ignore[import-not-found]  # noqa: F401

        result["torch_available"] = True
    except ImportError:
        result["warnings"].append(
            "torch no está instalado; la detección de CUDA intentará via ctranslate2."
        )

    try:
        import ctranslate2  # type: ignore[import-not-found]  # noqa: F401

        result["ctranslate2_available"] = True
    except ImportError:
        result["warnings"].append(
            "ctranslate2 no está instalado; faster-whisper no podrá cargar modelos."
        )

    try:
        import faster_whisper  # noqa: F401

        result["faster_whisper_available"] = True
    except ImportError:
        result["warnings"].append(
            "faster-whisper no está instalado; ejecuta `pip install -e .` de nuevo."
        )

    return result
