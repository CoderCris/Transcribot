"""Detección de hardware disponible (GPU/CPU) para elegir modelo y compute type."""

from __future__ import annotations

import logging
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
