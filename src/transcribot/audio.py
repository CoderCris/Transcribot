"""Extracción de audio a WAV 16 kHz mono para alimentar al transcriptor."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".mkv", ".webm", ".flac", ".wma", ".aac"}
)

TARGET_SAMPLE_RATE = 16_000
TARGET_CHANNELS = 1
TARGET_SAMPLE_WIDTH = 2  # 16-bit PCM


def extract_audio(input_path: Path, output_dir: Path | None = None) -> Path:
    """Extrae audio de cualquier contenedor soportado y lo convierte a WAV 16 kHz mono.

    Args:
        input_path: Ruta al archivo fuente (audio o video).
        output_dir: Directorio destino para el WAV. Si es None, se usa un temporal.

    Returns:
        Ruta al WAV generado (16 kHz, mono, 16-bit PCM).

    Raises:
        FileNotFoundError: Si `input_path` no existe.
        ValueError: Si la extensión no está en SUPPORTED_EXTENSIONS.
        RuntimeError: Si ffmpeg/pydub falla al decodificar el archivo.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"El archivo de entrada no existe: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Extensión no soportada: '{suffix}'. "
            f"Soportadas: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="transcribot_"))
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{input_path.stem}.wav"

    try:
        audio = AudioSegment.from_file(input_path)
    except CouldntDecodeError as exc:
        raise RuntimeError(
            f"ffmpeg no pudo decodificar '{input_path}'. "
            "Verifica que ffmpeg esté instalado y en el PATH."
        ) from exc
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffmpeg no está disponible en el PATH. Instálalo para continuar."
        ) from exc

    duration_s = len(audio) / 1000.0
    logger.info(
        "Audio cargado: %s (duración=%.2fs, sr=%d, canales=%d)",
        input_path,
        duration_s,
        audio.frame_rate,
        audio.channels,
    )

    audio = (
        audio.set_frame_rate(TARGET_SAMPLE_RATE)
        .set_channels(TARGET_CHANNELS)
        .set_sample_width(TARGET_SAMPLE_WIDTH)
    )
    audio.export(output_path, format="wav")

    logger.info("WAV 16 kHz mono exportado a: %s", output_path)
    return output_path
